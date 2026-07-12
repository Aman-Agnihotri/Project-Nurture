"""Compare a legacy India dashboard extract with a schema-v1.0 extract.

This script only reads local Tier 1 outputs and prints structural counts and
maximum numeric deltas. It never prints record contents or writes derived data.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

DEFAULT_OLD_PATH = Path("python_backend/outputs/regression_old.json")
DEFAULT_NEW_PATH = Path("python_backend/outputs/regression_new.json")
DEFAULT_TOLERANCE = 1e-6
EXCLUDED_NUMERIC_FIELDS = {"risk_score"}


def _numeric_diffs(old_row: dict, new_row: dict) -> dict[str, float]:
    diffs: dict[str, float] = {}
    for key in old_row.keys() & new_row.keys():
        if key in EXCLUDED_NUMERIC_FIELDS:
            continue
        old_value = old_row[key]
        new_value = new_row[key]
        if (
            isinstance(old_value, (int, float))
            and not isinstance(old_value, bool)
            and isinstance(new_value, (int, float))
            and not isinstance(new_value, bool)
        ):
            if not math.isfinite(float(old_value)) or not math.isfinite(float(new_value)):
                continue
            diffs[key] = abs(float(old_value) - float(new_value))
    return diffs


def _index_unique(rows: list[dict], key_field: str, label: str) -> dict[object, dict]:
    indexed: dict[object, dict] = {}
    for row in rows:
        key = row[key_field]
        if key in indexed:
            raise ValueError(f"{label} contains duplicate key {key!r}")
        indexed[key] = row
    return indexed


def _compare_keyed_rows(
    label: str,
    old_rows: dict[object, dict],
    new_rows: dict[object, dict],
    tolerance: float,
) -> list[str]:
    failures: list[str] = []
    old_keys = set(old_rows)
    new_keys = set(new_rows)
    missing = old_keys - new_keys
    unexpected = new_keys - old_keys
    if missing or unexpected:
        failures.append(
            f"{label}: key mismatch (missing={len(missing)}, unexpected={len(unexpected)})"
        )

    matched_keys = old_keys & new_keys
    if not matched_keys:
        failures.append(f"{label}: no matching rows")
        print(f"{label}: 0 matched")
        return failures

    row_diffs = [_numeric_diffs(old_rows[key], new_rows[key]) for key in matched_keys]
    if not any(row_diffs):
        failures.append(f"{label}: matching rows have no shared numeric indicator fields")
        max_delta = 0.0
    else:
        max_delta = max((value for diffs in row_diffs for value in diffs.values()), default=0.0)
        if max_delta > tolerance:
            failures.append(f"{label}: max delta {max_delta:.8f} exceeds {tolerance:.8f}")

    print(f"{label}: max delta = {max_delta:.8f} ({len(matched_keys)} matched)")
    return failures


def _index_segments(columns: list[str], rows: list[list], label: str) -> dict[tuple, dict]:
    indexes = [columns.index(name) for name in ("cluster_id", "sex", "wealth", "age_band")]
    indexed: dict[tuple, dict] = {}
    for row in rows:
        key = tuple(row[index] for index in indexes)
        if key in indexed:
            raise ValueError(f"{label} contains duplicate key {key!r}")
        indexed[key] = dict(zip(columns, row, strict=True))
    return indexed


def _legacy_segments(payload: dict) -> dict[tuple, dict]:
    return _index_segments(
        payload["cluster_segment_columns"], payload["cluster_segments"], "legacy segments"
    )


def _v1_segments(payload: dict) -> dict[tuple, dict]:
    entry = payload["segments"]["cluster"]
    return _index_segments(entry["columns"], entry["rows"], "v1 segments")


def compare_outputs(old: dict, new: dict, tolerance: float = DEFAULT_TOLERANCE) -> list[str]:
    """Return human-readable parity failures; an empty list means parity."""
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    failures: list[str] = []
    failures.extend(
        _compare_keyed_rows(
            "national",
            {"national": old["national"]},
            {"national": new["levels"]["national"]},
            tolerance,
        )
    )
    failures.extend(
        _compare_keyed_rows(
            "states",
            _index_unique(old["states"], "state_name", "legacy states"),
            _index_unique(new["levels"]["admin1"], "admin1_name", "v1 states"),
            tolerance,
        )
    )
    failures.extend(
        _compare_keyed_rows(
            "clusters",
            _index_unique(old["clusters"], "cluster_id", "legacy clusters"),
            _index_unique(new["levels"]["cluster"], "cluster_id", "v1 clusters"),
            tolerance,
        )
    )
    failures.extend(
        _compare_keyed_rows(
            "cluster_segments", _legacy_segments(old), _v1_segments(new), tolerance
        )
    )
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", type=Path, default=DEFAULT_OLD_PATH)
    parser.add_argument("--new", type=Path, default=DEFAULT_NEW_PATH)
    parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE)
    args = parser.parse_args(argv)

    try:
        old = json.loads(args.old.read_text(encoding="utf-8"))
        new = json.loads(args.new.read_text(encoding="utf-8"))
        failures = compare_outputs(old, new, args.tolerance)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"FAILED: invalid regression input: {exc}")
        return 2

    if failures:
        print("FAILED:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASSED: old and new pipelines agree structurally and within tolerance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
