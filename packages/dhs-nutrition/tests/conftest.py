"""Session-scoped fixtures built from the synthetic (fabricated) PR recode + GPS data.

See ``tests/fixtures/synthetic_recode.py`` for the full row-by-row layout. All
values are fabricated for arithmetic testing; nothing here is real DHS/NFHS data.
"""

# ruff: noqa: E402 -- package-root bootstrap must precede package-local imports.

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Pytest only adds the launch directory to sys.path. Add the package root so
# package-local test helpers remain importable when the suite is launched from
# the monorepo root as well as from packages/dhs-nutrition.
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from fixtures.synthetic_recode import write_synthetic_dta, write_synthetic_gps

from dhs_nutrition.compute import compute_indicators
from dhs_nutrition.loaders import load_gps_clusters, load_pr_recode


@pytest.fixture(scope="session")
def dta_path(tmp_path_factory):
    directory = tmp_path_factory.mktemp("dhs_nutrition_pr")
    return write_synthetic_dta(directory / "synthetic_pr.dta")


@pytest.fixture(scope="session")
def gps_path(tmp_path_factory):
    directory = tmp_path_factory.mktemp("dhs_nutrition_gps")
    return write_synthetic_gps(directory)


@pytest.fixture(scope="session")
def children(dta_path):
    return load_pr_recode(dta_path)


@pytest.fixture(scope="session")
def gps(gps_path):
    return load_gps_clusters(gps_path)


@pytest.fixture(scope="session")
def result(children, gps):
    return compute_indicators(children, gps=gps)
