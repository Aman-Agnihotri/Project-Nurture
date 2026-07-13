"""dhs_nutrition: survey-weighted child nutrition indicators from DHS PR recodes.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from dhs_nutrition.compute import compute_indicators
from dhs_nutrition.loaders import ChildRecords, GPSClusters, load_gps_clusters, load_pr_recode
from dhs_nutrition.result import IndicatorResult
from dhs_nutrition.validation import ValidationReport, validate_against_factsheet
from dhs_nutrition.variable_map import VariableMap

__version__ = "0.1.0"

__all__ = [
    "ChildRecords",
    "GPSClusters",
    "IndicatorResult",
    "ValidationReport",
    "VariableMap",
    "__version__",
    "compute_indicators",
    "load_gps_clusters",
    "load_pr_recode",
    "validate_against_factsheet",
]
