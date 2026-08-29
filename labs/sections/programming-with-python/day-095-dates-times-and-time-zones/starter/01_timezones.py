"""Day 095 starter — ten exercises. Your work goes in this file.

Read `starter/00_brief.md` first. Then work down this file, replacing each
`raise NotImplementedError(...)` with a real implementation, and re-running:

    bash starter/02_check.sh

after each one. It will tell you how many of the ten are done, and for each
failure it prints what it wanted and what it got.

Rules for this file:

  * Nothing here may read the clock. Every instant is passed in. A test that
    calls `datetime.now()` cannot be trusted on the one day of the year this
    material is about, which is the day the clocks change.
  * The standard library only: `datetime`, `zoneinfo`, `time`, `calendar`.
  * Do not edit the given code above the exercises, or the checker.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Callable

import zoneinfo
from zoneinfo import ZoneInfo

UTC = timezone.utc


# ===========================================================================
# GIVEN — the rule table types for exercises 9 and 10. Do not change these.
# ===========================================================================
@dataclass(frozen=True)
class Transition:
    """At `instant` (a UTC instant) the offset becomes `offset`, named `name`."""

    instant: datetime
    offset: timedelta
    name: str


@dataclass(frozen=True)
class ZoneRules:
    """The offset in force before the first transition, plus the transitions."""

    base_offset: timedelta
    base_name: str
    transitions: tuple[Transition, ...]


HOUR = timedelta(hours=1)

# Europe/London through 2026. London's clocks change at 01:00 UTC in both
# directions, which is why the instants below are round numbers in UTC and
# not in local time.
LONDON_2026 = ZoneRules(
    base_offset=timedelta(0),
    base_name="GMT",
    transitions=(
        Transition(datetime(2026, 3, 29, 1, 0, tzinfo=UTC), HOUR, "BST"),
        Transition(datetime(2026, 10, 25, 1, 0, tzinfo=UTC), timedelta(0), "GMT"),
    ),
)


# ===========================================================================
# EXERCISE 1 — is the zone database actually here, and how big is it?
# ===========================================================================
def zone_count() -> int:
    """Return the number of time zones this machine's database offers.

    One call does it: `zoneinfo.available_timezones()` returns a set of every
    zone name available, and you want its length. On the authoring machine
    this was 598; yours may differ, and the checker only requires it to be
    over 100, because a database with fewer than that is not a real one.

    Command to see it by hand:
        python3 -c "import zoneinfo; print(len(zoneinfo.available_timezones()))"
    """
    raise NotImplementedError("Exercise 1: count the zones in the database")


# ===========================================================================
# EXERCISE 2 — the storage format
# ===========================================================================
def to_utc_text(instant: datetime) -> str:
    """Render an aware datetime as RFC 3339 UTC text: 2026-10-25T01:30:00Z.

    Two steps, and the first is the one people forget:
      1. convert to UTC with `.astimezone(timezone.utc)`;
      2. format with `strftime("%Y-%m-%dT%H:%M:%SZ")`.

    Raise ValueError if `instant` is naive — a naive datetime has no offset,
    so there is no honest way to write a Z on the end of it. Check it with
    `instant.tzinfo is None or instant.utcoffset() is None`.
    """
    raise NotImplementedError("Exercise 2: render an instant as RFC 3339 UTC text")


# ===========================================================================
# EXERCISE 3 — how long is a day, really?
# ===========================================================================
def day_length_hours(day: date, zone_name: str) -> float:
    """Return the real elapsed hours in one local calendar day, as a float.

    The trap is that subtracting two local midnights gives 24.0 every time.
    Convert both to UTC first, and the difference becomes true:

        start = datetime.combine(day, time(0, 0), tzinfo=ZoneInfo(zone_name))
        end   = datetime.combine(day + timedelta(days=1), time(0, 0), ...)
        elapsed = end.astimezone(UTC) - start.astimezone(UTC)

    Expected: 23.0 for Europe/London on 2026-03-29, 25.0 on 2026-10-25,
    and 24.0 on any ordinary day.
    """
    raise NotImplementedError("Exercise 3: measure the real length of a local day")


# ===========================================================================
# EXERCISE 4 — the two offsets of an ambiguous wall clock
# ===========================================================================
def ambiguous_offsets(wall: datetime, zone_name: str) -> tuple[timedelta, timedelta]:
    """Return the offsets the same wall reading has at fold=0 and fold=1.

    `wall` arrives naive. Attach the zone with `.replace(tzinfo=..., fold=...)`
    and read `.utcoffset()` from each.

    For 2026-10-25 01:30 in Europe/London this is
    (timedelta(hours=1), timedelta(0)) — BST first, then GMT.
    On an ordinary wall reading both entries are the same, which is the point:
    fold only ever matters on the transition.
    """
    raise NotImplementedError("Exercise 4: read both offsets of a wall reading")


# ===========================================================================
# EXERCISE 5 — did this wall clock ever happen?
# ===========================================================================
def is_nonexistent(wall: datetime, zone_name: str) -> bool:
    """True if this local wall reading never occurred in this zone.

    The test is a round trip, and it is the standard one:

        aware = wall.replace(tzinfo=zone)
        back  = aware.astimezone(UTC).astimezone(zone)
        nonexistent = back.replace(tzinfo=None) != wall

    If the time exists, going out to UTC and back brings you home. If it was
    skipped, it does not.

    True for 2026-03-29 01:30 in Europe/London. False for 01:30 on 28 March,
    and false for 2026-10-25 01:30, which happened twice rather than never.
    """
    raise NotImplementedError("Exercise 5: detect a wall time that never happened")


# ===========================================================================
# EXERCISE 6 — did this wall clock happen twice?
# ===========================================================================
def is_ambiguous(wall: datetime, zone_name: str) -> bool:
    """True if this local wall reading occurred twice in this zone.

    Compare the two folds. If attaching the zone with fold=0 and with fold=1
    gives two different UTC instants, the reading is ambiguous:

        a = wall.replace(tzinfo=zone, fold=0).astimezone(UTC)
        b = wall.replace(tzinfo=zone, fold=1).astimezone(UTC)

    Two traps here, and the second is the interesting one.

    Comparing the two AWARE datetimes directly returns True even when they
    are an hour apart, because two datetimes with the same tzinfo object are
    compared by wall clock. Compare the UTC conversions.

    And `a != b` is not the answer, because the two folds differ on a
    NONEXISTENT reading too. Compare their direction instead: an ambiguous
    reading gives the earlier instant at fold=0, while a nonexistent one
    gives the later. So `a < b` is the whole test.

    True for 2026-10-25 01:30 in Europe/London, false for 2026-03-29 01:30.
    """
    raise NotImplementedError("Exercise 6: detect a wall time that happened twice")


# ===========================================================================
# EXERCISE 7 — sorting text and getting chronology for free
# ===========================================================================
def sorted_utc_texts(instants: list[datetime]) -> list[str]:
    """Render each instant with `to_utc_text` and return the list sorted AS TEXT.

    Use `sorted(...)` on the strings — a plain lexicographic sort, no key
    function, no parsing back into datetimes. The exercise is to demonstrate
    that you do not need to: for this format the text order and the
    chronological order are the same order, which is why Day 91 could store
    timestamps in a database with no date type and still write ORDER BY.

    The checker compares your result against the instants sorted properly.
    """
    raise NotImplementedError("Exercise 7: sort UTC ISO text lexicographically")


# ===========================================================================
# EXERCISE 8 — which clock measures a duration
# ===========================================================================
def measure_elapsed(work: Callable[[], object]) -> float:
    """Call `work()` once and return how long it took, in seconds.

    Use `time.monotonic()` — read it before and after and subtract. Not
    `time.time()`, which is adjustable and can move or go backwards while
    your code is between the two readings.

    The checker asserts three things: that the result is a float, that it is
    not negative, and that this file mentions `time.monotonic`. You will need
    to import `time` yourself — it is deliberately not imported above.
    """
    raise NotImplementedError("Exercise 8: time a callable with a monotonic clock")


# ===========================================================================
# EXERCISE 9 — the resolver, direction 1: an instant has exactly one offset
# ===========================================================================
def offset_at_instant(instant: datetime, rules: ZoneRules) -> timedelta:
    """Return the offset in force at a UTC instant, using the rule table only.

    No `zoneinfo` in this function. Start from `rules.base_offset`, walk
    `rules.transitions` in order, and every time the transition's instant is
    at or before `instant`, adopt that transition's offset. The transitions
    are already sorted.

    This direction is easy and always has exactly one answer, which is the
    argument for storing instants rather than wall clocks.
    """
    raise NotImplementedError("Exercise 9: resolve an instant to its offset")


# ===========================================================================
# EXERCISE 10 — the resolver, direction 2: a wall clock may have 0, 1 or 2
# ===========================================================================
def resolve_wall(wall: datetime, rules: ZoneRules, fold: int = 0) -> tuple[timedelta, str]:
    """Resolve a naive wall reading to (offset, kind) using the rule table only.

    `kind` is "normal", "ambiguous" or "nonexistent".

    The algorithm, which is the one `zoneinfo` runs:

      1. Chop the timeline into segments — one per offset, bounded by the
         transitions. For LONDON_2026 there are three: before 29 March (GMT),
         between the two transitions (BST), and after 25 October (GMT).
      2. For each segment, assume its offset applies and compute the instant
         that would produce this wall reading: `wall_as_utc - offset`.
      3. Keep the candidate only if that instant actually falls inside that
         segment. A candidate outside its own segment contradicts itself.
      4. One survivor: "normal". Two: "ambiguous" — fold picks which, 0 for
         the earlier instant and 1 for the later. None: "nonexistent" — the
         reading falls in the gap, and fold=0 means the offset before the gap
         while fold=1 means the offset after it.

    The checker runs this against `zoneinfo` for Europe/London on thirteen
    wall readings and both folds, twenty-six comparisons, and every one must
    agree. `examples/06_resolver.py` is a worked version; try it yourself
    first, because reading it teaches you much less than writing it.
    """
    raise NotImplementedError("Exercise 10: resolve a wall reading to an offset")


if __name__ == "__main__":
    print("This file is a workbook, not a program. Check your work with:")
    print("    bash starter/02_check.sh")
