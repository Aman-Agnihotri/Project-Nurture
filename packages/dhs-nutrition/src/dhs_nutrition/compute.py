"""Computation of survey-weighted nutrition indicators across levels and segments.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from __future__ import annotations

import pandas as pd

from dhs_nutrition import schemas
from dhs_nutrition.indicators import (
    AGGREGATIONS,
    COUNT_COLUMNS,
    add_indicator_rates,
    prepare_children,
)
from dhs_nutrition.loaders import ChildRecords, GPSClusters, _title_label
from dhs_nutrition.result import IndicatorResult

VALID_LEVELS = ("national", "admin1", "cluster")
VALID_SEGMENTS = ("sex", "residence", "wealth", "age_band")

INDICATOR_SET = [
    "child_count",
    "haz_valid_n",
    "waz_valid_n",
    "whz_valid_n",
    "anemia_valid_n",
    "stunting_rate",
    "severe_stunting_rate",
    "underweight_rate",
    "severe_underweight_rate",
    "wasting_rate",
    "severe_wasting_rate",
    "overweight_rate",
    "anemia_rate",
    "severe_anemia_rate",
    "mean_haz",
    "mean_waz",
    "mean_whz",
]

# Raw weighted-sum columns carried on segment tables (no derived rates).
RAW_SUM_COLUMNS = [
    "haz_den_w",
    "waz_den_w",
    "whz_den_w",
    "anemia_den_w",
    "stunted_w",
    "severely_stunted_w",
    "underweight_w",
    "severely_underweight_w",
    "wasted_w",
    "severely_wasted_w",
    "overweight_w",
    "anemia_w",
    "severe_anemia_w",
    "haz_z_w",
    "waz_z_w",
    "whz_z_w",
]


def _summarize(df: pd.DataFrame, group_by: list[str]) -> pd.DataFrame:
    if group_by:
        summary = df.groupby(group_by, dropna=False).agg(AGGREGATIONS).reset_index()
    else:
        summary = pd.DataFrame([df.agg(AGGREGATIONS)])
    return add_indicator_rates(summary)


def _as_integer_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for column in columns:
        if column in df.columns:
            df[column] = df[column].round().astype("Int64")
    return df


def _admin1_labels(children: ChildRecords) -> dict[int, str]:
    return {key: _title_label(value) for key, value in children.labels.get("admin1", {}).items()}


def _national_level(df: pd.DataFrame) -> pd.DataFrame:
    summary = _summarize(df, [])
    return summary[INDICATOR_SET]


def _admin1_level(df: pd.DataFrame, children: ChildRecords) -> pd.DataFrame:
    vm = children.variable_map
    summary = _summarize(df, [vm.admin1])
    summary["admin1_code"] = summary[vm.admin1].astype(int)
    summary["admin1_name"] = summary["admin1_code"].map(_admin1_labels(children))
    summary = summary.sort_values("admin1_name")
    summary = _as_integer_columns(summary, ["admin1_code", *COUNT_COLUMNS])
    return summary[["admin1_code", "admin1_name", *INDICATOR_SET]]


def _cluster_level(df: pd.DataFrame, children: ChildRecords, gps: GPSClusters) -> pd.DataFrame:
    vm = children.variable_map
    summary = _summarize(df, [vm.cluster])
    summary = summary.merge(gps.df, left_on=vm.cluster, right_on="cluster_id", how="left")
    summary = summary[summary["latitude"].notna()]
    summary = _as_integer_columns(summary, ["cluster_id", "admin1_code", *COUNT_COLUMNS])
    columns = [
        "cluster_id",
        "dhs_id",
        "admin1_code",
        "admin1_name",
        "admin2_name",
        "residence",
        "latitude",
        "longitude",
        *INDICATOR_SET,
    ]
    summary = summary[columns].sort_values(["admin1_name", "admin2_name", "cluster_id"])
    return summary


def _segment_table_national(df: pd.DataFrame, segments: tuple) -> tuple[list[str], pd.DataFrame]:
    keys = list(segments)
    summary = df.groupby(keys, dropna=False).agg(AGGREGATIONS).reset_index() if keys else (
        pd.DataFrame([df.agg(AGGREGATIONS)])
    )
    columns = [*segments, *COUNT_COLUMNS, *RAW_SUM_COLUMNS]
    summary = _as_integer_columns(summary, COUNT_COLUMNS)
    summary = summary.sort_values(list(segments)) if segments else summary
    return columns, summary[columns]


def _segment_table_admin1(
    df: pd.DataFrame, children: ChildRecords, segments: tuple
) -> tuple[list[str], pd.DataFrame]:
    vm = children.variable_map
    keys = [vm.admin1, *segments]
    summary = df.groupby(keys, dropna=False).agg(AGGREGATIONS).reset_index()
    summary["admin1_code"] = summary[vm.admin1].astype(int)
    summary = _as_integer_columns(summary, ["admin1_code", *COUNT_COLUMNS])
    summary = summary.sort_values(["admin1_code", *segments])
    columns = ["admin1_code", *segments, *COUNT_COLUMNS, *RAW_SUM_COLUMNS]
    return columns, summary[columns]


def _segment_table_cluster(
    df: pd.DataFrame, children: ChildRecords, segments: tuple, cluster_ids: pd.Series
) -> tuple[list[str], pd.DataFrame]:
    vm = children.variable_map
    keys = [vm.cluster, *segments]
    summary = df.groupby(keys, dropna=False).agg(AGGREGATIONS).reset_index()
    summary["cluster_id"] = summary[vm.cluster].astype(int)
    summary = summary[summary["cluster_id"].isin(cluster_ids)]
    summary = _as_integer_columns(summary, ["cluster_id", *COUNT_COLUMNS])
    summary = summary.sort_values(["cluster_id", *segments])
    columns = ["cluster_id", *segments, *COUNT_COLUMNS, *RAW_SUM_COLUMNS]
    return columns, summary[columns]


def compute_indicators(
    children: ChildRecords,
    *,
    gps: GPSClusters | None = None,
    levels: tuple = ("national", "admin1", "cluster"),
    segments: tuple = ("sex", "residence", "wealth", "age_band"),
) -> IndicatorResult:
    unknown_levels = sorted(set(levels) - set(VALID_LEVELS))
    if unknown_levels:
        raise ValueError(
            f"Unknown level(s): {', '.join(unknown_levels)}. Expected one of {VALID_LEVELS}"
        )

    unknown_segments = sorted(set(segments) - set(VALID_SEGMENTS))
    if unknown_segments:
        raise ValueError(
            f"Unknown segment(s): {', '.join(unknown_segments)}. Expected one of {VALID_SEGMENTS}"
        )

    if "cluster" in levels and gps is None:
        raise ValueError("cluster level requires gps=<GPSClusters> to be provided")

    df = prepare_children(children, segments=segments)

    level_tables: dict[str, pd.DataFrame] = {}
    segment_tables: dict[str, dict] = {}

    if "national" in levels:
        level_tables["national"] = _national_level(df)
        columns, table = _segment_table_national(df, segments)
        segment_tables["national"] = {"columns": columns, "table": table}
        schemas.level_schema("national").validate(level_tables["national"])

    if "admin1" in levels:
        level_tables["admin1"] = _admin1_level(df, children)
        columns, table = _segment_table_admin1(df, children, segments)
        segment_tables["admin1"] = {"columns": columns, "table": table}
        schemas.level_schema("admin1").validate(level_tables["admin1"])

    if "cluster" in levels:
        cluster_level = _cluster_level(df, children, gps)
        level_tables["cluster"] = cluster_level
        columns, table = _segment_table_cluster(
            df, children, segments, cluster_level["cluster_id"]
        )
        segment_tables["cluster"] = {"columns": columns, "table": table}
        schemas.level_schema("cluster").validate(level_tables["cluster"])

    source_paths = tuple(
        path
        for path in (children.source_path, gps.source_path if gps else None)
        if path is not None
    )

    return IndicatorResult(levels=level_tables, segments=segment_tables, source_paths=source_paths)
