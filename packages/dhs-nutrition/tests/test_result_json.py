"""Checks on IndicatorResult.to_json / from_json export shape and determinism."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from dhs_nutrition.result import IndicatorResult


def test_top_level_keys(result, tmp_path):
    out_path = result.to_json(tmp_path / "out.json", tier="restricted-local")
    payload = json.loads(out_path.read_text(encoding="utf-8"))

    assert set(payload.keys()) == {
        "schema_version",
        "tier",
        "generated_at",
        "package_version",
        "source_files",
        "levels",
        "segments",
    }
    assert payload["schema_version"] == "1.0"


def test_extra_meta_included_verbatim(result, tmp_path):
    meta = {"note": "synthetic fixture run", "count": 3}
    out_path = result.to_json(tmp_path / "out.json", tier="restricted-local", extra_meta=meta)
    payload = json.loads(out_path.read_text(encoding="utf-8"))

    assert set(payload.keys()) == {
        "schema_version",
        "tier",
        "generated_at",
        "package_version",
        "source_files",
        "levels",
        "segments",
        "meta",
    }
    assert payload["meta"] == meta


def test_level_payload_shapes(result, tmp_path):
    out_path = result.to_json(tmp_path / "out.json", tier="restricted-local")
    payload = json.loads(out_path.read_text(encoding="utf-8"))

    assert isinstance(payload["levels"]["national"], dict)
    assert isinstance(payload["levels"]["national"]["child_count"], int)
    assert isinstance(payload["levels"]["admin1"], list)
    assert isinstance(payload["levels"]["cluster"], list)


def test_cluster_segment_rows_match_columns_width(result, tmp_path):
    out_path = result.to_json(tmp_path / "out.json", tier="restricted-local")
    payload = json.loads(out_path.read_text(encoding="utf-8"))

    cluster_segment = payload["segments"]["cluster"]
    assert isinstance(cluster_segment["columns"], list)
    assert isinstance(cluster_segment["rows"], list)
    for row in cluster_segment["rows"]:
        assert isinstance(row, list)
        assert len(row) == len(cluster_segment["columns"])


def test_source_files_basenames_and_hex_digests(result, tmp_path):
    out_path = result.to_json(tmp_path / "out.json", tier="restricted-local")
    payload = json.loads(out_path.read_text(encoding="utf-8"))

    assert payload["source_files"]
    for name, digest in payload["source_files"].items():
        assert "/" not in name
        assert "\\" not in name
        assert len(digest) == 64
        assert digest == digest.lower()
        int(digest, 16)  # must be valid hex


def test_json_text_does_not_leak_tmp_path(result, tmp_path):
    out_path = result.to_json(tmp_path / "out.json", tier="restricted-local")
    text = out_path.read_text(encoding="utf-8")

    assert str(tmp_path) not in text


def test_determinism_with_source_date_epoch(result, tmp_path, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")

    path_a = result.to_json(tmp_path / "a.json", tier="restricted-local")
    path_b = result.to_json(tmp_path / "b.json", tier="restricted-local")

    bytes_a = path_a.read_bytes()
    bytes_b = path_b.read_bytes()
    assert bytes_a == bytes_b

    payload = json.loads(bytes_a.decode("utf-8"))
    expected = datetime.fromtimestamp(1700000000, tz=timezone.utc).isoformat()
    assert payload["generated_at"] == expected


def test_from_json_round_trip(result, tmp_path):
    out_path = result.to_json(tmp_path / "out.json", tier="restricted-local")
    reloaded = IndicatorResult.from_json(out_path)

    assert reloaded.national.shape == result.national.shape
    assert reloaded.admin1.shape == result.admin1.shape
    assert reloaded.cluster.shape == result.cluster.shape

    original_row = result.national.iloc[0]
    reloaded_row = reloaded.national.iloc[0]
    for column in result.national.columns:
        original_value = original_row[column]
        reloaded_value = reloaded_row[column]
        if isinstance(original_value, float):
            # to_json rounds floats to 6 decimal places, so compare with a
            # tolerance rather than exact equality.
            assert reloaded_value == pytest.approx(float(original_value), abs=1e-6)
        else:
            assert int(reloaded_value) == int(original_value)
