"""Loaders for DHS PR (household member) recode files and GPS cluster shapefiles.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from dhs_nutrition.variable_map import VariableMap


class ChildRecords:
    """Loaded child-level records extracted from a DHS PR recode file."""


class GPSClusters:
    """Loaded cluster geolocations extracted from a DHS GPS shapefile."""


def load_pr_recode(
    path: str, *, variable_map: VariableMap | None = None, columns_extra: tuple = ()
) -> ChildRecords:
    raise NotImplementedError("Implemented in Task 2.2")


def load_gps_clusters(path: str) -> GPSClusters:
    raise NotImplementedError("Implemented in Task 2.2")
