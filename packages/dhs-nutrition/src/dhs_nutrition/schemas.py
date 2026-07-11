"""Pandera schemas used to validate loaded DHS PR recode and GPS cluster data.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from __future__ import annotations

import pandera.pandas as pa
from pandera.pandas import Check, Column


def child_records_schema(variable_map) -> pa.DataFrameSchema:
    """Post-filter invariants for the child (de facto, 0-59 month) record set."""
    return pa.DataFrameSchema(
        {
            variable_map.de_facto: Column(
                int, checks=Check.isin([1]), nullable=False, coerce=True
            ),
            variable_map.age_months: Column(
                float,
                checks=Check.in_range(0, 59, include_min=True, include_max=True),
                nullable=False,
                coerce=True,
            ),
            variable_map.weight: Column(
                float, checks=Check.greater_than_or_equal_to(0), nullable=False, coerce=True
            ),
            variable_map.haz: Column(float, nullable=True, coerce=True),
            variable_map.waz: Column(float, nullable=True, coerce=True),
            variable_map.whz: Column(float, nullable=True, coerce=True),
            variable_map.cluster: Column(nullable=False),
        },
        strict=False,
        coerce=False,
    )


gps_schema = pa.DataFrameSchema(
    {
        "cluster_id": Column(int, nullable=False, unique=True, coerce=True),
        "latitude": Column(float, nullable=False, coerce=True),
        "longitude": Column(float, nullable=False, coerce=True),
        "residence": Column(str, checks=Check.isin(["Urban", "Rural"]), nullable=False),
        "admin1_name": Column(str, nullable=True),
        "admin2_name": Column(str, nullable=True),
    },
    strict=False,
)


_LEVEL_KEY_COLUMNS = {
    "national": {},
    "admin1": {
        "admin1_code": Column(int, nullable=False, coerce=True),
        "admin1_name": Column(str, nullable=True),
    },
    "cluster": {
        "cluster_id": Column(int, nullable=False, coerce=True),
    },
}

_RATE_COLUMNS = [
    "stunting_rate",
    "severe_stunting_rate",
    "underweight_rate",
    "severe_underweight_rate",
    "wasting_rate",
    "severe_wasting_rate",
    "overweight_rate",
    "anemia_rate",
    "severe_anemia_rate",
]

_MEAN_COLUMNS = ["mean_haz", "mean_waz", "mean_whz"]

_COUNT_COLUMNS = [
    "child_count",
    "haz_valid_n",
    "waz_valid_n",
    "whz_valid_n",
    "anemia_valid_n",
]


def level_schema(level: str) -> pa.DataFrameSchema:
    """Schema for a computed indicator level table (national/admin1/cluster)."""
    if level not in _LEVEL_KEY_COLUMNS:
        raise ValueError(f"Unknown level: {level!r}. Expected one of {sorted(_LEVEL_KEY_COLUMNS)}")

    columns: dict[str, Column] = dict(_LEVEL_KEY_COLUMNS[level])
    for name in _COUNT_COLUMNS:
        columns[name] = Column(
            int, checks=Check.greater_than_or_equal_to(0), nullable=False, coerce=True
        )
    for name in _RATE_COLUMNS:
        columns[name] = Column(
            float,
            checks=Check.in_range(0, 100, include_min=True, include_max=True),
            nullable=True,
            coerce=True,
        )
    for name in _MEAN_COLUMNS:
        columns[name] = Column(float, nullable=True, coerce=True)

    return pa.DataFrameSchema(columns, strict=False)


factsheet_schema = pa.DataFrameSchema(
    {
        "region": Column(str, nullable=False, unique=True),
        "stunting_rate": Column(
            float, checks=Check.in_range(0, 100), nullable=True, required=False, coerce=True
        ),
        "severe_stunting_rate": Column(
            float, checks=Check.in_range(0, 100), nullable=True, required=False, coerce=True
        ),
        "wasting_rate": Column(
            float, checks=Check.in_range(0, 100), nullable=True, required=False, coerce=True
        ),
        "severe_wasting_rate": Column(
            float, checks=Check.in_range(0, 100), nullable=True, required=False, coerce=True
        ),
        "underweight_rate": Column(
            float, checks=Check.in_range(0, 100), nullable=True, required=False, coerce=True
        ),
        "overweight_rate": Column(
            float, checks=Check.in_range(0, 100), nullable=True, required=False, coerce=True
        ),
        "anemia_rate": Column(
            float, checks=Check.in_range(0, 100), nullable=True, required=False, coerce=True
        ),
    },
    strict=False,
)
