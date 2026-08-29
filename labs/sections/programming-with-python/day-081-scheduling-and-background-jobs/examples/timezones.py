"""What "02:30 every day" means on the two days a year it does not.

A schedule written in local time is a schedule with two broken days per year.
On the spring-forward morning some wall-clock times do not happen; on the
autumn morning some happen twice. A daily job at 02:30 local therefore misses
a run in spring, and a daily job at 01:30 local runs twice in autumn — once as
daylight time and once as standard time, an hour apart in real elapsed time.

If the job is idempotent, the doubled run is harmless and the missing one is a
gap. If it is not idempotent, the doubled run is a doubled invoice.

Everything below is computed from Python's ``zoneinfo``, which reads the IANA
time zone database that ships with the operating system. The rules encoded
there are the real ones, so these functions tell you what your machine
actually believes rather than what a lesson asserts.

The answer, every time, is: **schedule in UTC and convert for display.** UTC
has no transitions, so 24 hours after an instant is always the same clock time
and always exactly 24 hours.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc


@dataclass(frozen=True)
class WallClockVerdict:
    """What one local wall-clock time turns out to mean."""

    wall_time: str
    zone: str
    kind: str  # "normal" | "skipped" | "repeated"
    instants: tuple[dt.datetime, ...]
    note: str

    @property
    def exists(self) -> bool:
        return self.kind != "skipped"


def classify_wall_time(naive: dt.datetime, zone_name: str) -> WallClockVerdict:
    """Does this local wall-clock time happen once, twice, or not at all?

    The method is the one PEP 495 made possible: build the same wall time with
    ``fold=0`` and ``fold=1`` and compare their UTC offsets.

    * offsets equal, and the value round-trips through UTC unchanged -> normal;
    * offsets differ, and both round-trip -> the time happens twice (fall back);
    * the value does not round-trip -> the time never happens (spring forward),
      and Python resolves it to the instant one hour away.
    """
    zone = ZoneInfo(zone_name)
    first = naive.replace(tzinfo=zone, fold=0)
    second = naive.replace(tzinfo=zone, fold=1)
    label = naive.strftime("%Y-%m-%d %H:%M")

    first_utc = first.astimezone(UTC)
    round_tripped = first_utc.astimezone(zone).replace(tzinfo=None)

    if round_tripped != naive:
        return WallClockVerdict(
            label,
            zone_name,
            "skipped",
            (first_utc,),
            (
                f"{label} never appears on the wall clock in {zone_name}; "
                f"the clocks jump over it. Python resolves it to "
                f"{first_utc.astimezone(zone):%H:%M %Z}, an hour later than intended."
            ),
        )

    if first.utcoffset() != second.utcoffset():
        return WallClockVerdict(
            label,
            zone_name,
            "repeated",
            (first_utc, second.astimezone(UTC)),
            (
                f"{label} happens twice in {zone_name}: once at "
                f"{first_utc:%H:%M} UTC ({first:%Z}) and again an hour later at "
                f"{second.astimezone(UTC):%H:%M} UTC ({second:%Z}). "
                "A job scheduled then runs twice unless it is idempotent."
            ),
        )

    return WallClockVerdict(
        label,
        zone_name,
        "normal",
        (first_utc,),
        f"{label} in {zone_name} is exactly one instant: {first_utc:%H:%M} UTC.",
    )


def daily_instants_local(
    *,
    start_date: dt.date,
    days: int,
    hour: int,
    minute: int,
    zone_name: str,
) -> list[dt.datetime]:
    """The UTC instants a "hour:minute every day, local time" job would fire at."""
    zone = ZoneInfo(zone_name)
    out = []
    for offset in range(days):
        day = start_date + dt.timedelta(days=offset)
        local = dt.datetime(day.year, day.month, day.day, hour, minute, tzinfo=zone)
        out.append(local.astimezone(UTC))
    return out


def gaps_between(instants: list[dt.datetime]) -> list[float]:
    """Hours between consecutive runs. For a daily job in UTC these are all 24."""
    return [
        (later - earlier).total_seconds() / 3600
        for earlier, later in zip(instants, instants[1:], strict=False)
    ]
