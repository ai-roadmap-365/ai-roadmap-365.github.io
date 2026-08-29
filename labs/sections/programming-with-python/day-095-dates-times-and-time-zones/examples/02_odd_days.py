"""The 23-hour day and the 25-hour day, measured rather than asserted.

"A day is 24 hours" is false twice a year in most of the world, and the two
exceptions are not rare edge cases — they are scheduled, published years in
advance, and they arrive on the same weekend as everybody's monthly billing
run.

The measurement below is the only honest one: convert both midnights to UTC
and subtract. Subtracting two local datetimes gives you the WALL-CLOCK
difference, which is 24 hours on every day of the year by construction and
therefore tells you nothing.

Run:  python3 examples/02_odd_days.py
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


def midnight(day: date, zone: ZoneInfo) -> datetime:
    """The first instant of a local calendar day, as an aware datetime."""
    return datetime.combine(day, time(0, 0), tzinfo=zone)


def real_length(day: date, zone: ZoneInfo) -> timedelta:
    """How much time actually elapsed during a local calendar day."""
    start = midnight(day, zone).astimezone(UTC)
    end = midnight(day + timedelta(days=1), zone).astimezone(UTC)
    return end - start


def wall_length(day: date, zone: ZoneInfo) -> timedelta:
    """What naive subtraction says. Always 24 hours. Always."""
    return midnight(day + timedelta(days=1), zone) - midnight(day, zone)


DAYS = [
    ("Europe/London", date(2026, 3, 29), "spring forward"),
    ("Europe/London", date(2026, 10, 25), "autumn back"),
    ("Europe/London", date(2026, 6, 15), "an ordinary day"),
    ("America/New_York", date(2026, 3, 8), "spring forward"),
    ("America/New_York", date(2026, 11, 1), "autumn back"),
    ("Australia/Lord_Howe", date(2026, 10, 4), "forward by half an hour"),
    ("Australia/Lord_Howe", date(2026, 4, 5), "back by half an hour"),
]


def main() -> int:
    print("How long is a day? Measured in elapsed time, not in wall clock.\n")
    header = f"{'zone':<20} {'local date':<12} {'real':>10} {'wall':>10}  what happened"
    print(header)
    print("-" * len(header))
    for zone_name, day, label in DAYS:
        zone = ZoneInfo(zone_name)
        real = real_length(day, zone)
        wall = wall_length(day, zone)
        hours = real.total_seconds() / 3600
        print(
            f"{zone_name:<20} {day.isoformat():<12} "
            f"{hours:>9.1f}h {wall.total_seconds() / 3600:>9.1f}h  {label}"
        )

    print("\nThe wall column is 24.0 on every row, including the two that are not.")
    print("That column is what you get if you subtract two local datetimes, and")
    print("it is why a report that measures a day by subtracting midnights is")
    print("wrong twice a year and right the rest of the time, which is the worst")
    print("possible failure schedule.\n")

    london = ZoneInfo("Europe/London")
    short = real_length(date(2026, 3, 29), london)
    long = real_length(date(2026, 10, 25), london)
    print(f"London 2026-03-29 lasted {short} — an hour was skipped.")
    print(f"London 2026-10-25 lasted {long} — an hour was repeated.")
    print(f"The two together: {short + long}, which is exactly two days.")
    print("Daylight saving borrows an hour in March and returns it in October.")

    print("\nAnd an hour is not the only step size. Lord Howe Island moves by")
    print("thirty minutes, so its short day measures 23.5 hours and its long")
    print("day 24.5. Any code that special-cases 'plus or minus exactly one")
    print("hour' is already wrong there, and it is in the table above.")

    print("\nThe hour that is missing, and the hour that is doubled:")
    for label, day, zone_name in [
        ("skipped", date(2026, 3, 29), "Europe/London"),
        ("repeated", date(2026, 10, 25), "Europe/London"),
    ]:
        zone = ZoneInfo(zone_name)
        start = midnight(day, zone).astimezone(UTC)
        seen: list[str] = []
        for step in range(6):
            local = (start + timedelta(hours=step)).astimezone(zone)
            seen.append(local.strftime("%H:%M"))
        print(f"  {day} {label:<8} first six real hours read: {' '.join(seen)}")
    print("  On 29 March the wall clock never shows 01:xx. On 25 October it")
    print("  shows 01:xx twice, and those two 01:30s are an hour apart.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
