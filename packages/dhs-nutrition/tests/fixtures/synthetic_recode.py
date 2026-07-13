"""Synthetic (entirely fabricated) DHS-shaped PR recode + GPS fixtures.

ALL values here are invented for testing arithmetic. No real DHS/NFHS
microdata, region names, or statistics appear anywhere in this module.
Region labels ("Alphaland"/"Betaland") and place names ("Alpha
District"/"Beta District") are deliberately fake.

``build_children_df`` is designed so that every indicator produced by
``dhs_nutrition`` from this fixture is hand-computable: sample weights are
restricted to {1.0, 2.0}, admin1/residence/wealth/sex codes take small label
sets, and z-score columns are drawn from a tiny fixed set of values whose
threshold membership (< -200, < -300, > 200, sentinel >= 9990) is obvious by
inspection.

Row layout (30 rows total):

- 9 "edge" rows (ids a-i below) each isolate exactly one filtering/validity
  rule described in ``dhs_nutrition.indicators``.
- 21 "regular" rows (ids r10-r30) spanning both sexes, wealth categories
  1-3 (except cluster 101, deliberately restricted to wealth in {1, 2} so a
  known segment combination is guaranteed absent), all three age bands, and
  residence/admin1 combinations tied 1:1 to cluster id.

Cluster -> admin1/residence mapping (fixed for every row using that cluster):
    101 -> admin1=1 (Alphaland), residence=1 (urban)
    102 -> admin1=1 (Alphaland), residence=2 (rural)
    201 -> admin1=2 (Betaland),  residence=2 (rural)
    202 -> admin1=2 (Betaland),  residence=1 (urban); ABSENT from the GPS
           fixture on purpose (see write_synthetic_gps).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import shapefile

# --- value label maps (only for the four Stata-labeled columns) -----------

_ADMIN1_LABELS = {1: "alphaland", 2: "betaland"}
_RESIDENCE_LABELS = {1: "urban", 2: "rural"}
_WEALTH_LABELS = {1: "poorest", 2: "middle", 3: "richest"}
_SEX_LABELS = {1: "male", 2: "female"}

_COLUMNS = [
    "hhid",
    "hvidx",
    "hv001",
    "hv002",
    "hv005",
    "hv024",
    "hv025",
    "hv042",
    "hv103",
    "hv104",
    "hv270",
    "hc1",
    "hc55",
    "hc56",
    "hc57",
    "hc70",
    "hc71",
    "hc72",
]


def _row(
    row_id: str,
    *,
    cluster: int,
    admin1: int,
    residence: int,
    wealth: int,
    sex: int,
    age_months: int,
    weight_units: int,
    hv042: int = 1,
    hv103: int = 1,
    hc55: int = 0,
    hc57: int,
    hc70: float,
    hc71: float,
    hc72: float,
    hh_number: int = 1,
) -> dict:
    return {
        "hhid": f"H{row_id}",
        "hvidx": 1,
        "hv001": cluster,
        "hv002": hh_number,
        "hv005": weight_units * 1_000_000,
        "hv024": admin1,
        "hv025": residence,
        "hv042": hv042,
        "hv103": hv103,
        "hv104": sex,
        "hv270": wealth,
        "hc1": age_months,
        "hc55": hc55,
        "hc56": 0,
        "hc57": hc57,
        "hc70": hc70,
        "hc71": hc71,
        "hc72": hc72,
    }


def build_children_df() -> tuple[pd.DataFrame, dict]:
    """Build the synthetic PR-recode-shaped DataFrame plus its Stata value labels."""
    rows = []

    # (a) hv103 == 0 (not de facto): must be filtered out entirely.
    rows.append(
        _row(
            "a",
            cluster=101,
            admin1=1,
            residence=1,
            wealth=1,
            sex=1,
            age_months=20,
            weight_units=1,
            hv103=0,
            hc57=2,
            hc70=-150,
            hc71=-150,
            hc72=-150,
        )
    )

    # (b) hc1 == 60 (age out of 0-59 range): must be filtered out.
    rows.append(
        _row(
            "b",
            cluster=101,
            admin1=1,
            residence=1,
            wealth=1,
            sex=2,
            age_months=60,
            weight_units=1,
            hc57=2,
            hc70=-150,
            hc71=-150,
            hc72=-150,
        )
    )

    # (c) hc70 == 9998 (sentinel, >= 9990): excluded from stunting numerator
    # AND denominator (haz_valid_n), but the child stays in the dataset and
    # counts toward waz/whz/anemia (hc71/hc72 are ordinary valid values,
    # hc57=4 -> anemia-eligible, "not anemic").
    rows.append(
        _row(
            "c",
            cluster=101,
            admin1=1,
            residence=1,
            wealth=1,
            sex=1,
            age_months=10,
            weight_units=2,
            hc57=4,
            hc70=9998,
            hc71=-150,
            hc72=-150,
        )
    )

    # (d) hc70 == NaN: excluded from the haz denominator; waz/whz/anemia
    # remain valid (hc57=3 -> anemic, not severe).
    rows.append(
        _row(
            "d",
            cluster=102,
            admin1=1,
            residence=2,
            wealth=2,
            sex=2,
            age_months=30,
            weight_units=1,
            hc57=3,
            hc70=float("nan"),
            hc71=-50,
            hc72=50,
        )
    )

    # (e) age 3 months (< 6): anemia-ineligible via the age gate even though
    # hc57=1 (would otherwise be severely anemic). Anthropometry is valid
    # and unremarkable (-50 for all three z-scores).
    rows.append(
        _row(
            "e",
            cluster=102,
            admin1=1,
            residence=2,
            wealth=2,
            sex=1,
            age_months=3,
            weight_units=1,
            hc57=1,
            hc70=-50,
            hc71=-50,
            hc72=-50,
        )
    )

    # (f) hv042 == 0 (household not selected for hemoglobin testing):
    # anemia-ineligible regardless of hc55/hc57. Anthropometry is stunted /
    # underweight / wasted (and severely so): -250 on all three.
    rows.append(
        _row(
            "f",
            cluster=102,
            admin1=1,
            residence=2,
            wealth=3,
            sex=2,
            age_months=40,
            weight_units=1,
            hv042=0,
            hc57=2,
            hc70=-250,
            hc71=-250,
            hc72=-250,
        )
    )

    # (g) hc55 == 1 (hemoglobin not obtained / invalid): anemia-ineligible.
    rows.append(
        _row(
            "g",
            cluster=201,
            admin1=2,
            residence=2,
            wealth=1,
            sex=1,
            age_months=50,
            weight_units=1,
            hc55=1,
            hc57=2,
            hc70=-50,
            hc71=-50,
            hc72=-50,
        )
    )

    # (h) hc57 == 8 (outside the coded 1..4 anemia categories):
    # anemia-ineligible.
    rows.append(
        _row(
            "h",
            cluster=201,
            admin1=2,
            residence=2,
            wealth=1,
            sex=2,
            age_months=45,
            weight_units=1,
            hc57=8,
            hc70=50,
            hc71=50,
            hc72=50,
        )
    )

    # (i) cluster 202: present in the recode but the GPS fixture has NO
    # record for cluster 202, so it must be dropped from cluster-level
    # output while remaining in national/admin1 aggregates. Fully valid,
    # severely stunted/underweight/wasted, anemic (not severe).
    rows.append(
        _row(
            "i",
            cluster=202,
            admin1=2,
            residence=1,
            wealth=2,
            sex=1,
            age_months=18,
            weight_units=2,
            hc57=3,
            hc70=-350,
            hc71=-350,
            hc72=-350,
        )
    )

    # -- regular rows: cluster 101 (admin1=1, urban), wealth restricted to
    # {1, 2} on purpose -> (cluster_id=101, wealth="Richest") is guaranteed
    # absent from any cluster-level segment table.
    rows.append(
        _row(
            "r10",
            cluster=101,
            admin1=1,
            residence=1,
            wealth=1,
            sex=1,
            age_months=2,
            weight_units=1,
            hc57=4,
            hc70=-50,
            hc71=-50,
            hc72=-50,
        )
    )
    rows.append(
        _row(
            "r11",
            cluster=101,
            admin1=1,
            residence=1,
            wealth=1,
            sex=2,
            age_months=12,
            weight_units=1,
            hc57=2,
            hc70=-250,
            hc71=-250,
            hc72=-250,
        )
    )
    rows.append(
        _row(
            "r12",
            cluster=101,
            admin1=1,
            residence=1,
            wealth=2,
            sex=1,
            age_months=36,
            weight_units=2,
            hc57=4,
            hc70=-150,
            hc71=-150,
            hc72=-150,
        )
    )
    rows.append(
        _row(
            "r13",
            cluster=101,
            admin1=1,
            residence=1,
            wealth=2,
            sex=2,
            age_months=45,
            weight_units=1,
            hc57=1,
            hc70=-350,
            hc71=-350,
            hc72=-350,
        )
    )
    rows.append(
        _row(
            "r14",
            cluster=101,
            admin1=1,
            residence=1,
            wealth=1,
            sex=1,
            age_months=8,
            weight_units=1,
            hc57=3,
            hc70=50,
            hc71=50,
            hc72=50,
        )
    )
    rows.append(
        _row(
            "r15",
            cluster=101,
            admin1=1,
            residence=1,
            wealth=2,
            sex=2,
            age_months=55,
            weight_units=1,
            hc57=4,
            hc70=250,
            hc71=250,
            hc72=250,
        )
    )

    # -- regular rows: cluster 102 (admin1=1, rural)
    rows.append(
        _row(
            "r16",
            cluster=102,
            admin1=1,
            residence=2,
            wealth=3,
            sex=1,
            age_months=4,
            weight_units=1,
            hc57=2,
            hc70=-150,
            hc71=-150,
            hc72=-150,
        )
    )
    rows.append(
        _row(
            "r17",
            cluster=102,
            admin1=1,
            residence=2,
            wealth=1,
            sex=2,
            age_months=20,
            weight_units=1,
            hc57=1,
            hc70=-350,
            hc71=-350,
            hc72=-350,
        )
    )
    rows.append(
        _row(
            "r18",
            cluster=102,
            admin1=1,
            residence=2,
            wealth=2,
            sex=1,
            age_months=48,
            weight_units=2,
            hc57=3,
            hc70=-50,
            hc71=-50,
            hc72=-50,
        )
    )
    rows.append(
        _row(
            "r19",
            cluster=102,
            admin1=1,
            residence=2,
            wealth=3,
            sex=2,
            age_months=15,
            weight_units=1,
            hc57=4,
            hc70=50,
            hc71=50,
            hc72=50,
        )
    )
    rows.append(
        _row(
            "r20",
            cluster=102,
            admin1=1,
            residence=2,
            wealth=1,
            sex=1,
            age_months=59,
            weight_units=1,
            hc57=2,
            hc70=-250,
            hc71=-250,
            hc72=-250,
        )
    )

    # -- regular rows: cluster 201 (admin1=2, rural)
    rows.append(
        _row(
            "r21",
            cluster=201,
            admin1=2,
            residence=2,
            wealth=1,
            sex=1,
            age_months=6,
            weight_units=1,
            hc57=1,
            hc70=-350,
            hc71=-350,
            hc72=-350,
        )
    )
    rows.append(
        _row(
            "r22",
            cluster=201,
            admin1=2,
            residence=2,
            wealth=2,
            sex=2,
            age_months=24,
            weight_units=1,
            hc57=3,
            hc70=-150,
            hc71=-150,
            hc72=-150,
        )
    )
    rows.append(
        _row(
            "r23",
            cluster=201,
            admin1=2,
            residence=2,
            wealth=3,
            sex=1,
            age_months=1,
            weight_units=1,
            hc57=4,
            hc70=-50,
            hc71=-50,
            hc72=-50,
        )
    )
    rows.append(
        _row(
            "r24",
            cluster=201,
            admin1=2,
            residence=2,
            wealth=1,
            sex=2,
            age_months=30,
            weight_units=2,
            hc57=2,
            hc70=250,
            hc71=250,
            hc72=250,
        )
    )
    rows.append(
        _row(
            "r25",
            cluster=201,
            admin1=2,
            residence=2,
            wealth=2,
            sex=1,
            age_months=18,
            weight_units=1,
            hc57=4,
            hc70=50,
            hc71=50,
            hc72=50,
        )
    )

    # -- regular rows: cluster 202 (admin1=2, urban; no GPS record)
    rows.append(
        _row(
            "r26",
            cluster=202,
            admin1=2,
            residence=1,
            wealth=1,
            sex=1,
            age_months=9,
            weight_units=1,
            hc57=3,
            hc70=-250,
            hc71=-250,
            hc72=-250,
        )
    )
    rows.append(
        _row(
            "r27",
            cluster=202,
            admin1=2,
            residence=1,
            wealth=2,
            sex=2,
            age_months=33,
            weight_units=1,
            hc57=1,
            hc70=-350,
            hc71=-350,
            hc72=-350,
        )
    )
    rows.append(
        _row(
            "r28",
            cluster=202,
            admin1=2,
            residence=1,
            wealth=3,
            sex=1,
            age_months=5,
            weight_units=1,
            hc57=2,
            hc70=-150,
            hc71=-150,
            hc72=-150,
        )
    )
    rows.append(
        _row(
            "r29",
            cluster=202,
            admin1=2,
            residence=1,
            wealth=1,
            sex=2,
            age_months=52,
            weight_units=1,
            hc57=4,
            hc70=50,
            hc71=50,
            hc72=50,
        )
    )
    rows.append(
        _row(
            "r30",
            cluster=202,
            admin1=2,
            residence=1,
            wealth=2,
            sex=1,
            age_months=22,
            weight_units=2,
            hc57=1,
            hc70=250,
            hc71=250,
            hc72=250,
        )
    )

    df = pd.DataFrame(rows, columns=_COLUMNS)

    # Columns carrying Stata value labels must be integer dtype for to_stata.
    for column in ("hv024", "hv025", "hv270", "hv104"):
        df[column] = df[column].astype("int32")
    _int64_columns = (
        "hvidx", "hv001", "hv002", "hv005", "hv042", "hv103", "hc1", "hc55", "hc56", "hc57",
    )
    for column in _int64_columns:
        df[column] = df[column].astype("int64")
    for column in ("hc70", "hc71", "hc72"):
        df[column] = df[column].astype("float64")

    value_labels = {
        "hv024": dict(_ADMIN1_LABELS),
        "hv025": dict(_RESIDENCE_LABELS),
        "hv270": dict(_WEALTH_LABELS),
        "hv104": dict(_SEX_LABELS),
    }

    return df, value_labels


def write_synthetic_dta(path: str | Path) -> Path:
    """Write the synthetic PR recode to ``path`` as a Stata .dta file."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df, value_labels = build_children_df()
    df.to_stata(out_path, write_index=False, value_labels=value_labels, version=118)
    return out_path


def write_synthetic_gps(directory: str | Path) -> Path:
    """Write a synthetic point shapefile named synthetic_gps.shp into ``directory``.

    Clusters:
        101 - Alphaland / Alpha District / Urban, ALT_GPS=120.0 (normal altitude)
        102 - Alphaland / Alpha District / Rural, ALT_GPS=9999 (sentinel -> None)
        201 - Betaland  / Beta District  / Rural, ALT_GPS=95.0 (normal altitude)
        999 - LATNUM=0.0/LONGNUM=0.0 -> the loader must skip this record entirely.

    Cluster 202 (present in the recode fixture) has NO record here on purpose.
    """
    out_dir = Path(directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    shp_path = out_dir / "synthetic_gps.shp"

    writer = shapefile.Writer(str(shp_path), shapeType=shapefile.POINT)
    writer.field("DHSCLUST", "N")
    writer.field("DHSID", "C")
    writer.field("ADM1DHS", "N")
    writer.field("ADM1NAME", "C")
    writer.field("DHSREGNA", "C")
    writer.field("URBAN_RURA", "C")
    writer.field("LATNUM", "F", decimal=6)
    writer.field("LONGNUM", "F", decimal=6)
    writer.field("ALT_GPS", "F", decimal=1)
    writer.field("SOURCE", "C")

    records = [
        (101, "AA0000101", 1, "Alphaland", "Alpha District", "U", 10.5, 76.5, 120.0),
        (102, "AA0000102", 1, "Alphaland", "Alpha District", "R", 10.6, 76.6, 9999.0),
        (201, "AA0000201", 2, "Betaland", "Beta District", "R", 11.5, 77.5, 95.0),
        (999, "AA0000999", 1, "Alphaland", "Alpha District", "U", 0.0, 0.0, 50.0),
    ]
    for cluster, dhs_id, admin1, admin1_name, admin2_name, urban_rural, lat, lon, alt in records:
        writer.point(lon, lat)
        writer.record(
            cluster, dhs_id, admin1, admin1_name, admin2_name, urban_rural, lat, lon, alt, "GPS"
        )

    writer.close()
    return shp_path
