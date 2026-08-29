"""Hand-written test doubles for the report core. No library involved.

Every one of these is under fifteen lines, and together they replace the whole
of `unittest.mock` for this program. They are also the only doubles in this lab
that a reader can fully understand by reading them — which is the argument the
lesson makes for preferring a fake over a mock whenever a fake is cheap.

One class per kind of double, so you can see the taxonomy in code:

  DummyClient          dummy  — passed to satisfy a signature, never used
  frozen_clock         stub   — canned answer, no recording
  StubSensorClient     stub   — canned answers, no recording
  RecordingSleep       spy    — real-ish behaviour plus a record of the calls
  FakeSensorClient     fake   — a working in-memory implementation
  InMemoryReportStore  fake   — a working in-memory stand-in for the filesystem
"""

from __future__ import annotations

import datetime

from report_v2 import ReadingsUnavailable


class DummyClient:
    """A dummy: it exists to fill an argument slot and must never be called."""

    def fetch_readings(self, station: str, day: str) -> list[float]:
        raise AssertionError("the dummy client was called — the test was wrong about the path taken")


def frozen_clock(day: datetime.date):
    """A stub clock: it always answers `day`, and remembers nothing."""
    return lambda: day


class StubSensorClient:
    """A stub: one canned answer, returned to every caller, forever."""

    def __init__(self, readings: list[float]) -> None:
        self._readings = list(readings)

    def fetch_readings(self, station: str, day: str) -> list[float]:
        return list(self._readings)


class SpyClock:
    """A spy clock: answers like a stub, and records how often it was asked."""

    def __init__(self, day: datetime.date) -> None:
        self.day = day
        self.calls = 0

    def __call__(self) -> datetime.date:
        self.calls += 1
        return self.day


class RecordingSleep:
    """A spy for the backoff: never actually waits, records what it was asked to wait."""

    def __init__(self) -> None:
        self.waits: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.waits.append(seconds)


class FakeSensorClient:
    """A fake: a real, working, in-memory sensor service.

    Give it a script of responses. A list is returned; an exception instance is
    raised. It records every call, so it can also answer the questions a spy
    would answer — which is why one fake usually replaces five mock assertions.
    """

    def __init__(self, script: list) -> None:
        self._script = list(script)
        self.calls: list[tuple[str, str]] = []

    def fetch_readings(self, station: str, day: str) -> list[float]:
        self.calls.append((station, day))
        if not self._script:
            raise ReadingsUnavailable(f"the fake ran out of scripted responses at call {len(self.calls)}")
        item = self._script.pop(0)
        if isinstance(item, Exception):
            raise item
        return list(item)


class ScriptedModel:
    """A fake language model: a scripted reply per call, and a record of prompts.

    Four lines of state stand in for a metered, slow, non-deterministic API. It
    is free, instant and identical on every run — which is exactly what a unit
    test needs, and exactly what the real thing can never be.
    """

    def __init__(self, script: list) -> None:
        self._script = list(script)
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self._script:
            raise AssertionError(f"the scripted model ran out of replies at call {len(self.prompts)}")
        item = self._script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class InMemoryReportStore:
    """A fake filesystem: same two operations, a dict instead of a disk."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}

    def write(self, name: str, body: str) -> str:
        self.files[name] = body
        return name

    def read(self, name: str) -> str:
        if name not in self.files:
            raise FileNotFoundError(name)
        return self.files[name]
