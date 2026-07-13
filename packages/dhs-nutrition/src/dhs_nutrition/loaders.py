"""Loaders for DHS PR (household member) recode files and GPS cluster shapefiles.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import shapefile

from dhs_nutrition import schemas
from dhs_nutrition.variable_map import VariableMap


def _title_label(value: object) -> str | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None

    text = str(value).strip()
    if not text or text.upper() == "NULL":
        return None

    special = {
        "nct": "NCT",
        "and": "and",
        "of": "of",
        "daman": "Daman",
        "diu": "Diu",
    }
    words = []
    for word in text.lower().split():
        clean = word.strip()
        words.append(special.get(clean, clean.title()))
    return " ".join(words).replace("&", "&")


@dataclass
class ChildRecords:
    """Loaded child-level records extracted from a DHS PR recode file."""

    df: pd.DataFrame
    labels: dict[str, dict[int, str]]
    variable_map: VariableMap
    source_path: Path | None = None

    def summary(self) -> dict:
        vm = self.variable_map
        age_col = self.df[vm.age_months]
        return {
            "children": len(self.df),
            "clusters": int(self.df[vm.cluster].nunique()),
            "admin1_units": int(self.df[vm.admin1].nunique()),
            "age_months_min": int(age_col.min()),
            "age_months_max": int(age_col.max()),
        }


@dataclass
class GPSClusters:
    """Loaded cluster geolocations extracted from a DHS GPS shapefile."""

    df: pd.DataFrame
    source_path: Path | None = None


def _extract_label_maps(dta_path: Path, variables: dict[str, str]) -> dict[str, dict[int, str]]:
    """Extract Stata value-label maps for several variables in a single read pass."""
    reader = pd.read_stata(dta_path, iterator=True, convert_categoricals=False)
    reader.read(nrows=1)
    var_to_label = dict(zip(reader._varlist, reader._lbllist, strict=True))
    value_labels = reader.value_labels()

    result: dict[str, dict[int, str]] = {}
    for name, variable in variables.items():
        label_key = var_to_label.get(variable)
        labels = value_labels.get(label_key, {})
        result[name] = {int(key): str(value) for key, value in labels.items()}
    return result


def load_pr_recode(
    path: str | Path, *, variable_map: VariableMap | None = None, columns_extra: tuple = ()
) -> ChildRecords:
    """Load a DHS PR (household member) recode file and filter to de facto children 0-59 months."""
    pr_path = Path(path)
    if not pr_path.exists():
        raise FileNotFoundError(f"Missing PR recode file: {pr_path}")

    vm = variable_map or VariableMap.dhs7()

    labels = _extract_label_maps(
        pr_path,
        {
            "admin1": vm.admin1,
            "residence": vm.residence,
            "wealth": vm.wealth,
            "sex": vm.sex,
        },
    )

    columns = vm.columns() + [column for column in columns_extra if column not in vm.columns()]
    df = pd.read_stata(pr_path, columns=columns, convert_categoricals=False)

    children = df[
        (df[vm.de_facto] == 1) & (df[vm.age_months].between(0, 59, inclusive="both"))
    ].copy()

    schemas.child_records_schema(vm).validate(children)

    return ChildRecords(df=children, labels=labels, variable_map=vm, source_path=pr_path)


def load_gps_clusters(path: str | Path) -> GPSClusters:
    """Load a DHS GPS cluster shapefile into a generic cluster geolocation table."""
    gps_path = Path(path)
    if not gps_path.exists():
        raise FileNotFoundError(f"Missing GPS shapefile: {gps_path}")

    reader = shapefile.Reader(str(gps_path))
    rows = []

    for record in reader.records():
        row = record.as_dict()
        lat = float(row["LATNUM"])
        lon = float(row["LONGNUM"])
        if not lat or not lon:
            continue

        rows.append(
            {
                "cluster_id": int(row["DHSCLUST"]),
                "dhs_id": row["DHSID"],
                "admin1_code": int(row["ADM1DHS"]),
                "admin1_name": _title_label(row["ADM1NAME"]),
                "admin2_name": _title_label(row["DHSREGNA"]),
                "residence": "Urban" if str(row["URBAN_RURA"]).upper() == "U" else "Rural",
                "latitude": lat,
                "longitude": lon,
                "altitude_m": None if float(row["ALT_GPS"]) == 9999 else float(row["ALT_GPS"]),
                "source": row["SOURCE"],
            }
        )

    df = pd.DataFrame(rows)
    schemas.gps_schema.validate(df)

    return GPSClusters(df=df, source_path=gps_path)
