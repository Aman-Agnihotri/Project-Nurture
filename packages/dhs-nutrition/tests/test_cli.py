"""End-to-end checks on dhs_nutrition.cli.main using the synthetic fixture."""

from __future__ import annotations

import json

from dhs_nutrition import cli


def test_inspect_reports_coverage_and_labels(dta_path, capsys):
    exit_code = cli.main(["inspect", "--pr", str(dta_path)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "Variable map:" in out
    assert "non_null=" in out
    assert "Label maps:" in out


def test_compute_with_gps_writes_v1_json(dta_path, gps_path, tmp_path):
    out_path = tmp_path / "with_gps.json"
    exit_code = cli.main(
        [
            "compute",
            "--pr",
            str(dta_path),
            "--gps",
            str(gps_path),
            "--out",
            str(out_path),
        ]
    )

    assert exit_code == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert set(payload["levels"].keys()) == {"national", "admin1", "cluster"}


def test_compute_without_levels_or_gps_defaults_national_admin1(dta_path, tmp_path):
    out_path = tmp_path / "no_gps.json"
    exit_code = cli.main(
        ["compute", "--pr", str(dta_path), "--out", str(out_path)]
    )

    assert exit_code == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert set(payload["levels"].keys()) == {"national", "admin1"}


def test_compute_explicit_cluster_level_without_gps_errors(dta_path, tmp_path, capsys):
    out_path = tmp_path / "should_not_exist.json"
    exit_code = cli.main(
        [
            "compute",
            "--pr",
            str(dta_path),
            "--levels",
            "cluster",
            "--out",
            str(out_path),
        ]
    )

    assert exit_code == 2
    err = capsys.readouterr().err
    assert "cluster" in err
    assert not out_path.exists()


def test_validate_pass_and_fail(dta_path, gps_path, tmp_path):
    import csv

    result_path = tmp_path / "result.json"
    cli.main(
        [
            "compute",
            "--pr",
            str(dta_path),
            "--gps",
            str(gps_path),
            "--out",
            str(result_path),
        ]
    )

    from dhs_nutrition.result import IndicatorResult

    loaded = IndicatorResult.from_json(result_path)
    admin1 = loaded.admin1

    def _write_csv(path, bump):
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["region", "stunting_rate", "wasting_rate", "anemia_rate"])
            for _, row in admin1.iterrows():
                writer.writerow(
                    [
                        row["admin1_name"],
                        float(row["stunting_rate"]) + bump,
                        float(row["wasting_rate"]) + bump,
                        float(row["anemia_rate"]) + bump,
                    ]
                )
        return path

    pass_csv = _write_csv(tmp_path / "pass.csv", 0.0)
    fail_csv = _write_csv(tmp_path / "fail.csv", 5.0)

    exit_code_pass = cli.main(
        ["validate", "--result", str(result_path), "--factsheet", str(pass_csv)]
    )
    assert exit_code_pass == 0

    exit_code_fail = cli.main(
        ["validate", "--result", str(result_path), "--factsheet", str(fail_csv)]
    )
    assert exit_code_fail == 1


def test_validate_nonexistent_factsheet_errors(dta_path, gps_path, tmp_path):
    result_path = tmp_path / "result.json"
    cli.main(
        [
            "compute",
            "--pr",
            str(dta_path),
            "--gps",
            str(gps_path),
            "--out",
            str(result_path),
        ]
    )

    exit_code = cli.main(
        [
            "validate",
            "--result",
            str(result_path),
            "--factsheet",
            str(tmp_path / "does_not_exist.csv"),
        ]
    )
    assert exit_code == 2


def test_compute_missing_pr_file_errors(tmp_path, capsys):
    exit_code = cli.main(
        [
            "compute",
            "--pr",
            str(tmp_path / "missing.dta"),
            "--out",
            str(tmp_path / "out.json"),
        ]
    )

    assert exit_code == 2
    err = capsys.readouterr().err
    assert "error:" in err
