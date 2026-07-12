"""Checks on dhs_nutrition.validation.validate_against_factsheet using the
synthetic fixture's admin1-level golden values (re-derived below; the
underlying children/rate arithmetic is documented in test_indicators.py).

Alphaland (admin1=1, rows c,d,e,f,r10..r20 = 15 rows):
  haz_den_w = 15 (13 haz-valid rows: e,f,r10..r20 minus c,d which are
    haz-invalid); stunted weighted = f(1)+r11(1)+r13(1)+r17(1)+r20(1) = 5
    -> stunting_rate = 100*5/15 = 33.333333333333336
  whz_den_w = 15 + c(2) + d(1) = 18 (all 15 rows are whz-valid); wasted
    weighted = same 5 rows as stunted = 5 -> wasting_rate = 100*5/18
    = 27.77777777777778
  anemia eligible rows (admin1=1): c,d,r11,r12,r13,r14,r15,r17,r18,r19,r20
    (11 rows; e,f,r10,r16 excluded by age<6/hv042); weighted denominator
    = c2+d1+r11(1)+r12(2)+r13(1)+r14(1)+r15(1)+r17(1)+r18(2)+r19(1)+r20(1)
    = 14; anemic weighted = d(1)+r11(1)+r13(1)+r14(1)+r17(1)+r18(2)+r20(1)
    = 8 -> anemia_rate = 100*8/14 = 57.142857142857146

Betaland (admin1=2, rows g,h,i,r21..r30 = 13 rows):
  haz_den_w = 16 (all 13 rows haz-valid: g1+h1+i2+r21..r30 weights);
    stunted weighted = i(2)+r21(1)+r26(1)+r27(1) = 5
    -> stunting_rate = 100*5/16 = 31.25
  whz_den_w = 16 (all 13 rows whz-valid too); wasted weighted = same 4 rows
    = 5 -> wasting_rate = 100*5/16 = 31.25
  anemia eligible rows (admin1=2): i,r21,r22,r24,r25,r26,r27,r29,r30 (9 rows;
    g,h,r23,r28 excluded by hc55/hc57/age<6); weighted denominator
    = i2+r21(1)+r22(1)+r24(2)+r25(1)+r26(1)+r27(1)+r29(1)+r30(2) = 12;
    anemic weighted = i(2)+r21(1)+r22(1)+r24(2)+r26(1)+r27(1)+r30(2) = 10
    -> anemia_rate = 100*10/12 = 83.33333333333333
"""

from __future__ import annotations

import csv

import pytest

from dhs_nutrition.validation import ValidationReport, validate_against_factsheet

ALPHALAND_STUNTING = 100 * 5 / 15
ALPHALAND_WASTING = 100 * 5 / 18
ALPHALAND_ANEMIA = 100 * 8 / 14

BETALAND_STUNTING = 100 * 5 / 16
BETALAND_WASTING = 100 * 5 / 16
BETALAND_ANEMIA = 100 * 10 / 12


def _write_factsheet(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["region", "stunting_rate", "wasting_rate", "anemia_rate"])
        for row in rows:
            writer.writerow(row)
    return path


def _matching_rows():
    return [
        ["alphaland", ALPHALAND_STUNTING, ALPHALAND_WASTING, ALPHALAND_ANEMIA],
        ["betaland", BETALAND_STUNTING, BETALAND_WASTING, BETALAND_ANEMIA],
    ]


def test_pass_case(result, tmp_path):
    csv_path = _write_factsheet(tmp_path / "factsheet_pass.csv", _matching_rows())

    report = validate_against_factsheet(result, csv_path, level="admin1")

    assert report.passed is True
    assert "All validation checks passed." in report.summary()


def test_fail_case_sign_convention(result, tmp_path):
    rows = _matching_rows()
    # Bump Alphaland's official stunting rate by +5.0.
    rows[0][1] = ALPHALAND_STUNTING + 5.0
    csv_path = _write_factsheet(tmp_path / "factsheet_fail.csv", rows)

    report = validate_against_factsheet(result, csv_path, level="admin1")

    assert report.passed is False

    target = [
        row
        for row in report.rows
        if row.region.lower() == "alphaland" and row.indicator == "stunting_rate"
    ]
    assert len(target) == 1
    assert target[0].status == "fail"

    # validate_against_factsheet computes difference = generated - official
    # (see validation.py: `difference = round(float(generated_value) -
    # float(official_value), 3)`). Since official was bumped +5.0 while
    # generated stayed the same, the difference must be -5.0.
    assert target[0].difference == pytest.approx(-5.0, abs=1e-9)

    other_rows = [row for row in report.rows if row is not target[0]]
    assert all(row.status == "pass" for row in other_rows)


def test_extra_region_reports_missing_generated(result, tmp_path):
    rows = _matching_rows()
    rows.append(["gammaland", 10.0, 10.0, 10.0])
    csv_path = _write_factsheet(tmp_path / "factsheet_extra.csv", rows)

    report = validate_against_factsheet(result, csv_path, level="admin1")

    assert report.passed is False
    missing = [row for row in report.rows if row.status == "missing_generated_region"]
    assert len(missing) == 1
    assert missing[0].region.lower() == "gammaland"


def test_missing_factsheet_region_fails_coverage(result, tmp_path):
    csv_path = _write_factsheet(tmp_path / "partial.csv", [_matching_rows()[0]])

    report = validate_against_factsheet(result, csv_path, level="admin1")

    assert report.passed is False
    missing = [row for row in report.rows if row.status == "missing_factsheet_region"]
    assert len(missing) == 1
    assert missing[0].region == "Betaland"


def test_empty_report_never_passes():
    report = ValidationReport(rows=[], tolerance_pp=0.15)

    assert report.passed is False
    assert "No validation checks" in report.summary()


def test_empty_factsheet_is_rejected(result, tmp_path):
    csv_path = _write_factsheet(tmp_path / "empty.csv", [])

    with pytest.raises(ValueError, match="no regions"):
        validate_against_factsheet(result, csv_path, level="admin1")


def test_national_level_accepts_country_name(result, tmp_path):
    national = result.national.iloc[0]
    csv_path = _write_factsheet(
        tmp_path / "national.csv",
        [["India", national["stunting_rate"], national["wasting_rate"], national["anemia_rate"]]],
    )

    report = validate_against_factsheet(result, csv_path, level="national")

    assert report.passed is True
    assert {row.region for row in report.rows} == {"India"}


def test_national_level_rejects_multiple_rows(result, tmp_path):
    csv_path = _write_factsheet(tmp_path / "multiple.csv", _matching_rows())

    with pytest.raises(ValueError, match="exactly one"):
        validate_against_factsheet(result, csv_path, level="national")


def test_negative_tolerance_is_rejected(result, tmp_path):
    csv_path = _write_factsheet(tmp_path / "factsheet.csv", _matching_rows())

    with pytest.raises(ValueError, match="non-negative"):
        validate_against_factsheet(result, csv_path, tolerance_pp=-0.1)


def test_to_csv_header(result, tmp_path):
    csv_path = _write_factsheet(tmp_path / "factsheet_pass.csv", _matching_rows())
    report = validate_against_factsheet(result, csv_path, level="admin1")

    out_path = report.to_csv(tmp_path / "report.csv")
    with open(out_path, encoding="utf-8") as handle:
        header = next(csv.reader(handle))

    assert header == ["region", "indicator", "official", "generated", "difference", "status"]


def test_cluster_level_not_supported(result, tmp_path):
    csv_path = _write_factsheet(tmp_path / "factsheet_pass.csv", _matching_rows())

    with pytest.raises(ValueError):
        validate_against_factsheet(result, csv_path, level="cluster")
