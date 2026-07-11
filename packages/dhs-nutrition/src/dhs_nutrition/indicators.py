"""Definitions of child nutrition indicators (stunting, wasting, underweight,
overweight, anemia, mean z-scores) computed from anthropometric measurements.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.

Indicator definitions (recode variables in parentheses use the effective
:class:`~dhs_nutrition.variable_map.VariableMap`, shown here with their
DHS-7 defaults):

- **Population**: de facto living children age 0-59 months (``hv103`` == 1
  and ``hc1`` in 0..59), selected by :func:`~dhs_nutrition.loaders.load_pr_recode`.
- **Sample weight**: ``hv005`` / 1,000,000.
- **Validity (anthropometry)**: a height/weight z-score is valid when it is
  not null and less than 9990 (DHS uses >=9990 as a family of sentinel/flag
  codes for missing or implausible measurements).
- **Stunting** (haz = ``hc70``): stunted when valid haz < -200 (z < -2.00,
  values are stored as z-score x 100); severely stunted when valid
  haz < -300 (z < -3.00).
- **Underweight** (waz = ``hc71``): underweight when valid waz < -200;
  severely underweight when valid waz < -300.
- **Wasting** (whz = ``hc72``): wasted when valid whz < -200; severely
  wasted when valid whz < -300; overweight when valid whz > 200.
- **Anemia validity**: a child is eligible for the anemia denominator when
  selected for hemoglobin testing (``hv042`` == 1), aged 6-59 months
  (``hc1`` in 6..59), the hemoglobin measurement was obtained
  (``hc55`` == 0), and the anemia level is one of the coded categories
  (``hc57`` in {1, 2, 3, 4}).
- **Anemia**: among the anemia-valid population, anemic when
  ``hc57`` in {1, 2, 3}; severely anemic when ``hc57`` == 1.
  (``hc56``, the altitude/smoking-adjusted hemoglobin level, is part of the
  DHS anemia variable set but is NOT used by any indicator rule here.)
- **Weighted rates**: 100 * (sum of numerator weights) / (sum of
  denominator weights), where the denominator is the sum of sample weights
  over the valid population for that indicator; undefined (null) when the
  denominator is 0.
- **Weighted mean z-scores**: (sum of z * weight) / (sum of weight) / 100,
  over the valid population for that z-score; undefined (null) when the
  denominator is 0.

Note: this package intentionally does NOT compute a composite risk score
(such logic lives in the frontend, which derives its own presentation-layer
scores from these indicators).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dhs_nutrition.loaders import ChildRecords, _title_label
from dhs_nutrition.variable_map import VariableMap


def prepare_children(children: ChildRecords, *, segments: tuple = ()) -> pd.DataFrame:
    """Return a copy of ``children.df`` with derived columns needed for aggregation."""
    vm: VariableMap = children.variable_map
    df = children.df.copy()

    df["sample_weight"] = df[vm.weight] / 1_000_000
    df["child_count"] = 1

    sex_labels = {key: _title_label(value) for key, value in children.labels.get("sex", {}).items()}
    wealth_labels = {
        key: _title_label(value) for key, value in children.labels.get("wealth", {}).items()
    }
    residence_labels = {
        key: _title_label(value) for key, value in children.labels.get("residence", {}).items()
    }

    df["sex"] = df[vm.sex].map(sex_labels)
    df["wealth"] = df[vm.wealth].map(wealth_labels)
    df["residence"] = df[vm.residence].map(residence_labels)

    df["age_band"] = np.select(
        [
            df[vm.age_months].between(0, 5, inclusive="both"),
            df[vm.age_months].between(6, 23, inclusive="both"),
            df[vm.age_months].between(24, 59, inclusive="both"),
        ],
        ["0-5 months", "6-23 months", "24-59 months"],
        default="Unknown",
    )

    haz_valid = df[vm.haz].notna() & (df[vm.haz] < 9990)
    waz_valid = df[vm.waz].notna() & (df[vm.waz] < 9990)
    whz_valid = df[vm.whz].notna() & (df[vm.whz] < 9990)
    anemia_valid = (
        (df[vm.hemoglobin_selected] == 1)
        & df[vm.age_months].between(6, 59, inclusive="both")
        & (df[vm.hemoglobin_result] == 0)
        & df[vm.anemia_level].isin([1, 2, 3, 4])
    )

    df["haz_valid_n"] = haz_valid.astype(int)
    df["waz_valid_n"] = waz_valid.astype(int)
    df["whz_valid_n"] = whz_valid.astype(int)
    df["anemia_valid_n"] = anemia_valid.astype(int)

    df["haz_den_w"] = df["sample_weight"].where(haz_valid, 0)
    df["waz_den_w"] = df["sample_weight"].where(waz_valid, 0)
    df["whz_den_w"] = df["sample_weight"].where(whz_valid, 0)
    df["anemia_den_w"] = df["sample_weight"].where(anemia_valid, 0)

    df["stunted_w"] = df["sample_weight"].where(haz_valid & (df[vm.haz] < -200), 0)
    df["severely_stunted_w"] = df["sample_weight"].where(haz_valid & (df[vm.haz] < -300), 0)
    df["underweight_w"] = df["sample_weight"].where(waz_valid & (df[vm.waz] < -200), 0)
    df["severely_underweight_w"] = df["sample_weight"].where(waz_valid & (df[vm.waz] < -300), 0)
    df["wasted_w"] = df["sample_weight"].where(whz_valid & (df[vm.whz] < -200), 0)
    df["severely_wasted_w"] = df["sample_weight"].where(whz_valid & (df[vm.whz] < -300), 0)
    df["overweight_w"] = df["sample_weight"].where(whz_valid & (df[vm.whz] > 200), 0)
    df["anemia_w"] = df["sample_weight"].where(
        anemia_valid & df[vm.anemia_level].isin([1, 2, 3]), 0
    )
    df["severe_anemia_w"] = df["sample_weight"].where(
        anemia_valid & (df[vm.anemia_level] == 1), 0
    )

    df["haz_z_w"] = (df[vm.haz] * df["sample_weight"]).where(haz_valid, 0)
    df["waz_z_w"] = (df[vm.waz] * df["sample_weight"]).where(waz_valid, 0)
    df["whz_z_w"] = (df[vm.whz] * df["sample_weight"]).where(whz_valid, 0)

    return df


AGGREGATIONS = {
    "child_count": "sum",
    "sample_weight": "sum",
    "haz_valid_n": "sum",
    "waz_valid_n": "sum",
    "whz_valid_n": "sum",
    "anemia_valid_n": "sum",
    "haz_den_w": "sum",
    "waz_den_w": "sum",
    "whz_den_w": "sum",
    "anemia_den_w": "sum",
    "stunted_w": "sum",
    "severely_stunted_w": "sum",
    "underweight_w": "sum",
    "severely_underweight_w": "sum",
    "wasted_w": "sum",
    "severely_wasted_w": "sum",
    "overweight_w": "sum",
    "anemia_w": "sum",
    "severe_anemia_w": "sum",
    "haz_z_w": "sum",
    "waz_z_w": "sum",
    "whz_z_w": "sum",
}

COUNT_COLUMNS = [
    "child_count",
    "haz_valid_n",
    "waz_valid_n",
    "whz_valid_n",
    "anemia_valid_n",
]

RATE_COLUMNS = [
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


def _weighted_rate(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return (100 * numerator / denominator).where(denominator > 0)


def _weighted_mean_z(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return (numerator / denominator / 100).where(denominator > 0)


def add_indicator_rates(summary: pd.DataFrame) -> pd.DataFrame:
    """Add the nine weighted rate columns and three weighted mean z-score columns."""
    summary = summary.copy()

    summary["stunting_rate"] = _weighted_rate(summary["stunted_w"], summary["haz_den_w"])
    summary["severe_stunting_rate"] = _weighted_rate(
        summary["severely_stunted_w"], summary["haz_den_w"]
    )
    summary["underweight_rate"] = _weighted_rate(summary["underweight_w"], summary["waz_den_w"])
    summary["severe_underweight_rate"] = _weighted_rate(
        summary["severely_underweight_w"], summary["waz_den_w"]
    )
    summary["wasting_rate"] = _weighted_rate(summary["wasted_w"], summary["whz_den_w"])
    summary["severe_wasting_rate"] = _weighted_rate(
        summary["severely_wasted_w"], summary["whz_den_w"]
    )
    summary["overweight_rate"] = _weighted_rate(summary["overweight_w"], summary["whz_den_w"])
    summary["anemia_rate"] = _weighted_rate(summary["anemia_w"], summary["anemia_den_w"])
    summary["severe_anemia_rate"] = _weighted_rate(
        summary["severe_anemia_w"], summary["anemia_den_w"]
    )

    summary["mean_haz"] = _weighted_mean_z(summary["haz_z_w"], summary["haz_den_w"])
    summary["mean_waz"] = _weighted_mean_z(summary["waz_z_w"], summary["waz_den_w"])
    summary["mean_whz"] = _weighted_mean_z(summary["whz_z_w"], summary["whz_den_w"])

    return summary
