"""Shared fixtures. pytest finds this file by itself -- nothing imports it.

`points` returns the same seeded cloud on every test, so two tests that
render it are rendering the identical data.

`png_dir` is a temporary directory OUTSIDE the lab, created and removed by
the fixture itself. Every render in this suite writes there and nowhere
else, which is why `tests/run_tests.sh` can assert afterwards that the lab
directory contains no `.png` at all.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

import render as R


@pytest.fixture
def points():
    return R.sample_points()


@pytest.fixture
def png_dir():
    with tempfile.TemporaryDirectory(prefix="d127-render-") as d:
        yield Path(d)
