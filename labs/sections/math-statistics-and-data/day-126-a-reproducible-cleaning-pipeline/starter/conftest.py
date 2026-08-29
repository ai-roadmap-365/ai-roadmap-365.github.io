"""Shared fixtures. pytest finds this file by itself -- nothing imports it.

`raw_orders` returns a FRESH copy of the raw data on every test, so one
test's mutation can never leak into the next. `config` returns a fresh
COPY of the dict too, for the same reason -- a test that mutates its own
config must never affect another test's.
"""

import copy

import pytest

from data import CONFIG, build_raw_orders


@pytest.fixture
def raw_orders():
    return build_raw_orders()


@pytest.fixture
def config():
    return copy.deepcopy(CONFIG)
