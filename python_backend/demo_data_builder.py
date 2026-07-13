"""Deterministic synthetic "demo" (T2) child-nutrition dataset builder.

PURPOSE
-------
Produces `project_nurture/public/demo/demo_cluster_nutrition.json`, a
publicly committable, fully synthetic stand-in for the restricted-local
`dhs_cluster_nutrition.json` payload produced by `dhs_pipeline.py`. The demo
tier lets the frontend ship and run without any DHS microdata present.

DATA TIER
---------
This script is T2: it reads ONLY the committed, public fact-sheet CSV at
`python_backend/data/nfhs5_district_factsheet.csv` (district-level published
NFHS-5 numbers). It never reads, lists, or otherwise touches `dhs_data/`,
`project_nurture/public/generated/`, or `python_backend/outputs/`. All
per-cluster and per-segment numbers below this district level are
synthetically generated and are NOT real survey observations.

STRUCTURAL PARITY WITH dhs_pipeline.py
---------------------------------------
The output JSON has exactly the same top-level shape the India pipeline
emits (`metadata`, `cluster_segment_columns`, `national`, `states`,
`clusters`, `cluster_segments`), the same `cluster_columns`,
`state_columns`, `national_columns`, and `segment_columns` field lists
(copied verbatim from dhs_pipeline.py lines ~404-478), the same
`sample_quality` thresholds (haz_valid_n >= 10 -> "stable"; 5-9 ->
"limited"; else -> "sparse"; dhs_pipeline.py lines ~357-364), the same
weighted-rate / weighted-mean-z / risk-score formulas (dhs_pipeline.py
lines ~236-277, mirrored in project_nurture/src/lib/nutritionData.js lines
~181-225), and the same row sort orders (clusters by
["state_name","district_name","cluster_id"]; segments by
["state_name","district_name","cluster_id","sex","wealth","age_band"]).

Per dhs_pipeline.py's own column lists, the cluster/state/national records
do NOT include severe_underweight_rate or severe_anemia_rate as output
rate fields (only the underlying segment-level weighted numerators
severely_underweight_w / severe_anemia_w exist) -- this builder matches
that omission exactly, even though it also computes those two derived
rates internally at the segment level.

METADATA
--------
`metadata` here intentionally carries far fewer keys than the pipeline's
metadata block. It omits `name`, `survey`, `source_files`, `unit`,
`local_only`, `privacy_note`, `coverage_note`, `indicator_notes`, and
`label_maps` because no frontend code path
(project_nurture/src/lib/nutritionData.js) reads any of those keys; the
only metadata key the frontend consumes is `filter_dimensions`
(nutritionData.js line ~584: `dashboardData.metadata?.filter_dimensions`).
Instead this builder emits: `schema_version` ("legacy", matching the value
now also stamped onto the restricted pipeline's metadata), `tier`
("demo"), `generated_at`, `seed`, a `disclaimer` describing the synthetic
nature of the data, and `filter_dimensions` (sex/wealth/age_band label
lists, structured identically to dhs_pipeline.py's
metadata["filter_dimensions"], lines ~536-540).

LABELS
------
Sex and wealth-quintile labels follow the standard DHS/NFHS codebook value
labels for hv104 (sex: 1=Male, 2=Female) and hv270 (wealth index:
1=Poorest, 2=Poorer, 3=Middle, 4=Richer, 5=Richest) -- these are public
DHS coding conventions, not values read from any restricted microdata
file. Age bands reuse dhs_pipeline.py's exact hardcoded labels
("0-5 months", "6-23 months", "24-59 months"; dhs_pipeline.py lines
~141-149 and ~539).

SYNTHESIS -- PLAUSIBILITY RULES (NOT REAL STATISTICS)
-------------------------------------------------------
All numbers below the district level in the fact-sheet CSV are invented
by these fixed, documented rules so the payload is internally consistent
and exercises every dashboard code path. None of these rules encode any
real epidemiological relationship; they exist only to produce a
plausible-looking, deterministic demo dataset.

0. GAP RESOLUTION -- severe_underweight_rate / severe_anemia_rate: the
   fact-sheet CSV has no columns for these two indicators. District base
   values for them are derived as fixed synthetic plausibility fractions
   of their parent indicators (chosen only so all 9 weighted numerator
   fields are populated and internally consistent; a maintainer may
   revise these fractions):
       severe_underweight_rate = 0.4 * underweight_rate
       severe_anemia_rate      = 0.1 * anemia_rate

1. RNG: a single `numpy.random.default_rng(seed)` instance is created once
   and consumed in a fixed, deterministic order: CSV rows in file order;
   within a district, clusters in index order 0..N-1; within a cluster,
   draws happen in this fixed sequence: latitude offset, longitude offset,
   the 9 indicator noise draws (in INDICATOR_ORDER, see below),
   child_count, then (if there is a remainder) the segment-remainder
   `rng.choice` draw.

2. Per district: `--clusters-per-district` (N) clusters are generated.
   Each cluster's position is `centroid + independent Normal(0, 0.15)` on
   each of latitude/longitude. Urban/rural: the first `round(N *
   urban_share)` clusters (by index) are "Urban", the remainder "Rural"
   (deterministic by index, not by an additional RNG draw).

3. Cluster base value per indicator (the 7 fact-sheet indicators --
   stunting_rate, severe_stunting_rate, underweight_rate, wasting_rate,
   severe_wasting_rate, overweight_rate, anemia_rate -- plus the 2 derived
   severe rates from rule 0) = district value + Normal(0, 0.10 *
   district value), clipped to [0, 100].

4. child_count per cluster: `rng.integers(15, 41)` (i.e. 15..40
   inclusive). It is distributed over the 30-way segment cross-product
   (2 sexes x 5 wealth quintiles x 3 age bands) as evenly as possible:
   `base = child_count // 30` per segment, remainder `r = child_count %
   30` extra children assigned one each to `r` segments chosen via
   `rng.choice(30, size=r, replace=False)` over a fixed canonical
   enumeration order of the 30 segments (itertools.product over
   SEX_ORDER, WEALTH_ORDER, AGE_BANDS). Every segment count is >= 0 and
   the segment counts sum exactly to child_count.

5. Segment rate multipliers, applied to each cluster's base indicator
   value, then the combined result is clipped to [0, 100]:
     - residence (cluster attribute): rural clusters multiply
       stunting_rate, severe_stunting_rate, underweight_rate, and
       severe_underweight_rate by x1.15. Other indicators are
       unaffected by residence.
     - wealth: applies to ALL 9 indicators. Multiplier is linear across
       the five quintiles from x1.30 (Poorest) down to x1.00 (Richest):
       Poorest=1.30, Poorer=1.225, Middle=1.15, Richer=1.075,
       Richest=1.00 (`numpy.linspace(1.30, 1.00, 5)`).
     - sex: applies to ALL 9 indicators. Male x1.03, Female x0.97 (this
       assignment is an arbitrary synthetic choice with no epidemiological
       basis).
     - age bands: applies ONLY to wasting_rate and severe_wasting_rate.
       x1.2 in the "6-23 months" band, x0.9 in "0-5 months" and
       "24-59 months".

6. Weighted fields per segment (n = the segment's child_count from rule
   4): haz_den_w = waz_den_w = whz_den_w = anemia_den_w = float(n);
   haz_valid_n = waz_valid_n = whz_valid_n = anemia_valid_n = n (no
   missingness is modeled in the demo tier). Each of the 9 numerator
   fields is `(segment_rate_X / 100) * matching_den_w` (stunted_w /
   severely_stunted_w <- haz_den_w; underweight_w /
   severely_underweight_w <- waz_den_w; wasted_w / severely_wasted_w /
   overweight_w <- whz_den_w; anemia_w / severe_anemia_w <-
   anemia_den_w). Z-score sums use a synthetic monotone mapping from the
   segment's own stunting/underweight/wasting rate (documented as
   synthetic, not a real anthropometric relationship):
       mean_haz = -min(segment_stunting_rate / 20, 3)
       mean_waz = -min(segment_underweight_rate / 20, 3)
       mean_whz = -min(segment_wasting_rate / 20, 3)
       haz_z_w = mean_haz * haz_den_w * 100  (and likewise waz_z_w, whz_z_w)

7. Cluster (and state / national) records are DERIVED from segment sums
   using the exact formulas dhs_pipeline.py / nutritionData.js use:
   rate = 100 * sum(numerator) / sum(matching denominator); mean_z =
   sum(z_w) / sum(den_w) / 100; risk_score = 0.45 * stunting_rate + 0.35
   * underweight_rate + 0.20 * wasting_rate. child_count and the four
   *_valid_n fields are the segment sums. sample_quality is derived from
   the aggregated haz_valid_n using the pipeline's exact thresholds.

DETERMINISM
------------
All floats are rounded to 6 decimal places and NaN/Inf collapse to
`None`, mirroring dhs_pipeline.py's `_sanitize` (lines ~285-299).
`generated_at` uses `SOURCE_DATE_EPOCH` (as an integer Unix timestamp) if
set in the environment, else the current UTC time. The payload is
serialized with `json.dumps(payload, sort_keys=True, separators=(",",
":"))`, so the same `--seed` and the same `SOURCE_DATE_EPOCH` always
produce a byte-identical file.

Note: this demo builder emits the full sex x wealth x age_band
cross-product (30 segments) per cluster, including zero-count segments,
whereas the real pipeline (dhs_pipeline.py) emits only observed
combinations -- both are internally consistent and intentional.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from manifest_utils import update_manifest
    from name_normalization import normalize
except ImportError:  # running as a script from repo root rather than python_backend/
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from manifest_utils import update_manifest
    from name_normalization import normalize

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    REPO_ROOT / "project_nurture" / "public" / "demo" / "demo_cluster_nutrition.json"
)
DEFAULT_DISTRICT_OUTPUT = (
    REPO_ROOT / "project_nurture" / "public" / "demo" / "district_indicators.json"
)
DEFAULT_INPUT = Path(__file__).resolve().parent / "data" / "nfhs5_district_factsheet.csv"
DEMO_DIR = REPO_ROOT / "project_nurture" / "public" / "demo"

DISCLAIMER = (
    "Synthetic demonstration data derived from published NFHS-5 district fact "
    "sheets. Cluster locations are randomly generated and do not represent real "
    "survey clusters."
)

SEX_ORDER = ["Female", "Male"]
SEX_MULTIPLIERS = {"Male": 1.03, "Female": 0.97}

WEALTH_ORDER = ["Poorest", "Poorer", "Middle", "Richer", "Richest"]
WEALTH_MULTIPLIERS = dict(zip(WEALTH_ORDER, np.linspace(1.30, 1.00, 5)))

AGE_BANDS = ["0-5 months", "6-23 months", "24-59 months"]
AGE_WASTING_MULTIPLIERS = {
    "0-5 months": 0.9,
    "6-23 months": 1.2,
    "24-59 months": 0.9,
}

INDICATOR_ORDER = [
    "stunting_rate",
    "severe_stunting_rate",
    "underweight_rate",
    "severe_underweight_rate",
    "wasting_rate",
    "severe_wasting_rate",
    "overweight_rate",
    "anemia_rate",
    "severe_anemia_rate",
]

RESIDENCE_AFFECTED = {
    "stunting_rate",
    "severe_stunting_rate",
    "underweight_rate",
    "severe_underweight_rate",
}
AGE_AFFECTED = {"wasting_rate", "severe_wasting_rate"}

# Indicator -> (numerator field, denominator field), mirrors
# dhs_pipeline.py's _add_indicator_columns (lines ~244-277) and
# nutritionData.js addDerivedIndicators (lines ~187-213).
INDICATOR_FIELD_MAP = {
    "stunting_rate": ("stunted_w", "haz_den_w"),
    "severe_stunting_rate": ("severely_stunted_w", "haz_den_w"),
    "underweight_rate": ("underweight_w", "waz_den_w"),
    "severe_underweight_rate": ("severely_underweight_w", "waz_den_w"),
    "wasting_rate": ("wasted_w", "whz_den_w"),
    "severe_wasting_rate": ("severely_wasted_w", "whz_den_w"),
    "overweight_rate": ("overweight_w", "whz_den_w"),
    "anemia_rate": ("anemia_w", "anemia_den_w"),
    "severe_anemia_rate": ("severe_anemia_w", "anemia_den_w"),
}

# Copied verbatim (field list + order) from dhs_pipeline.py segment_columns,
# lines ~452-478.
SEGMENT_COLUMNS = [
    "cluster_id",
    "sex",
    "wealth",
    "age_band",
    "child_count",
    "haz_valid_n",
    "waz_valid_n",
    "whz_valid_n",
    "anemia_valid_n",
    "haz_den_w",
    "waz_den_w",
    "whz_den_w",
    "anemia_den_w",
    "stunted_w",
    "severely_stunted_w",
    "underweight_w",
    "severely_underweight_w",
    "wasted_w",
    "severely_wasted_w",
    "overweight_w",
    "anemia_w",
    "severe_anemia_w",
    "haz_z_w",
    "waz_z_w",
    "whz_z_w",
]

# Copied from dhs_pipeline.py cluster_columns, lines ~404-430.
CLUSTER_COLUMNS = [
    "cluster_id",
    "dhs_id",
    "state_code_gps",
    "state_name",
    "district_name",
    "urban_rural_gps",
    "latitude",
    "longitude",
    "child_count",
    "haz_valid_n",
    "waz_valid_n",
    "whz_valid_n",
    "anemia_valid_n",
    "stunting_rate",
    "severe_stunting_rate",
    "underweight_rate",
    "wasting_rate",
    "severe_wasting_rate",
    "overweight_rate",
    "anemia_rate",
    "mean_haz",
    "mean_waz",
    "mean_whz",
    "risk_score",
    "sample_quality",
]

# Copied from dhs_pipeline.py state_columns, lines ~431-450.
STATE_COLUMNS = [
    "state_code",
    "state_name",
    "child_count",
    "haz_valid_n",
    "waz_valid_n",
    "whz_valid_n",
    "anemia_valid_n",
    "stunting_rate",
    "severe_stunting_rate",
    "underweight_rate",
    "wasting_rate",
    "severe_wasting_rate",
    "overweight_rate",
    "anemia_rate",
    "mean_haz",
    "mean_waz",
    "mean_whz",
    "risk_score",
]

# Copied from dhs_pipeline.py national_columns, lines ~480-497.
NATIONAL_COLUMNS = [
    "child_count",
    "haz_valid_n",
    "waz_valid_n",
    "whz_valid_n",
    "anemia_valid_n",
    "stunting_rate",
    "severe_stunting_rate",
    "underweight_rate",
    "wasting_rate",
    "severe_wasting_rate",
    "overweight_rate",
    "anemia_rate",
    "mean_haz",
    "mean_waz",
    "mean_whz",
    "risk_score",
]

# Copied verbatim from project_nurture/src/lib/nutritionData.js sumFields,
# lines ~47-69.
SUM_FIELDS = [
    "child_count",
    "haz_valid_n",
    "waz_valid_n",
    "whz_valid_n",
    "anemia_valid_n",
    "haz_den_w",
    "waz_den_w",
    "whz_den_w",
    "anemia_den_w",
    "stunted_w",
    "severely_stunted_w",
    "underweight_w",
    "severely_underweight_w",
    "wasted_w",
    "severely_wasted_w",
    "overweight_w",
    "anemia_w",
    "severe_anemia_w",
    "haz_z_w",
    "waz_z_w",
    "whz_z_w",
]

SEGMENT_ENUMERATION = list(itertools.product(SEX_ORDER, WEALTH_ORDER, AGE_BANDS))


def _sanitize(value: object) -> object:
    """Mirrors dhs_pipeline.py's _sanitize (lines ~285-299)."""
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return round(number, 6)
    if isinstance(value, float):
        return round(value, 6)
    return value


def _slug(value: object) -> str:
    """Stable public route key; the source name remains in each record."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower().replace("&", " and ")
    slug = "".join(char if char.isalnum() else "-" for char in text)
    return re.sub(r"-+", "-", slug).strip("-") or "unnamed"


def _unique_slug(value: object, used: dict[str, int]) -> str:
    base = _slug(value)
    count = used.get(base, 0)
    used[base] = count + 1
    return f"{base}-{count + 1}" if count else base


def _sample_quality(haz_valid_n: int) -> str:
    """Mirrors dhs_pipeline.py's sample_quality rule (lines ~357-364),
    derived from haz_valid_n: >=10 -> stable; 5-9 -> limited; else sparse."""
    if haz_valid_n >= 10:
        return "stable"
    if 5 <= haz_valid_n <= 9:
        return "limited"
    return "sparse"


def _weighted_rate(numerator: float, denominator: float) -> float | None:
    return (100 * numerator / denominator) if denominator > 0 else None


def _weighted_mean_z(numerator: float, denominator: float) -> float | None:
    return (numerator / denominator / 100) if denominator > 0 else None


def _add_derived_indicators(agg: dict[str, float]) -> dict[str, object]:
    """Mirrors nutritionData.js addDerivedIndicators (lines ~187-213) /
    dhs_pipeline.py _add_indicator_columns (lines ~244-277)."""
    summary = dict(agg)

    summary["stunting_rate"] = _weighted_rate(summary["stunted_w"], summary["haz_den_w"])
    summary["severe_stunting_rate"] = _weighted_rate(
        summary["severely_stunted_w"], summary["haz_den_w"]
    )
    summary["underweight_rate"] = _weighted_rate(summary["underweight_w"], summary["waz_den_w"])
    summary["severe_underweight_rate"] = _weighted_rate(
        summary["severely_underweight_w"], summary["waz_den_w"]
    )
    summary["wasting_rate"] = _weighted_rate(summary["wasted_w"], summary["whz_den_w"])
    summary["severe_wasting_rate"] = _weighted_rate(
        summary["severely_wasted_w"], summary["whz_den_w"]
    )
    summary["overweight_rate"] = _weighted_rate(summary["overweight_w"], summary["whz_den_w"])
    summary["anemia_rate"] = _weighted_rate(summary["anemia_w"], summary["anemia_den_w"])
    summary["severe_anemia_rate"] = _weighted_rate(
        summary["severe_anemia_w"], summary["anemia_den_w"]
    )

    summary["mean_haz"] = _weighted_mean_z(summary["haz_z_w"], summary["haz_den_w"])
    summary["mean_waz"] = _weighted_mean_z(summary["waz_z_w"], summary["waz_den_w"])
    summary["mean_whz"] = _weighted_mean_z(summary["whz_z_w"], summary["whz_den_w"])

    core = [summary["stunting_rate"], summary["underweight_rate"], summary["wasting_rate"]]
    if all(value is not None for value in core):
        summary["risk_score"] = core[0] * 0.45 + core[1] * 0.35 + core[2] * 0.20
    else:
        summary["risk_score"] = None

    return summary


def _aggregate_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    agg = {field: 0.0 for field in SUM_FIELDS}
    for row in rows:
        for field in SUM_FIELDS:
            agg[field] += float(row.get(field) or 0)
    return _add_derived_indicators(agg)


def _generate_segments(
    rng: np.random.Generator,
    cluster_id: int,
    cluster_base: dict[str, float],
    urban_rural: str,
) -> list[dict[str, object]]:
    child_count = int(rng.integers(15, 41))

    base_n = child_count // 30
    remainder = child_count - base_n * 30
    counts = [base_n] * 30
    if remainder > 0:
        extra_idx = rng.choice(30, size=remainder, replace=False)
        for idx in extra_idx:
            counts[int(idx)] += 1

    segments = []
    for (sex, wealth, age_band), n in zip(SEGMENT_ENUMERATION, counts):
        rates = {}
        for indicator in INDICATOR_ORDER:
            value = cluster_base[indicator]
            if indicator in RESIDENCE_AFFECTED and urban_rural == "Rural":
                value *= 1.15
            value *= WEALTH_MULTIPLIERS[wealth]
            value *= SEX_MULTIPLIERS[sex]
            if indicator in AGE_AFFECTED:
                value *= AGE_WASTING_MULTIPLIERS[age_band]
            rates[indicator] = min(max(value, 0.0), 100.0)

        den = float(n)
        row = {
            "cluster_id": cluster_id,
            "sex": sex,
            "wealth": wealth,
            "age_band": age_band,
            "child_count": n,
            "haz_valid_n": n,
            "waz_valid_n": n,
            "whz_valid_n": n,
            "anemia_valid_n": n,
            "haz_den_w": den,
            "waz_den_w": den,
            "whz_den_w": den,
            "anemia_den_w": den,
        }
        for indicator, (num_field, den_field) in INDICATOR_FIELD_MAP.items():
            row[num_field] = (rates[indicator] / 100) * row[den_field]

        mean_haz = -min(rates["stunting_rate"] / 20, 3)
        mean_waz = -min(rates["underweight_rate"] / 20, 3)
        mean_whz = -min(rates["wasting_rate"] / 20, 3)
        row["haz_z_w"] = mean_haz * row["haz_den_w"] * 100
        row["waz_z_w"] = mean_waz * row["waz_den_w"] * 100
        row["whz_z_w"] = mean_whz * row["whz_den_w"] * 100

        segments.append(row)

    return segments


def build_demo_data(input_path: Path, output_path: Path, seed: int, clusters_per_district: int) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Missing fact-sheet CSV: {input_path}")

    df = pd.read_csv(input_path)
    rng = np.random.default_rng(seed)

    state_codes: dict[str, int] = {}
    next_state_code = 1

    all_clusters: list[dict[str, object]] = []
    all_segments_by_cluster: dict[int, list[dict[str, object]]] = {}
    cluster_meta: dict[int, dict[str, object]] = {}

    cluster_id = 0

    for _, district in df.iterrows():
        state_name = str(district["state_name"])
        district_name = str(district["district_name"])

        if state_name not in state_codes:
            state_codes[state_name] = next_state_code
            next_state_code += 1
        state_code_gps = state_codes[state_name]

        district_values = {
            "stunting_rate": float(district["stunting_rate"]),
            "severe_stunting_rate": float(district["severe_stunting_rate"]),
            "underweight_rate": float(district["underweight_rate"]),
            "severe_underweight_rate": 0.4 * float(district["underweight_rate"]),
            "wasting_rate": float(district["wasting_rate"]),
            "severe_wasting_rate": float(district["severe_wasting_rate"]),
            "overweight_rate": float(district["overweight_rate"]),
            "anemia_rate": float(district["anemia_rate"]),
            "severe_anemia_rate": 0.1 * float(district["anemia_rate"]),
        }

        urban_share = float(district["urban_share"])
        urban_count = round(clusters_per_district * urban_share)

        for i in range(clusters_per_district):
            cluster_id += 1

            lat = float(district["centroid_lat"]) + float(rng.normal(0, 0.15))
            lon = float(district["centroid_lon"]) + float(rng.normal(0, 0.15))
            urban_rural = "Urban" if i < urban_count else "Rural"

            cluster_base = {}
            for indicator in INDICATOR_ORDER:
                district_value = district_values[indicator]
                noise = float(rng.normal(0, 0.10 * district_value))
                cluster_base[indicator] = min(max(district_value + noise, 0.0), 100.0)

            segments = _generate_segments(rng, cluster_id, cluster_base, urban_rural)
            all_segments_by_cluster[cluster_id] = segments

            cluster_meta[cluster_id] = {
                "dhs_id": f"DEMO{cluster_id:05d}",
                "state_code_gps": state_code_gps,
                "state_name": state_name,
                "district_name": district_name,
                "urban_rural_gps": urban_rural,
                "latitude": lat,
                "longitude": lon,
            }

    for clid, segments in all_segments_by_cluster.items():
        agg = _aggregate_rows(segments)
        meta = cluster_meta[clid]
        record = {
            "cluster_id": clid,
            "dhs_id": meta["dhs_id"],
            "state_code_gps": meta["state_code_gps"],
            "state_name": meta["state_name"],
            "district_name": meta["district_name"],
            "urban_rural_gps": meta["urban_rural_gps"],
            "latitude": meta["latitude"],
            "longitude": meta["longitude"],
            "child_count": int(agg["child_count"]),
            "haz_valid_n": int(agg["haz_valid_n"]),
            "waz_valid_n": int(agg["waz_valid_n"]),
            "whz_valid_n": int(agg["whz_valid_n"]),
            "anemia_valid_n": int(agg["anemia_valid_n"]),
            "stunting_rate": agg["stunting_rate"],
            "severe_stunting_rate": agg["severe_stunting_rate"],
            "underweight_rate": agg["underweight_rate"],
            "wasting_rate": agg["wasting_rate"],
            "severe_wasting_rate": agg["severe_wasting_rate"],
            "overweight_rate": agg["overweight_rate"],
            "anemia_rate": agg["anemia_rate"],
            "mean_haz": agg["mean_haz"],
            "mean_waz": agg["mean_waz"],
            "mean_whz": agg["mean_whz"],
            "risk_score": agg["risk_score"],
            "sample_quality": _sample_quality(int(agg["haz_valid_n"])),
        }
        all_clusters.append(record)

    all_clusters.sort(key=lambda row: (row["state_name"], row["district_name"], row["cluster_id"]))

    all_segment_rows: list[dict[str, object]] = []
    for clid, segments in all_segments_by_cluster.items():
        meta = cluster_meta[clid]
        for seg in segments:
            enriched = dict(seg)
            enriched["state_name"] = meta["state_name"]
            enriched["district_name"] = meta["district_name"]
            all_segment_rows.append(enriched)

    all_segment_rows.sort(
        key=lambda row: (
            row["state_name"],
            row["district_name"],
            row["cluster_id"],
            row["sex"],
            row["wealth"],
            row["age_band"],
        )
    )

    # States.
    segments_by_state: dict[str, list[dict[str, object]]] = {}
    for row in all_segment_rows:
        segments_by_state.setdefault(row["state_name"], []).append(row)

    state_records = []
    for state_name, rows in segments_by_state.items():
        agg = _aggregate_rows(rows)
        state_records.append(
            {
                "state_code": state_codes[state_name],
                "state_name": state_name,
                "child_count": int(agg["child_count"]),
                "haz_valid_n": int(agg["haz_valid_n"]),
                "waz_valid_n": int(agg["waz_valid_n"]),
                "whz_valid_n": int(agg["whz_valid_n"]),
                "anemia_valid_n": int(agg["anemia_valid_n"]),
                "stunting_rate": agg["stunting_rate"],
                "severe_stunting_rate": agg["severe_stunting_rate"],
                "underweight_rate": agg["underweight_rate"],
                "wasting_rate": agg["wasting_rate"],
                "severe_wasting_rate": agg["severe_wasting_rate"],
                "overweight_rate": agg["overweight_rate"],
                "anemia_rate": agg["anemia_rate"],
                "mean_haz": agg["mean_haz"],
                "mean_waz": agg["mean_waz"],
                "mean_whz": agg["mean_whz"],
                "risk_score": agg["risk_score"],
            }
        )
    state_records.sort(key=lambda row: row["state_name"])

    # National.
    national_agg = _aggregate_rows(all_segment_rows)
    national_record = {
        "child_count": int(national_agg["child_count"]),
        "haz_valid_n": int(national_agg["haz_valid_n"]),
        "waz_valid_n": int(national_agg["waz_valid_n"]),
        "whz_valid_n": int(national_agg["whz_valid_n"]),
        "anemia_valid_n": int(national_agg["anemia_valid_n"]),
        "stunting_rate": national_agg["stunting_rate"],
        "severe_stunting_rate": national_agg["severe_stunting_rate"],
        "underweight_rate": national_agg["underweight_rate"],
        "wasting_rate": national_agg["wasting_rate"],
        "severe_wasting_rate": national_agg["severe_wasting_rate"],
        "overweight_rate": national_agg["overweight_rate"],
        "anemia_rate": national_agg["anemia_rate"],
        "mean_haz": national_agg["mean_haz"],
        "mean_waz": national_agg["mean_waz"],
        "mean_whz": national_agg["mean_whz"],
        "risk_score": national_agg["risk_score"],
    }

    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        generated_at = datetime.fromtimestamp(int(epoch), timezone.utc).isoformat()
    else:
        generated_at = datetime.now(timezone.utc).isoformat()

    payload = {
        "metadata": {
            "schema_version": "legacy",
            "tier": "demo",
            "generated_at": generated_at,
            "seed": seed,
            "disclaimer": DISCLAIMER,
            "filter_dimensions": {
                "sex": sorted(SEX_ORDER),
                "wealth": sorted(WEALTH_ORDER),
                "age_band": list(AGE_BANDS),
            },
        },
        "cluster_segment_columns": SEGMENT_COLUMNS,
        "national": {key: _sanitize(national_record[key]) for key in NATIONAL_COLUMNS},
        "states": [
            {key: _sanitize(row[key]) for key in STATE_COLUMNS} for row in state_records
        ],
        "clusters": [
            {key: _sanitize(row[key]) for key in CLUSTER_COLUMNS} for row in all_clusters
        ],
        "cluster_segments": [
            [_sanitize(row[key]) for key in SEGMENT_COLUMNS] for row in all_segment_rows
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8"
    )

    print(f"Wrote {output_path}")
    print(f"Clusters: {len(payload['clusters']):,}")
    print(f"Cluster segments: {len(payload['cluster_segments']):,}")
    print(f"States: {len(payload['states']):,}")
    print(f"Children (synthetic): {payload['national']['child_count']:,}")

    # Only record manifest entries for artifacts written into the committed public demo dir;
    # temp/smoke runs with a custom --out must not pollute the manifest.
    resolved_output = output_path.resolve()
    if resolved_output.parent == DEMO_DIR:
        update_manifest(
            resolved_output,
            "python_backend/demo_data_builder.py",
            {"seed": seed, "clusters_per_district": clusters_per_district},
        )


DISTRICT_INDICATORS = [
    "stunting_rate",
    "severe_stunting_rate",
    "underweight_rate",
    "wasting_rate",
    "severe_wasting_rate",
    "overweight_rate",
    "anemia_rate",
]


def build_district_indicators(input_path: Path, output_path: Path, seed: int) -> None:
    """Emit public placeholder district values and unweighted demo state rollups."""
    if not input_path.exists():
        raise FileNotFoundError(f"Missing fact-sheet CSV: {input_path}")

    source_rows = sorted(
        pd.read_csv(input_path).to_dict(orient="records"),
        key=lambda row: (str(row["state_name"]), str(row["district_name"])),
    )
    used_state_slugs: dict[str, int] = {}
    state_slugs = {
        state_name: _unique_slug(state_name, used_state_slugs)
        for state_name in sorted({str(row["state_name"]) for row in source_rows})
    }
    used_district_slugs: dict[str, dict[str, int]] = {
        state_name: {} for state_name in state_slugs
    }

    districts = []
    for row in source_rows:
        state_name = str(row["state_name"])
        district_name = str(row["district_name"])
        record = {
            "state_name": state_name,
            "district_name": district_name,
            "normalized_state_name": normalize(state_name),
            "normalized_district_name": normalize(district_name),
            "state_slug": state_slugs[state_name],
            "district_slug": _unique_slug(
                district_name, used_district_slugs[state_name]
            ),
        }
        for indicator in DISTRICT_INDICATORS:
            record[indicator] = _sanitize(float(row[indicator]))
        record["risk_score"] = _sanitize(
            record["stunting_rate"] * 0.45
            + record["underweight_rate"] * 0.35
            + record["wasting_rate"] * 0.20
        )
        districts.append(record)
    states = []
    for state_name in sorted({row["state_name"] for row in districts}):
        state_districts = [row for row in districts if row["state_name"] == state_name]
        rollup = {
            "state_name": state_name,
            "normalized_state_name": normalize(state_name),
            "state_slug": state_slugs[state_name],
            "district_count": len(state_districts),
        }
        for indicator in [*DISTRICT_INDICATORS, "risk_score"]:
            rollup[indicator] = _sanitize(
                sum(float(row[indicator]) for row in state_districts) / len(state_districts)
            )
        states.append(rollup)

    national = {"district_count": len(districts)}
    for indicator in [*DISTRICT_INDICATORS, "risk_score"]:
        national[indicator] = _sanitize(
            sum(float(row[indicator]) for row in districts) / len(districts)
        )

    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    generated_at = (
        datetime.fromtimestamp(int(epoch), timezone.utc).isoformat()
        if epoch
        else datetime.now(timezone.utc).isoformat()
    )
    payload = {
        "schema_version": "1.0",
        "metadata": {
            "tier": "demo",
            "aggregation": "unweighted, demo-tier",
            "generated_at": generated_at,
            "seed": seed,
            "placeholder_status": "All values are documented demo placeholders, not NFHS estimates.",
            "source": "python_backend/data/nfhs5_district_factsheet.csv",
        },
        "districts": districts,
        "states": states,
        "national": national,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8"
    )
    print(f"Wrote {output_path}")
    print(f"District indicators: {len(districts):,}")
    if output_path.resolve().parent == DEMO_DIR:
        update_manifest(
            output_path,
            "python_backend/demo_data_builder.py",
            {"seed": seed, "artifact": "district_indicators"},
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a deterministic synthetic demo child nutrition dataset."
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--clusters-per-district", type=int, default=10)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--district-out", type=Path, default=DEFAULT_DISTRICT_OUTPUT)
    args = parser.parse_args()

    build_demo_data(DEFAULT_INPUT, args.out, args.seed, args.clusters_per_district)
    build_district_indicators(DEFAULT_INPUT, args.district_out, args.seed)


if __name__ == "__main__":
    main()
