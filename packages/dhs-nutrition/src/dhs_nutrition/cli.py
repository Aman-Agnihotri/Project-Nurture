"""Command-line interface for dhs-nutrition (inspect, compute, validate subcommands).

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pandera.errors import SchemaError

from dhs_nutrition.compute import compute_indicators
from dhs_nutrition.loaders import load_gps_clusters, load_pr_recode
from dhs_nutrition.result import IndicatorResult
from dhs_nutrition.validation import validate_against_factsheet


def _cmd_compute(args: argparse.Namespace) -> int:
    gps = load_gps_clusters(args.gps) if args.gps else None
    levels = tuple(args.levels)

    children = load_pr_recode(args.pr)
    result = compute_indicators(children, gps=gps, levels=levels, segments=tuple(args.segments))
    out_path = result.to_json(args.out, tier=args.tier)

    print(f"Wrote {out_path}")
    for level, table in result.levels.items():
        print(f"  {level}: {len(table)} row(s)")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    result = IndicatorResult.from_json(args.result)
    report = validate_against_factsheet(
        result, args.factsheet, level=args.level, tolerance_pp=args.tolerance
    )
    print(report.summary())

    if args.report:
        report.to_csv(args.report)
        print(f"Report written to {args.report}")

    return 0 if report.passed else 1


def _cmd_inspect(args: argparse.Namespace) -> int:
    children = load_pr_recode(args.pr)
    vm = children.variable_map

    source_name = children.source_path.name if children.source_path else "<unknown>"
    print(f"Source: {source_name}")

    for key, value in children.summary().items():
        print(f"  {key}: {value}")

    print("\nVariable map:")
    for field_name in [
        "weight",
        "admin1",
        "residence",
        "wealth",
        "de_facto",
        "sex",
        "age_months",
        "haz",
        "waz",
        "whz",
        "hemoglobin_selected",
        "hemoglobin_result",
        "hemoglobin_adjusted",
        "anemia_level",
        "household_id",
        "line_number",
        "cluster",
        "household_number",
    ]:
        variable = getattr(vm, field_name)
        present = variable in children.df.columns
        non_null = int(children.df[variable].notna().sum()) if present else 0
        print(
            f"  {field_name} ({variable}): present={'yes' if present else 'no'} "
            f"non_null={non_null}"
        )

    print("\nLabel maps:")
    for name, mapping in children.labels.items():
        print(f"  {name}: {mapping}")

    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dhs-nutrition")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compute_parser = subparsers.add_parser("compute", help="Compute nutrition indicators")
    compute_parser.add_argument("--pr", required=True, type=Path)
    compute_parser.add_argument("--gps", type=Path)
    compute_parser.add_argument(
        "--levels",
        nargs="+",
        default=None,
        help=(
            "Levels to compute (default: national admin1 cluster if --gps given, "
            "else national admin1)"
        ),
    )
    compute_parser.add_argument(
        "--segments", nargs="+", default=["sex", "residence", "wealth", "age_band"]
    )
    compute_parser.add_argument("--out", type=Path, default=Path("nutrition.json"))
    compute_parser.add_argument("--tier", default="restricted-local")
    compute_parser.set_defaults(func=_cmd_compute)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate computed indicators against a published factsheet"
    )
    validate_parser.add_argument("--result", required=True, type=Path)
    validate_parser.add_argument("--factsheet", required=True, type=Path)
    validate_parser.add_argument("--tolerance", type=float, default=0.15)
    validate_parser.add_argument("--level", default="admin1")
    validate_parser.add_argument("--report", type=Path)
    validate_parser.set_defaults(func=_cmd_validate)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect a DHS PR recode file")
    inspect_parser.add_argument("--pr", required=True, type=Path)
    inspect_parser.set_defaults(func=_cmd_inspect)

    return parser


def main(argv: list | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "compute" and args.levels is None:
        args.levels = ["national", "admin1", "cluster"] if args.gps else ["national", "admin1"]

    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, SchemaError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
