"""A zone-offset resolver from scratch, then the same questions to zoneinfo.

`zoneinfo` looks like magic until you write the thirty lines it is doing. A
compiled zone file is, in essence, a sorted list of UTC instants at which the
offset changes, plus the offset in force after each one. Given that list, both
directions are ordinary code:

  * instant -> offset is a search: find the last transition at or before it.
  * wall clock -> instant is a search with a twist: try each segment, and see
    how many of them can produce that wall reading. One is the ordinary case.
    Two is an ambiguous time. Zero is a nonexistent one.

The resolver below has no access to the database beyond a table you can read.
It is then checked against `zoneinfo` on every case, both values of `fold`.

Run:  python3 examples/06_resolver.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


# ---------------------------------------------------------------------------
# The rule table. Three columns, and that is genuinely all a zone is.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Transition:
    """At `instant` (UTC) the offset becomes `offset` and the name `name`."""

    instant: datetime
    offset: timedelta
    name: str


@dataclass(frozen=True)
class ZoneRules:
    """A base offset, plus every instant at which it changes. Sorted."""

    base_offset: timedelta
    base_name: str
    transitions: tuple[Transition, ...]


HOUR = timedelta(hours=1)

# Europe/London across 2026, written out by hand from the two transitions.
# The transition instants are in UTC because that is the only ruler that does
# not move: London's clocks change at 01:00 UTC in both directions.
LONDON_2026 = ZoneRules(
    base_offset=timedelta(0),
    base_name="GMT",
    transitions=(
        Transition(datetime(2026, 3, 29, 1, 0, tzinfo=UTC), HOUR, "BST"),
        Transition(datetime(2026, 10, 25, 1, 0, tzinfo=UTC), timedelta(0), "GMT"),
    ),
)


# ---------------------------------------------------------------------------
# Direction 1: an instant is easy. There is exactly one answer, always.
# ---------------------------------------------------------------------------
def offset_at_instant(instant: datetime, rules: ZoneRules) -> tuple[timedelta, str]:
    """The offset in force at a UTC instant: the last transition at or before it."""
    if instant.tzinfo is not UTC:
        raise ValueError("pass a UTC instant")
    offset, name = rules.base_offset, rules.base_name
    for transition in rules.transitions:
        if instant >= transition.instant:
            offset, name = transition.offset, transition.name
        else:
            break
    return offset, name


# ---------------------------------------------------------------------------
# Direction 2: a wall clock is hard, because it may name 0, 1 or 2 instants.
# ---------------------------------------------------------------------------
def segments(rules: ZoneRules) -> list[tuple[datetime | None, datetime | None, timedelta, str]]:
    """The timeline chopped into (start, end, offset, name) pieces.

    `None` at either end means unbounded. Each piece is a stretch of UTC
    during which the offset does not change.
    """
    edges = [None, *[t.instant for t in rules.transitions], None]
    offsets = [(rules.base_offset, rules.base_name)]
    offsets += [(t.offset, t.name) for t in rules.transitions]
    return [
        (edges[i], edges[i + 1], offsets[i][0], offsets[i][1])
        for i in range(len(offsets))
    ]


def candidates(wall: datetime, rules: ZoneRules) -> list[tuple[datetime, timedelta, str]]:
    """Every UTC instant whose local reading in this zone is `wall`.

    The whole algorithm: for each segment, assume its offset applies, compute
    the UTC instant that would produce this wall reading, and keep it only if
    that instant really falls inside the segment. A candidate that lands
    outside its own segment is a self-contradiction — it says "the offset was
    +1 at a moment when the offset was not +1" — and is discarded. What
    survives is 1, 2, or 0 answers.
    """
    if wall.tzinfo is not None:
        raise ValueError("pass a naive wall-clock reading")
    found = []
    for start, end, offset, name in segments(rules):
        instant = wall.replace(tzinfo=UTC) - offset
        if (start is None or instant >= start) and (end is None or instant < end):
            found.append((instant, offset, name))
    return found


def resolve(wall: datetime, rules: ZoneRules, fold: int = 0) -> tuple[timedelta, str, str]:
    """Resolve a wall reading to (offset, name, kind).

    kind is one of "normal", "ambiguous", "nonexistent". The `fold` rule below
    is PEP 495's, and it is worth stating precisely because it is the whole
    specification in two sentences:

      * ambiguous — fold=0 picks the FIRST of the two instants, fold=1 the
        second.
      * nonexistent — fold=0 uses the offset in force BEFORE the gap, fold=1
        the offset after it. Neither produces the wall time you asked for,
        because no instant does.
    """
    found = candidates(wall, rules)
    if len(found) == 1:
        _, offset, name = found[0]
        return offset, name, "normal"
    if len(found) == 2:
        _, offset, name = found[fold]
        return offset, name, "ambiguous"
    if not found:
        pieces = segments(rules)
        for index in range(len(pieces) - 1):
            before, after = pieces[index], pieces[index + 1]
            boundary = before[1]
            if boundary is None:
                continue
            gap_start = boundary + before[2]
            gap_end = boundary + after[2]
            if gap_start <= wall.replace(tzinfo=UTC) < gap_end:
                chosen = before if fold == 0 else after
                return chosen[2], chosen[3], "nonexistent"
    raise ValueError(f"no rule covers {wall}")


# ---------------------------------------------------------------------------
# The check: does the hand-written resolver agree with the real database?
# ---------------------------------------------------------------------------
CASES = [
    (datetime(2026, 1, 15, 12, 0), "midwinter", "normal"),
    (datetime(2026, 3, 29, 0, 59), "one minute before the gap", "normal"),
    (datetime(2026, 3, 29, 1, 0), "the first instant of the gap", "nonexistent"),
    (datetime(2026, 3, 29, 1, 30), "the middle of the gap", "nonexistent"),
    (datetime(2026, 3, 29, 1, 59), "the last minute of the gap", "nonexistent"),
    (datetime(2026, 3, 29, 2, 0), "the first instant after it", "normal"),
    (datetime(2026, 7, 1, 12, 0), "midsummer", "normal"),
    (datetime(2026, 10, 25, 0, 59), "one minute before the repeat", "normal"),
    (datetime(2026, 10, 25, 1, 0), "the first repeated minute", "ambiguous"),
    (datetime(2026, 10, 25, 1, 30), "the middle of the repeat", "ambiguous"),
    (datetime(2026, 10, 25, 1, 59), "the last repeated minute", "ambiguous"),
    (datetime(2026, 10, 25, 2, 0), "the first instant after it", "normal"),
    (datetime(2026, 12, 25, 9, 0), "midwinter again", "normal"),
]


def fmt(delta: timedelta) -> str:
    total = int(delta.total_seconds())
    sign = "-" if total < 0 else "+"
    total = abs(total)
    return f"{sign}{total // 3600:02d}:{total % 3600 // 60:02d}"


def main() -> int:
    london = ZoneInfo("Europe/London")
    print("A hand-written resolver over a three-line rule table, checked")
    print("against the real IANA database on every case and both folds.\n")
    print(f"rule table: base {fmt(LONDON_2026.base_offset)} {LONDON_2026.base_name}")
    for transition in LONDON_2026.transitions:
        print(
            f"            at {transition.instant.isoformat()} -> "
            f"{fmt(transition.offset)} {transition.name}"
        )
    print()

    header = (
        f"{'wall clock':<20} {'fold':<5} {'mine':<8} {'zoneinfo':<9} "
        f"{'kind':<12} agree"
    )
    print(header)
    print("-" * len(header))

    disagreements = 0
    kind_errors = 0
    for wall, label, expected_kind in CASES:
        for fold in (0, 1):
            mine, name, kind = resolve(wall, LONDON_2026, fold=fold)
            theirs = wall.replace(tzinfo=london, fold=fold).utcoffset()
            agree = mine == theirs
            if not agree:
                disagreements += 1
            if kind != expected_kind:
                kind_errors += 1
            print(
                f"{wall.isoformat():<20} {fold:<5} {fmt(mine):<8} {fmt(theirs):<9} "
                f"{kind:<12} {'yes' if agree else 'NO'}"
            )
    print()
    print(f"cases: {len(CASES)} wall readings x 2 folds = {len(CASES) * 2} comparisons")
    print(f"disagreements with zoneinfo: {disagreements}")
    print(f"cases classified wrongly:    {kind_errors}")

    print("\nAnd the other direction, which has no ambiguity to resolve:")
    for probe in [
        datetime(2026, 3, 29, 0, 59, 59, tzinfo=UTC),
        datetime(2026, 3, 29, 1, 0, 0, tzinfo=UTC),
        datetime(2026, 10, 25, 0, 59, 59, tzinfo=UTC),
        datetime(2026, 10, 25, 1, 0, 0, tzinfo=UTC),
    ]:
        mine, name = offset_at_instant(probe, LONDON_2026)
        theirs = probe.astimezone(london).utcoffset()
        status = "agree" if mine == theirs else "DISAGREE"
        print(
            f"  {probe.isoformat()}  mine {fmt(mine)} {name:<4} "
            f"zoneinfo {fmt(theirs)}  {status}"
        )
        if mine != theirs:
            disagreements += 1

    print("\nWhat the real thing adds, and it is worth being honest about it:")
    print("  * every zone in the database instead of one, and every recorded")
    print("    change each of them has ever made, not just the two in 2026;")
    print("  * a compiled binary file and a cache of loaded zones, instead of a")
    print("    table typed out by hand and scanned from the top;")
    print("  * the rule string at the end of each file, which extrapolates the")
    print("    rules past the last stored transition into the future;")
    print("  * and correct handling of the historical oddities — offsets that")
    print("    were not whole minutes, zones that changed name without changing")
    print("    offset, and days that were skipped entirely.")
    print("  The ALGORITHM, though, is the one above. That is the whole trick.")

    return 1 if (disagreements or kind_errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())
