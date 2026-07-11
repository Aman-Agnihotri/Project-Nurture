"""Validate a v1.0 India dashboard extract against an official factsheet CSV.

Thin CLI wrapper around ``dhs_nutrition.validate_against_factsheet``. The old
PDF-parsing flow (extracting values directly from NFHS-5 fact sheet PDFs) is
retired: the maintainer must transcribe official state-level factsheet
values into a CSV by hand (columns: region, stunting_rate, ...; see
``dhs_nutrition.schemas.factsheet_schema``). Fabricating or approximating
official values instead of transcribing them from the source documents is
forbidden.

Note: the old ``--anemia-tolerance`` (default 2.0pp) flag is gone. Anemia
indicators typically need a looser tolerance than anthropometric ones; pass
a higher ``--tolerance`` for a full run, or filter the report CSV for
anemia rows afterward if you need a tighter tolerance on other indicators.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dhs_nutrition import IndicatorResult, validate_against_factsheet

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DASHBOARD_JSON = (
    REPO_ROOT
    / "project_nurture"
    / "public"
    / "generated"
    / "dhs_cluster_nutrition.json"
)
DEFAULT_REPORT_PATH = REPO_ROOT / "python_backend" / "outputs" / "dhs_validation_report.csv"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a v1.0 India dashboard extract against a maintainer-transcribed "
            "state-level factsheet CSV."
        )
    )
    parser.add_argument("--dashboard-json", type=Path, default=DEFAULT_DASHBOARD_JSON)
    parser.add_argument(
        "--factsheet",
        type=Path,
        required=True,
        help=(
            "CSV of official NFHS-5 fact sheet values, transcribed by hand from the source "
            "PDFs (columns: region,stunting_rate,...). No default is provided; no state-level "
            "factsheet is committed to this repository."
        ),
    )
    parser.add_argument("--level", default="admin1")
    parser.add_argument("--tolerance", type=float, default=0.15)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    try:
        result = IndicatorResult.from_json(args.dashboard_json)
        report = validate_against_factsheet(
            result, args.factsheet, level=args.level, tolerance_pp=args.tolerance
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    report.to_csv(args.report)
    print(report.summary())
    print(f"Report: {args.report}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
