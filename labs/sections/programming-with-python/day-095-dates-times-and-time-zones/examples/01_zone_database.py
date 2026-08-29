"""Prove the zone database exists on this machine, then count what is in it.

Nothing in this file is a claim about time. It is a claim about a FILE, which
is the point: `zoneinfo` does not know when the clocks change in London. It
looks the answer up in a database of compiled rules shipped by your operating
system, and if that database is missing or out of date, every answer below
changes.

Run:  python3 examples/01_zone_database.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import zoneinfo
except ImportError:  # pragma: no cover - zoneinfo is standard from 3.9
    sys.exit("zoneinfo is missing: this lab needs Python 3.9 or newer.")

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = timezone.utc


def fmt_offset(delta: timedelta | None) -> str:
    """Format a UTC offset as +HH:MM.

    Worth its own function: str(timedelta(hours=-4)) is '-1 day, 20:00:00',
    which is arithmetically correct and useless in a table.
    """
    if delta is None:
        return "  none"
    total = int(delta.total_seconds())
    sign = "-" if total < 0 else "+"
    total = abs(total)
    return f"{sign}{total // 3600:02d}:{total % 3600 // 60:02d}"


def report_search_path() -> list[str]:
    """Print every directory zoneinfo will search, and say which ones exist."""
    print("zoneinfo.TZPATH — searched in this order, first match wins:")
    present = []
    for entry in zoneinfo.TZPATH:
        exists = Path(entry).is_dir()
        print(f"  {'present' if exists else 'absent '}  {entry}")
        if exists:
            present.append(entry)
    if not present:
        print("  none of those exist — zoneinfo would fall back to the tzdata package")
    return present


def report_database_version(present: list[str]) -> str | None:
    """The IANA database is versioned. Read the version file if it is there."""
    for entry in present:
        version_file = Path(entry) / "+VERSION"
        if version_file.is_file():
            version = version_file.read_text(encoding="utf-8").strip()
            print(f"\nIANA database version: {version}  (from {version_file})")
            return version
    print("\nIANA database version: no +VERSION file found in the search path")
    return None


def count_zones() -> int:
    """Every zone name the database offers, including links and aliases."""
    names = zoneinfo.available_timezones()
    print(f"\nzones available here: {len(names)}")
    return len(names)


def show_a_few() -> None:
    """One instant, five places, five different local readings of it."""
    instant = datetime(2026, 8, 16, 12, 0, tzinfo=UTC)
    print(f"\nOne instant — {instant.isoformat()} — read in five places:")
    print(f"  {'zone':<20} {'local time':<21} {'offset':>7}  name")
    for name in [
        "UTC",
        "Europe/London",
        "America/New_York",
        "Asia/Kolkata",
        "Asia/Kathmandu",
    ]:
        local = instant.astimezone(ZoneInfo(name))
        print(
            f"  {name:<20} {local.strftime('%Y-%m-%d %H:%M:%S'):<21} "
            f"{fmt_offset(local.utcoffset()):>7}  {local.tzname()}"
        )
    print("  Kolkata is +05:30 and Kathmandu +05:45. Offsets are not whole hours,")
    print("  which is why an offset is a timedelta and not an integer of hours.")


def find_transition(zone: ZoneInfo, low: datetime, high: datetime) -> datetime | None:
    """Bisect for the first instant in (low, high] where the offset changes.

    This is how you discover a zone's rules without parsing the binary file:
    ask the database for the offset at two instants, and if they differ, halve
    the interval until you have the second the change lands on. It assumes at
    most one change in the window, which is why the callers pass narrow ones.
    """
    if low.utcoffset() is None or low.tzinfo is not UTC:
        raise ValueError("bisect over UTC instants, not local ones")
    before = low.astimezone(zone).utcoffset()
    after = high.astimezone(zone).utcoffset()
    if before == after:
        return None
    while high - low > timedelta(seconds=1):
        middle = low + (high - low) / 2
        if middle.astimezone(zone).utcoffset() == before:
            low = middle
        else:
            high = middle
    return high.replace(microsecond=0)


def show_rules_are_data() -> None:
    """The same zone, different years, different answers — read from the file."""
    london = ZoneInfo("Europe/London")
    print("\nA zone is not a constant. Europe/London at noon on 1 January:")
    for year in (1967, 1969, 1970, 1971, 1972, 2026):
        moment = datetime(year, 1, 1, 12, 0, tzinfo=london)
        print(
            f"  {year}: offset {fmt_offset(moment.utcoffset())}  "
            f"name {moment.tzname():<4}  daylight saving {moment.dst()}"
        )
    print("  For three winters London sat at +01:00 with no daylight saving in")
    print("  force: Britain ran an experiment with year-round summer time.")

    start = find_transition(
        london,
        datetime(1968, 1, 1, tzinfo=UTC),
        datetime(1969, 1, 1, tzinfo=UTC),
    )
    end = find_transition(
        london,
        datetime(1971, 6, 1, tzinfo=UTC),
        datetime(1972, 1, 1, tzinfo=UTC),
    )
    print("  Bisecting the database for the two boundary instants:")
    print(f"    clocks went forward  {start.isoformat() if start else 'not found'}")
    print(f"    and did not go back until  {end.isoformat() if end else 'not found'}")
    print("  Three years and eight months between one spring forward and the")
    print("  next autumn back. No code models that; a file records it.")
    print("  Those two instants are facts about a file, and a future one would")
    print("  be a prediction: a government can move a transition, and then the")
    print("  database is updated and your 'fixed' timestamp moves with it.")


def main() -> int:
    print("Day 095 — is the zone database actually here?\n")
    print(f"python: {sys.version.split()[0]}")
    present = report_search_path()
    report_database_version(present)

    try:
        ZoneInfo("Europe/London")
    except ZoneInfoNotFoundError as exc:
        print(f"\nEurope/London could not be loaded: {exc}")
        print("Install your system's tzdata package, or add the tzdata module.")
        return 1

    count_zones()
    show_a_few()
    show_rules_are_data()
    print("\nEverything above came from files on disk. None of it is in Python.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
