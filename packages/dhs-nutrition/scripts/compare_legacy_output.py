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
STATE_FIELD_MAP = {"state_code": "admin1_code", "state_name": "admin1_name"}
CLUSTER_FIELD_MAP = {
    "state_code_gps": "admin1_code",
    "state_name": "admin1_name",
    "district_name": "admin2_name",
    "urban_rural_gps": "residence",
}
CLUSTER_EXCLUDED_FIELDS = {"risk_score", "sample_quality"}


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


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
    *,
    field_map: dict[str, str] | None = None,
    excluded_fields: set[str] | None = None,
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

    field_map = field_map or {}
    excluded_fields = excluded_fields or EXCLUDED_NUMERIC_FIELDS
    field_failures: set[str] = set()
    numeric_diffs: list[float] = []

    for key in matched_keys:
        old_row = old_rows[key]
        new_row = new_rows[key]
        for old_field, old_value in old_row.items():
            if old_field in excluded_fields:
                continue
            new_field = field_map.get(old_field, old_field)
            if new_field not in new_row:
                field_failures.add(
                    f"{label}: required field {old_field!r} is missing as {new_field!r}"
                )
                continue

            new_value = new_row[new_field]
            if _is_number(old_value):
                if not _is_number(new_value):
                    field_failures.add(
                        f"{label}: numeric field {old_field!r} changed type or became null"
                    )
                    continue
                if not math.isfinite(float(old_value)) or not math.isfinite(float(new_value)):
                    field_failures.add(f"{label}: numeric field {old_field!r} is non-finite")
                    continue
                numeric_diffs.append(abs(float(old_value) - float(new_value)))
            elif old_value != new_value:
                field_failures.add(
                    f"{label}: field {old_field!r} differs from mapped field {new_field!r}"
                )

    failures.extend(sorted(field_failures))
    max_delta = max(numeric_diffs, default=0.0)
    if not numeric_diffs:
        failures.append(f"{label}: matching rows have no comparable numeric indicator fields")
    elif max_delta > tolerance:
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
            field_map=STATE_FIELD_MAP,
        )
    )
    failures.extend(
        _compare_keyed_rows(
            "clusters",
            _index_unique(old["clusters"], "cluster_id", "legacy clusters"),
            _index_unique(new["levels"]["cluster"], "cluster_id", "v1 clusters"),
            tolerance,
            field_map=CLUSTER_FIELD_MAP,
            excluded_fields=CLUSTER_EXCLUDED_FIELDS,
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
