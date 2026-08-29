"""Stage 4 — Report.

**The promise:** the report answers the question the pipeline exists for, and it
answers it the same way tomorrow as it does today for the same instant.

That second half is the whole reason ``report_at`` is a **parameter** and not a
call to ``datetime.now``. A function that reads the clock cannot be asserted on;
its output changes every time you run it, so "is this number right?" has no
answer you can put in a test. Passing the instant in costs one argument and buys
three things: a testable report, a backfill (ask for last Tuesday and get last
Tuesday's answer), and an incident timeline (ask for 03:00 and see what the
3 a.m. run saw). Day 91 made this choice for the same reason; Day 95 explains
why the instant must be timezone-aware.

The report also carries the one check the validation gate structurally cannot
make. A field validator sees one record. It cannot know that 41.3 Celsius five
minutes after 15.0 Celsius is a broken sensor, because both values are legal.
``suspect_jumps`` compares consecutive readings per station, and it **flags**
rather than deletes: a value that is valid but wrong is a fact about the world
that somebody has to look at, and silently dropping it would replace a visible
anomaly with an invisible gap.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from store import StoredReading

#: Flag a change larger than this many deci-Celsius inside one hour.
JUMP_THRESHOLD_DC = 100
JUMP_WINDOW_MINUTES = 60


@dataclass(frozen=True)
class StationSummary:
    station_id: str
    readings: int
    min_dc: int | None
    max_dc: int | None
    mean_dc: int | None

    @staticmethod
    def _c(value: int | None) -> str:
        return "-" if value is None else f"{value / 10:.1f}"

    def line(self) -> str:
        return (
            f"  {self.station_id:<12} {self.readings:>8} {self._c(self.min_dc):>9}"
            f" {self._c(self.max_dc):>9} {self._c(self.mean_dc):>9}"
        )


@dataclass(frozen=True)
class SuspectJump:
    station_id: str
    previous_at: str
    observed_at: str
    change_dc: int
    minutes: int

    def line(self) -> str:
        return (
            f"  {self.station_id}: {self.change_dc / 10:+.1f} C in {self.minutes} minutes "
            f"({self.previous_at} -> {self.observed_at})"
        )


@dataclass(frozen=True)
class Report:
    report_at: str
    window_start: str
    window_hours: int
    readings_in_window: int
    total_rows: int
    stations: tuple[StationSummary, ...]
    suspect: tuple[SuspectJump, ...]


def _parse_instant(text: str) -> datetime:
    moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        raise ValueError(f"report_at must carry a UTC offset, got {text!r}")
    return moment.astimezone(timezone.utc)


def build_report(
    session: Session,
    *,
    report_at: str,
    window_hours: int,
    stations: list[str],
) -> Report:
    """Summarise the window ending at ``report_at``, per station."""
    end = _parse_instant(report_at)
    start = end - timedelta(hours=window_hours)
    end_text = end.strftime("%Y-%m-%dT%H:%M:%SZ")
    start_text = start.strftime("%Y-%m-%dT%H:%M:%SZ")

    rows = session.execute(
        select(
            StoredReading.station_id,
            StoredReading.observed_at,
            StoredReading.temperature_dc,
        )
        .where(StoredReading.observed_at >= start_text)
        .where(StoredReading.observed_at <= end_text)
        .order_by(StoredReading.station_id, StoredReading.observed_at)
    ).all()

    by_station: dict[str, list[tuple[str, int]]] = {name: [] for name in stations}
    for station_id, observed_at, temperature_dc in rows:
        by_station.setdefault(station_id, []).append((observed_at, temperature_dc))

    summaries = []
    for station_id in sorted(by_station):
        values = [temp for _, temp in by_station[station_id]]
        if values:
            summaries.append(
                StationSummary(
                    station_id=station_id,
                    readings=len(values),
                    min_dc=min(values),
                    max_dc=max(values),
                    mean_dc=round(sum(values) / len(values)),
                )
            )
        else:
            summaries.append(StationSummary(station_id, 0, None, None, None))

    total = session.execute(select(StoredReading.id)).all()

    return Report(
        report_at=end_text,
        window_start=start_text,
        window_hours=window_hours,
        readings_in_window=len(rows),
        total_rows=len(total),
        stations=tuple(summaries),
        suspect=tuple(suspect_jumps(by_station)),
    )


def suspect_jumps(by_station: dict[str, list[tuple[str, int]]]) -> list[SuspectJump]:
    """Consecutive readings that changed too far, too fast, to be believable."""
    found: list[SuspectJump] = []
    for station_id in sorted(by_station):
        series = sorted(by_station[station_id])
        for (previous_at, previous_dc), (observed_at, observed_dc) in zip(series, series[1:]):
            gap = _parse_instant(observed_at) - _parse_instant(previous_at)
            minutes = int(gap.total_seconds() // 60)
            change = observed_dc - previous_dc
            if minutes <= JUMP_WINDOW_MINUTES and abs(change) > JUMP_THRESHOLD_DC:
                found.append(
                    SuspectJump(
                        station_id=station_id,
                        previous_at=previous_at,
                        observed_at=observed_at,
                        change_dc=change,
                        minutes=minutes,
                    )
                )
    return found


def format_report(report: Report) -> str:
    lines = [
        "Station readings report",
        f"  as of        {report.report_at}",
        f"  window       {report.window_hours}h, from {report.window_start}",
        f"  in window    {report.readings_in_window} of {report.total_rows} stored readings",
        "",
        f"  {'station':<12} {'readings':>8} {'min C':>9} {'max C':>9} {'mean C':>9}",
        f"  {'-' * 12} {'-' * 8} {'-' * 9} {'-' * 9} {'-' * 9}",
    ]
    lines.extend(summary.line() for summary in report.stations)
    lines.append("")
    if report.suspect:
        lines.append(f"  suspect readings ({len(report.suspect)}) — stored and flagged, not dropped:")
        lines.extend(jump.line() for jump in report.suspect)
    else:
        lines.append("  suspect readings (0)")
    return "\n".join(lines)
