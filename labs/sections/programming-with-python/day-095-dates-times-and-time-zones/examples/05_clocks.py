"""Two clocks, two jobs: wall-clock time and monotonic time.

Day 81 measured the drift in a scheduled job by subtracting wall-clock
readings. That works right up until the wall clock is adjusted underneath you
— by NTP correcting a few milliseconds, by a daylight-saving transition, by an
administrator typing `date`, by a laptop waking from sleep — at which point
the measurement is not merely imprecise, it can be negative.

`time.monotonic()` never goes backwards and is never adjusted. It has no
relationship to any calendar and cannot tell you the date. That is not a
limitation; it is the entire design.

Run:  python3 examples/05_clocks.py
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc
LONDON = ZoneInfo("Europe/London")


def show_clock_properties() -> None:
    print("=" * 68)
    print("What the standard library says about each clock")
    print("=" * 68)
    print(f"  {'clock':<16} {'monotonic':<10} {'adjustable':<11} implementation")
    for name in ("time", "monotonic", "perf_counter", "process_time"):
        info = time.get_clock_info(name)
        print(
            f"  {name:<16} {str(info.monotonic):<10} {str(info.adjustable):<11} "
            f"{info.implementation}"
        )
    print()
    print("  Read the `adjustable` column. `time.time()` is adjustable, which")
    print("  is a polite way of saying something else may move it while your")
    print("  code is between two readings of it. `time.monotonic()` is not.")
    print()
    for name in ("time", "monotonic", "perf_counter"):
        info = time.get_clock_info(name)
        print(f"  {name:<13} resolution {info.resolution:.9f} s")


def measure_with_both() -> tuple[float, float]:
    print()
    print("=" * 68)
    print("Measuring the same piece of work with both")
    print("=" * 68)
    wall_start = time.time()
    mono_start = time.monotonic()

    total = 0
    for value in range(2_000_000):
        total += value

    wall_elapsed = time.time() - wall_start
    mono_elapsed = time.monotonic() - mono_start
    print(f"  the work summed to {total}")
    print(f"  time.time()      measured {wall_elapsed:.6f} s")
    print(f"  time.monotonic() measured {mono_elapsed:.6f} s")
    print(f"  both positive: {wall_elapsed > 0 and mono_elapsed > 0}")
    print("\n  On an undisturbed machine they agree to within their resolution,")
    print("  and that agreement is exactly what makes the bug invisible in")
    print("  testing. The difference only appears on the day the clock moves.")
    return wall_elapsed, mono_elapsed


def show_wall_clock_hazard() -> None:
    print()
    print("=" * 68)
    print("What a wall-clock measurement does when the clock moves")
    print("=" * 68)
    print("  Nothing below changes your system clock — that would need root and")
    print("  would be a rude thing for a lab to do. Instead it computes what a")
    print("  wall-clock stopwatch WOULD have reported, using real transitions.\n")

    scenarios = [
        (
            "autumn back in London: a task starting at 01:30 BST and",
            "  ending 20 real minutes later",
            datetime(2026, 10, 25, 0, 30, tzinfo=UTC),
            timedelta(minutes=20),
            LONDON,
        ),
        (
            "a task spanning the whole repeated hour",
            "  (starts 01:00 BST, ends 01:15 GMT)",
            datetime(2026, 10, 25, 0, 0, tzinfo=UTC),
            timedelta(minutes=75),
            LONDON,
        ),
        (
            "a task ending after the clocks go back",
            "  (starts 01:50 BST, ends 20 real minutes later at 01:10 GMT)",
            datetime(2026, 10, 25, 0, 50, tzinfo=UTC),
            timedelta(minutes=20),
            LONDON,
        ),
        (
            "spring forward in London: a task over the gap",
            "  (starts 00:45 GMT, ends 25 real minutes later)",
            datetime(2026, 3, 29, 0, 45, tzinfo=UTC),
            timedelta(minutes=25),
            LONDON,
        ),
    ]
    for title, detail, start_utc, duration, zone in scenarios:
        end_utc = start_utc + duration
        local_start = start_utc.astimezone(zone).replace(tzinfo=None)
        local_end = end_utc.astimezone(zone).replace(tzinfo=None)
        naive_measure = local_end - local_start
        print(f"  {title}\n  {detail}")
        print(f"    real elapsed time                {duration}")
        print(f"    local clock at start / end       {local_start.time()} / {local_end.time()}")
        print(f"    a naive local stopwatch reports  {naive_measure}")
        wrong = naive_measure != duration
        print(f"    wrong?                           {wrong}")
        print()
    print("  Three failures, three different shapes. The second under-reports")
    print("  by a full hour: a job that ran for 75 minutes is logged as 15. The")
    print("  third reports a NEGATIVE duration — minus forty minutes for work")
    print("  that took twenty — and a retry loop written as `while elapsed <")
    print("  timeout` never terminates on a negative elapsed. The fourth")
    print("  over-reports by an hour, which is how a healthy job ends up paged")
    print("  as a timeout. All three are one line of monotonic away from")
    print("  correct, and all three pass every test you will ever run in June.")


def show_epoch() -> None:
    print()
    print("=" * 68)
    print("Epoch seconds: what they are, and where they stop")
    print("=" * 68)
    instant = datetime(2026, 10, 25, 1, 30, tzinfo=UTC)
    stamp = instant.timestamp()
    print(f"  {instant.isoformat()}")
    print(f"    epoch seconds        {stamp:.0f}")
    print(f"    back again           {datetime.fromtimestamp(stamp, UTC).isoformat()}")
    print(f"    the epoch itself     {datetime.fromtimestamp(0, UTC).isoformat()}")
    print(f"    signed 32-bit limit  {datetime.fromtimestamp(2**31 - 1, UTC).isoformat()}")
    print("\n  An epoch count is unambiguous by construction — it names an")
    print("  instant with no zone, no offset and no wall clock anywhere in it.")
    print("  It is also unreadable, which is a real cost: nobody spots that")
    print("  1792891800 is wrong by a month while reading a log.")
    print()
    print("  Two limits worth knowing. The first is that famous one above: a")
    print("  signed 32-bit count of seconds runs out in January 2038, and code")
    print("  storing seconds in an int32 anywhere still exists. The second is")
    print("  quieter — Python's timestamp() returns a float, and a float has")
    print("  53 bits of mantissa:")
    micro = datetime(2026, 8, 16, 9, 0, 0, 123456, tzinfo=UTC)
    print(f"    {micro.isoformat()}")
    print(f"      -> {micro.timestamp()!r}")
    print(f"      -> {datetime.fromtimestamp(micro.timestamp(), UTC).isoformat()}")
    print(f"    smallest representable step near now: {2**-52 * 1.79e9:.3e} s")
    print("  Microseconds survive today. Nanoseconds do not, which is why")
    print("  time.time_ns() exists and returns an integer.")
    print(f"    time.time_ns() returns an integer: {type(time.time_ns()).__name__}")


def show_leap_seconds() -> None:
    print()
    print("=" * 68)
    print("Leap seconds: why Python does not model them")
    print("=" * 68)
    print("  A leap second is an extra second inserted into UTC to keep it in")
    print("  step with the Earth's rotation, which is neither constant nor")
    print("  predictable. When one is inserted, that UTC minute really does")
    print("  contain 61 seconds, labelled 23:59:60.")
    print()
    print("  Ask Python for one:")
    try:
        datetime(2016, 12, 31, 23, 59, 60, tzinfo=UTC)
    except ValueError as exc:
        print(f"    datetime(2016, 12, 31, 23, 59, 60) -> ValueError: {exc}")
    print()
    print("  Python's datetime implements POSIX time, in which every day has")
    print("  exactly 86400 seconds by definition. A leap second is therefore")
    print("  not representable, and epoch counts silently repeat or stretch a")
    print("  second when one occurs. Most large operators now smear the extra")
    print("  second across a whole day instead, so no clock ever shows :60.")
    print()
    print("  The practical position: if you are timing rocket launches or")
    print("  reconciling financial trades to the microsecond you need TAI and a")
    print("  specialist library. For everything else, treat 'a day has 86400")
    print("  seconds' as true, know that it is an approximation, and use a")
    print("  monotonic clock for any duration you actually care about.")


def show_recommendation() -> None:
    print()
    print("=" * 68)
    print("Which clock, for which question")
    print("=" * 68)
    rows = [
        ("How long did this take?", "time.monotonic()", "never adjusted"),
        ("Has the timeout expired?", "time.monotonic()", "never goes backwards"),
        ("How fast is this function?", "time.perf_counter()", "highest resolution"),
        ("How much CPU did it use?", "time.process_time()", "excludes sleep"),
        ("When did this happen?", "datetime.now(timezone.utc)", "a calendar instant"),
        ("What should the log say?", "datetime.now(timezone.utc)", "comparable across hosts"),
    ]
    print(f"  {'question':<28} {'use':<28} why")
    for question, tool, why in rows:
        print(f"  {question:<28} {tool:<28} {why}")
    print()
    print("  And the one to stop using: datetime.utcnow() returns a NAIVE")
    print("  datetime holding UTC fields, which is the worst of both worlds —")
    print("  it looks like a local time and is not one. It is deprecated.")
    print("  Write datetime.now(timezone.utc) and get an aware one.")


def main() -> int:
    show_clock_properties()
    measure_with_both()
    show_wall_clock_hazard()
    show_epoch()
    show_leap_seconds()
    show_recommendation()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
