"""Variable name mappings between DHS recode phases and internal field names.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, fields
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - exercised only on Python < 3.11
    import tomli as tomllib


@dataclass(frozen=True)
class VariableMap:
    """Maps internal field names to DHS recode variable names.

    The default values correspond to the DHS-7 (Phase 7) recode variable
    names. Earlier or later recode phases that rename variables should be
    represented as alternative ``VariableMap`` instances (e.g. loaded via
    :meth:`from_toml`) rather than by branching logic in this class.
    """

    #: Household sample weight (divide by 1,000,000 to use).
    weight: str = "hv005"
    #: Admin-1 (state/region) code.
    admin1: str = "hv024"
    #: Urban/rural residence code.
    residence: str = "hv025"
    #: Wealth index quintile/category code.
    wealth: str = "hv270"
    #: De facto household membership flag (1 = usual resident, present night before).
    de_facto: str = "hv103"
    #: Sex of household member code.
    sex: str = "hv104"
    #: Child's age in months.
    age_months: str = "hc1"
    #: Height-for-age z-score (x100).
    haz: str = "hc70"
    #: Weight-for-age z-score (x100).
    waz: str = "hc71"
    #: Weight-for-height z-score (x100).
    whz: str = "hc72"
    #: Hemoglobin: whether the member was selected for hemoglobin testing.
    hemoglobin_selected: str = "hv042"
    #: Hemoglobin measurement result code (0 = measured).
    hemoglobin_result: str = "hc55"
    #: Altitude/smoking-adjusted hemoglobin level (g/dl x10). Carried for
    #: completeness of the anemia variable set but is NOT used by any
    #: indicator logic in this package.
    hemoglobin_adjusted: str = "hc56"
    #: Anemia level category code (1=severe, 2=moderate, 3=mild, 4=not anemic).
    anemia_level: str = "hc57"
    #: Household identifier.
    household_id: str = "hhid"
    #: Line number within household.
    line_number: str = "hvidx"
    #: DHS cluster number.
    cluster: str = "hv001"
    #: Household number within cluster.
    household_number: str = "hv002"

    def columns(self) -> list[str]:
        """Return the ordered, de-duplicated list of all recode variable names."""
        seen: dict[str, None] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            seen.setdefault(value, None)
        return list(seen.keys())

    @classmethod
    def dhs7(cls) -> VariableMap:
        """Return the DHS-7 variable map (the defaults ARE the DHS-7 map)."""
        return cls()

    @classmethod
    def from_toml(cls, path: str | Path) -> VariableMap:
        """Load a variable map from a TOML file of ``field = "variable_name"`` overrides."""
        toml_path = Path(path)
        with toml_path.open("rb") as handle:
            data = tomllib.load(handle)

        valid_fields = {field.name for field in fields(cls)}
        unknown_keys = sorted(set(data) - valid_fields)
        if unknown_keys:
            raise ValueError(
                f"Unknown VariableMap field(s) in {toml_path}: {', '.join(unknown_keys)}"
            )

        return cls(**data)
