"""Shared fixtures. pytest finds this file by itself -- nothing imports it.

Each fixture returns a FRESH copy of its table, so one test's mutation
(there should not be any, but fixtures should not have to trust that) can
never leak into the next test.
"""

import pytest

from data import (
    build_cat_sales,
    build_large,
    build_orders,
    build_sales,
    build_weighted,
)


@pytest.fixture
def orders():
    return build_orders()


@pytest.fixture
def sales():
    return build_sales()


@pytest.fixture
def cat_sales():
    return build_cat_sales()


@pytest.fixture
def weighted():
    return build_weighted()


@pytest.fixture
def large():
    return build_large()
