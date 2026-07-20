import hashlib
import json
import math
import os

import numpy as np
import pytest

from analytics.risk_methodology import (
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    DEFAULT_WEIGHTS,
    build_payload,
    percentile_ranks,
    sensitivity_scenarios,
    spearman_correlation,
    validate_weights,
    write_artifact,
)
from manifest_utils import MANIFEST_PATH


def _restore_epoch(previous):
    if previous is None:
        os.environ.pop("SOURCE_DATE_EPOCH", None)
    else:
        os.environ["SOURCE_DATE_EPOCH"] = previous


def test_weight_validation_accepts_boundaries_and_rejects_invalid_values():
    assert validate_weights([0.45, 0.35, 0.20]) == DEFAULT_WEIGHTS
    assert validate_weights([0.0, 0.5, 0.5])["stunting"] == 0.0
    with pytest.raises(ValueError, match="Exactly three"):
        validate_weights([0.5, 0.5])
    with pytest.raises(ValueError, match="finite"):
        validate_weights([math.nan, 0.5, 0.5])
    with pytest.raises(ValueError, match="non-negative"):
        validate_weights([-0.1, 0.5, 0.6])
    with pytest.raises(ValueError, match="sum to 1"):
        validate_weights([0.4, 0.4, 0.4])


def test_percentile_ranks_map_endpoints_and_average_ties():
    assert percentile_ranks([10, 20, 20, 40]).tolist() == [0.0, 50.0, 50.0, 100.0]
    assert percentile_ranks([40, 10, 20]).tolist() == [100.0, 0.0, 50.0]
    assert percentile_ranks([7, 7, 7]).tolist() == [50.0, 50.0, 50.0]
    with pytest.raises(ValueError, match="finite"):
        percentile_ranks([1, np.inf])


def test_spearman_handles_ties_and_zero_variance_deliberately():
    assert spearman_correlation([1, 2, 2, 4], [10, 20, 20, 40]) == pytest.approx(1.0)
    assert spearman_correlation([1, 2, 3], [3, 2, 1]) == pytest.approx(-1.0)
    assert spearman_correlation([1, 1, 1], [2, 3, 4]) is None


def test_sensitivity_has_six_renormalized_scenarios():
    components = {
        "stunting": np.array([0.0, 50.0, 100.0]),
        "underweight": np.array([0.0, 50.0, 100.0]),
        "wasting": np.array([100.0, 50.0, 0.0]),
    }
    scenarios = sensitivity_scenarios(components, DEFAULT_WEIGHTS)
    assert len(scenarios) == 6
    assert [row["id"] for row in scenarios] == [
        "stunting_minus_0_1",
        "stunting_plus_0_1",
        "underweight_minus_0_1",
        "underweight_plus_0_1",
        "wasting_minus_0_1",
        "wasting_plus_0_1",
    ]
    for scenario in scenarios:
        assert sum(scenario["weights"].values()) == pytest.approx(1.0, abs=2e-6)
    stunting_plus = scenarios[1]
    assert stunting_plus["weights"] == {
        "stunting": 0.5,
        "underweight": 0.318182,
        "wasting": 0.181818,
    }


def test_payload_schema_and_repeated_bytes_are_deterministic(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    previous = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = "1784592000"
    try:
        write_artifact(first, DEFAULT_WEIGHTS)
        write_artifact(second, DEFAULT_WEIGHTS)
    finally:
        _restore_epoch(previous)

    assert first.read_bytes() == second.read_bytes()
    payload = json.loads(first.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["metadata"]["input"] == "district_indicators.json"
    assert payload["metadata"]["tier"] == "demo"
    assert "placeholder" in payload["metadata"]["placeholder_status"].lower()
    assert len(payload["districts"]) == 10
    assert len(payload["sensitivity"]) == 6
    assert list(payload["districts"][0]) == [
        "composite_score",
        "district_slug",
        "stunting_percentile",
        "underweight_percentile",
        "wasting_percentile",
    ]


def test_committed_artifact_matches_builder_and_manifest():
    previous = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = "1784592000"
    try:
        expected = json.dumps(
            build_payload(DEFAULT_INPUT, DEFAULT_WEIGHTS),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    finally:
        _restore_epoch(previous)
    assert DEFAULT_OUTPUT.read_bytes() == expected

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entry = next(row for row in manifest["artifacts"] if row["file"] == "district_risk.json")
    assert entry["schema_version"] == "1.0"
    assert entry["sha256"] == hashlib.sha256(DEFAULT_OUTPUT.read_bytes()).hexdigest()
