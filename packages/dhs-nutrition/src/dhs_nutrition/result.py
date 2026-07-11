"""Container for computed nutrition indicator results and export helpers.

Operates on restricted (T1) DHS microdata supplied by the user; never bundles data.
"""


class IndicatorResult:
    """Holds computed nutrition indicators across levels and segments, with
    export helpers (e.g. to_json) that tag output data-tier for downstream handling.
    """
