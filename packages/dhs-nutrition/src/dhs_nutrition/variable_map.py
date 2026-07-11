"""Variable name mappings between DHS recode phases and internal field names.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VariableMap:
    """Field definitions arrive in Task 2.2."""

    @classmethod
    def dhs7(cls) -> "VariableMap":
        raise NotImplementedError("Implemented in Task 2.2")

    @classmethod
    def from_toml(cls, path: str) -> "VariableMap":
        raise NotImplementedError("Implemented in Task 2.2")
