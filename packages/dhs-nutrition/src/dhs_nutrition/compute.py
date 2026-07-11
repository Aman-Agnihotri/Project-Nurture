"""Computation of survey-weighted nutrition indicators across levels and segments.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from dhs_nutrition.loaders import ChildRecords, GPSClusters
from dhs_nutrition.result import IndicatorResult


def compute_indicators(
    children: ChildRecords,
    *,
    gps: GPSClusters | None = None,
    levels: tuple = ("national", "admin1", "cluster"),
    segments: tuple = ("sex", "residence", "wealth", "age_band"),
) -> IndicatorResult:
    raise NotImplementedError("Implemented in Task 2.2")
