"""Build deterministic nutrition typologies from committed demo districts.

This T2 generator reads only ``district_indicators.json``. It clusters an
explicit list of nutrition prevalence fields and excludes identifiers,
coordinates, metadata, and all existing composite risk scores.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

PYTHON_BACKEND = Path(__file__).resolve().parents[1]
REPO_ROOT = PYTHON_BACKEND.parent
DEMO_DIR = REPO_ROOT / "project_nurture" / "public" / "demo"
DEFAULT_INPUT = DEMO_DIR / "district_indicators.json"
DEFAULT_OUTPUT = DEMO_DIR / "district_typologies.json"

if str(PYTHON_BACKEND) not in sys.path:
    sys.path.insert(0, str(PYTHON_BACKEND))

from manifest_utils import update_manifest  # noqa: E402

SCHEMA_VERSION = "1.0"
DEFAULT_SEED = 42
ROUND_DIGITS = 6
CENTROID_THRESHOLD = 0.5
SILHOUETTE_TIE_TOLERANCE = 1e-12
FEATURES = (
    ("stunting_rate", "stunting"),
    ("severe_stunting_rate", "severe stunting"),
    ("underweight_rate", "underweight"),
    ("wasting_rate", "wasting"),
    ("severe_wasting_rate", "severe wasting"),
    ("overweight_rate", "overweight"),
    ("anemia_rate", "anemia"),
)
PLACEHOLDER_STATUS = (
    "Typologies use documented demo placeholder district values, not authoritative NFHS findings."
)


def generated_at() -> str:
    """Return a UTC timestamp, honoring SOURCE_DATE_EPOCH when provided."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    moment = (
        datetime.fromtimestamp(int(epoch), timezone.utc)
        if epoch is not None
        else datetime.now(timezone.utc)
    )
    return moment.isoformat()


def load_districts(input_path: Path = DEFAULT_INPUT) -> list[dict[str, object]]:
    """Load finite, uniquely keyed district prevalence records."""
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError("district_indicators.json must use schema_version 1.0")
    districts = payload.get("districts")
    if not isinstance(districts, list) or len(districts) < 4:
        raise ValueError("At least four districts are required for silhouette selection")

    slugs: set[str] = set()
    validated = []
    for district in districts:
        slug = district.get("district_slug")
        if not isinstance(slug, str) or not slug:
            raise ValueError("Every district must have a non-empty district_slug")
        if slug in slugs:
            raise ValueError(f"district_slug values must be unique: {slug}")
        slugs.add(slug)
        for field, _ in FEATURES:
            value = district.get(field)
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError(f"{slug}: {field} must be finite")
        validated.append(district)
    return sorted(validated, key=lambda row: str(row["district_slug"]))


def feature_matrix(districts: list[dict[str, object]]) -> np.ndarray:
    """Return the explicit prevalence feature matrix in documented order."""
    return np.asarray(
        [[float(district[field]) for field, _ in FEATURES] for district in districts],
        dtype=float,
    )


def select_clustering(
    standardized: np.ndarray, seed: int
) -> tuple[int, np.ndarray, np.ndarray, float, list[dict[str, float]]]:
    """Evaluate valid k=3..6 and choose highest silhouette, then smallest k."""
    if standardized.ndim != 2 or standardized.shape[0] < 4:
        raise ValueError("A two-dimensional matrix with at least four districts is required")
    if not np.isfinite(standardized).all():
        raise ValueError("Standardized features must be finite")

    sample_count = standardized.shape[0]
    distinct_count = np.unique(standardized, axis=0).shape[0]
    valid_k = range(3, min(6, sample_count - 1, distinct_count) + 1)
    candidates = []
    for k in valid_k:
        model = KMeans(n_clusters=k, random_state=seed, n_init=10)
        labels = model.fit_predict(standardized)
        if np.unique(labels).size != k:
            continue
        score = float(silhouette_score(standardized, labels))
        candidates.append((k, labels, model.cluster_centers_, score))
    if not candidates:
        raise ValueError("No valid k in 3..6 is available for these district profiles")

    best = candidates[0]
    for candidate in candidates[1:]:
        if candidate[3] > best[3] + SILHOUETTE_TIE_TOLERANCE:
            best = candidate
    evaluated = [
        {"k": k, "silhouette": round(score, ROUND_DIGITS)}
        for k, _, _, score in candidates
    ]
    return best[0], best[1], best[2], best[3], evaluated


def _join_terms(terms: list[str]) -> str:
    if len(terms) < 2:
        return terms[0] if terms else ""
    if len(terms) == 2:
        return f"{terms[0]} and {terms[1]}"
    return f"{', '.join(terms[:-1])}, and {terms[-1]}"


def label_for_centroid(centroid: np.ndarray | list[float]) -> tuple[str, str]:
    """Generate a label and one-sentence description from +/-0.5 SD extremes."""
    values = np.asarray(centroid, dtype=float)
    if values.shape != (len(FEATURES),) or not np.isfinite(values).all():
        raise ValueError("Centroid must contain one finite value per feature")
    high = [label for value, (_, label) in zip(values, FEATURES, strict=True) if value >= 0.5]
    low = [label for value, (_, label) in zip(values, FEATURES, strict=True) if value <= -0.5]
    phrases = [*[f"High {label}" for label in high], *[f"low {label}" for label in low]]
    if not phrases:
        return (
            "Near-average profile",
            "No included nutrition prevalence centroid is at least 0.5 SD from the demo mean.",
        )

    label = ", ".join(phrases)
    if high and low:
        description = (
            f"Higher-than-average {_join_terms(high)} and lower-than-average "
            f"{_join_terms(low)} among the included demo districts."
        )
    elif high:
        description = (
            f"Higher-than-average {_join_terms(high)} among the included demo districts."
        )
    else:
        description = (
            f"Lower-than-average {_join_terms(low)} among the included demo districts."
        )
    return label, description


def build_payload(input_path: Path = DEFAULT_INPUT, seed: int = DEFAULT_SEED) -> dict[str, object]:
    """Build the schema-versioned district typology payload in stable order."""
    districts = load_districts(input_path)
    matrix = feature_matrix(districts)
    standardized = StandardScaler().fit_transform(matrix)
    k, raw_labels, centroids, silhouette, evaluated = select_clustering(standardized, seed)

    # Canonicalize KMeans' arbitrary numeric labels by standardized centroid.
    cluster_order = sorted(
        range(k), key=lambda index: tuple(np.round(centroids[index], 12).tolist())
    )
    typology_id_by_raw = {
        raw_label: f"typology-{index + 1}"
        for index, raw_label in enumerate(cluster_order)
    }
    typologies = []
    for raw_label in cluster_order:
        centroid = centroids[raw_label]
        label, description = label_for_centroid(centroid)
        typologies.append(
            {
                "id": typology_id_by_raw[raw_label],
                "label": label,
                "description": description,
                "centroid": {
                    field: round(float(value), ROUND_DIGITS)
                    for value, (field, _) in zip(centroid, FEATURES, strict=True)
                },
            }
        )

    district_assignments = [
        {
            "district_slug": district["district_slug"],
            "typology_id": typology_id_by_raw[int(raw_label)],
        }
        for district, raw_label in zip(districts, raw_labels, strict=True)
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "tier": "demo",
            "generated_at": generated_at(),
            "input": "district_indicators.json",
            "placeholder_status": PLACEHOLDER_STATUS,
            "k": k,
            "silhouette": round(silhouette, ROUND_DIGITS),
            "evaluated_k": evaluated,
            "seed": seed,
            "feature_list": [field for field, _ in FEATURES],
            "standardization": "Population z-scores across included demo districts.",
            "selection": (
                "Highest silhouette for valid k=3..6; smallest k wins within 1e-12."
            ),
        },
        "districts": district_assignments,
        "typologies": typologies,
    }


def write_artifact(output_path: Path = DEFAULT_OUTPUT, seed: int = DEFAULT_SEED) -> dict[str, object]:
    """Write district typologies and update the T2 manifest for the public path."""
    payload = build_payload(DEFAULT_INPUT, seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8"
    )
    if output_path.resolve().parent == DEMO_DIR.resolve():
        update_manifest(
            output_path,
            "python_backend/analytics/district_typologies.py",
            {"seed": seed},
        )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build deterministic T2 district nutrition typologies."
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        payload = write_artifact(args.out, args.seed)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(f"Wrote {args.out}")
    print(
        f"District typologies: {len(payload['districts']):,} districts, "
        f"k={payload['metadata']['k']}"
    )


if __name__ == "__main__":
    main()
