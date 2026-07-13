"""Prepare maintainer-supplied India district GeoJSON for the public demo tier.

This script deliberately does not ship or obtain geography.  Its default output
is only enabled after a maintainer has reviewed the input's licence and
attribution.  Test fixtures should always use an explicit temporary ``--out``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from manifest_utils import update_manifest
from name_normalization import normalize


REPO_ROOT = Path(__file__).resolve().parents[1]
FACTSHEET_PATH = Path(__file__).resolve().parent / "data" / "nfhs5_district_factsheet.csv"
PUBLIC_OUTPUT = REPO_ROOT / "project_nurture" / "public" / "demo" / "geo" / "india_districts.geojson"
STATE_PROPERTY_NAMES = ("state_name", "state", "state_name_en", "st_name", "st_nm", "statename")
DISTRICT_PROPERTY_NAMES = (
    "district_name", "district", "district_name_en", "district_name_", "district_na", "dist_name", "dist_nm", "districtname",
)


def detect_property(properties: dict[str, object], candidates: tuple[str, ...]) -> str | None:
    """Find a common property spelling, ignoring case and punctuation."""
    by_normalized = {"".join(char for char in key.lower() if char.isalnum()): key for key in properties}
    for candidate in candidates:
        found = by_normalized.get("".join(char for char in candidate.lower() if char.isalnum()))
        if found:
            return found
    return None


def prepare_feature(feature: dict[str, object]) -> dict[str, object]:
    """Keep geometry plus the four matching/display names required by the app."""
    properties = feature.get("properties") or {}
    if not isinstance(properties, dict):
        raise ValueError("Every GeoJSON feature must have an object properties member.")
    state_key = detect_property(properties, STATE_PROPERTY_NAMES)
    district_key = detect_property(properties, DISTRICT_PROPERTY_NAMES)
    if not state_key or not district_key:
        raise ValueError("Feature is missing a recognised state or district property.")
    state_name, district_name = properties.get(state_key), properties.get(district_key)
    if not state_name or not district_name:
        raise ValueError("Feature has an empty state or district name.")
    return {
        "type": "Feature",
        "properties": {
            "state_name": str(state_name),
            "district_name": str(district_name),
            "normalized_state_name": normalize(state_name),
            "normalized_district_name": normalize(district_name),
        },
        "geometry": feature.get("geometry"),
    }


def coverage_report(features: list[dict[str, object]], factsheet_path: Path = FACTSHEET_PATH) -> dict[str, list[str] | int]:
    factsheet = pd.read_csv(factsheet_path)
    known = {
        (normalize(row.state_name), normalize(row.district_name))
        for row in factsheet.itertuples(index=False)
    }
    polygon_names = {
        (feature["properties"]["normalized_state_name"], feature["properties"]["normalized_district_name"])
        for feature in features
    }
    matched = sorted(polygon_names & known)
    unmatched_polygons = sorted(polygon_names - known)
    unmatched_factsheet = sorted(known - polygon_names)
    return {
        "matched": len(matched),
        "polygon_total": len(polygon_names),
        "unmatched_polygons": [f"{state} / {district}" for state, district in unmatched_polygons],
        "unmatched_factsheet": [f"{state} / {district}" for state, district in unmatched_factsheet],
    }


def prepare_geojson(input_path: Path, output_path: Path, license_reviewed: bool = False) -> dict[str, list[str] | int]:
    input_path = Path(input_path)
    output_path = Path(output_path)
    if output_path.resolve() == PUBLIC_OUTPUT.resolve() and not license_reviewed:
        raise ValueError("Refusing public output without --license-reviewed.")
    source = json.loads(input_path.read_text(encoding="utf-8"))
    if source.get("type") != "FeatureCollection" or not isinstance(source.get("features"), list):
        raise ValueError("Input must be a GeoJSON FeatureCollection.")
    features = [prepare_feature(feature) for feature in source["features"]]
    payload = {"type": "FeatureCollection", "features": features}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    report = coverage_report(features)
    if output_path.resolve() == PUBLIC_OUTPUT.resolve():
        update_manifest(output_path, "python_backend/prepare_geojson.py", {"license_reviewed": True})
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare reviewed, maintainer-supplied district boundaries.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, default=PUBLIC_OUTPUT)
    parser.add_argument("--license-reviewed", action="store_true")
    args = parser.parse_args()
    report = prepare_geojson(args.input, args.out, args.license_reviewed)
    print(f"Matched polygons: {report['matched']}/{report['polygon_total']}")
    print("Unmatched polygon names:")
    for name in report["unmatched_polygons"]:
        print(f"- {name}")
    print("Fact-sheet districts without polygons:")
    for name in report["unmatched_factsheet"]:
        print(f"- {name}")


if __name__ == "__main__":
    main()
