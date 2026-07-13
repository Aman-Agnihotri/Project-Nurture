import csv
import hashlib
import json
import os

from demo_data_builder import (
    DEFAULT_DISTRICT_OUTPUT,
    DEFAULT_INPUT,
    build_district_indicators,
)
from manifest_utils import MANIFEST_PATH


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


def test_committed_artifact_matches_deterministic_builder_bytes(tmp_path):
    output = tmp_path / "district_indicators.json"
    previous = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = "1783728000"
    try:
        build_district_indicators(DEFAULT_INPUT, output, 42)
    finally:
        if previous is None:
            os.environ.pop("SOURCE_DATE_EPOCH", None)
        else:
            os.environ["SOURCE_DATE_EPOCH"] = previous
    assert output.read_bytes() == DEFAULT_DISTRICT_OUTPUT.read_bytes()


def test_committed_artifact_hash_matches_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entry = next(
        item for item in manifest["artifacts"]
        if item["file"] == "district_indicators.json"
    )
    digest = hashlib.sha256(DEFAULT_DISTRICT_OUTPUT.read_bytes()).hexdigest()
    assert entry["sha256"] == digest


def test_builder_resolves_state_and_district_slug_collisions(tmp_path):
    input_path = tmp_path / "factsheet.csv"
    output_path = tmp_path / "districts.json"
    header = DEFAULT_INPUT.read_text(encoding="utf-8").splitlines()[0].split(",")
    base_values = DEFAULT_INPUT.read_text(encoding="utf-8").splitlines()[1].split(",")[2:]
    rows = [
        ["A & B", "One"],
        ["A and B", "Two"],
        ["A--and B", "Three"],
        ["Example State", "D & E"],
        ["Example State", "D and E"],
        ["Example State", "D--and E"],
    ]
    with input_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows([row + base_values for row in rows])

    build_district_indicators(input_path, output_path, 42)
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    state_slugs = {row["state_name"]: row["state_slug"] for row in payload["states"]}
    assert len(set(state_slugs.values())) == 4
    example_districts = [
        row["district_slug"] for row in payload["districts"]
        if row["state_name"] == "Example State"
    ]
    assert example_districts == ["d-and-e", "d-and-e-2", "d-and-e-3"]
