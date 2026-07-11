"""Validation of computed indicators against published DHS state/national factsheets.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from dhs_nutrition import schemas
from dhs_nutrition.result import IndicatorResult

_AREA_ALIASES = {
    "nct delhi": "nct of delhi",
}

_COMPARABLE_INDICATORS = [
    "stunting_rate",
    "severe_stunting_rate",
    "wasting_rate",
    "severe_wasting_rate",
    "underweight_rate",
    "overweight_rate",
    "anemia_rate",
]


def _normalize_region(value: str) -> str:
    normalized = re.sub(r"\s+", " ", str(value).strip().lower())
    return _AREA_ALIASES.get(normalized, normalized)


@dataclass(frozen=True)
class ValidationRow:
    region: str
    indicator: str
    official: float | None
    generated: float | None
    difference: float | None
    status: str


class ValidationReport:
    """Holds the comparison between computed indicators and factsheet values."""

    def __init__(self, rows: list[ValidationRow], tolerance_pp: float):
        self.rows = rows
        self.tolerance_pp = tolerance_pp

    @property
    def passed(self) -> bool:
        return all(row.status == "pass" for row in self.rows)

    def to_csv(self, path: str | Path) -> Path:
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        frame = pd.DataFrame(
            [
                {
                    "region": row.region,
                    "indicator": row.indicator,
                    "official": row.official,
                    "generated": row.generated,
                    "difference": row.difference,
                    "status": row.status,
                }
                for row in self.rows
            ],
            columns=["region", "indicator", "official", "generated", "difference", "status"],
        )
        frame.to_csv(out_path, index=False)
        return out_path

    def summary(self) -> str:
        comparable = [row for row in self.rows if row.difference is not None]
        failures = [row for row in self.rows if row.status != "pass"]
        regions = {row.region for row in self.rows}
        max_abs_diff = max((abs(row.difference) for row in comparable), default=0)

        lines = [
            f"Compared {len(comparable)} indicators across {len(regions)} regions.",
            f"Tolerance: +/- {self.tolerance_pp:.2f} percentage points",
            f"Max absolute difference: {max_abs_diff:.3f} percentage points",
        ]

        if failures:
            lines.append("")
            lines.append("Failures:")
            for row in failures[:20]:
                lines.append(
                    f"- {row.region} / {row.indicator}: official={row.official}, "
                    f"generated={row.generated}, diff={row.difference}, status={row.status}"
                )
            if len(failures) > 20:
                lines.append(f"- ... {len(failures) - 20} more")
        else:
            lines.append("All validation checks passed.")

        return "\n".join(lines)


def validate_against_factsheet(
    result: IndicatorResult,
    factsheet_csv: str | Path,
    *,
    level: str = "admin1",
    tolerance_pp: float = 0.15,
) -> ValidationReport:
    if level not in ("national", "admin1"):
        raise ValueError(
            f"Unsupported level {level!r}: factsheet validation supports national/admin1"
        )

    csv_path = Path(factsheet_csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing factsheet CSV: {csv_path}")

    factsheet = pd.read_csv(csv_path)
    schemas.factsheet_schema.validate(factsheet)

    indicator_columns = [col for col in _COMPARABLE_INDICATORS if col in factsheet.columns]
    if not indicator_columns:
        raise ValueError(
            f"Factsheet {csv_path} does not contain any recognized indicator columns "
            f"(expected one of {_COMPARABLE_INDICATORS})"
        )

    generated_df = result.to_dataframe(level)

    generated_by_region: dict[str, dict] = {}
    if level == "national":
        row = generated_df.iloc[0].to_dict()
        generated_by_region["national"] = row
    else:
        for _, row in generated_df.iterrows():
            region_key = _normalize_region(row["admin1_name"])
            generated_by_region[region_key] = row.to_dict()

    factsheet_by_region: dict[str, dict] = {}
    for _, row in factsheet.iterrows():
        factsheet_by_region[_normalize_region(row["region"])] = row.to_dict()

    rows: list[ValidationRow] = []
    for region_key, official_values in sorted(factsheet_by_region.items()):
        generated_values = generated_by_region.get(region_key)
        region_name = str(
            next(
                (
                    r["region"]
                    for _, r in factsheet.iterrows()
                    if _normalize_region(r["region"]) == region_key
                ),
                region_key,
            )
        )

        if generated_values is None:
            rows.append(
                ValidationRow(
                    region=region_name,
                    indicator="region",
                    official=None,
                    generated=None,
                    difference=None,
                    status="missing_generated_region",
                )
            )
            continue

        for indicator in indicator_columns:
            official_value = official_values.get(indicator)
            generated_value = generated_values.get(indicator)

            official_is_missing = official_value is None or (
                isinstance(official_value, float) and pd.isna(official_value)
            )
            generated_is_missing = generated_value is None or (
                isinstance(generated_value, float) and pd.isna(generated_value)
            )

            if official_is_missing or generated_is_missing:
                rows.append(
                    ValidationRow(
                        region=region_name,
                        indicator=indicator,
                        official=None if official_is_missing else float(official_value),
                        generated=None if generated_is_missing else float(generated_value),
                        difference=None,
                        status="missing_indicator",
                    )
                )
                continue

            difference = round(float(generated_value) - float(official_value), 3)
            status = "pass" if abs(difference) <= tolerance_pp else "fail"
            rows.append(
                ValidationRow(
                    region=region_name,
                    indicator=indicator,
                    official=float(official_value),
                    generated=float(generated_value),
                    difference=difference,
                    status=status,
                )
            )

    return ValidationReport(rows=rows, tolerance_pp=tolerance_pp)
