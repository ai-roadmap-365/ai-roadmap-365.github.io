"""Shared fixtures. pytest finds this file by itself -- nothing imports it.

Each fixture returns a FRESH copy of its table, so one test's mutation can
never leak into the next test.
"""

import pytest

from data import (
    build_clean_customers,
    build_coerce_frame,
    build_contract_violating_customers,
    build_country_frame,
    build_dropna_frame,
    build_duplicates_frame,
    build_income_spending,
    build_sensor_timeseries,
    build_temperature_readings,
    shuffle_rows,
)


@pytest.fixture
def income_spending():
    return build_income_spending()


@pytest.fixture
def temperature_readings():
    return build_temperature_readings()


@pytest.fixture
def dropna_frame():
    return build_dropna_frame()


@pytest.fixture
def sensor_timeseries():
    return build_sensor_timeseries()


@pytest.fixture
def shuffled_sensor_timeseries():
    return shuffle_rows(build_sensor_timeseries())


@pytest.fixture
def coerce_frame():
    return build_coerce_frame()


@pytest.fixture
def country_frame():
    return build_country_frame()


@pytest.fixture
def duplicates_frame():
    return build_duplicates_frame()


@pytest.fixture
def clean_customers():
    return build_clean_customers()


@pytest.fixture
def contract_violating_customers():
    return build_contract_violating_customers()
