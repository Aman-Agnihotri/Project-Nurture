"""Safe district/state name normalization for public demo boundary matching."""

from __future__ import annotations

import csv
import unicodedata
from functools import lru_cache
from pathlib import Path


CROSSWALK_PATH = Path(__file__).resolve().parent / "data" / "district_crosswalk.csv"


def _basic_normalize(value: object) -> str:
    """Normalize spelling mechanics without applying any geographic aliases."""
    text = unicodedata.normalize("NFKC", str(value or "")).lower().replace("&", " and ")
    text = "".join(" " if unicodedata.category(char).startswith("P") else char for char in text)
    return " ".join(text.split())


@lru_cache(maxsize=1)
def _aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}
    with CROSSWALK_PATH.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            raw_name = _basic_normalize(row.get("raw_name"))
            canonical_name = _basic_normalize(row.get("canonical_name"))
            if raw_name and canonical_name and not raw_name.startswith("example aliases"):
                aliases[raw_name] = canonical_name
    return aliases


def normalize(name: object) -> str:
    """Return a stable matching key, including documented crosswalk aliases."""
    normalized = _basic_normalize(name)
    return _aliases().get(normalized, normalized)
