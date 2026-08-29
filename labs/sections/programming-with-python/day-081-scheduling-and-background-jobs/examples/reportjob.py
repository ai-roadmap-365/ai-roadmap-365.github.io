"""The work itself: a daily report, written idempotently.

The job is deliberately dull — read yesterday's readings out of a CSV, total
them per station, write a JSON file. The interesting part is not what it
computes but the two properties it has:

**Idempotence.** Running it twice for the same day produces one report, not
two, and not a doubled one. This is the single most important property a
scheduled job can have, because retries, catch-up runs and a nervous operator
typing the command again all mean "run it twice", and every one of those
happens eventually.

**Atomic output.** The file is written to a temporary name in the same
directory and then moved into place with ``os.replace``, which on POSIX is an
atomic rename. Without that, a job killed halfway through leaves a truncated
JSON file that *looks* finished to the next run — so the next run skips it,
and the truncated file lives forever. This is one of those bugs that is
invisible for months and then ruins a morning.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import os
import statistics
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StationSummary:
    """One station's numbers for one day."""

    station: str
    count: int
    minimum: float
    maximum: float
    mean: float

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "station": self.station,
            "count": self.count,
            "min_celsius": round(self.minimum, 2),
            "max_celsius": round(self.maximum, 2),
            "mean_celsius": round(self.mean, 2),
        }


@dataclass(frozen=True)
class DailyReport:
    """The whole report for one day. A value — it writes nothing itself."""

    report_date: dt.date
    generated_at: dt.datetime
    stations: tuple[StationSummary, ...] = field(default_factory=tuple)

    @property
    def reading_count(self) -> int:
        return sum(s.count for s in self.stations)

    def as_dict(self) -> dict[str, object]:
        return {
            "report_date": self.report_date.isoformat(),
            "generated_at": self.generated_at.isoformat(),
            "reading_count": self.reading_count,
            "stations": [s.as_dict() for s in self.stations],
        }


def load_readings(source: Path, report_date: dt.date) -> dict[str, list[float]]:
    """Read the CSV and group one day's Celsius values by station."""
    grouped: dict[str, list[float]] = {}
    wanted = report_date.isoformat()
    with open(source, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["date"] != wanted:
                continue
            grouped.setdefault(row["station"], []).append(float(row["celsius"]))
    return grouped


def build_report(
    readings: dict[str, list[float]],
    *,
    report_date: dt.date,
    generated_at: dt.datetime,
) -> DailyReport:
    """Pure: values in, value out. No clock, no filesystem, no exceptions to catch."""
    summaries = tuple(
        StationSummary(
            station=station,
            count=len(values),
            minimum=min(values),
            maximum=max(values),
            mean=statistics.fmean(values),
        )
        for station, values in sorted(readings.items())
    )
    return DailyReport(
        report_date=report_date, generated_at=generated_at, stations=summaries
    )


def report_path(output_dir: Path, report_date: dt.date) -> Path:
    """The output name IS the idempotence key. One day, one file, one name."""
    return Path(output_dir) / f"report-{report_date.isoformat()}.json"


def already_written(output_dir: Path, report_date: dt.date) -> bool:
    """Has a *complete* report for this day already been written?

    "Complete" means the file parses as JSON and carries the marker key. A
    partially written file fails both tests, so a crashed run is retried rather
    than mistaken for a success.
    """
    path = report_path(output_dir, report_date)
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False
    return payload.get("report_date") == report_date.isoformat()


def write_report_atomically(report: DailyReport, output_dir: Path) -> Path:
    """Write to a temporary file in the same directory, then rename into place.

    Same directory matters: ``os.replace`` is only atomic within one
    filesystem, and ``/tmp`` is frequently a different one.
    """
    destination = report_path(output_dir, report.report_date)
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=destination.parent,
        prefix=destination.name + ".",
        suffix=".partial",
        delete=False,
    )
    try:
        with handle:
            json.dump(report.as_dict(), handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(handle.name, destination)
    except BaseException:
        Path(handle.name).unlink(missing_ok=True)
        raise
    return destination


def generate_daily_report(
    *,
    source: Path,
    output_dir: Path,
    report_date: dt.date,
    generated_at: dt.datetime,
) -> tuple[str, Path]:
    """The whole unit of work. Returns ``("written" | "skipped", path)``.

    The skip branch is what makes the job idempotent, and it is checked before
    any work is done rather than after, so a repeat run is also cheap.
    """
    if already_written(output_dir, report_date):
        return "skipped", report_path(output_dir, report_date)
    readings = load_readings(source, report_date)
    report = build_report(
        readings, report_date=report_date, generated_at=generated_at
    )
    return "written", write_report_atomically(report, output_dir)
