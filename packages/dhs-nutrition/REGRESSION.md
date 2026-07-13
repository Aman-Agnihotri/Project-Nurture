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

Run the committed comparison tool. It ignores metadata, requires identical
state/cluster/segment key sets, requires every legacy field (using the
documented legacy-to-v1 state and cluster name mappings), rejects label,
missing/null, and non-finite mismatches, and compares numeric values within
the export's six-decimal rounding tolerance:

```sh
python packages/dhs-nutrition/scripts/compare_legacy_output.py
```

If you used different output locations:

```sh
python packages/dhs-nutrition/scripts/compare_legacy_output.py \
  --old path/to/regression_old.json \
  --new path/to/regression_new.json
```

## Expected outcome

All four printed max-delta lines should read `0.00000000` (or values no
greater than `1e-6`), every matched-row count must be non-zero, and the script
should exit `0`.

## Latest local verification status

On 2026-07-13, the legacy pipeline at commit `e87b285` and the Phase 2 India
pipeline were run against the same maintainer-authorized local NFHS-5 PR and
GPS inputs. The earlier comparator exited `0` for key sets and shared numeric
fields. Commit `4304539` subsequently hardened the comparator to reject
dropped fields, mapped-label differences, numeric-to-null changes, and
non-finite values. The maintainer must rerun Steps 1-3 with the hardened
comparator before final acceptance. Both comparison outputs must remain in the
ignored `python_backend/outputs/` Tier 1 directory.

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
