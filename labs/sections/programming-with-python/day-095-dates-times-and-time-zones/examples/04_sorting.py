"""Why UTC ISO 8601 text sorts correctly, and what breaks when it is local.

Day 91 stored every timestamp in SQLite as ISO 8601 text in UTC and leaned on
one property: for that exact format, comparing the strings character by
character gives the same order as comparing the instants. This file proves it
and then breaks it in the two ways it can be broken.

Run:  python3 examples/04_sorting.py
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc
LONDON = ZoneInfo("Europe/London")
NEW_YORK = ZoneInfo("America/New_York")
KOLKATA = ZoneInfo("Asia/Kolkata")

# Four events, each a real instant, each recorded by a different office.
EVENTS = [
    ("checkout", datetime(2026, 8, 16, 18, 0, tzinfo=UTC), NEW_YORK),
    ("dispatch", datetime(2026, 8, 16, 16, 0, tzinfo=UTC), LONDON),
    ("packed", datetime(2026, 8, 16, 15, 0, tzinfo=UTC), KOLKATA),
    ("ordered", datetime(2026, 8, 16, 11, 30, tzinfo=UTC), KOLKATA),
]


def utc_text(instant: datetime) -> str:
    """The storage format: UTC, fixed width, Z suffix, no offset to parse."""
    return instant.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def local_text(instant: datetime, zone: ZoneInfo) -> str:
    """What you get if you store what the local clock said. Do not do this."""
    return instant.astimezone(zone).strftime("%Y-%m-%dT%H:%M:%S")


def local_text_with_offset(instant: datetime, zone: ZoneInfo) -> str:
    """Local time with its offset. Correct, complete — and still sorts wrong."""
    return instant.astimezone(zone).isoformat()


def show_utc_sorts() -> None:
    print("=" * 68)
    print("UTC ISO 8601 text: lexicographic order IS chronological order")
    print("=" * 68)
    by_text = sorted(utc_text(i) for _, i, _ in EVENTS)
    by_instant = [utc_text(i) for _, i, _ in sorted(EVENTS, key=lambda e: e[1])]
    for name, instant, _ in sorted(EVENTS, key=lambda e: e[1]):
        print(f"  {utc_text(instant)}  {name}")
    print(f"\n  sorted as text     == sorted as instants : {by_text == by_instant}")
    print("\n  It works because the format was designed so it would: the fields")
    print("  run most-significant first, every one is zero-padded to a fixed")
    print("  width, and the offset is always the same. Character 1 outranks")
    print("  character 2 in exactly the way a year outranks a month.")
    print("  That is what lets a database with no date type — SQLite, a CSV, a")
    print("  key in a key-value store — do ORDER BY, MIN, MAX, BETWEEN and a")
    print("  range scan on a plain text column and be right.")


def show_local_breaks() -> None:
    print()
    print("=" * 68)
    print("Local text: lexicographic order is NOT chronological order")
    print("=" * 68)
    print("  Same four events, each stored as the local clock in its own office:\n")
    rows = [(name, local_text(i, z), i) for name, i, z in EVENTS]
    text_order = [name for name, _, _ in sorted(rows, key=lambda r: r[1])]
    true_order = [name for name, _, _ in sorted(rows, key=lambda r: r[2])]
    for name, text, instant in sorted(rows, key=lambda r: r[1]):
        print(f"  {text}  {name}")
    print(f"\n  sorted as text     : {text_order}")
    print(f"  sorted as instants : {true_order}")
    print(f"  same order?        : {text_order == true_order}")
    print("\n  Reversed, in this case. The strings are all well-formed ISO 8601")
    print("  and every one of them is true. They are simply not comparable to")
    print("  each other, because they are measured against different rulers.")


def show_offset_text_also_breaks() -> None:
    print()
    print("=" * 68)
    print("Local text WITH the offset: still not sortable as text")
    print("=" * 68)
    rows = [(name, local_text_with_offset(i, z), i) for name, i, z in EVENTS]
    text_order = [name for name, _, _ in sorted(rows, key=lambda r: r[1])]
    true_order = [name for name, _, _ in sorted(rows, key=lambda r: r[2])]
    for name, text, _ in sorted(rows, key=lambda r: r[1]):
        print(f"  {text}  {name}")
    print(f"\n  sorted as text     : {text_order}")
    print(f"  sorted as instants : {true_order}")
    print(f"  same order?        : {text_order == true_order}")
    print("\n  This is the subtle one. These strings carry their offsets, so")
    print("  nothing is lost — a parser can recover every instant exactly. But")
    print("  a text sort compares the digits left to right and never reaches")
    print("  the offset on the end, so an index, a sorted file or an ORDER BY")
    print("  over the raw column is still wrong. Losslessness and sortability")
    print("  are different properties. UTC text has both.")


def show_ambiguous_collision() -> None:
    print()
    print("=" * 68)
    print("The third failure: two instants, one local string")
    print("=" * 68)
    first = datetime(2026, 10, 25, 0, 30, tzinfo=UTC)
    second = datetime(2026, 10, 25, 1, 30, tzinfo=UTC)
    print(f"  {utc_text(first)}  ->  London local  {local_text(first, LONDON)}")
    print(f"  {utc_text(second)}  ->  London local  {local_text(second, LONDON)}")
    same = local_text(first, LONDON) == local_text(second, LONDON)
    print(f"\n  identical local strings? {same}")
    print("  Two instants an hour apart collapse to one string, so no sort of")
    print("  any kind can order them and no query can tell them apart. This is")
    print("  not a sorting bug you can fix with a better comparator; the")
    print("  information is gone at the moment of writing.")


def show_formats() -> None:
    print()
    print("=" * 68)
    print("ISO 8601 and RFC 3339 are not the same thing")
    print("=" * 68)
    instant = datetime(2026, 10, 25, 1, 30, tzinfo=UTC)
    print("  Renderings of one instant:")
    print(f"    isoformat()              {instant.isoformat()}")
    print(f"    strftime Z form          {utc_text(instant)}")
    print(f"    basic ISO 8601 form      {instant.strftime('%Y%m%dT%H%M%SZ')}")
    print(f"    ordinal date (ISO 8601)  {instant.strftime('%Y-%jT%H:%M:%SZ')}")
    print(f"    ISO week date            {date(2026, 10, 25).isocalendar()}")
    print()
    print("  ISO 8601 is a large standard: it allows the basic form with no")
    print("  separators, week dates, ordinal dates, durations, intervals and")
    print("  reduced precision. RFC 3339 is a small profile of it for the")
    print("  internet: date, T or a space, time, and a mandatory offset. Every")
    print("  RFC 3339 timestamp is valid ISO 8601; the reverse is not true —")
    print("  '2026-W43-7' is ISO 8601 and is not a timestamp at all.")
    print("  Write RFC 3339 with Z. It is the intersection everything reads.")
    print()
    print("  What Python actually parses on this machine:")
    samples = [
        "2026-10-25T01:30:00+00:00",
        "2026-10-25T01:30:00Z",
        "2026-10-25 01:30:00Z",
        "20261025T013000Z",
        "2026-W43-7",
        "2026-10-25T01:30:00+0100",
        "Sun, 25 Oct 2026 01:30:00 GMT",
    ]
    for text in samples:
        try:
            parsed = datetime.fromisoformat(text)
            print(f"    fromisoformat({text!r:<32}) -> {parsed.isoformat()}")
        except ValueError as exc:
            print(f"    fromisoformat({text!r:<32}) -> ValueError: {exc}")
    print()
    print("  `fromisoformat` was strict before Python 3.11 and accepts most of")
    print("  ISO 8601 from 3.11 onward, including the trailing Z. Note the")
    print("  week-date line: it parses, and it silently becomes a midnight.")
    print("  The last line is RFC 2822, the email date format, which")
    print("  `fromisoformat` refuses — `email.utils.parsedate_to_datetime`")
    print("  is the standard-library function for that one.")


def show_strptime_traps() -> None:
    print()
    print("=" * 68)
    print("strftime and strptime: the two traps")
    print("=" * 68)
    print("  Trap 1 — %Z parses almost nothing, and throws the zone away:")
    for name in ["UTC", "GMT", "BST", "EST"]:
        text = f"2026-10-25 01:30:00 {name}"
        try:
            parsed = datetime.strptime(text, "%Y-%m-%d %H:%M:%S %Z")
            print(f"    {name:<4} -> {parsed!r}")
            print(f"         tzinfo is {parsed.tzinfo} — the zone name is gone")
        except ValueError:
            print(f"    {name:<4} -> ValueError: does not match the format")
    print("    %z with a numeric offset is the one that works:")
    numeric = datetime.strptime("2026-10-25 01:30:00 +0100", "%Y-%m-%d %H:%M:%S %z")
    print(f"    {numeric!r}")
    print("    And an abbreviation could not identify a zone even if it parsed:")
    print("    IST is India, Ireland and Israel; CST is at least three places.")
    print()
    print("  Trap 2 — the order of the numbers is a cultural convention:")
    text = "05/03/2026"
    day_first = datetime.strptime(text, "%d/%m/%Y").date()
    month_first = datetime.strptime(text, "%m/%d/%Y").date()
    print(f"    {text} parsed as %d/%m/%Y -> {day_first}")
    print(f"    {text} parsed as %m/%d/%Y -> {month_first}")
    print("    Both parse. Both succeed. They are two months apart, and no")
    print("    error is raised in either direction. This is exactly the failure")
    print("    ISO 8601 was written to end.")
    print()
    print("  %c and %x follow the C locale, so their output changes with the")
    print(f"    environment: %c here gives {datetime(2026, 10, 25, 1, 30):%c}")
    print(f"    and %x gives {datetime(2026, 10, 25, 1, 30):%x}")
    print("    Never write either into a file another program will read.")


def show_month_arithmetic() -> None:
    print()
    print("=" * 68)
    print("'Add one month' is not a timedelta")
    print("=" * 68)
    start = datetime(2026, 1, 31, 12, 0, tzinfo=UTC)
    print(f"  start                       {start.date()}")
    print(f"  + timedelta(days=30)        {(start + timedelta(days=30)).date()}")
    print(f"  + timedelta(days=31)        {(start + timedelta(days=31)).date()}")
    print("\n  Neither is 'one month later', because a month is not a fixed")
    print("  number of days — it is 28, 29, 30 or 31 depending on which one and")
    print("  which year. timedelta carries days, seconds and microseconds and")
    print("  deliberately has no months or years field, because it could not")
    print("  give them a length.")
    print("\n  So 'the 31st of the next month' has to be a policy decision:")
    print("    31 January + 1 month = 28 February (clamp to the month end)?")
    print("    or 3 March (overflow the extra days)?")
    print("    or an error, because the caller has not said which they meant?")
    print("  Pick one, write it down, and put it in a named function. The")
    print("  standard library has calendar.monthrange to tell you the length;")
    print("  it deliberately does not choose the policy for you.")


def main() -> int:
    show_utc_sorts()
    show_local_breaks()
    show_offset_text_also_breaks()
    show_ambiguous_collision()
    show_formats()
    show_strptime_traps()
    show_month_arithmetic()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
