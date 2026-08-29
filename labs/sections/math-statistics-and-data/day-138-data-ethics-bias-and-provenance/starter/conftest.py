"""Shared fixtures for the Day 138 lab.

All four fixtures are built from a fixed seed, so every test in the suite
sees exactly the same synthetic table and every assertion below is a claim
about a specific, reproducible set of numbers rather than about a
distribution "on average".
"""

from __future__ import annotations

import pytest

import ethics as et

SEED = 138


@pytest.fixture(scope="session")
def register():
    """The synthetic register: quasi-identifiers plus one sensitive column."""
    return et.synthetic_register(n=5_000, seed=SEED)


@pytest.fixture(scope="session")
def generalised(register):
    """The same register with birth year coarsened to a decade band."""
    return et.generalise_quasi_ids(register)


@pytest.fixture(scope="session")
def fairness_pop():
    """The integer-exact, perfectly calibrated two-group population."""
    return et.fairness_population()


@pytest.fixture(scope="session")
def versions():
    """Two releases of one dataset, differing only in group composition."""
    return et.build_versions(n=2_000, seed=SEED)
