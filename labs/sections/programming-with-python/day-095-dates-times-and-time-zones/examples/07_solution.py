"""The reference answers to the ten starter exercises.

Read this AFTER you have tried them. It is marked by the same checker:

    bash starter/02_check.sh examples/07_solution.py

which prints "10 of 10 exercises complete." and exits 0.

The comments explain the choice made, not the syntax used.
"""

from __future__ import annotations

import time
import zoneinfo
from dataclasses import dataclass
from datetime import date, datetime, time as time_of_day, timedelta, timezone
from typing import Callable

from zoneinfo import ZoneInfo

UTC = timezone.utc


# ===========================================================================
# GIVEN — identical to the starter.
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

LONDON_2026 = ZoneRules(
    base_offset=timedelta(0),
    base_name="GMT",
    transitions=(
        Transition(datetime(2026, 3, 29, 1, 0, tzinfo=UTC), HOUR, "BST"),
        Transition(datetime(2026, 10, 25, 1, 0, tzinfo=UTC), timedelta(0), "GMT"),
    ),
)


def zone_count() -> int:
    """Exercise 1. The set includes links and aliases, which is correct: they
    are all names you may legitimately be handed."""
    return len(zoneinfo.available_timezones())


def to_utc_text(instant: datetime) -> str:
    """Exercise 2. Refusing the naive input is the important half.

    A naive datetime has no offset, so converting it to UTC would mean
    guessing which zone it came from — and the only guess available is the
    machine's local zone, which changes when the code moves to a server. The
    error is better than the guess.
    """
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("a naive datetime has no offset and cannot be written as UTC")
    return instant.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def day_length_hours(day: date, zone_name: str) -> float:
    """Exercise 3. Both midnights go to UTC before the subtraction.

    Without those two .astimezone(UTC) calls this returns 24.0 for every day
    ever, including the two it exists to detect.
    """
    zone = ZoneInfo(zone_name)
    start = datetime.combine(day, time_of_day(0, 0), tzinfo=zone)
    end = datetime.combine(day + timedelta(days=1), time_of_day(0, 0), tzinfo=zone)
    return (end.astimezone(UTC) - start.astimezone(UTC)).total_seconds() / 3600


def ambiguous_offsets(wall: datetime, zone_name: str) -> tuple[timedelta, timedelta]:
    """Exercise 4. Two folds, two offsets — equal on any ordinary reading."""
    zone = ZoneInfo(zone_name)
    return (
        wall.replace(tzinfo=zone, fold=0).utcoffset(),
        wall.replace(tzinfo=zone, fold=1).utcoffset(),
    )


def is_nonexistent(wall: datetime, zone_name: str) -> bool:
    """Exercise 5. The round trip, which is the standard idiom.

    Out to UTC and back. If the wall reading exists, it comes home. If it was
    skipped, the return trip lands somewhere else, because the instant Python
    picked for it renders as a different local time.
    """
    zone = ZoneInfo(zone_name)
    aware = wall.replace(tzinfo=zone)
    round_tripped = aware.astimezone(UTC).astimezone(zone)
    return round_tripped.replace(tzinfo=None) != wall


def is_ambiguous(wall: datetime, zone_name: str) -> bool:
    """Exercise 6. Compare the INSTANTS, and compare them with `<`.

    Two things to get right, and the second one bites everybody once.

    First: `wall.replace(tzinfo=zone, fold=0) == wall.replace(tzinfo=zone,
    fold=1)` is True even in the repeated hour, because two datetimes sharing
    a tzinfo object are compared by their wall fields. Convert to UTC before
    comparing.

    Second: `!=` is not enough, because the two folds also differ on a
    NONEXISTENT reading. The direction is what separates them:

        ambiguous   fold=0 -> 00:30Z, fold=1 -> 01:30Z   first < second
        nonexistent fold=0 -> 01:30Z, fold=1 -> 00:30Z   first > second

    An ambiguous reading picks the earlier instant first, and a nonexistent
    one picks the later, so a single `<` classifies both cases.
    """
    zone = ZoneInfo(zone_name)
    first = wall.replace(tzinfo=zone, fold=0).astimezone(UTC)
    second = wall.replace(tzinfo=zone, fold=1).astimezone(UTC)
    return first < second


def sorted_utc_texts(instants: list[datetime]) -> list[str]:
    """Exercise 7. A plain text sort. No key, no parsing, and still correct."""
    return sorted(to_utc_text(instant) for instant in instants)


def measure_elapsed(work: Callable[[], object]) -> float:
    """Exercise 8. time.monotonic, because a duration is not a calendar fact.

    time.time() would give the same answer nearly always and a wrong one — a
    negative one — on the day something adjusts the clock underneath you.
    """
    started = time.monotonic()
    work()
    return time.monotonic() - started


def offset_at_instant(instant: datetime, rules: ZoneRules) -> timedelta:
    """Exercise 9. One instant, one answer, no fold required."""
    if instant.tzinfo is None:
        raise ValueError("pass an aware instant")
    instant = instant.astimezone(UTC)
    offset = rules.base_offset
    for transition in rules.transitions:
        if instant >= transition.instant:
            offset = transition.offset
        else:
            break
    return offset


def _segments(rules: ZoneRules) -> list[tuple[datetime | None, datetime | None, timedelta]]:
    """The timeline as (start, end, offset) pieces; None means unbounded."""
    edges: list[datetime | None] = [None]
    edges += [transition.instant for transition in rules.transitions]
    edges.append(None)
    offsets = [rules.base_offset] + [t.offset for t in rules.transitions]
    return [(edges[i], edges[i + 1], offsets[i]) for i in range(len(offsets))]


def resolve_wall(wall: datetime, rules: ZoneRules, fold: int = 0) -> tuple[timedelta, str]:
    """Exercise 10. Zero, one or two candidates — and that is the whole idea.

    For each segment: assume its offset, compute the instant that would give
    this wall reading, and keep it only if that instant lies inside the
    segment. The count of survivors classifies the reading.
    """
    if wall.tzinfo is not None:
        raise ValueError("pass a naive wall-clock reading")
    as_utc = wall.replace(tzinfo=UTC)
    pieces = _segments(rules)

    found = []
    for start, end, offset in pieces:
        instant = as_utc - offset
        if (start is None or instant >= start) and (end is None or instant < end):
            found.append(offset)

    if len(found) == 1:
        return found[0], "normal"
    if len(found) == 2:
        # Ordered by segment, so index 0 is the earlier instant. PEP 495 says
        # fold=0 selects it.
        return found[fold], "ambiguous"

    # No candidate: the reading falls in a gap. PEP 495 says fold=0 uses the
    # offset before the gap and fold=1 the offset after it.
    for index in range(len(pieces) - 1):
        boundary = pieces[index][1]
        if boundary is None:
            continue
        before_offset = pieces[index][2]
        after_offset = pieces[index + 1][2]
        if boundary + before_offset <= as_utc < boundary + after_offset:
            return (before_offset if fold == 0 else after_offset), "nonexistent"

    raise ValueError(f"no rule in this table covers {wall}")


if __name__ == "__main__":
    print("The reference answers. Mark them with:")
    print("    bash starter/02_check.sh examples/07_solution.py")
