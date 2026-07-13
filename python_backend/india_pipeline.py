"""India NFHS-5 dashboard extract builder.

This is a thin consumer of the ``dhs_nutrition`` package: all survey-weighted
indicator arithmetic lives in the package, and this module only supplies
India-specific file layout, labels, and metadata.

Tier note: this script writes a Tier 1 (restricted-local) JSON extract built
from restricted DHS microdata supplied by the user. The output is written to
``project_nurture/public/generated/`` (git-ignored) by default; never commit
or redistribute it.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dhs_nutrition import VariableMap, compute_indicators, load_gps_clusters, load_pr_recode

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DHS_DIR = REPO_ROOT / "dhs_data"
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "project_nurture"
    / "public"
    / "generated"
    / "dhs_cluster_nutrition.json"
)

PR_RELATIVE_PATH = Path("IAPR7EDT") / "IAPR7EFL.DTA"
GPS_RELATIVE_PATH = Path("IAGE7AFL") / "IAGE7AFL.shp"

PRIVACY_NOTE = (
    "Generated from restricted DHS microdata and GPS files. Use locally; "
    "do not commit or redistribute this JSON."
)


def build_dashboard_data(dhs_dir: Path, output_path: Path) -> None:
    pr_path = dhs_dir / PR_RELATIVE_PATH
    gps_path = dhs_dir / GPS_RELATIVE_PATH

    if not pr_path.exists():
        raise FileNotFoundError(f"Missing PR file: {pr_path}")
    if not gps_path.exists():
        raise FileNotFoundError(f"Missing GPS shapefile: {gps_path}")

    children = load_pr_recode(pr_path, variable_map=VariableMap.dhs7())
    gps = load_gps_clusters(gps_path)

    result = compute_indicators(
        children,
        gps=gps,
        levels=("national", "admin1", "cluster"),
        segments=("sex", "wealth", "age_band"),
    )

    cluster_segments = result.segments["cluster"]["table"]

    extra_meta = {
        "survey": "India Standard DHS, 2019-21",
        "label_maps": {
            "state": children.labels["admin1"],
            "residence": children.labels["residence"],
            "wealth": children.labels["wealth"],
            "sex": children.labels["sex"],
        },
        "filter_dimensions": {
            "sex": sorted(cluster_segments["sex"].dropna().unique().tolist()),
            "wealth": sorted(cluster_segments["wealth"].dropna().unique().tolist()),
            "age_band": ["0-5 months", "6-23 months", "24-59 months"],
        },
        "privacy_note": PRIVACY_NOTE,
        "unit": "DHS displaced survey cluster",
    }

    result.to_json(output_path, tier="restricted-local", extra_meta=extra_meta)

    national = result.national
    admin1 = result.admin1
    cluster = result.cluster

    print(f"Wrote {output_path}")
    print(f"Clusters: {len(cluster):,}")
    print(f"States/UTs: {len(admin1):,}")
    print(f"Children 0-59 months: {int(national.iloc[0]['child_count']):,}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a local India Standard DHS child nutrition dashboard dataset."
    )
    parser.add_argument("--dhs-dir", type=Path, default=DEFAULT_DHS_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    build_dashboard_data(args.dhs_dir, args.output)


if __name__ == "__main__":
    main()
