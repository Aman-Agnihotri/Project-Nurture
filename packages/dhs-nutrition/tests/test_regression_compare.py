"""Tests for the maintainer-run legacy/v1 regression comparison tool."""

from __future__ import annotations

import json
from copy import deepcopy

import pytest

from scripts.compare_legacy_output import compare_outputs, main


def _matching_payloads() -> tuple[dict, dict]:
    segment_columns = ["cluster_id", "sex", "wealth", "age_band", "stunted_w"]
    old = {
        "national": {"stunting_rate": 25.0},
        "states": [{"state_name": "Alphaland", "stunting_rate": 25.0}],
        "clusters": [{"cluster_id": 101, "stunting_rate": 25.0}],
        "cluster_segment_columns": segment_columns,
        "cluster_segments": [[101, "Female", "Poor", "6-23 months", 1.0]],
    }
    new = {
        "levels": {
            "national": {"stunting_rate": 25.0},
            "admin1": [{"admin1_name": "Alphaland", "stunting_rate": 25.0}],
            "cluster": [{"cluster_id": 101, "stunting_rate": 25.0}],
        },
        "segments": {
            "cluster": {
                "columns": segment_columns,
                "rows": [[101, "Female", "Poor", "6-23 months", 1.0]],
            }
        },
    }
    return old, new


def test_matching_outputs_pass():
    old, new = _matching_payloads()

    assert compare_outputs(old, new) == []


def test_state_key_mismatch_fails_even_when_intersection_is_empty():
    old, new = _matching_payloads()
    new["levels"]["admin1"][0]["admin1_name"] = "Renamed"

    failures = compare_outputs(old, new)

    assert any("states: key mismatch" in failure for failure in failures)
    assert any("states: no matching rows" in failure for failure in failures)


def test_empty_segment_tables_do_not_pass_vacuously():
    old, new = _matching_payloads()
    old["cluster_segments"] = []
    new["segments"]["cluster"]["rows"] = []

    failures = compare_outputs(old, new)

    assert "cluster_segments: no matching rows" in failures


def test_numeric_delta_over_tolerance_fails():
    old, new = _matching_payloads()
    changed = deepcopy(new)
    changed["levels"]["cluster"][0]["stunting_rate"] = 25.1

    failures = compare_outputs(old, changed, tolerance=1e-6)

    assert any("clusters: max delta" in failure for failure in failures)


def test_duplicate_keys_are_rejected():
    old, new = _matching_payloads()
    new["levels"]["cluster"].append(deepcopy(new["levels"]["cluster"][0]))

    with pytest.raises(ValueError, match="duplicate key"):
        compare_outputs(old, new)


def test_script_main_returns_success_for_matching_files(tmp_path, capsys):
    old, new = _matching_payloads()
    old_path = tmp_path / "old.json"
    new_path = tmp_path / "new.json"
    old_path.write_text(json.dumps(old), encoding="utf-8")
    new_path.write_text(json.dumps(new), encoding="utf-8")

    exit_code = main(["--old", str(old_path), "--new", str(new_path)])

    assert exit_code == 0
    assert "PASSED" in capsys.readouterr().out


def test_script_main_returns_failure_for_unmatched_keys(tmp_path, capsys):
    old, new = _matching_payloads()
    new["levels"]["cluster"][0]["cluster_id"] = 999
    old_path = tmp_path / "old.json"
    new_path = tmp_path / "new.json"
    old_path.write_text(json.dumps(old), encoding="utf-8")
    new_path.write_text(json.dumps(new), encoding="utf-8")

    exit_code = main(["--old", str(old_path), "--new", str(new_path)])

    assert exit_code == 1
    output = capsys.readouterr().out
    assert "key mismatch" in output
    assert "no matching rows" in output
