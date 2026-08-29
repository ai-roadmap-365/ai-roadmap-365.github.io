"""Shared fixtures.

pytest finds this file by itself -- nothing imports it. Every experiment
is wrapped in a session-scoped fixture so the whole suite runs each one
exactly once; several of them average over a hundred or more train/test
splits and would otherwise be repeated for every assertion.

Nothing here writes to disk, binds a port or reaches the network.
"""

from __future__ import annotations

import pytest

import experiments as E


@pytest.fixture(scope="session")
def leakage():
    return E.target_leakage()


@pytest.fixture(scope="session")
def scaler_contamination():
    return E.scaling_contamination()


@pytest.fixture(scope="session")
def imputer_contamination():
    return E.imputer_contamination()


@pytest.fixture(scope="session")
def encoding():
    return E.target_encoding()


@pytest.fixture(scope="session")
def temporal():
    return E.temporal_leakage()


@pytest.fixture(scope="session")
def cyclical():
    return E.cyclical_distances()


@pytest.fixture(scope="session")
def colours():
    return E.ordinal_versus_one_hot()


@pytest.fixture(scope="session")
def interaction():
    return E.interaction()


@pytest.fixture(scope="session")
def vocabulary():
    return E.vocabulary_contamination()


@pytest.fixture(scope="session")
def audit():
    return E.audit_result()
