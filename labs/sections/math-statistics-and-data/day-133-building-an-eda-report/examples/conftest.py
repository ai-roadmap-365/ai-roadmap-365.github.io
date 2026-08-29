"""Shared fixtures and headless matplotlib setup.

pytest finds this file by itself -- nothing imports it. `matplotlib.use`
must run before `pyplot` is imported anywhere, which is why it happens
here, first and unconditionally. Every figure this lab opens is closed by
the code that opened it; `_close_all_figures` is a backstop, not a
substitute.

Every directory fixture is a real temporary directory that is deleted when
the test finishes, so a full run of this lab leaves no image and no
Markdown file behind anywhere on your disk.
"""

import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from analysis import candidate_figures
from data import monthly_sales, perturbed


@pytest.fixture
def frame():
    return monthly_sales()


@pytest.fixture
def perturbed_frame():
    return perturbed()


@pytest.fixture
def candidates():
    return candidate_figures()


def _temporary_directory():
    with tempfile.TemporaryDirectory(prefix="d133-report-") as name:
        yield Path(name)


@pytest.fixture
def report_dir():
    yield from _temporary_directory()


@pytest.fixture
def second_report_dir():
    yield from _temporary_directory()


@pytest.fixture
def third_report_dir():
    yield from _temporary_directory()


@pytest.fixture(autouse=True)
def _close_all_figures():
    yield
    plt.close("all")
