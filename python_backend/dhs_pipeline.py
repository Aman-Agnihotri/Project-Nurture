from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import shapefile


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DHS_DIR = REPO_ROOT / "dhs_data"
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "project_nurture"
    / "public"
    / "generated"
    / "dhs_cluster_nutrition.json"
)

PR_RELATIVE_PATH = Path("IAPR7EDT") / "IAPR7EFL.DTA"
GPS_RELATIVE_PATH = Path("IAGE7AFL") / "IAGE7AFL.shp"

PR_COLUMNS = [
    "hhid",
    "hvidx",
    "hv001",
    "hv002",
    "hv005",
    "hv021",
    "hv022",
    "hv023",
    "hv024",
    "hv025",
    "hv042",
    "hv103",
    "hv104",
    "hv105",
    "hv270",
    "hc1",
    "hc2",
    "hc3",
    "hc13",
    "hc53",
    "hc55",
    "hc56",
    "hc57",
    "hc70",
    "hc71",
    "hc72",
    "hc73",
]


def _stata_label_map(dta_path: Path, variable: str) -> dict[int, str]:
    reader = pd.read_stata(dta_path, iterator=True, convert_categoricals=False)
    reader.read(nrows=1)
    var_to_label = dict(zip(reader._varlist, reader._lbllist))
    label_key = var_to_label.get(variable)
    labels = reader.value_labels().get(label_key, {})
    return {int(key): str(value) for key, value in labels.items()}


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


def _load_gps(gps_path: Path) -> pd.DataFrame:
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
                "state_code_gps": int(row["ADM1DHS"]),
                "state_name_gps": _title_label(row["ADM1NAME"]),
                "district_name": _title_label(row["DHSREGNA"]),
                "urban_rural_gps": "Urban"
                if str(row["URBAN_RURA"]).upper() == "U"
                else "Rural",
                "latitude": lat,
                "longitude": lon,
                "altitude_m": None if float(row["ALT_GPS"]) == 9999 else float(row["ALT_GPS"]),
                "source": row["SOURCE"],
            }
        )

    return pd.DataFrame(rows)


def _load_children(
    pr_path: Path,
) -> tuple[pd.DataFrame, dict[int, str], dict[int, str], dict[int, str], dict[int, str]]:
    state_labels = _stata_label_map(pr_path, "hv024")
    residence_labels = _stata_label_map(pr_path, "hv025")
    wealth_labels = _stata_label_map(pr_path, "hv270")
    sex_labels = _stata_label_map(pr_path, "hv104")

    df = pd.read_stata(pr_path, columns=PR_COLUMNS, convert_categoricals=False)

    children = df[
        (df["hv103"] == 1)
        & (df["hc1"].between(0, 59, inclusive="both"))
    ].copy()

    children["sample_weight"] = children["hv005"] / 1_000_000
    children["child_count"] = 1
    children["sex"] = children["hv104"].map({key: _title_label(value) for key, value in sex_labels.items()})
    children["wealth"] = children["hv270"].map(
        {key: _title_label(value) for key, value in wealth_labels.items()}
    )
    children["age_band"] = np.select(
        [
            children["hc1"].between(0, 5, inclusive="both"),
            children["hc1"].between(6, 23, inclusive="both"),
            children["hc1"].between(24, 59, inclusive="both"),
        ],
        ["0-5 months", "6-23 months", "24-59 months"],
        default="Unknown",
    )

    haz_valid = children["hc70"].notna() & (children["hc70"] < 9990)
    waz_valid = children["hc71"].notna() & (children["hc71"] < 9990)
    whz_valid = children["hc72"].notna() & (children["hc72"] < 9990)
    anemia_valid = (
        (children["hv042"] == 1)
        & children["hc1"].between(6, 59, inclusive="both")
        & (children["hc55"] == 0)
        & children["hc57"].isin([1, 2, 3, 4])
    )

    children["haz_valid_n"] = haz_valid.astype(int)
    children["waz_valid_n"] = waz_valid.astype(int)
    children["whz_valid_n"] = whz_valid.astype(int)
    children["anemia_valid_n"] = anemia_valid.astype(int)

    children["haz_den_w"] = children["sample_weight"].where(haz_valid, 0)
    children["waz_den_w"] = children["sample_weight"].where(waz_valid, 0)
    children["whz_den_w"] = children["sample_weight"].where(whz_valid, 0)
    children["anemia_den_w"] = children["sample_weight"].where(anemia_valid, 0)

    children["stunted_w"] = children["sample_weight"].where(haz_valid & (children["hc70"] < -200), 0)
    children["severely_stunted_w"] = children["sample_weight"].where(
        haz_valid & (children["hc70"] < -300), 0
    )
    children["underweight_w"] = children["sample_weight"].where(
        waz_valid & (children["hc71"] < -200), 0
    )
    children["severely_underweight_w"] = children["sample_weight"].where(
        waz_valid & (children["hc71"] < -300), 0
    )
    children["wasted_w"] = children["sample_weight"].where(whz_valid & (children["hc72"] < -200), 0)
    children["severely_wasted_w"] = children["sample_weight"].where(
        whz_valid & (children["hc72"] < -300), 0
    )
    children["overweight_w"] = children["sample_weight"].where(
        whz_valid & (children["hc72"] > 200), 0
    )
    children["anemia_w"] = children["sample_weight"].where(
        anemia_valid & children["hc57"].isin([1, 2, 3]), 0
    )
    children["severe_anemia_w"] = children["sample_weight"].where(
        anemia_valid & (children["hc57"] == 1), 0
    )

    children["haz_z_w"] = (children["hc70"] * children["sample_weight"]).where(haz_valid, 0)
    children["waz_z_w"] = (children["hc71"] * children["sample_weight"]).where(waz_valid, 0)
    children["whz_z_w"] = (children["hc72"] * children["sample_weight"]).where(whz_valid, 0)

    return children, state_labels, residence_labels, wealth_labels, sex_labels


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


def _weighted_rate(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return (100 * numerator / denominator).where(denominator > 0)


def _weighted_mean_z(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return (numerator / denominator / 100).where(denominator > 0)


def _add_indicator_columns(summary: pd.DataFrame) -> pd.DataFrame:
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

    rates = summary[["stunting_rate", "underweight_rate", "wasting_rate"]]
    summary["risk_score"] = (
        rates["stunting_rate"] * 0.45
        + rates["underweight_rate"] * 0.35
        + rates["wasting_rate"] * 0.20
    )
    summary["risk_score"] = summary["risk_score"].where(rates.notna().all(axis=1))

    return summary


def _summarize(children: pd.DataFrame, group_by: list[str]) -> pd.DataFrame:
    summary = children.groupby(group_by, dropna=False).agg(AGGREGATIONS).reset_index()
    return _add_indicator_columns(summary)


def _sanitize(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return round(number, 6)
    if isinstance(value, float):
        return round(value, 6)
    return value


def _records(df: pd.DataFrame, columns: list[str]) -> list[dict[str, object]]:
    output = []
    for row in df[columns].to_dict(orient="records"):
        output.append({key: _sanitize(value) for key, value in row.items()})
    return output


def _table_rows(df: pd.DataFrame, columns: list[str]) -> list[list[object]]:
    output = []
    for row in df[columns].to_dict(orient="records"):
        output.append([_sanitize(row[key]) for key in columns])
    return output


def _as_integer_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for column in columns:
        if column in df.columns:
            df[column] = df[column].round().astype("Int64")
    return df


def _national_record(row: pd.Series, columns: list[str]) -> dict[str, object]:
    record = {}
    for key in columns:
        value = row[key]
        if key in COUNT_COLUMNS:
            record[key] = int(round(float(value)))
        else:
            record[key] = _sanitize(value)
    return record


def build_dashboard_data(dhs_dir: Path, output_path: Path) -> None:
    pr_path = dhs_dir / PR_RELATIVE_PATH
    gps_path = dhs_dir / GPS_RELATIVE_PATH

    if not pr_path.exists():
        raise FileNotFoundError(f"Missing PR file: {pr_path}")
    if not gps_path.exists():
        raise FileNotFoundError(f"Missing GPS shapefile: {gps_path}")

    children, state_labels, residence_labels, wealth_labels, sex_labels = _load_children(pr_path)
    gps = _load_gps(gps_path)

    cluster_summary = _summarize(children, ["hv001"])
    cluster_summary = cluster_summary.merge(
        gps,
        left_on="hv001",
        right_on="cluster_id",
        how="left",
    )
    cluster_summary = cluster_summary[cluster_summary["latitude"].notna()]

    cluster_summary["state_name"] = cluster_summary["state_name_gps"]
    cluster_summary["sample_quality"] = np.select(
        [
            cluster_summary["haz_valid_n"] >= 10,
            cluster_summary["haz_valid_n"].between(5, 9, inclusive="both"),
        ],
        ["stable", "limited"],
        default="sparse",
    )
    cluster_summary = _as_integer_columns(
        cluster_summary,
        ["cluster_id", "state_code_gps", *COUNT_COLUMNS],
    )

    segment_summary = _summarize(children, ["hv001", "sex", "wealth", "age_band"])
    segment_summary = segment_summary.merge(
        gps,
        left_on="hv001",
        right_on="cluster_id",
        how="left",
    )
    segment_summary = segment_summary[segment_summary["latitude"].notna()]
    segment_summary["state_name"] = segment_summary["state_name_gps"]
    segment_summary["sample_quality"] = np.select(
        [
            segment_summary["haz_valid_n"] >= 10,
            segment_summary["haz_valid_n"].between(5, 9, inclusive="both"),
        ],
        ["stable", "limited"],
        default="sparse",
    )
    segment_summary = _as_integer_columns(
        segment_summary,
        ["cluster_id", "state_code_gps", *COUNT_COLUMNS],
    )

    state_summary = _summarize(children, ["hv024"])
    state_summary["state_code"] = state_summary["hv024"].astype(int)
    state_summary["state_name"] = state_summary["state_code"].map(
        {key: _title_label(value) for key, value in state_labels.items()}
    )
    state_summary = state_summary.sort_values("state_name")
    state_summary = _as_integer_columns(state_summary, ["state_code", *COUNT_COLUMNS])

    national = _add_indicator_columns(
        pd.DataFrame([children.agg(AGGREGATIONS)])
    ).iloc[0]

    cluster_columns = [
        "cluster_id",
        "dhs_id",
        "state_code_gps",
        "state_name",
        "district_name",
        "urban_rural_gps",
        "latitude",
        "longitude",
        "child_count",
        "haz_valid_n",
        "waz_valid_n",
        "whz_valid_n",
        "anemia_valid_n",
        "stunting_rate",
        "severe_stunting_rate",
        "underweight_rate",
        "wasting_rate",
        "severe_wasting_rate",
        "overweight_rate",
        "anemia_rate",
        "mean_haz",
        "mean_waz",
        "mean_whz",
        "risk_score",
        "sample_quality",
    ]
    state_columns = [
        "state_code",
        "state_name",
        "child_count",
        "haz_valid_n",
        "waz_valid_n",
        "whz_valid_n",
        "anemia_valid_n",
        "stunting_rate",
        "severe_stunting_rate",
        "underweight_rate",
        "wasting_rate",
        "severe_wasting_rate",
        "overweight_rate",
        "anemia_rate",
        "mean_haz",
        "mean_waz",
        "mean_whz",
        "risk_score",
    ]

    segment_columns = [
        "cluster_id",
        "sex",
        "wealth",
        "age_band",
        "child_count",
        "haz_valid_n",
        "waz_valid_n",
        "whz_valid_n",
        "anemia_valid_n",
        "haz_den_w",
        "waz_den_w",
        "whz_den_w",
        "anemia_den_w",
        "stunted_w",
        "severely_stunted_w",
        "underweight_w",
        "severely_underweight_w",
        "wasted_w",
        "severely_wasted_w",
        "overweight_w",
        "anemia_w",
        "severe_anemia_w",
        "haz_z_w",
        "waz_z_w",
        "whz_z_w",
    ]

    national_columns = [
        "child_count",
        "haz_valid_n",
        "waz_valid_n",
        "whz_valid_n",
        "anemia_valid_n",
        "stunting_rate",
        "severe_stunting_rate",
        "underweight_rate",
        "wasting_rate",
        "severe_wasting_rate",
        "overweight_rate",
        "anemia_rate",
        "mean_haz",
        "mean_waz",
        "mean_whz",
        "risk_score",
    ]

    payload = {
        "metadata": {
            "name": "India Standard DHS child nutrition dashboard extract",
            "survey": "India Standard DHS, 2019-21",
            "source_files": {
                "household_member_recode": str(PR_RELATIVE_PATH).replace("\\", "/"),
                "gps_clusters": str(GPS_RELATIVE_PATH).replace("\\", "/"),
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": "legacy",
            "tier": "restricted-local",
            "seed": None,
            "unit": "DHS displaced survey cluster",
            "local_only": True,
            "privacy_note": (
                "Generated from restricted DHS microdata and GPS files. Use locally; "
                "do not commit or redistribute this JSON."
            ),
            "coverage_note": (
                "National and state summaries use all eligible PR records. Map and filter "
                "segments use clusters matched to DHS GPS coordinates."
            ),
            "indicator_notes": {
                "population": "De facto living children age 0-59 months from the PR file.",
                "weight": "Household sample weight hv005 / 1,000,000.",
                "stunting": "hc70 < -200 among valid hc70 < 9990.",
                "underweight": "hc71 < -200 among valid hc71 < 9990.",
                "wasting": "hc72 < -200 among valid hc72 < 9990.",
                "anemia": (
                    "hc57 in 1..3 among children age 6-59 months selected for hemoglobin "
                    "testing with valid hemoglobin measurement (hv042 = 1, hc55 = 0)."
                ),
                "gps": "DHS GPS cluster coordinates are displaced for confidentiality.",
            },
            "label_maps": {
                "state": state_labels,
                "residence": residence_labels,
                "wealth": wealth_labels,
                "sex": sex_labels,
            },
            "filter_dimensions": {
                "sex": sorted(segment_summary["sex"].dropna().unique().tolist()),
                "wealth": sorted(segment_summary["wealth"].dropna().unique().tolist()),
                "age_band": ["0-5 months", "6-23 months", "24-59 months"],
            },
        },
        "cluster_segment_columns": segment_columns,
        "national": _national_record(national, national_columns),
        "states": _records(state_summary, state_columns),
        "clusters": _records(
            cluster_summary.sort_values(["state_name", "district_name", "cluster_id"]),
            cluster_columns,
        ),
        "cluster_segments": _table_rows(
            segment_summary.sort_values(
                ["state_name", "district_name", "cluster_id", "sex", "wealth", "age_band"]
            ),
            segment_columns,
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")

    print(f"Wrote {output_path}")
    print(f"Clusters: {len(payload['clusters']):,}")
    print(f"Cluster segments: {len(payload['cluster_segments']):,}")
    print(f"States/UTs: {len(payload['states']):,}")
    print(f"Children 0-59 months: {payload['national']['child_count']:,}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a local India Standard DHS child nutrition dashboard dataset."
    )
    parser.add_argument("--dhs-dir", type=Path, default=DEFAULT_DHS_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    build_dashboard_data(args.dhs_dir, args.output)


if __name__ == "__main__":
    main()
