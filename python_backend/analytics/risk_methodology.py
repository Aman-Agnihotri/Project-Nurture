"""Build the deterministic public-demo district percentile risk artifact.

This T2 generator reads only the committed ``district_indicators.json`` demo
artifact. It never reads restricted DHS inputs or locally generated research
outputs.
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
import pandas as pd

PYTHON_BACKEND = Path(__file__).resolve().parents[1]
REPO_ROOT = PYTHON_BACKEND.parent
DEMO_DIR = REPO_ROOT / "project_nurture" / "public" / "demo"
DEFAULT_INPUT = DEMO_DIR / "district_indicators.json"
DEFAULT_OUTPUT = DEMO_DIR / "district_risk.json"

if str(PYTHON_BACKEND) not in sys.path:
    sys.path.insert(0, str(PYTHON_BACKEND))

from manifest_utils import update_manifest  # noqa: E402

SCHEMA_VERSION = "1.0"
WEIGHT_TOLERANCE = 1e-9
ROUND_DIGITS = 6
COMPONENTS = (
    ("stunting", "stunting_rate"),
    ("underweight", "underweight_rate"),
    ("wasting", "wasting_rate"),
)
DEFAULT_WEIGHTS = {
    "stunting": 0.45,
    "underweight": 0.35,
    "wasting": 0.20,
}
PLACEHOLDER_STATUS = (
    "Scores use documented demo placeholder district values, not authoritative NFHS estimates."
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


def validate_weights(values: list[float] | tuple[float, ...]) -> dict[str, float]:
    """Validate three finite, non-negative weights whose sum is one."""
    if len(values) != len(COMPONENTS):
        raise ValueError("Exactly three weights are required: stunting, underweight, wasting")
    numeric = [float(value) for value in values]
    if not all(math.isfinite(value) for value in numeric):
        raise ValueError("Weights must be finite")
    if any(value < 0 for value in numeric):
        raise ValueError("Weights must be non-negative")
    if not math.isclose(sum(numeric), 1.0, rel_tol=0.0, abs_tol=WEIGHT_TOLERANCE):
        raise ValueError(f"Weights must sum to 1 within {WEIGHT_TOLERANCE:g}")
    return {
        component: value
        for (component, _), value in zip(COMPONENTS, numeric, strict=True)
    }


def percentile_ranks(values: np.ndarray | list[float]) -> np.ndarray:
    """Map average ranks to 0..100, preserving ties and endpoint mapping.

    Tied values receive their average one-based rank. Those average ranks are
    then min-max mapped so the observed minimum is exactly 0 and the observed
    maximum is exactly 100. A zero-variance input has no ordering information,
    so every item receives the neutral percentile 50.
    """
    numeric = np.asarray(values, dtype=float)
    if numeric.ndim != 1 or numeric.size == 0:
        raise ValueError("Percentile input must be a non-empty one-dimensional array")
    if not np.isfinite(numeric).all():
        raise ValueError("Percentile input values must be finite")
    ranks = pd.Series(numeric).rank(method="average").to_numpy(dtype=float)
    low = float(ranks.min())
    high = float(ranks.max())
    if math.isclose(low, high, rel_tol=0.0, abs_tol=0.0):
        return np.full(numeric.shape, 50.0, dtype=float)
    return (ranks - low) * 100.0 / (high - low)


def spearman_correlation(
    left: np.ndarray | list[float], right: np.ndarray | list[float]
) -> float | None:
    """Return Spearman correlation using average tied ranks.

    Spearman correlation is undefined when either ranked input has zero
    variance; this function returns ``None`` deliberately in that case.
    """
    left_values = np.asarray(left, dtype=float)
    right_values = np.asarray(right, dtype=float)
    if left_values.ndim != 1 or right_values.ndim != 1:
        raise ValueError("Spearman inputs must be one-dimensional")
    if left_values.size == 0 or left_values.size != right_values.size:
        raise ValueError("Spearman inputs must be non-empty and have equal length")
    if not np.isfinite(left_values).all() or not np.isfinite(right_values).all():
        raise ValueError("Spearman inputs must be finite")

    left_ranks = pd.Series(left_values).rank(method="average").to_numpy(dtype=float)
    right_ranks = pd.Series(right_values).rank(method="average").to_numpy(dtype=float)
    if np.var(left_ranks) == 0 or np.var(right_ranks) == 0:
        return None
    return float(np.corrcoef(left_ranks, right_ranks)[0, 1])


def _renormalized_perturbation(
    weights: dict[str, float], component: str, delta: float
) -> dict[str, float]:
    adjusted = dict(weights)
    # Boundary clipping keeps all otherwise-valid CLI weight vectors usable.
    adjusted[component] = max(0.0, adjusted[component] + delta)
    total = sum(adjusted.values())
    if total <= 0:
        raise ValueError("Sensitivity perturbation produced a zero weight total")
    return {key: value / total for key, value in adjusted.items()}


def sensitivity_scenarios(
    component_percentiles: dict[str, np.ndarray], weights: dict[str, float]
) -> list[dict[str, object]]:
    """Calculate six renormalized +/-0.1 one-component sensitivity scenarios."""
    baseline = sum(
        component_percentiles[component] * weights[component]
        for component, _ in COMPONENTS
    )
    scenarios = []
    for component, _ in COMPONENTS:
        for delta in (-0.1, 0.1):
            scenario_weights = _renormalized_perturbation(weights, component, delta)
            perturbed = sum(
                component_percentiles[name] * scenario_weights[name]
                for name, _ in COMPONENTS
            )
            correlation = spearman_correlation(baseline, perturbed)
            scenarios.append(
                {
                    "id": f"{component}_{'minus' if delta < 0 else 'plus'}_0_1",
                    "component": component,
                    "delta": delta,
                    "weights": {
                        key: round(scenario_weights[key], ROUND_DIGITS)
                        for key, _ in COMPONENTS
                    },
                    "spearman_correlation": (
                        None if correlation is None else round(correlation, ROUND_DIGITS)
                    ),
                }
            )
    return scenarios


def load_districts(input_path: Path = DEFAULT_INPUT) -> list[dict[str, object]]:
    """Load and validate the committed district indicator records."""
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError("district_indicators.json must use schema_version 1.0")
    districts = payload.get("districts")
    if not isinstance(districts, list) or not districts:
        raise ValueError("district_indicators.json must contain at least one district")

    slugs: set[str] = set()
    validated = []
    for district in districts:
        slug = district.get("district_slug")
        if not isinstance(slug, str) or not slug:
            raise ValueError("Every district must have a non-empty district_slug")
        if slug in slugs:
            raise ValueError(f"district_slug values must be unique: {slug}")
        slugs.add(slug)
        for _, field in COMPONENTS:
            value = district.get(field)
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError(f"{slug}: {field} must be finite")
        validated.append(district)
    return sorted(validated, key=lambda row: str(row["district_slug"]))


def build_payload(
    input_path: Path = DEFAULT_INPUT,
    weights: dict[str, float] | None = None,
) -> dict[str, object]:
    """Build the schema-versioned district risk payload in stable order."""
    active_weights = weights or dict(DEFAULT_WEIGHTS)
    active_weights = validate_weights(
        [active_weights[component] for component, _ in COMPONENTS]
    )
    districts = load_districts(input_path)
    components = {
        component: percentile_ranks([float(row[field]) for row in districts])
        for component, field in COMPONENTS
    }
    composite = sum(
        components[component] * active_weights[component]
        for component, _ in COMPONENTS
    )

    output_districts = []
    for index, district in enumerate(districts):
        output_districts.append(
            {
                "district_slug": district["district_slug"],
                **{
                    f"{component}_percentile": round(
                        float(components[component][index]), ROUND_DIGITS
                    )
                    for component, _ in COMPONENTS
                },
                "composite_score": round(float(composite[index]), ROUND_DIGITS),
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "tier": "demo",
            "generated_at": generated_at(),
            "input": "district_indicators.json",
            "placeholder_status": PLACEHOLDER_STATUS,
            "percentile_method": (
                "Average tied ranks, min-max mapped to 0-100; zero variance maps to 50."
            ),
            "weights": active_weights,
            "weight_sum_tolerance": WEIGHT_TOLERANCE,
        },
        "districts": output_districts,
        "sensitivity": sensitivity_scenarios(components, active_weights),
    }


def write_artifact(
    output_path: Path = DEFAULT_OUTPUT,
    weights: dict[str, float] | None = None,
) -> dict[str, object]:
    """Write district risk JSON and update the T2 manifest for the public path."""
    payload = build_payload(DEFAULT_INPUT, weights)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8"
    )
    if output_path.resolve().parent == DEMO_DIR.resolve():
        update_manifest(
            output_path,
            "python_backend/analytics/risk_methodology.py",
            {"weights": payload["metadata"]["weights"]},
        )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the deterministic T2 district percentile risk artifact."
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--weights",
        nargs=3,
        type=float,
        metavar=("STUNTING", "UNDERWEIGHT", "WASTING"),
        default=list(DEFAULT_WEIGHTS.values()),
        help=(
            "Finite non-negative weights that sum to 1 within "
            f"{WEIGHT_TOLERANCE:g} (default: 0.45 0.35 0.20)."
        ),
    )
    args = parser.parse_args()
    try:
        weights = validate_weights(args.weights)
        payload = write_artifact(args.out, weights)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(f"Wrote {args.out}")
    print(f"District risk records: {len(payload['districts']):,}")


if __name__ == "__main__":
    main()
