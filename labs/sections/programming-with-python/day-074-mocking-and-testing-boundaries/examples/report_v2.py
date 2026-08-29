"""Version 2 — the boundaries moved out. This is the "after" picture.

Same behaviour as `report_v1.py`, one structural difference: nothing in this
file reads a clock, calls a service, sleeps, or writes a file. The clock, the
client and the sleep arrive as **arguments**, and the report comes back as a
value that somebody else may choose to write down.

Check the imports. `datetime` and `dataclasses` are ways of writing a value
down; neither can touch the outside world. There is no `pathlib`, no `time`,
no `random`, no `open`, no `print`. That is the same purity property Day 70's
domain core had, and it has the same payoff: every rule in this file can be
exercised from an empty directory with no patching at all.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass


class ReportError(Exception):
    """Any refusal that belongs to the reporting domain."""


class ReadingsUnavailable(ReportError):
    """A client could not supply readings for this attempt.

    The client raises this; `build_report` decides whether to try again. Note
    that the core defines the error it retries on, rather than importing the
    service's own exception type — so a second client for a different service
    can be written without the core learning anything about it.
    """


class ReportUnavailable(ReportError):
    """Every attempt to obtain readings failed."""


@dataclass(frozen=True)
class DailyReport:
    """One day of one station, reduced to the four numbers the report shows."""

    station: str
    day: datetime.date
    count: int
    minimum: float
    maximum: float
    mean: float

    def render(self) -> str:
        return "\n".join(
            [
                f"station {self.station} — {self.day.isoformat()}",
                f"  readings {self.count}",
                f"  minimum  {self.minimum:.1f}",
                f"  maximum  {self.maximum:.1f}",
                f"  mean     {self.mean:.1f}",
            ]
        )

    def filename(self) -> str:
        return f"{self.station}-{self.day.isoformat()}.txt"


def summarise(station: str, day: datetime.date, readings: list[float]) -> DailyReport:
    """Reduce a day of readings to a report. Pure: a list in, a value out."""
    if not readings:
        raise ReportError("cannot summarise an empty day of readings")
    return DailyReport(
        station=station,
        day=day,
        count=len(readings),
        minimum=min(readings),
        maximum=max(readings),
        mean=round(sum(readings) / len(readings), 1),
    )


def build_report(
    station: str,
    *,
    clock,
    client,
    attempts: int = 3,
    sleep=lambda seconds: None,
    backoff_seconds: float = 0.5,
) -> DailyReport:
    """Build today's report for one station.

    `clock`  — a zero-argument callable returning a `datetime.date`.
    `client` — any object with `fetch_readings(station, iso_day) -> list[float]`
               that raises `ReadingsUnavailable` when it cannot answer.
    `sleep`  — a one-argument callable used for backoff between attempts. The
               default does nothing, so tests never wait; the adapter passes
               the real `time.sleep`.

    Every boundary this function needs is a parameter, so a test supplies them
    and nothing has to be patched.
    """
    if attempts < 1:
        raise ReportError(f"attempts must be at least 1, got {attempts}")

    day = clock()
    last_reason = ""
    for attempt in range(1, attempts + 1):
        try:
            readings = client.fetch_readings(station, day.isoformat())
        except ReadingsUnavailable as exc:
            last_reason = str(exc)
            if attempt < attempts:
                sleep(backoff_seconds * attempt)
            continue
        return summarise(station, day, readings)

    raise ReportUnavailable(
        f"no readings for {station} on {day.isoformat()} after {attempts} attempts: {last_reason}"
    )
