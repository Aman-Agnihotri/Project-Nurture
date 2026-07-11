"""Deprecated: use python_backend/india_pipeline.py instead.

This module is kept only as a thin CLI shim so existing invocations of
``python python_backend/dhs_pipeline.py ...`` keep working during the
transition to the ``dhs_nutrition`` package-backed pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from india_pipeline import main as _main  # noqa: E402


def main() -> None:
    print(
        "DEPRECATED: python_backend/dhs_pipeline.py is now a shim; "
        "use python_backend/india_pipeline.py instead.",
        file=sys.stderr,
    )
    _main()


if __name__ == "__main__":
    main()
