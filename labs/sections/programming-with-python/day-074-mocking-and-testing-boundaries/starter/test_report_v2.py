"""Exercise 5 — test the refactored core with your own doubles.

    .venv/bin/pytest starter/test_report_v2.py -q

Not one `patch` call in this file, not one temporary directory, nothing to
undo. Every boundary is an argument, so a test just passes a different one.

Delete each `raise NotImplementedError(...)` as you complete that exercise.
"""

import datetime

import pytest
from fakes import (
    DummyClient,
    FakeSensorClient,
    RecordingSleep,
    SpyClock,
    StubSensorClient,
    frozen_clock,
)
from report_v2 import (
    DailyReport,
    ReadingsUnavailable,
    ReportError,
    ReportUnavailable,
    build_report,
    summarise,
)

DAY = datetime.date(2026, 4, 12)
READINGS = [12.0, 14.0, 20.0, 22.0] * 6  # 24 values; the mean is exactly 17.0


def test_summarise_reduces_a_day_to_four_numbers():
    """Exercise 5a — assert `summarise("ALPHA", DAY, READINGS)` equals
    `DailyReport("ALPHA", DAY, 24, 12.0, 22.0, 17.0)`. A frozen dataclass
    compares by value, so one `==` covers all six fields."""
    raise NotImplementedError("Exercise 5a: compare the whole report value")


def test_summarise_refuses_an_empty_day():
    """Exercise 5b — use `pytest.raises(ReportError, match="empty day")` around
    `summarise("ALPHA", DAY, [])`."""
    raise NotImplementedError("Exercise 5b: assert the empty-day refusal")


def test_build_report_uses_the_injected_clock_and_client():
    """Exercise 5c — build a report with `clock=frozen_clock(DAY)` and
    `client=StubSensorClient(READINGS)`. Assert `report.day == DAY` and
    `report.mean == 17.0`."""
    raise NotImplementedError("Exercise 5c: build a report from a stub clock and stub client")


def test_the_client_is_asked_for_the_clock_s_day():
    """Exercise 5d — build a report for station `"BRAVO"` with a
    `FakeSensorClient([READINGS])`, then assert
    `client.calls == [("BRAVO", "2026-04-12")]`. The fake answers the question a
    mock's `assert_called_once_with` would answer, and you can read how."""
    raise NotImplementedError("Exercise 5d: assert what the client was asked")


def test_the_clock_is_read_exactly_once():
    """Exercise 5e — pass a `SpyClock(DAY)` and assert `clock.calls == 1` after
    one report. A report that read the clock twice could straddle midnight."""
    raise NotImplementedError("Exercise 5e: assert the clock was read once")


def test_a_transient_failure_is_retried_and_then_succeeds():
    """Exercise 5f — script a fake with
    `[ReadingsUnavailable("timeout"), ReadingsUnavailable("timeout"), READINGS]`,
    call `build_report(..., attempts=3)`, and assert the mean is 17.0 and the
    fake recorded three calls."""
    raise NotImplementedError("Exercise 5f: assert two failures then a success")


def test_backoff_grows_between_attempts_without_anyone_waiting():
    """Exercise 5g — repeat 5f with `sleep=RecordingSleep()` and
    `backoff_seconds=0.5`, then assert the spy recorded `[0.5, 1.0]`. The suite
    still finishes instantly, because the thing that would have slept is a list
    append."""
    raise NotImplementedError("Exercise 5g: assert the backoff schedule without waiting")


def test_exhausting_every_attempt_raises_a_domain_error():
    """Exercise 5h — script three failures and assert
    `pytest.raises(ReportUnavailable, match="after 3 attempts")`."""
    raise NotImplementedError("Exercise 5h: assert the give-up error")


def test_a_bad_attempts_argument_is_refused_before_the_client_is_touched():
    """Exercise 5i — call `build_report(..., client=DummyClient(), attempts=0)`
    inside `pytest.raises(ReportError, match="attempts must be at least 1")`.

    If your `build_report` calls the client before validating `attempts`, the
    dummy raises `AssertionError` and this test fails — which is exactly what a
    dummy is for."""
    raise NotImplementedError("Exercise 5i: assert the guard fires before the client is used")
