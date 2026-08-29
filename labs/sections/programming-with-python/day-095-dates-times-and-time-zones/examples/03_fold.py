"""The hour that happened twice, and the hour that never happened at all.

A wall-clock reading plus a zone name is not enough to identify an instant.
Twice a year it identifies two instants, or none. `fold` is the single bit
that chooses between the two, and it is the whole reason this lesson exists.

Everything here is pinned to explicit dates. Nothing reads a clock, because a
test that uses "now" cannot be trusted on the one day of the year it matters.

Run:  python3 examples/03_fold.py
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc
LONDON = ZoneInfo("Europe/London")

# 25 October 2026, 02:00 local, clocks go back to 01:00. Wall times from
# 01:00 up to but not including 02:00 happen twice.
AMBIGUOUS = datetime(2026, 10, 25, 1, 30)
# 29 March 2026, 01:00 local, clocks jump to 02:00. Wall times from 01:00 up
# to but not including 02:00 do not happen at all.
NONEXISTENT = datetime(2026, 3, 29, 1, 30)


def fmt_offset(delta: timedelta | None) -> str:
    """Format a UTC offset as +HH:MM. See 01_zone_database.py for why."""
    if delta is None:
        return "none"
    total = int(delta.total_seconds())
    sign = "-" if total < 0 else "+"
    total = abs(total)
    return f"{sign}{total // 3600:02d}:{total % 3600 // 60:02d}"


def show_ambiguous() -> None:
    print("=" * 68)
    print("AMBIGUOUS — the same wall clock, two different instants")
    print("=" * 68)
    print(f"wall reading: {AMBIGUOUS.isoformat()}  zone: Europe/London\n")

    first = AMBIGUOUS.replace(tzinfo=LONDON, fold=0)
    second = AMBIGUOUS.replace(tzinfo=LONDON, fold=1)

    for label, moment in [("fold=0", first), ("fold=1", second)]:
        print(f"  {label}")
        print(f"    local     {moment.isoformat()}")
        print(f"    offset    {fmt_offset(moment.utcoffset())}  ({moment.tzname()})")
        print(f"    the UTC instant it means  {moment.astimezone(UTC).isoformat()}")
        print(f"    epoch seconds             {moment.timestamp():.0f}")
    gap = second.astimezone(UTC) - first.astimezone(UTC)
    print(f"\n  They are {gap} apart. Same string, same zone, different moments.")

    print("\n  The trap, and it is a real one:")
    print(f"    first == second            -> {first == second}")
    print(f"    same instant?              -> {first.astimezone(UTC) == second.astimezone(UTC)}")
    print(f"    first.timestamp() equal?   -> {first.timestamp() == second.timestamp()}")
    print("    Comparing two aware datetimes that carry the SAME tzinfo object")
    print("    compares their wall readings and ignores fold, so two moments an")
    print("    hour apart test equal. Convert to UTC before you compare, sort or")
    print("    deduplicate anything.")


def show_nonexistent() -> None:
    print()
    print("=" * 68)
    print("NONEXISTENT — a wall clock reading nobody ever saw")
    print("=" * 68)
    print(f"wall reading: {NONEXISTENT.isoformat()}  zone: Europe/London\n")

    for fold in (0, 1):
        moment = NONEXISTENT.replace(tzinfo=LONDON, fold=fold)
        as_utc = moment.astimezone(UTC)
        back = as_utc.astimezone(LONDON)
        print(f"  fold={fold}")
        print(f"    local     {moment.isoformat()}  offset {fmt_offset(moment.utcoffset())}")
        print(f"    as UTC    {as_utc.isoformat()}")
        print(f"    back to London  {back.isoformat()}  <- NOT what you started with")
    print("\n  Python constructs the object without complaining, because a naive")
    print("  wall reading plus a zone is a request, not a fact. The round trip")
    print("  is where it shows: local -> UTC -> local does not come home.")
    print("  fold=0 uses the offset in force BEFORE the gap, fold=1 the offset")
    print("  after it, and neither answer is the time you asked for, because")
    print("  the time you asked for did not occur.")


def show_job_firing_twice() -> None:
    print()
    print("=" * 68)
    print("THE CONSEQUENCE — a job scheduled at 01:30 local")
    print("=" * 68)
    print("A scheduler that wakes every minute and fires when the local clock")
    print("reads 01:30 will fire once on an ordinary day. Walk 25 October 2026")
    print("minute by minute in real elapsed time and count:\n")

    start = datetime(2026, 10, 25, 0, 0, tzinfo=LONDON).astimezone(UTC)
    fires = []
    for minute in range(5 * 60):
        instant = start + timedelta(minutes=minute)
        local = instant.astimezone(LONDON)
        if (local.hour, local.minute) == (1, 30):
            fires.append(instant)
    print(f"  the local clock read 01:30 {len(fires)} times:")
    for instant in fires:
        local = instant.astimezone(LONDON)
        print(
            f"    {instant.isoformat()} UTC  =  {local.strftime('%H:%M')} "
            f"{local.tzname()} (fold={local.fold})"
        )
    print("\n  Two firings, one hour apart, from one schedule entry. If that job")
    print("  charges a card, sends a statement or writes a daily partition, it")
    print("  has now done it twice. On 29 March 2026 the same schedule fires")
    print("  zero times, because 01:30 never arrives:")

    spring_start = datetime(2026, 3, 29, 0, 0, tzinfo=LONDON).astimezone(UTC)
    spring_fires = sum(
        1
        for minute in range(5 * 60)
        if (lambda local: (local.hour, local.minute) == (1, 30))(
            (spring_start + timedelta(minutes=minute)).astimezone(LONDON)
        )
    )
    print(f"    firings on 2026-03-29: {spring_fires}")
    print("\n  Schedule in UTC and you get exactly one firing on both days. That")
    print("  is not a workaround; it is what 'daily at 01:30' actually meant.")


def show_arithmetic() -> None:
    print()
    print("=" * 68)
    print("ARITHMETIC — 'one hour later' has two different meanings")
    print("=" * 68)
    start = datetime(2026, 10, 25, 0, 30, tzinfo=LONDON)
    wall = start + timedelta(hours=1)
    absolute = (start.astimezone(UTC) + timedelta(hours=1)).astimezone(LONDON)
    print(f"  start                      {start.isoformat()}")
    print(f"  + timedelta(hours=1)       {wall.isoformat()}   <- wall arithmetic")
    print(f"  + one hour of real time    {absolute.isoformat()}   <- elapsed time")
    print("  Here they agree by luck: both land on the first 01:30. Cross the")
    print("  transition and they part company:")
    start2 = datetime(2026, 10, 25, 0, 30, tzinfo=LONDON)
    wall2 = start2 + timedelta(hours=2)
    abs2 = (start2.astimezone(UTC) + timedelta(hours=2)).astimezone(LONDON)
    print(f"  + timedelta(hours=2)       {wall2.isoformat()}")
    print(f"  + two hours of real time   {abs2.isoformat()}")
    print(f"  a whole hour apart: {wall2.astimezone(UTC) - abs2.astimezone(UTC)}")
    print("\n  timedelta arithmetic on an aware datetime adds to the WALL clock")
    print("  fields and then re-derives the offset from the result, so two")
    print("  hours of wall clock can be one, two or three hours of elapsed")
    print("  time. To add elapsed time, convert to UTC, add,")
    print("  and convert back. Decide which one you meant; both are legitimate.")
    print("  'The meeting is at 09:00 next Tuesday' is wall arithmetic. 'The")
    print("  token expires in one hour' is elapsed time.")


def main() -> int:
    show_ambiguous()
    show_nonexistent()
    show_job_firing_twice()
    show_arithmetic()
    print("\nEvery instant above is pinned in the source. Nothing read a clock.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
