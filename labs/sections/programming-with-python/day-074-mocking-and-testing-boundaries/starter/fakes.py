"""Exercise 4 — write the test doubles by hand. No library, no magic.

Five small classes and one function. Together they replace every use of
`unittest.mock` in this program, and unlike a mock they can be read.

Delete each `raise NotImplementedError(...)` as you complete that exercise.
"""

from __future__ import annotations

import datetime

from report_v2 import ReadingsUnavailable


class DummyClient:
    """Exercise 4a — a DUMMY. It exists to fill an argument slot.

    Implement `fetch_readings(self, station, day)` so that it raises
    `AssertionError` with a message saying the dummy should not have been
    called. A test passes this where a client is required on a path that must
    never reach the client; if the path is wrong, the dummy says so loudly.
    """

    def fetch_readings(self, station: str, day: str) -> list[float]:
        raise NotImplementedError("Exercise 4a: a dummy that refuses to be used")


def frozen_clock(day: datetime.date):
    """Exercise 4b — a STUB clock. Return a zero-argument callable giving `day`.

    One line. `lambda: day` is a complete answer.
    """
    raise NotImplementedError("Exercise 4b: return a callable that always answers `day`")


class StubSensorClient:
    """Exercise 4c — a STUB client: one canned answer, recorded nothing.

    `__init__(self, readings)` stores a copy. `fetch_readings(station, day)`
    returns a copy of it, ignoring both arguments. Return a copy rather than the
    stored list, so a test that mutates the result cannot corrupt later calls.
    """

    def __init__(self, readings: list[float]) -> None:
        raise NotImplementedError("Exercise 4c: store a copy of the readings")

    def fetch_readings(self, station: str, day: str) -> list[float]:
        raise NotImplementedError("Exercise 4c: return a copy of the stored readings")


class SpyClock:
    """Exercise 4d — a SPY clock: answers like a stub, and counts the questions.

    `__init__(self, day)` sets `self.day = day` and `self.calls = 0`.
    `__call__(self)` increments `self.calls` and returns `self.day`.
    """

    def __init__(self, day: datetime.date) -> None:
        raise NotImplementedError("Exercise 4d: store the day and a call counter")

    def __call__(self) -> datetime.date:
        raise NotImplementedError("Exercise 4d: count the call and return the day")


class RecordingSleep:
    """Exercise 4e — a SPY for the backoff. It records; it never waits.

    `__init__(self)` sets `self.waits = []`. `__call__(self, seconds)` appends
    `seconds` and returns `None`. This is the whole reason a retry test finishes
    in microseconds instead of seconds.
    """

    def __init__(self) -> None:
        raise NotImplementedError("Exercise 4e: start with an empty list of waits")

    def __call__(self, seconds: float) -> None:
        raise NotImplementedError("Exercise 4e: record the requested wait, do not sleep")


class FakeSensorClient:
    """Exercise 4f — a FAKE: a working in-memory sensor service.

    `__init__(self, script)` keeps a copy of `script` and an empty
    `self.calls` list.

    `fetch_readings(self, station, day)`:
      1. append `(station, day)` to `self.calls`;
      2. if the script is empty, raise `ReadingsUnavailable` saying so;
      3. pop the next item; if it is an `Exception` instance, raise it;
      4. otherwise return a copy of it.

    This one class answers the stub question ("what does the client return?"),
    the spy question ("what was it asked?") and the mock question ("was it
    called with the right arguments?") — which is the argument for preferring a
    fake to five mock assertions.
    """

    def __init__(self, script: list) -> None:
        raise NotImplementedError("Exercise 4f: keep a copy of the script and an empty call log")

    def fetch_readings(self, station: str, day: str) -> list[float]:
        raise NotImplementedError("Exercise 4f: record the call, then play the next scripted item")
