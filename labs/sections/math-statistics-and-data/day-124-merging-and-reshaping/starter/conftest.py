"""Shared fixtures. pytest finds this file by itself -- nothing imports it.

Each fixture returns a FRESH copy of its table, so one test's mutation
(there should not be any, but fixtures should not have to trust that) can
never leak into the next test.
"""

import pytest

from data import (
    build_dup_index_col,
    build_int_keyed,
    build_left_dup,
    build_left_keys,
    build_price_left,
    build_price_right,
    build_right_dup,
    build_right_keys,
    build_str_keyed,
    build_wide,
)


@pytest.fixture
def left_dup():
    return build_left_dup()


@pytest.fixture
def right_dup():
    return build_right_dup()


@pytest.fixture
def left_keys():
    return build_left_keys()


@pytest.fixture
def right_keys():
    return build_right_keys()


@pytest.fixture
def int_keyed():
    return build_int_keyed()


@pytest.fixture
def str_keyed():
    return build_str_keyed()


@pytest.fixture
def price_left():
    return build_price_left()


@pytest.fixture
def price_right():
    return build_price_right()


@pytest.fixture
def wide():
    return build_wide()


@pytest.fixture
def dup_index_col():
    return build_dup_index_col()
