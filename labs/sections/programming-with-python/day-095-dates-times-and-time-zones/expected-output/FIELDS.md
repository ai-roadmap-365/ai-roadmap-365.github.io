# What must match, and what may differ

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
bash 3.2.57, and the IANA time zone database version **2026c** found at
`/usr/share/zoneinfo`, offering **598** zones.

That last line is the one to read carefully, because this lab's subject is a
database that is updated several times a year. Zone rules are data. If your
`+VERSION` file says something other than 2026c, your zone count will differ
from 598 and one or two historical answers may differ too. Every value in the
"must match" table below is a 2026 transition that has been published for
years, so it should hold on any database from the last several releases — and
if one of them does not hold on yours, your database is the authority and this
capture is the stale one. Run `python3 examples/01_zone_database.py` and see
what you have.

## Must match exactly, on any machine

These are values, not formatting, and a difference means something is wrong —
either in your code or in your zone database.

| Value | Where | Must be |
| --- | --- | --- |
| Europe/London 2026-03-29 | `odd-days.txt` | 23.0 hours |
| Europe/London 2026-10-25 | `odd-days.txt` | 25.0 hours |
| Europe/London 2026-06-15 | `odd-days.txt` | 24.0 hours |
| America/New_York 2026-03-08 / 2026-11-01 | `odd-days.txt` | 23.0 and 25.0 |
| Australia/Lord_Howe 2026-10-04 | `test-run.txt` | 23.5 — the half-hour step |
| Wall-clock length of every day | `odd-days.txt` | 24.0, including the two that are not |
| 2026-10-25 01:30 London, fold=0 | `fold.txt` | offset +01:00, BST, `2026-10-25T00:30:00+00:00`, epoch 1792888200 |
| 2026-10-25 01:30 London, fold=1 | `fold.txt` | offset +00:00, GMT, `2026-10-25T01:30:00+00:00`, epoch 1792891800 |
| `fold=0 == fold=1` on the ambiguous reading | `fold.txt` | **True** — the comparison trap |
| Their UTC instants compared | `fold.txt` | **False** — an hour apart |
| 2026-03-29 01:30 London round trip | `fold.txt` | comes back as `2026-03-29T02:30:00+01:00` |
| Firings of a local-01:30 schedule | `fold.txt` | **2** on 25 October, **0** on 29 March |
| UTC ISO text sort vs instant sort | `sorting.txt` | identical |
| Local text sort of the four events | `sorting.txt` | `checkout, dispatch, ordered, packed` — the exact reverse of the true order |
| Local text *with* offsets | `sorting.txt` | also wrong: `same order? False` |
| The two 01:30 local strings | `sorting.txt` | identical, from two instants an hour apart |
| `%Z` parsing "BST" | `sorting.txt` | ValueError |
| `%Z` parsing "UTC" | `sorting.txt` | succeeds, and `tzinfo` is `None` |
| `05/03/2026` two ways | `sorting.txt` | 2026-03-05 and 2026-05-03 |
| 31 Jan + `timedelta(days=30)` | `sorting.txt` | 2026-03-02 |
| `datetime(..., second=60)` | `clocks.txt` | ValueError: second must be in 0..59 |
| `2**31 - 1` as an instant | `clocks.txt` | `2038-01-19T03:14:07+00:00` |
| Wall stopwatch across the repeated hour | `clocks.txt` | reports 0:15:00 for 1:15:00 of work |
| Wall stopwatch ending after the change | `clocks.txt` | reports `-1 day, 23:20:00` — a negative duration |
| Resolver agreement | `resolver.txt` | 26 comparisons, **0 disagreements, 0 misclassified** |
| Starter before | `starter-progress.txt` | `0 of 10 exercises complete.`, exit 1 |
| Reference answers | `starter-progress.txt` | `10 of 10 exercises complete.`, exit 0 |
| Harness total | `test-run.txt` | `75 checks, 0 failure(s).`, exit 0 |

## Expected to differ on your machine

- **The zone count and the database version** in `zone-database.txt` and in
  the `test-run.txt` banner. 598 zones and version 2026c is what this machine
  had. The suite only requires more than 100, because a database with fewer
  than that is not a real one.
- **The `TZPATH` listing.** On this macOS machine only `/usr/share/zoneinfo`
  exists; on Linux you may see `/usr/share/zoneinfo` and `/etc/zoneinfo` both
  present. On Windows there is usually no system database at all and
  `zoneinfo` falls back to the `tzdata` package — see the platform notes.
- **The two measured timings in `clocks.txt`.** `time.time() measured ...` and
  `time.monotonic() measured ...` are a real measurement of real work on this
  processor and will differ on yours. Nothing asserts on them. What the suite
  asserts is that both are positive and that monotonic never decreases across
  20,000 samples — a shape, not a duration.
- **The clock resolutions and implementations in `clocks.txt`.**
  `mach_absolute_time()` is macOS; Linux reports `clock_gettime(CLOCK_MONOTONIC)`.
  The `monotonic`/`adjustable` columns are what matters, and those are the
  same everywhere.
- **The `%c` and `%x` lines in `sorting.txt`**, which follow the C locale. On
  this machine `LC_TIME` was `C`. A machine with a different locale prints
  different text, and that is the entire point being made there.
- **The 1968 and 1971 boundary instants** printed by `zone-database.txt`. They
  came out of the database by bisection, so a database that records them
  differently will print differently. On this one they were
  `1968-02-18T02:00:00+00:00` and `1971-10-31T02:00:00+00:00`.

## Deliberately stable, and why

Not one value in this lab depends on when you run it. Every instant is written
out in the source: `datetime(2026, 10, 25, 1, 30)`, `datetime(2026, 3, 29, 1,
0, tzinfo=UTC)`, and so on. That is not a testing convenience — it is the
subject. A suite that used `datetime.now()` would pass on 363 days of the year
and fail on the two the material is about, which is precisely the failure
schedule that makes these bugs survive to production.

The one place a clock is read at all is `measure_elapsed` and the timing
demonstration in `05_clocks.py`, and there the assertions are on shape
(positive, non-decreasing) rather than on any number of seconds.

## Platform notes

- **Linux** — identical output expected, given Python 3.11+ and a system
  `tzdata` package. The clock implementation strings differ as noted above.
- **Windows** — Windows ships no IANA database, so `zoneinfo` needs the
  `tzdata` package from PyPI before `ZoneInfo("Europe/London")` will load. Use
  WSL and follow the Linux path; `tests/run_tests.sh` and `starter/02_check.sh`
  are bash scripts and were not run on native Windows here, so no output is
  claimed for it.
