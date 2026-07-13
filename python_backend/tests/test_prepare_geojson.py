from pathlib import Path

from prepare_geojson import PUBLIC_OUTPUT, prepare_geojson


FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_districts.geojson"


def test_prepare_geojson_reduces_properties_and_reports_coverage(tmp_path):
    output = tmp_path / "prepared.geojson"
    report = prepare_geojson(FIXTURE, output)
    assert report["matched"] == 2
    assert report["polygon_total"] == 3
    assert report["unmatched_polygons"] == ["example state / unmatched invented district"]
    assert "bihar / demo district b2" in report["unmatched_factsheet"]
    assert '"unused"' not in output.read_text(encoding="utf-8")


def test_default_public_output_requires_licence_review():
    try:
        prepare_geojson(FIXTURE, PUBLIC_OUTPUT)
    except ValueError as error:
        assert "license-reviewed" in str(error)
    else:
        raise AssertionError("public output unexpectedly allowed")
