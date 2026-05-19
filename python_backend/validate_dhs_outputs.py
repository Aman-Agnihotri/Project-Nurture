from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import json
from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DASHBOARD_JSON = (
    REPO_ROOT
    / "project_nurture"
    / "public"
    / "generated"
    / "dhs_cluster_nutrition.json"
)
DEFAULT_DOCS_DIR = REPO_ROOT / "dhs_data" / "docs"
DEFAULT_REPORT_PATH = REPO_ROOT / "python_backend" / "outputs" / "dhs_validation_report.csv"
FACT_SHEET_DIR_PATTERN = "National, State and Union Territory, and District Fact Sheets*"

INDICATOR_PATTERNS = {
    "stunting_rate": r"81\.\s*Children under 5 years who are stunted.*?\(.*?\)\s+",
    "wasting_rate": r"82\.\s*Children under 5 years who are wasted.*?\(.*?\)\s+",
    "severe_wasting_rate": r"83\.\s*Children under 5 years who are severely wasted.*?\(.*?\)\s+",
    "underweight_rate": r"84\.\s*Children under 5 years who are underweight.*?\(.*?\)\s+",
    "overweight_rate": r"85\.\s*Children under 5 years who are overweight.*?\(.*?\)\s+",
    "anemia_rate": r"92\.\s*Children age 6-59 months who are anaemic.*?\(.*?\)\s+",
}

INDICATOR_LABELS = {
    "stunting_rate": "Stunting",
    "wasting_rate": "Wasting",
    "severe_wasting_rate": "Severe wasting",
    "underweight_rate": "Underweight",
    "overweight_rate": "Overweight",
    "anemia_rate": "Anemia",
}

VALUE_TOKEN = r"(?:\(?\d+(?:\.\d+)?\)?|na|\*)"
AREA_ALIASES = {
    "nct delhi": "nct of delhi",
}


@dataclass(frozen=True)
class ValidationRow:
    area: str
    indicator: str
    official: float | None
    generated: float | None
    difference: float | None
    status: str


def normalize_area_name(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip().lower())
    return AREA_ALIASES.get(normalized, normalized)


def parse_number(value: str) -> float | None:
    value = value.strip().strip("()")
    if value.lower() in {"na", "*"}:
        return None
    return float(value)


def extract_area_name(page_text: str) -> str | None:
    match = re.search(r"([A-Za-z& ]+?)\s+-\s+Key Indicators", page_text)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()


def parse_fact_sheet_pdf(path: Path) -> dict[str, dict[str, float]]:
    reader = PdfReader(str(path))
    areas: dict[str, dict[str, float]] = {}

    for page in reader.pages:
        text = (page.extract_text() or "").replace("\n", " ")
        if "Children under 5 years who are stunted" not in text:
            continue

        area_name = extract_area_name(text)
        if not area_name:
            continue

        indicators: dict[str, float] = {}
        for key, pattern in INDICATOR_PATTERNS.items():
            match = re.search(
                pattern + f"({VALUE_TOKEN})\\s+({VALUE_TOKEN})\\s+({VALUE_TOKEN})\\s+({VALUE_TOKEN})",
                text,
                flags=re.IGNORECASE,
            )
            if match:
                total_dhs = parse_number(match.group(3))
                if total_dhs is not None:
                    indicators[key] = total_dhs

        if indicators:
            areas[area_name] = indicators

    return areas


def load_official_values(docs_dir: Path) -> dict[str, dict[str, float]]:
    fact_sheet_dirs = sorted(path for path in docs_dir.glob(FACT_SHEET_DIR_PATTERN) if path.is_dir())
    if not fact_sheet_dirs:
        raise FileNotFoundError(f"Missing India DHS fact sheet directory in: {docs_dir}")

    fact_sheet_dir = fact_sheet_dirs[0]

    pdfs = [
        fact_sheet_dir / "India_National_Fact_Sheet.pdf",
    ]

    pdfs.extend(sorted(fact_sheet_dir.glob("*Compendium_Phase-I.pdf")))
    pdfs.extend(sorted(fact_sheet_dir.glob("*Compendium_Phase-II.pdf")))

    official: dict[str, dict[str, float]] = {}
    for pdf in pdfs:
        if not pdf.exists():
            raise FileNotFoundError(f"Missing India DHS fact sheet PDF: {pdf}")
        for area, values in parse_fact_sheet_pdf(pdf).items():
            official[normalize_area_name(area)] = values

    return official


def load_generated_values(path: Path) -> dict[str, dict[str, float]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing dashboard extract: {path}. Run python_backend/dhs_pipeline.py first."
        )

    data = json.loads(path.read_text(encoding="utf-8"))
    generated = {"india": data["national"]}

    for state in data.get("states", []):
        generated[normalize_area_name(state["state_name"])] = state

    return generated


def compare_values(
    official: dict[str, dict[str, float]],
    generated: dict[str, dict[str, float]],
    tolerance: float,
    anemia_tolerance: float,
) -> list[ValidationRow]:
    rows: list[ValidationRow] = []

    for area_key, official_values in sorted(official.items()):
        generated_values = generated.get(area_key)
        area_name = area_key.title().replace("Nct", "NCT")

        if not generated_values:
            rows.append(
                ValidationRow(
                    area=area_name,
                    indicator="Area",
                    official=None,
                    generated=None,
                    difference=None,
                    status="missing_generated_area",
                )
            )
            continue

        for key, label in INDICATOR_LABELS.items():
            official_value = official_values.get(key)
            generated_value = generated_values.get(key)
            if official_value is None or generated_value is None:
                rows.append(
                    ValidationRow(
                        area=area_name,
                        indicator=label,
                        official=official_value,
                        generated=generated_value,
                        difference=None,
                        status="missing_indicator",
                    )
                )
                continue

            difference = round(float(generated_value) - float(official_value), 3)
            indicator_tolerance = anemia_tolerance if key == "anemia_rate" else tolerance
            rows.append(
                ValidationRow(
                    area=area_name,
                    indicator=label,
                    official=float(official_value),
                    generated=float(generated_value),
                    difference=difference,
                    status="pass" if abs(difference) <= indicator_tolerance else "fail",
                )
            )

    return rows


def write_report(path: Path, rows: list[ValidationRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["area", "indicator", "official", "generated", "difference", "status"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "area": row.area,
                    "indicator": row.indicator,
                    "official": row.official,
                    "generated": row.generated,
                    "difference": row.difference,
                    "status": row.status,
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate generated India DHS dashboard indicators against official India DHS fact sheets."
    )
    parser.add_argument("--dashboard-json", type=Path, default=DEFAULT_DASHBOARD_JSON)
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--tolerance", type=float, default=0.15)
    parser.add_argument("--anemia-tolerance", type=float, default=2.0)
    args = parser.parse_args()

    official = load_official_values(args.docs_dir)
    generated = load_generated_values(args.dashboard_json)
    rows = compare_values(official, generated, args.tolerance, args.anemia_tolerance)
    write_report(args.report, rows)

    failures = [row for row in rows if row.status != "pass"]
    comparable = [row for row in rows if row.difference is not None]
    max_abs_diff = max((abs(row.difference) for row in comparable), default=0)

    print(f"Compared {len(comparable)} indicators across {len(official)} areas.")
    print(f"Tolerance: +/- {args.tolerance:.2f} percentage points")
    print(f"Anemia tolerance: +/- {args.anemia_tolerance:.2f} percentage points")
    print(f"Max absolute difference: {max_abs_diff:.3f} percentage points")
    print(f"Report: {args.report}")

    if failures:
        print("\nFailures:")
        for row in failures[:20]:
            print(
                f"- {row.area} / {row.indicator}: official={row.official}, "
                f"generated={row.generated}, diff={row.difference}, status={row.status}"
            )
        if len(failures) > 20:
            print(f"- ... {len(failures) - 20} more")
        return 1

    print("All validation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
