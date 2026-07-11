"""Validation of computed indicators against published DHS state/national factsheets.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from dhs_nutrition.result import IndicatorResult


class ValidationReport:
    """Holds the comparison between computed indicators and factsheet values."""


def validate_against_factsheet(
    result: IndicatorResult,
    factsheet_csv: str,
    *,
    level: str = "admin1",
    tolerance_pp: float = 0.15,
) -> ValidationReport:
    raise NotImplementedError("Implemented in Task 2.2")
