# Day 095 lab — The Hour That Happened Twice

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Dates, Times, and Time Zones
- **Day number:** 95 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-095-dates-times-and-time-zones
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-095-dates-times-and-time-zones` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 95 of 365, and the day the course stops trusting a timestamp.

A nightly job charged every customer twice on 25 October and did not run at
all on 29 March. The schedule entry was correct both times. Its author had
written **01:30, Europe/London**, and on one of those nights the local clock
read 01:30 twice, an hour apart, while on the other it never read 01:30 at
all.

By the end of this lab you will have reproduced every trap in that story with
real output on your own machine, and then written the thirty lines that
`zoneinfo` is running when it answers the question.

The sentence the whole day hangs on:

> A timestamp without a time zone is not a time. It is a rumour.

The spine, in order:

1. Prove your machine has an IANA zone database at all, and count what is in
   it — because the rules are **data on your disk**, not code in Python.
2. Build the 23-hour day and the 25-hour day and assert their lengths.
3. Find the wall-clock time that never happened and watch a round trip fail to
   come home.
4. Produce the two distinct instants that both render as `01:30` and separate
   them with `fold`.
5. Sort a list of ISO UTC strings **as text** and prove it matches chronology
   — then do the same with local text and watch it come out reversed.
6. Measure elapsed time with `time.time()` and `time.monotonic()` and say
   which one you would trust, with the reason.
7. Implement the offset resolver from scratch and assert it agrees with
   `zoneinfo` on twenty-six comparisons.

## Learning objectives

By the end of this lab you will be able to:

- Show where `zoneinfo` gets its data, name the database, read its version,
  and say what happens when it is out of date.
- Explain what a naive `datetime` is, why the standard library lets you make
  one, and what it costs.
- Measure the real length of a local calendar day, and explain why subtracting
  two local midnights cannot do it.
- Detect a nonexistent wall-clock reading with a round trip, and an ambiguous
  one by the order of its two folds.
- State exactly what `fold` selects in each of those two cases.
- Explain why two aware datetimes an hour apart can compare equal, and what to
  do about it.
- Argue, rather than assert, why UTC is the storage format and local time a
  display concern — with a sort that proves it.
- Distinguish ISO 8601 from RFC 3339 and say which one to write.
- Name the two traps in `strptime`: `%Z` parsing almost nothing and throwing
  the zone away, and the day-first/month-first ambiguity that raises no error.
- Choose between wall-clock and monotonic time for a given question, and say
  what a wall clock does to a duration when the clocks change.
- Explain why "add one month" is not a `timedelta`, and why the standard
  library refuses to choose the policy for you.
- Implement a zone-offset resolver over a rule table, in both directions, and
  classify a wall reading as normal, ambiguous or nonexistent.

## Prerequisites

- **Day 43** — a working `python3` on your `PATH`.
- **Day 70** — floating point, which is why `timestamp()` has a precision
  limit worth knowing.
- **Day 81** — scheduling and background jobs. The drift that day measured
  with a wall clock is the bug this day fixes properly.
- **Day 91** — storing timestamps as ISO 8601 text in UTC in a database with
  no date type. That day used the sorting property; this day proves it and
  shows what breaks it.
- Comfort with the shell, and with reading a Python traceback.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64, zone database 2026c |
| Linux (any current distribution) | Expected identical, given Python 3.11+ and a system `tzdata` package |
| Windows | Windows ships no IANA database; `zoneinfo` needs the `tzdata` PyPI package. Use WSL and follow the Linux path. The two scripts are bash and were not run on native Windows here, so no output is claimed for it |

## Hardware requirements

Anything. Every script finishes in well under a second, nothing is written to
disk, and the largest data structure is a list of 598 zone names.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | `zoneinfo` needs 3.9; `fromisoformat` accepting a trailing `Z` needs 3.11; `fold` has existed since 3.6 |
| IANA time zone database | any current release | 2026c | `zoneinfo` reads it; it is not part of Python |
| `bash` | 3.2 | 3.2.57 | The two harness scripts |

Check all three in one line:

```bash
python3 --version
python3 -c "import zoneinfo; print(zoneinfo.TZPATH, len(zoneinfo.available_timezones()))"
```

That printed `598` zones here. A different number is fine and is itself part
of the lesson.

## Free and open-source options

Everything here is free, and two of the three are unusually so.

- **Python** is under the PSF licence, and this lab uses only its standard
  library — `datetime`, `zoneinfo`, `time`, `calendar`. Nothing to install.
- **The IANA time zone database** is in the **public domain**, maintained
  collaboratively, and distributed with essentially every operating system. It
  is one of the quietest pieces of shared infrastructure in computing.
- **`tzdata`** (the PyPI package) is the same data packaged for Python, needed
  only on systems without a system database. Also free.
- The alternatives — `dateutil`, `arrow`, `pendulum` — are all free and open
  source, and the lesson covers what each buys. **None of them is installed
  here and no output is reproduced for any of them.** `pytz` is covered as
  history, because its unusual API exists for a reason worth understanding.

No account, no key, no paid tier, and nothing in this lab is degraded without
one.

## Installation

None. Change into this directory and start.

```bash
cd labs/sections/programming-with-python/day-095-dates-times-and-time-zones
python3 --version
python3 -c "from zoneinfo import ZoneInfo; print(ZoneInfo('Europe/London'))"
```

If the second line raises `ZoneInfoNotFoundError`, your machine has no zone
database where `zoneinfo` looks — see `troubleshooting.md`, which has the fix
for each platform. If `python3` lives somewhere unusual, both scripts take an
override rather than guessing:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## File structure

```text
day-095-dates-times-and-time-zones/
├── README.md                  this file
├── metadata.yml               lab metadata and the recorded run
├── security.md                what this lab does to your machine, and why a
│                              timestamp is more often personal data than
│                              people expect
├── troubleshooting.md         grouped by the message you see — and by the
│                              wrong answer you get with no message at all
├── requirements/
│   ├── README.md              versions, the dependency that is not a package,
│   │                          and what is deliberately absent
│   └── requirements.txt       empty of packages, on purpose
├── starter/                   YOUR work happens here
│   ├── 00_brief.md            the incident, and the ten exercises
│   ├── 01_timezones.py        ten numbered exercises, each with its method
│   ├── 02_check.sh            "N of 10 exercises complete."
│   └── check_exercises.py     the marker. Do not edit
├── examples/                  the reference. Read AFTER you have tried
│   ├── 01_zone_database.py    where the rules live, and that they are data
│   ├── 02_odd_days.py         the 23-hour and 25-hour days, measured
│   ├── 03_fold.py             the repeated hour, the skipped hour, and fold
│   ├── 04_sorting.py          UTC text sorts; local text does not; formats
│   ├── 05_clocks.py           wall clock against monotonic, epoch, leap seconds
│   ├── 06_resolver.py         the from-scratch resolver, checked against zoneinfo
│   └── 07_solution.py         the ten reference answers
├── tests/
│   └── run_tests.sh           75 checks of real values
└── expected-output/           captured from a real run on 2026-08-16
    ├── FIELDS.md              what must match and what may differ
    ├── zone-database.txt      the search path, version and zone count here
    ├── odd-days.txt           23.0h, 25.0h, and 24.0h on the wall every time
    ├── fold.txt               two instants, one wall clock, and a job firing twice
    ├── sorting.txt            the sorts, the formats, the strptime traps
    ├── clocks.txt             clock properties, the epoch, leap seconds
    ├── resolver.txt           26 comparisons, 0 disagreements
    ├── starter-progress.txt   0 of 10 before, 10 of 10 with the answers
    └── test-run.txt           the full harness run
```

## How to run

```bash
# 1. The whole thing. It should be green before you change anything, and
#    green again when you have finished.
bash tests/run_tests.sh
echo "exit code: $?"

# 2. Read the brief. It is the incident this lab reproduces.
#    starter/00_brief.md

# 3. Find out where you stand. It will say 0 of 10, and name each exercise.
bash starter/02_check.sh

# 4. Now do the work in starter/01_timezones.py, re-running step 3 as you go.

# --- everything below is the reference. Look after you have tried. ---

# 5. Does this machine have a zone database, and what is in it?
python3 examples/01_zone_database.py

# 6. The 23-hour day and the 25-hour day, measured rather than asserted.
python3 examples/02_odd_days.py

# 7. The hour that happened twice and the hour that never happened.
python3 examples/03_fold.py

# 8. Why UTC ISO text sorts correctly, and the three ways local text does not.
python3 examples/04_sorting.py

# 9. Which clock measures a duration, and what the other one does when the
#    clocks change.
python3 examples/05_clocks.py

# 10. The resolver from scratch, checked against the real database.
python3 examples/06_resolver.py

# 11. The reference answers, marked by the same checker.
bash starter/02_check.sh examples/07_solution.py
```

## What the commands do

**`bash tests/run_tests.sh`** runs 75 checks of real values: that the zone
database is present and loadable, that the two odd days measure 23 and 25
hours, that the ambiguous reading yields two offsets and two instants an hour
apart, that the nonexistent one does not survive a round trip, that a
local-01:30 schedule fires twice on one night and zero times on another, that
UTC text sorts chronologically and local text does not, that `%Z` rejects
`BST`, that a leap second is not representable, that monotonic time never goes
backwards across 20,000 samples, and that the hand-written resolver agrees
with `zoneinfo` on all 26 comparisons. Everything happens in a temporary
directory removed on exit.

**`bash starter/02_check.sh`** loads your starter file by path, calls each of
the ten functions with pinned inputs, and compares against values that do not
depend on when you run it. An unfinished exercise is reported as *not
started*, a wrong one as *WRONG* with what it wanted and what it got. It never
looks at how you wrote anything, with one exception: exercise 8 checks that
the file mentions `time.monotonic`, because the entire content of that
exercise is which clock you chose.

**`python3 examples/01_zone_database.py`** prints `zoneinfo.TZPATH` and which
entries exist, reads the database version from `+VERSION`, counts the zones,
renders one instant in five places to show that offsets are not whole hours,
and then bisects the database to find the two instants bounding a real
historical oddity — the years London spent at `+01:00` through the winter.

**`python3 examples/02_odd_days.py`** measures six calendar days in three
zones, in both real elapsed time and wall-clock time, and shows the wall
column reading 24.0 on every row including the two that are not.

**`python3 examples/03_fold.py`** is the heart of it: the same wall reading at
`fold=0` and `fold=1`, the two instants and two epoch seconds it names, the
comparison trap, the round trip that does not come home, a scheduler walked
minute by minute and firing twice, and the difference between adding a
`timedelta` and adding elapsed time.

**`python3 examples/04_sorting.py`** sorts the same four events three ways —
UTC text, local text, local text with offsets — and prints all three orders.
Then it renders one instant in five ISO 8601 forms, shows what
`fromisoformat` accepts on your Python, and demonstrates both `strptime`
traps.

**`python3 examples/05_clocks.py`** prints `time.get_clock_info` for four
clocks, measures real work with both, computes what a wall-clock stopwatch
*would* have reported across four real transitions, and covers epoch seconds,
the 2038 limit, float precision, and leap seconds.

**`python3 examples/06_resolver.py`** implements the resolver over a
three-line rule table and prints a 26-row comparison against `zoneinfo`,
ending with the two counts that must both be zero.

## Expected output

The harness ends with a real captured line:

```text
75 checks, 0 failure(s).
```

and exits 0. The starter reports `0 of 10 exercises complete.` with exit 1
before you begin, and `10 of 10 exercises complete.` with exit 0 once the
answers are in place.

The measurement the day is named after:

```text
  fold=0
    local     2026-10-25T01:30:00+01:00
    offset    +01:00  (BST)
    the UTC instant it means  2026-10-25T00:30:00+00:00
    epoch seconds             1792888200
  fold=1
    local     2026-10-25T01:30:00+00:00
    offset    +00:00  (GMT)
    the UTC instant it means  2026-10-25T01:30:00+00:00
    epoch seconds             1792891800

  They are 1:00:00 apart. Same string, same zone, different moments.
```

and the consequence:

```text
  the local clock read 01:30 2 times:
    2026-10-25T00:30:00+00:00 UTC  =  01:30 BST (fold=0)
    2026-10-25T01:30:00+00:00 UTC  =  01:30 GMT (fold=1)
```

with the mirror image on the other transition:

```text
    firings on 2026-03-29: 0
```

The day lengths:

```text
zone                 local date         real       wall  what happened
----------------------------------------------------------------------
Europe/London        2026-03-29        23.0h      24.0h  spring forward
Europe/London        2026-10-25        25.0h      24.0h  autumn back
Europe/London        2026-06-15        24.0h      24.0h  an ordinary day
```

And the resolver, which is the exercise the day is built around:

```text
cases: 13 wall readings x 2 folds = 26 comparisons
disagreements with zoneinfo: 0
cases classified wrongly:    0
```

The full captures are in `expected-output/`, and
`expected-output/FIELDS.md` says which values must match on any machine and
which are allowed to differ on yours — the zone count and the database version
being the two that legitimately will.

## Validation steps

1. `bash tests/run_tests.sh` ends with `75 checks, 0 failure(s).` and exits 0.
2. `python3 -c "import zoneinfo; print(len(zoneinfo.available_timezones()))"`
   prints a number over 100. It printed **598** here.
3. Europe/London on 2026-03-29 measures **23.0** hours and on 2026-10-25
   **25.0** hours — and subtracting the two local midnights says **24.0** on
   both.
4. `2026-10-25 01:30` in Europe/London gives offset **+01:00** at `fold=0` and
   **+00:00** at `fold=1`, naming two instants **exactly one hour** apart.
5. Those two aware datetimes compare **equal** with `==`, and their UTC
   conversions do not. If your code sorts or deduplicates aware datetimes
   without converting first, this is why it is wrong.
6. `2026-03-29 01:30` in Europe/London does **not** survive a round trip
   through UTC: it comes back as `02:30+01:00`.
7. A schedule matching local `01:30` fires **twice** on 25 October 2026 and
   **zero** times on 29 March 2026.
8. Four events sorted by UTC ISO text come out in true chronological order;
   sorted by local text they come out in the **exact reverse**; and sorted by
   local text *with the offset attached* they are still wrong.
9. `%Z` raises `ValueError` on `BST`, and on `UTC` it succeeds and leaves
   `tzinfo` as `None`.
10. `datetime(2016, 12, 31, 23, 59, 60)` raises `ValueError`.
11. `examples/06_resolver.py` exits 0 with **0 disagreements** across 26
    comparisons — and the suite proves that check is real by corrupting one
    transition date and confirming the run then fails.
12. After the harness finishes, `find . -type d -name __pycache__` finds
    nothing and no file has been added to this directory.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

75 checks, exit 0 when they all pass and non-zero otherwise. They are value
checks: exact offsets, exact instants, exact epoch seconds, exact sort orders
and exact classifications.

Two of them exist to prove the suite is not vacuous, and they are worth
pointing at:

- The suite copies `examples/06_resolver.py`, moves one transition date a week
  earlier, runs it, and **requires that it fail**. A resolver that agreed with
  `zoneinfo` no matter what its rule table said would be checking nothing.
- The suite copies `examples/07_solution.py`, replaces `first < second` with
  `first != second` in `is_ambiguous` — the single most likely mistake in the
  whole lab — and requires the marker to catch it and report `9 of 10`.

No check anywhere in this suite asserts a timing. Durations are asserted by
shape: positive, and never decreasing across 20,000 samples. A test that
asserted a millisecond figure would be flaky on somebody else's machine and
would be measuring their processor rather than your code.

Overrides, if `python3` is somewhere unusual:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## Cleanup

```bash
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

Both scripts export `PYTHONDONTWRITEBYTECODE=1` and do their work inside
`mktemp -d`, removed in a `trap`, so if you only ran those there is nothing to
clean up — and the suite asserts as much before it finishes. Nothing was
installed, no database or file was created, and nothing outside this directory
was touched.

To reset your own work and start the exercises again:

```bash
git checkout -- starter/
```

## Troubleshooting

`troubleshooting.md` has the full list, grouped by the message you see and —
longer, because this subject fails quietly — by the wrong answer you get with
no message at all. The ones you are most likely to meet:

- **`ZoneInfoNotFoundError`** — your machine, or more likely your container
  image, has no IANA database. Install `tzdata`.
- **`ValueError: Invalid isoformat string: '...Z'`** — Python 3.10 or older;
  `fromisoformat` did not accept the trailing `Z` until 3.11.
- **Every day measures 24 hours** — you subtracted two local datetimes.
  Convert both to UTC first.
- **Two datetimes an hour apart compare equal** — expected and documented:
  same `tzinfo` means comparison by wall clock, and `fold` is ignored. Compare
  in UTC.
- **`is_ambiguous` is also true for the skipped hour** — `!=` cannot separate
  them; the fold *order* can. Test `first < second`.
- **A duration comes out negative** — you measured with a wall clock.
- **The test suite passes today and fails in October** — it reads the clock
  somewhere.

## Security notes

`security.md` has the full account. In short: nothing here opens a socket,
runs `sudo`, needs a credential, or installs anything — and the suite checks
each of those rather than promising them, including that no URL appears
anywhere in the lab's scripts. In particular **nothing changes your system
clock or your system time zone**; every "what if the clock jumped"
demonstration computes the answer from real transition data instead.

The point worth repeating is the one that does not feel like security at all:
a precise timestamp plus a local zone is a location signal, a sequence of them
is a behavioural profile, and microsecond precision is a strong fingerprint
for correlating one person across two systems. Precision is a decision you
make at collection time, and you cannot un-collect it later. `security.md`
also covers the three genuine vulnerability classes that follow directly from
this lab: expiry checks on a wall clock, certificate validity windows compared
against naive datetimes, and lockout windows a clock jump can reset.

## Extension exercises

1. **Extend the rule table backwards and find something strange.** Add
   Europe/London's transitions for 1968 to 1972 to `LONDON_2026` and re-run
   your resolver against `zoneinfo` for wall readings in those years. The
   three winters at `+01:00` are in `examples/01_zone_database.py`; find their
   boundary instants by bisection, add them, and see whether your resolver
   still agrees. Then answer this: how many segments does your table have now,
   and does your `resolve_wall` still terminate correctly on the first one?
2. **Write `add_months(instant, n, policy)` and defend the policy.** Implement
   at least two — clamp to the month end, and overflow into the next month —
   using `calendar.monthrange`. Then find a case where they differ by more
   than three days, and write a paragraph on which one a billing system should
   use and why. There is a defensible answer and it is not the same for every
   business.
3. **Break the sort deliberately.** Take the four events in
   `examples/04_sorting.py`, store them as local text, and write the query you
   would need to sort them correctly anyway. Then count how many rows you have
   to parse to do it, and compare that with an index on a UTC text column.
   Write down what storing local time actually cost.
4. **Find a zone whose offset is not a whole number of minutes.** They exist,
   historically. Search `zoneinfo.available_timezones()` for a zone and a year
   where `utcoffset().total_seconds() % 60 != 0`, print the instant it
   changed, and then work out what that does to a system storing offsets as an
   integer number of minutes — which many do.
5. **Rewrite Day 81's drift measurement.** Take the scheduled job from Day 81,
   find every place it subtracts two clock readings, and convert each to
   `time.monotonic()` — except the ones that are recording *when* something
   happened, which must stay on a UTC instant. Write down the rule you used to
   decide which was which; that rule is the whole day in one sentence.

## Navigation

- **Previous day:** Day 94 — Data Validation with pydantic
  (`labs/sections/programming-with-python/day-094-data-validation-with-pydantic/`).
- **Next day:** Day 96 — Concurrency and async Basics
  (`labs/sections/programming-with-python/day-096-concurrency-and-async-basics/`).
- **Week 14** — Data Formats and Pipelines: this day supplies the timestamp
  handling every pipeline in the week depends on.
