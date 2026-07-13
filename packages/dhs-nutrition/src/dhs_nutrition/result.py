"""Container for computed nutrition indicator results and export helpers.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from dhs_nutrition.indicators import COUNT_COLUMNS

SCHEMA_VERSION = "1.0"
SHAPEFILE_COMPONENT_SUFFIXES = (".shp", ".shx", ".dbf")


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
    if isinstance(value, np.bool_):
        return bool(value)
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


def _national_record(row: pd.Series, columns: list[str]) -> dict[str, object]:
    record = {}
    for key in columns:
        value = row[key]
        if key in COUNT_COLUMNS:
            record[key] = int(round(float(value)))
        else:
            record[key] = _sanitize(value)
    return record


def _source_components(source_path: Path) -> tuple[Path, ...]:
    """Return every file whose bytes are consumed for a declared input path."""
    if source_path.suffix.lower() != ".shp":
        return (source_path,)
    return tuple(
        component
        for suffix in SHAPEFILE_COMPONENT_SUFFIXES
        if (component := source_path.with_suffix(suffix)).exists()
    )


@dataclass
class IndicatorResult:
    """Holds computed nutrition indicators across levels and segments, with
    export helpers (e.g. to_json) that tag output data-tier for downstream handling.
    """

    levels: dict[str, pd.DataFrame] = field(default_factory=dict)
    segments: dict[str, dict] = field(default_factory=dict)
    source_paths: tuple = ()

    @property
    def national(self) -> pd.DataFrame:
        return self._level("national")

    @property
    def admin1(self) -> pd.DataFrame:
        return self._level("admin1")

    @property
    def cluster(self) -> pd.DataFrame:
        return self._level("cluster")

    def _level(self, level: str) -> pd.DataFrame:
        try:
            return self.levels[level]
        except KeyError as exc:
            raise KeyError(
                f"Level {level!r} is not present in this IndicatorResult "
                f"(available: {sorted(self.levels)})"
            ) from exc

    def to_dataframe(self, level: str) -> pd.DataFrame:
        return self._level(level).copy()

    def to_json(self, path: str | Path, *, tier: str, extra_meta: dict | None = None) -> Path:
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
        if source_date_epoch:
            generated_at = datetime.fromtimestamp(int(source_date_epoch), tz=timezone.utc)
        else:
            generated_at = datetime.now(timezone.utc)

        from dhs_nutrition import __version__

        source_files: dict[str, str] = {}
        for source_path in self.source_paths:
            if source_path is None:
                continue
            source_path = Path(source_path)
            for component in _source_components(source_path):
                if not component.exists():
                    continue
                if component.name in source_files:
                    raise ValueError(
                        f"Duplicate source basename {component.name!r}; "
                        "source_files cannot represent both inputs without leaking paths"
                    )
                digest = hashlib.sha256(component.read_bytes()).hexdigest()
                source_files[component.name] = digest

        levels_payload: dict[str, object] = {}
        if "national" in self.levels:
            national_df = self.levels["national"]
            columns = list(national_df.columns)
            levels_payload["national"] = _national_record(national_df.iloc[0], columns)
        if "admin1" in self.levels:
            admin1_df = self.levels["admin1"]
            levels_payload["admin1"] = _records(admin1_df, list(admin1_df.columns))
        if "cluster" in self.levels:
            cluster_df = self.levels["cluster"]
            levels_payload["cluster"] = _records(cluster_df, list(cluster_df.columns))

        segments_payload: dict[str, object] = {}
        for level, entry in self.segments.items():
            columns = entry["columns"]
            table = entry["table"]
            segments_payload[level] = {
                "columns": columns,
                "rows": _table_rows(table, columns),
            }

        payload = {
            "schema_version": SCHEMA_VERSION,
            "tier": tier,
            "generated_at": generated_at.isoformat(),
            "package_version": __version__,
            "source_files": source_files,
            "levels": levels_payload,
            "segments": segments_payload,
        }
        if extra_meta is not None:
            payload["meta"] = extra_meta

        out_path.write_text(
            json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8"
        )
        return out_path

    @classmethod
    def from_json(cls, path: str | Path) -> IndicatorResult:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported schema_version {data.get('schema_version')!r}; "
                f"expected {SCHEMA_VERSION!r}"
            )

        levels: dict[str, pd.DataFrame] = {}
        raw_levels = data.get("levels", {})
        if "national" in raw_levels:
            levels["national"] = pd.DataFrame([raw_levels["national"]])
        if "admin1" in raw_levels:
            levels["admin1"] = pd.DataFrame(raw_levels["admin1"])
        if "cluster" in raw_levels:
            levels["cluster"] = pd.DataFrame(raw_levels["cluster"])

        segments: dict[str, dict] = {}
        for level, entry in data.get("segments", {}).items():
            columns = entry["columns"]
            rows = entry["rows"]
            segments[level] = {"columns": columns, "table": pd.DataFrame(rows, columns=columns)}

        return cls(levels=levels, segments=segments, source_paths=())
