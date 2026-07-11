"""Structural checks on dhs_nutrition.compute.compute_indicators output shapes,
using the synthetic fixture in tests/fixtures/synthetic_recode.py.
"""

from __future__ import annotations

import pytest

from dhs_nutrition.compute import (
    COUNT_COLUMNS,
    INDICATOR_SET,
    RAW_SUM_COLUMNS,
    compute_indicators,
)


def test_cluster_level_requires_gps(children):
    with pytest.raises(ValueError, match="cluster"):
        compute_indicators(children, levels=("cluster",))


def test_unknown_level_name_raises(children, gps):
    with pytest.raises(ValueError, match="Unknown level"):
        compute_indicators(children, gps=gps, levels=("national", "planet"))


def test_unknown_segment_name_raises(children, gps):
    with pytest.raises(ValueError, match="Unknown segment"):
        compute_indicators(children, gps=gps, segments=("galaxy",))


def test_cluster_202_absent_from_gps_dropped_from_cluster_level(result, children):
    vm = children.variable_map
    # Cluster 202 exists in the recode fixture but has no GPS record.
    assert 202 in children.df[vm.cluster].to_numpy()
    assert 202 not in result.cluster["cluster_id"].to_numpy()


def test_admin1_table_has_two_sorted_title_case_regions(result):
    assert len(result.admin1) == 2
    assert result.admin1["admin1_name"].tolist() == ["Alphaland", "Betaland"]


def test_cluster_table_columns(result):
    expected = [
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
    assert len(INDICATOR_SET) == 17
    assert list(result.cluster.columns) == expected


def test_cluster_segment_table_columns_and_no_rate_columns(result):
    entry = result.segments["cluster"]
    expected = [
        "cluster_id",
        "sex",
        "residence",
        "wealth",
        "age_band",
        *COUNT_COLUMNS,
        *RAW_SUM_COLUMNS,
    ]
    assert entry["columns"] == expected
    assert not any(column.endswith("_rate") for column in entry["columns"])


def test_cluster_segment_missing_combo_absent(result):
    # Cluster 101 is deliberately restricted to wealth in {1, 2} in the
    # fixture, so (cluster_id=101, wealth="Richest") must have no row.
    table = result.segments["cluster"]["table"]
    combo = table[(table["cluster_id"] == 101) & (table["wealth"] == "Richest")]
    assert combo.empty


def test_gps_altitude_sentinel_and_zero_coordinate_skip(gps):
    # Cluster 102 has ALT_GPS=9999 (sentinel) -> altitude_m must be None/NaN.
    row_102 = gps.df.loc[gps.df["cluster_id"] == 102].iloc[0]
    assert row_102["altitude_m"] is None or row_102["altitude_m"] != row_102["altitude_m"]

    # The record with LATNUM=0.0/LONGNUM=0.0 (cluster 999) must be skipped.
    assert 999 not in gps.df["cluster_id"].to_numpy()
