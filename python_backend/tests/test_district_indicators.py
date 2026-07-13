import json
import os
from pathlib import Path

from demo_data_builder import DEFAULT_INPUT, build_district_indicators


def test_district_indicators_are_deterministic_and_have_unweighted_rollups(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    previous = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = "1783728000"
    try:
        build_district_indicators(DEFAULT_INPUT, first, 42)
        build_district_indicators(DEFAULT_INPUT, second, 42)
    finally:
        if previous is None:
            os.environ.pop("SOURCE_DATE_EPOCH", None)
        else:
            os.environ["SOURCE_DATE_EPOCH"] = previous
    assert first.read_bytes() == second.read_bytes()
    payload = json.loads(first.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["metadata"]["aggregation"] == "unweighted, demo-tier"
    assert payload["districts"][0]["state_slug"] == "bihar"
    bihar = next(row for row in payload["states"] if row["state_name"] == "Bihar")
    assert bihar["stunting_rate"] == 40.0
    assert "placeholder" in payload["metadata"]["placeholder_status"].lower()
