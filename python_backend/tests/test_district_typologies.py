import hashlib
import json
import os

import numpy as np
import pytest

from analytics import district_typologies as typologies
from analytics.district_typologies import (
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    FEATURES,
    build_payload,
    label_for_centroid,
    load_districts,
    select_clustering,
    write_artifact,
)
from manifest_utils import MANIFEST_PATH


def _district(slug, value):
    return {
        "district_slug": slug,
        **{field: float(value + index) for index, (field, _) in enumerate(FEATURES)},
    }


def _write_input(path, districts, schema_version="1.0"):
    path.write_text(
        json.dumps({"schema_version": schema_version, "districts": districts}),
        encoding="utf-8",
    )


def _restore_epoch(previous):
    if previous is None:
        os.environ.pop("SOURCE_DATE_EPOCH", None)
    else:
        os.environ["SOURCE_DATE_EPOCH"] = previous


def test_input_validation_rejects_too_few_nonfinite_and_duplicate_districts(tmp_path):
    input_path = tmp_path / "districts.json"
    _write_input(input_path, [_district(f"d-{index}", index) for index in range(3)])
    with pytest.raises(ValueError, match="At least four"):
        load_districts(input_path)

    invalid = [_district(f"d-{index}", index) for index in range(4)]
    invalid[0][FEATURES[0][0]] = float("nan")
    _write_input(input_path, invalid)
    with pytest.raises(ValueError, match="must be finite"):
        load_districts(input_path)

    duplicates = [_district(f"d-{index}", index) for index in range(4)]
    duplicates[1]["district_slug"] = duplicates[0]["district_slug"]
    _write_input(input_path, duplicates)
    with pytest.raises(ValueError, match="must be unique"):
        load_districts(input_path)


def test_selection_is_seeded_and_smallest_k_wins_equal_silhouettes(monkeypatch):
    matrix = np.asarray([[index, index**2] for index in range(8)], dtype=float)
    first = select_clustering(matrix, 42)
    second = select_clustering(matrix, 42)
    assert first[0] == second[0]
    assert np.array_equal(first[1], second[1])
    assert np.allclose(first[2], second[2])

    monkeypatch.setattr(typologies, "silhouette_score", lambda _matrix, _labels: 0.5)
    tied = select_clustering(matrix, 42)
    assert tied[0] == 3
    assert [row["k"] for row in tied[4]] == [3, 4, 5, 6]


def test_label_generation_lists_extremes_and_has_near_average_fallback():
    centroid = np.array([0.7, 0.1, -0.6, 0.0, 0.5, -0.2, -0.8])
    label, description = label_for_centroid(centroid)
    assert label == "High stunting, High severe wasting, low underweight, low anemia"
    assert description.endswith("among the included demo districts.")

    fallback_label, fallback_description = label_for_centroid(np.zeros(len(FEATURES)))
    assert fallback_label == "Near-average profile"
    assert "0.5 SD" in fallback_description


def test_payload_schema_and_repeated_bytes_are_deterministic(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    previous = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = "1784592000"
    try:
        write_artifact(first, 42)
        write_artifact(second, 42)
    finally:
        _restore_epoch(previous)

    assert first.read_bytes() == second.read_bytes()
    payload = json.loads(first.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["metadata"]["tier"] == "demo"
    assert payload["metadata"]["seed"] == 42
    assert payload["metadata"]["feature_list"] == [field for field, _ in FEATURES]
    assert 3 <= payload["metadata"]["k"] <= 6
    assert "placeholder" in payload["metadata"]["placeholder_status"].lower()
    assert len(payload["districts"]) == 10
    assert len(payload["typologies"]) == payload["metadata"]["k"]
    assert all(set(row) == {"district_slug", "typology_id"} for row in payload["districts"])


def test_committed_artifact_matches_builder_and_manifest():
    previous = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = "1784592000"
    try:
        expected = json.dumps(
            build_payload(DEFAULT_INPUT, 42),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    finally:
        _restore_epoch(previous)
    assert DEFAULT_OUTPUT.read_bytes() == expected

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entry = next(
        row for row in manifest["artifacts"] if row["file"] == "district_typologies.json"
    )
    assert entry["schema_version"] == "1.0"
    assert entry["sha256"] == hashlib.sha256(DEFAULT_OUTPUT.read_bytes()).hexdigest()
