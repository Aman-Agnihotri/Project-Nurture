# Phase 2 regression: old vs new India pipeline

## Purpose

Phase 2 (rewriting `python_backend/dhs_pipeline.py` as a thin consumer of the
`dhs_nutrition` package) is **not accepted** until a maintainer with local
access to restricted NFHS-5 microdata confirms that the new pipeline
(`python_backend/india_pipeline.py`) produces indicator values that match the
old, pre-Phase-2 pipeline within floating-point rounding. This comparison
uses real DHS microdata and therefore **cannot be run in CI, or by an
assistant/agent** — only a human maintainer with the restricted `dhs_data/`
files on their own machine can run it.

## Prerequisites

- A local `dhs_data/` directory (repo root) containing the restricted India
  NFHS-5 files, at minimum:
  - `dhs_data/IAPR7EDT/IAPR7EFL.DTA`
  - `dhs_data/IAGE7AFL/IAGE7AFL.shp` (plus its `.dbf`/`.shx` siblings)
- A Python virtual environment with the `dhs_nutrition` package installed
  editable:
  ```sh
  python -m venv .venv-regression
  source .venv-regression/Scripts/activate   # or bin/activate on macOS/Linux
  pip install -e packages/dhs-nutrition
  ```

## Step 1: generate the old (pre-Phase-2) output

Check out the last pre-Phase-2 commit into a separate worktree so you can run
the old pipeline without disturbing your current branch:

```sh
git worktree add ../nurture-phase1 e87b285
python ../nurture-phase1/python_backend/dhs_pipeline.py \
  --dhs-dir dhs_data \
  --output python_backend/outputs/regression_old.json
```

(`python_backend/outputs/` is git-ignored T1 space; it is safe to write
restricted-derived JSON there.)

## Step 2: generate the new output

```sh
python python_backend/india_pipeline.py \
  --dhs-dir dhs_data \
  --output python_backend/outputs/regression_new.json
```

## Step 3: compare

Run the following script (adjust the two paths if you used different
`--output` locations). It ignores all metadata and compares only indicator
columns present in both schemas.

```python
"""Compare old (legacy-schema) vs new (v1.0-schema) India dashboard extracts.

Values in the new schema are rounded to 6 decimal places by
IndicatorResult.to_json; the tolerance below accounts for that rounding.
"""
import json
import sys
from pathlib import Path

OLD_PATH = Path("python_backend/outputs/regression_old.json")
NEW_PATH = Path("python_backend/outputs/regression_new.json")
TOLERANCE = 1e-6

EXCLUDE = {"risk_score", "sample_quality"}


def shared_numeric_diffs(old_row, new_row):
    diffs = {}
    for key in old_row.keys() & new_row.keys():
        if key in EXCLUDE:
            continue
        old_val, new_val = old_row[key], new_row[key]
        if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
            diffs[key] = abs(old_val - new_val)
    return diffs


def max_delta(deltas_list):
    flat = [d for deltas in deltas_list for d in deltas.values()]
    return max(flat) if flat else 0.0


def main() -> int:
    old = json.loads(OLD_PATH.read_text(encoding="utf-8"))
    new = json.loads(NEW_PATH.read_text(encoding="utf-8"))

    failures = []

    national_diffs = [shared_numeric_diffs(old["national"], new["levels"]["national"])]
    print(f"national: max delta = {max_delta(national_diffs):.8f}")
    if max_delta(national_diffs) >= TOLERANCE:
        failures.append("national")

    old_states = {row["state_name"]: row for row in old["states"]}
    new_states = {row["admin1_name"]: row for row in new["levels"]["admin1"]}
    state_diffs = [
        shared_numeric_diffs(old_states[name], new_states[name])
        for name in old_states.keys() & new_states.keys()
    ]
    print(f"states: max delta = {max_delta(state_diffs):.8f} ({len(state_diffs)} matched)")
    if max_delta(state_diffs) >= TOLERANCE:
        failures.append("states")

    old_clusters = {row["cluster_id"]: row for row in old["clusters"]}
    new_clusters = {row["cluster_id"]: row for row in new["levels"]["cluster"]}
    cluster_diffs = [
        shared_numeric_diffs(old_clusters[cid], new_clusters[cid])
        for cid in old_clusters.keys() & new_clusters.keys()
    ]
    print(f"clusters: max delta = {max_delta(cluster_diffs):.8f} ({len(cluster_diffs)} matched)")
    if max_delta(cluster_diffs) >= TOLERANCE:
        failures.append("clusters")

    old_seg_cols = old["cluster_segment_columns"]
    old_segments = {
        (row[old_seg_cols.index(k)] for k in ("cluster_id", "sex", "wealth", "age_band")): dict(
            zip(old_seg_cols, row)
        )
        for row in old["cluster_segments"]
    }
    old_segments = {tuple(k): v for k, v in old_segments.items()}

    new_seg_cols = new["segments"]["cluster"]["columns"]
    new_segments = {}
    for row in new["segments"]["cluster"]["rows"]:
        record = dict(zip(new_seg_cols, row))
        key = (record["cluster_id"], record["sex"], record["wealth"], record["age_band"])
        new_segments[key] = record

    segment_diffs = [
        shared_numeric_diffs(old_segments[key], new_segments[key])
        for key in old_segments.keys() & new_segments.keys()
    ]
    print(
        f"cluster_segments: max delta = {max_delta(segment_diffs):.8f} "
        f"({len(segment_diffs)} matched)"
    )
    if max_delta(segment_diffs) >= TOLERANCE:
        failures.append("cluster_segments")

    if failures:
        print(f"FAILED: mismatches in {failures}", file=sys.stderr)
        return 1

    print("PASSED: old and new pipelines agree within tolerance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Expected outcome

All five printed max-delta lines should read `0.00000000` (or values below
`1e-6`), and the script should exit `0`.

**On mismatch:** do not adjust `dhs_nutrition` package logic to "fix" the
diff without review. File an issue with the full script output (the
per-table max deltas and matched-row counts) so a maintainer can determine
whether the discrepancy is a rounding artifact, an intentional behavior
change (see Notes below), or a real regression.

## Notes

- `risk_score` and `sample_quality` are no longer computed by the pipeline
  itself. They are now derived client-side in
  `project_nurture/src/lib/dataSource.js` (`riskScore` / `sampleQuality`
  functions), using the same formulas as before. They are intentionally
  excluded from this comparison.
- The validation flow (`python_backend/validate_dhs_outputs.py`) now
  requires a maintainer-transcribed state-level factsheet CSV; the old
  PDF-parsing flow against the DHS fact sheet PDFs is retired.
- The old `--anemia-tolerance` flag (default 2.0pp) is gone; the new
  `validate_dhs_outputs.py` takes a single `--tolerance` for all indicators.
  Pass a higher `--tolerance` if you need a looser bound for anemia, or
  filter the report CSV afterward.
- Clean up the worktree when done:
  ```sh
  git worktree remove ../nurture-phase1
  ```
