"""Exercise 3 — move the boundaries out of the function.

Same behaviour as `report_v1.write_daily_report`, one structural difference:
the clock and the client arrive as arguments, and the file writing is somebody
else's job entirely. When you are finished, this module must import NOTHING
that can touch the outside world — no `pathlib`, no `time`, no `random`, no
`open`, no `print`. The two imports already here are all you need.

The test suite checks that purity by parsing this file, and again by running
your code from an empty directory.

Delete each `raise NotImplementedError(...)` as you complete that exercise.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass


class ReportError(Exception):
    """Any refusal that belongs to the reporting domain."""


class ReadingsUnavailable(ReportError):
    """A client could not supply readings for this attempt. Retryable."""


class ReportUnavailable(ReportError):
    """Every attempt to obtain readings failed."""


@dataclass(frozen=True)
class DailyReport:
    """Exercise 3a — the report as a value.

    Give it six fields, in this order and with these types:
    `station: str`, `day: datetime.date`, `count: int`, `minimum: float`,
    `maximum: float`, `mean: float`. Frozen, as Day 69 and Day 70 taught, so a
    finished report cannot be edited by whatever prints it.
    """

    station: str
    day: datetime.date
    count: int
    minimum: float
    maximum: float
    mean: float

    def render(self) -> str:
        """Exercise 3b — return exactly these five lines, joined by newlines:

            station ALPHA — 2026-04-12
              readings 24
              minimum  12.0
              maximum  22.0
              mean     17.0

        The three numbers use `:.1f`. There is an em dash after the station.
        """
        raise NotImplementedError("Exercise 3b: render the five report lines")

    def filename(self) -> str:
        """Exercise 3c — return `ALPHA-2026-04-12.txt` for the report above."""
        raise NotImplementedError("Exercise 3c: build the filename from station and day")


def summarise(station: str, day: datetime.date, readings: list[float]) -> DailyReport:
    """Exercise 3d — reduce a day of readings to a `DailyReport`.

    Raise `ReportError` on an empty list with a message containing the words
    "empty day". Otherwise return a `DailyReport` whose `count` is the length,
    `minimum` and `maximum` are the extremes, and `mean` is the average rounded
    to one decimal place with `round(..., 1)`.

    Pure: a list in, a value out. No clock, no client, no file.
    """
    raise NotImplementedError("Exercise 3d: reduce readings to a DailyReport")


def build_report(
    station: str,
    *,
    clock,
    client,
    attempts: int = 3,
    sleep=lambda seconds: None,
    backoff_seconds: float = 0.5,
) -> DailyReport:
    """Exercise 3e — the same job as `write_daily_report`, with the seams open.

    `clock`  — a zero-argument callable returning a `datetime.date`.
    `client` — any object with `fetch_readings(station, iso_day) -> list[float]`
               that raises `ReadingsUnavailable` when it cannot answer.
    `sleep`  — a one-argument callable used between attempts. The default does
               nothing, so tests never wait.

    Behaviour to implement:

      1. If `attempts` is less than 1, raise `ReportError` with a message
         containing "attempts must be at least 1". Do this BEFORE calling the
         clock or the client — the dummy in exercise 4 proves you did.
      2. Read the clock exactly once and keep the day. (A report that read the
         clock twice could straddle midnight.)
      3. Up to `attempts` times, call
         `client.fetch_readings(station, day.isoformat())`. On success, return
         `summarise(station, day, readings)`.
      4. On `ReadingsUnavailable`, remember the message. If another attempt is
         left, call `sleep(backoff_seconds * attempt)` — so the waits grow:
         0.5, then 1.0, then 1.5.
      5. If every attempt failed, raise `ReportUnavailable` with a message
         containing "after N attempts" and the last failure's text.

    Note what is NOT here: no `import time`, no `import pathlib`. The signature
    is the design.
    """
    raise NotImplementedError("Exercise 3e: build the report from the injected boundaries")
