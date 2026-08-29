# Day 089 lab — Make It Fast

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Indexes and Query Performance
- **Day number:** 89 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-089-indexes-and-query-performance
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-089-indexes-and-query-performance` when the site is running.
<!-- generated-links:end -->

## Purpose

Generate a large table, measure it, index it, and measure it again — and
believe nothing you did not time.

That last clause is the rule of the lab, and it applies to the lab itself.
Everything here is arranged so that you can check the claim rather than
accept it: the data is seeded so your rows are my rows, every timing is a
best-of-seven with its median and spread printed beside it, and every
`EXPLAIN QUERY PLAN` is captured before and after so you can watch the
planner change its mind.

You will do six things:

1. **See the idea without a database.** `scan_vs_bisect.py` finds a value
   in a Python list two ways — walking it, and binary-searching a sorted
   copy — over inputs from a thousand to a million. It counts steps as
   well as timing them, because the step count is the same on every
   machine and the milliseconds are not.
2. **Build something big enough to measure.** 400,000 rows of an
   evaluation log, deterministic and deliberately un-indexed.
3. **Add one index.** The same lookup, before and after, at four table
   sizes. Watch one column grow with the table and the other stay put.
4. **Find out what an index can and cannot serve.** The leftmost-prefix
   rule proved query by query, a covering index that never opens the
   table, an `ORDER BY` that loses its temporary B-tree, and a partial
   index a tenth the size of the full one.
5. **Meet the queries that ignore your index.** A function around the
   column, a leading wildcard, an `OR` with one bare branch — with the
   rewrite for each, and an honest "there is no fix" where there is none.
6. **Pay for it.** The same bulk insert into an unindexed copy and a
   five-index copy, timed. Reads got faster; something had to.

Then you build the measuring tool yourself: `starter/measure.py` has five
numbered exercises, and `starter/indexes.sql` has six.

All 40 checks run offline. No server, no port, no credential, no
third-party package — the standard library and the `sqlite3` shell.

## Learning objectives

- Measure the difference between a scan and a seek at four table sizes,
  and describe the two different shapes the numbers make.
- Read `EXPLAIN QUERY PLAN` correctly, including the trap: `SCAN ... USING
  INDEX` names your index and is still a walk over everything.
- Prove the leftmost-prefix rule query by query rather than quoting it,
  and explain why the order of conditions in `WHERE` is irrelevant while
  the order of columns in the index decides everything.
- Build a covering index and recognise the plan that says the table was
  never opened.
- Remove a sort by giving `ORDER BY` an index that already supplies the
  order.
- Build a partial index, measure how much smaller it is, and find the
  query it will not serve.
- Diagnose the four common reasons a present index goes unused, and apply
  the rewrite or the expression index that fixes each one.
- Measure the write cost of indexes and state the trade in numbers you
  produced.
- Write tests around a measurement that assert shape and direction rather
  than a duration, and say why the alternative is a flaky suite.
- Implement a linear scan and a binary search over the same data and show
  that sorting changed the work and not the answer.

## Prerequisites

- The Day 89 lesson (read it first).
- Day 85: SQLite, the B-tree layer, and the one `EXPLAIN QUERY PLAN`
  output that lesson previewed.
- Day 86: `SELECT` with `WHERE`, `ORDER BY` and `GROUP BY`. Every query
  measured here is one you can already write.
- Day 88: `INSERT` and transactions — the write cost measured today is the
  cost of the statements you learned there.
- A terminal and a text editor. Nothing to install.

## Supported operating systems

- **macOS** — fully supported. Captures taken on macOS 26.5.2 (Apple
  Silicon, arm64), Python 3.14.0, bash 3.2.57, `sqlite3` shell 3.51.0.
- **Linux** — fully supported on any distribution with Python 3.11+, bash
  and the `sqlite3` shell (`sudo apt install sqlite3` on Debian or Ubuntu).
- **Windows** — use WSL and follow the Linux path. On native Windows,
  `tests/run_tests.sh` is a bash script and will not run; the Python and
  SQL files work unchanged, and `expected-output/FIELDS.md` records what
  may legitimately differ rather than guessing at captures never taken.

## Hardware requirements

Any computer that runs Python 3.11 or newer. No GPU.

Disk matters a little today: the main table is about **30 MB** and the
write-cost experiment builds several more databases, the largest about
**35 MB**, all inside a temporary directory that is removed afterwards.
The full suite took about **12 seconds** on the authoring machine.

If space or patience is short, every script takes a row count —
`python3 generate.py events.db 100000`. The shapes still show at 100,000
rows. Below roughly 50,000 they start hiding inside the noise, which is
worth seeing once so you know what "too small to measure" looks like.

## Required software

- `python3`, 3.11 or newer (captures on 3.14.0), with the standard-library
  `sqlite3` module — already there.
- The `sqlite3` command-line shell (captures on 3.51.0).
- `bash` for the test harness — preinstalled on macOS and Linux.

**No packages to install.** See
[`requirements/README.md`](requirements/README.md), which also explains why
the two SQLite version numbers on your machine may differ — and why that
matters slightly more today, since the query planner lives inside the
library.

## Free and open-source options

Everything here is free. SQLite's source is in the **public domain**;
Python and its `sqlite3` module are free under the Python Software
Foundation License; bash is free under the GPL. No account, no tier, no
signup.

Deliberately absent: any benchmarking framework. `timeit` and
`pytest-benchmark` are good tools and both would sit between you and the
thing being measured. `examples/timing.py` is thirty lines of standard
library you can read in a minute, which is the point.

## Installation

```bash
cd labs/sections/programming-with-python/day-089-indexes-and-query-performance
sqlite3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

That is the installation. Read both numbers and note whether they agree —
on the authoring machine they do not, and that is normal.

If the `sqlite3` shell is missing, install it (`sudo apt install sqlite3`
on Debian or Ubuntu) or point the harness at one you have:

```bash
SQLITE=/path/to/sqlite3 PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## File structure

```text
day-089-indexes-and-query-performance/
├── README.md                    ← you are here
├── metadata.yml
├── examples/                    ← the finished work, all runnable
│   ├── scan_vs_bisect.py        ← the idea in plain Python: O(n) against O(log n)
│   ├── generate.py              ← 400,000 seeded rows, deliberately un-indexed
│   ├── timing.py                ← best, median, spread, and the plan helper
│   ├── lookup.py                ← scan against seek at four table sizes
│   ├── composite.py             ← leftmost prefix, covering, ORDER BY, partial, ANALYZE
│   ├── blocked.py               ← five ways to make an index unusable, and the fixes
│   ├── write_cost.py            ← what indexes cost on the way in
│   └── plans.sql                ← the same story in the sqlite3 shell
├── starter/                     ← YOUR work
│   ├── measure.py               ← 5 numbered exercises; names the next one and exits 1
│   └── indexes.sql              ← 6 numbered exercises; applies as shipped
├── tests/
│   └── run_tests.sh             ← 40 behavioural checks, one exit code
├── expected-output/
│   ├── test-run.txt             ← the full harness run
│   ├── scan-vs-bisect.txt       ← steps and microseconds at four sizes
│   ├── generate.txt             ← what the table is
│   ├── lookup.txt               ← the central measurement
│   ├── composite.txt            ← the five index experiments
│   ├── blocked.txt              ← the unusable-index cases
│   ├── write-cost.txt           ← the price of the speed-up
│   ├── plans.txt                ← the shell walkthrough
│   └── FIELDS.md                ← what must match, what may differ — read this
├── requirements/
│   ├── requirements.txt         ← deliberately empty; the note says why
│   └── README.md
├── troubleshooting.md
└── security.md
```

## How to run

Everything runs from this directory. Work in a scratch copy:

```bash
mkdir -p scratch && cp examples/* scratch/ && cd scratch
```

```bash
# 1. The idea, with no database in sight. Watch the steps columns.
python3 scan_vs_bisect.py

# 2. Build something big enough that the difference is unmistakable.
python3 generate.py events.db
ls -l events.db

# 3. The central measurement: one lookup, four table sizes, before and after.
python3 lookup.py events.db

# 4. What an index can and cannot serve.
python3 composite.py events.db

# 5. When the index is there and the planner will not touch it.
python3 blocked.py events.db

# 6. The bill.
python3 write_cost.py

# 7. The same story in the shell, if you prefer reading plans there.
sqlite3 events.db < plans.sql

# 8. Or drive it interactively.
sqlite3 events.db
#   sqlite> .mode box
#   sqlite> EXPLAIN QUERY PLAN SELECT * FROM events WHERE run_id = 200;
#   sqlite> CREATE INDEX ix_run ON events(run_id);
#   sqlite> EXPLAIN QUERY PLAN SELECT * FROM events WHERE run_id = 200;
#   sqlite> .quit

# 9. Your task. Build the measuring tool and the indexes yourself.
cd ../starter
python3 ../examples/generate.py mine.db 200000
sqlite3 mine.db < indexes.sql       # applies as shipped; every plan a scan
python3 measure.py mine.db          # names the next exercise
# ... complete exercises 1-5 in measure.py and 1-6 in indexes.sql ...
```

And the whole thing behind one command, from the lab directory:

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

## What the commands do

- `python3 scan_vs_bisect.py` — finds a value in a sorted list of 1,000,
  10,000, 100,000 and 1,000,000 elements, by walking it and by
  binary-searching it. Prints microseconds **and counted steps**; the
  steps are identical on every machine and are the honest half of the
  comparison. Raises if the two ever return different answers.
- `python3 generate.py events.db [rows]` — builds the table from a
  `random.Random(20260816)` seed, so two runs produce identical data.
  Reports rows, pages, file size, and that there are no indexes yet.
- `python3 lookup.py events.db` — the central measurement. Builds tables of
  25,000, 100,000, 200,000 and 400,000 rows, times the same lookup with and
  without an index on `run_id`, captures both plans, checks the two results
  are identical, reports the index's page cost, then **drops the index and
  re-times the scan** so you can see the first scan figures were not a
  cold-cache artefact.
- `python3 composite.py events.db` — five experiments: the leftmost-prefix
  rule across four query shapes; a covering index; an `ORDER BY` losing its
  temporary B-tree; a partial index with its page cost and the query it
  will not serve; and `ANALYZE` with the contents of `sqlite_stat1`.
- `python3 blocked.py events.db` — a function around the column, an
  expression, a leading wildcard, a trailing wildcard, and an `OR` across
  two columns. Each with its plan, its timing, and its fix where one
  exists.
- `python3 write_cost.py` — builds two identical 100,000-row tables, gives
  one of them five indexes, inserts the same further 100,000 rows into
  each, three trials apiece. Reports time and file size.
- `sqlite3 events.db < plans.sql` — the same material as `EXPLAIN QUERY
  PLAN` output in the shell, in `.mode box`. Tidies up after itself.
- `bash tests/run_tests.sh` — all 40 checks in eleven sections, on copies
  in a temporary directory. Exits 0 on success, non-zero on any failure.

## Expected output

The harness ends like this — a real captured run; see
[`expected-output/test-run.txt`](expected-output/test-run.txt) for all of
it:

```text
11. Nothing here reaches the network or needs anything installed
  ok: no executable lab file contains a network address of any kind
  ok: no lab file imports a third-party package — standard library only
  ok: every database this run created lives under a temporary directory

40 checks, 0 failure(s).
```

The central measurement
([`expected-output/lookup.txt`](expected-output/lookup.txt)):

```text
     rows |  scan best |  seek best |   faster |  scan median |  seek median | matched
--------------------------------------------------------------------------------------
   25,000 |       0.31 |      0.028 |      11x |         0.31 |        0.028 |     100
  100,000 |       1.96 |      0.027 |      73x |         2.06 |        0.028 |     100
  200,000 |       4.13 |      0.028 |     149x |         4.16 |        0.029 |     100
  400,000 |       8.41 |      0.027 |     309x |         8.47 |        0.029 |     100
```

Read the columns, not the digits. **Those milliseconds are from one machine
on one day and yours will differ.** What travels is that the scan column
roughly doubles as the table doubles while the seek column does not move,
and that `matched` is 100 every time: the index changed the work and never
the answer.

The same shape without a database
([`expected-output/scan-vs-bisect.txt`](expected-output/scan-vs-bisect.txt)),
where the step counts are machine-independent:

```text
          n |   scan us | bisect us |   faster |  scan steps | bisect steps | log2(n)
-------------------------------------------------------------------------------------
      1,000 |      6.05 |     0.131 |      46x |         494 |         10.0 |    10.0
  1,000,000 |   7978.41 |     1.027 |    7768x |     605,052 |         19.9 |    19.9
```

The leftmost-prefix rule, one index on `(run_id, status)`
([`expected-output/composite.txt`](expected-output/composite.txt)):

```text
  b) the leading column alone     WHERE run_id = ?
    plan : [SEEK] SEARCH events USING COVERING INDEX ix_run_status (run_id=?)
  c) the trailing column alone    WHERE status = ?
    plan : [SCAN] SCAN events USING COVERING INDEX ix_run_status
```

Note that (c) names the index and is still a scan. That is the reading
mistake this lab exists to prevent.

And the bill
([`expected-output/write-cost.txt`](expected-output/write-cost.txt)):

```text
configuration    | indexes |   best ms |  median ms |  worst ms
---------------------------------------------------------------
bare             |       0 |      53.9 |       54.0 |      54.1
indexed          |       5 |     632.3 |      642.5 |     658.4
```

[`expected-output/FIELDS.md`](expected-output/FIELDS.md) states exactly
which values must be identical on your machine and which are expected to
differ. **Read it before concluding anything is wrong.**

## Validation steps

1. `bash tests/run_tests.sh` ends with `40 checks, 0 failure(s).` and
   exits 0.
2. `python3 scan_vs_bisect.py` reports bisect steps of about 10, 13, 17 and
   20 against `log2(n)` of 10.0, 13.3, 16.6 and 19.9 — those are counted,
   so they must match.
3. `python3 lookup.py events.db` prints `matched` = 100 at all four sizes,
   the scan column growing with the table and the seek column roughly flat.
4. The plan before the index contains `SCAN events`; after it, `SEARCH
   events USING INDEX ix_events_run (run_id=?)`.
5. In `composite.py`, the composite index seeks for `run_id` alone and for
   both columns, and **scans** for `status` alone.
6. `SELECT score FROM events WHERE run_id = ?` reports `COVERING INDEX`
   once the index is `(run_id, score)`.
7. `USE TEMP B-TREE FOR ORDER BY` is present without an index on
   `created_on` and absent with one.
8. The partial index costs 186 pages against the full index's 1,857, and
   is not used for the same date range without `status = 'failed'`.
9. In `blocked.py`, `lower(trace_id) = ?` scans; the expression index makes
   it seek; the leading wildcard scans; the range rewrite seeks and returns
   the same rows.
10. `python3 write_cost.py` reports the five-index insert as several times
    slower and the file as several times larger.
11. `python3 measure.py mine.db` exits non-zero and names the next exercise
    until all five are done.
12. After the harness, `find . -name "*.db"` inside the lab finds nothing.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `40 checks, 0 failure(s).` The command exits 0 on
success and non-zero on any failure.

**This suite is a lesson about testing measurements, and it is worth
reading before you run it.** There is one rule:

> No check asserts a millisecond figure. Not a floor, not a ceiling, not a
> range.

A test that says "the indexed lookup takes under 0.05 ms" passes on the
machine it was written on and fails on a busy laptop, a slower disk, a CI
container, or the same machine next year. It would not be measuring the
lab; it would be measuring the computer, and it would go red for reasons
nobody can act on. That is how test suites become things people ignore.

So every check asserts a **shape** instead: the plan changed from `SCAN` to
`SEARCH`; the two results contain exactly the same rows; the indexed lookup
is at least **20x** faster; inserting with five indexes is at least **1.5x**
slower; the composite index serves these shapes and cannot serve that one.
The two ratio thresholds sit far below what this machine measured — 20x
against roughly 300x, 1.5x against roughly 12x — so a slow machine still
passes while a broken lab still fails. Assert the direction and an order of
magnitude; never the number.

Section 2 is worth reading for a different reason: it builds the same table
twice and requires the two to be identical, because a lab about
reproducible measurement has to start with reproducible data.

## Cleanup

```bash
rm -rf scratch
rm -f starter/mine.db starter/events.db
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
git checkout -- starter/          # optional: reset your work
```

A SQLite database is one ordinary file, and today's are large — check with
`du -sh .` afterwards if you like. Deleting them removes them completely.
If you see `events.db-journal` or `events.db-wal` beside one, those belong
to the same database and go with it.

`tests/run_tests.sh` makes its own temporary directory with `mktemp -d` and
removes it in a `trap`, so a completed run leaves nothing behind — and one
of its checks asserts exactly that.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md). The four you are most likely
to meet: your numbers not matching the captures (expected — read
`expected-output/FIELDS.md`); a plan that names your index and is still a
`SCAN` (read the first word, not the index name); an index that changed
nothing (a function around the column, the wrong leading column, a leading
wildcard, or one bare branch of an `OR`); and a difference too small to
see, which is nearly always a table too small or a machine too busy — look
at the `spread` figure.

## Security notes

See [security.md](security.md). The one that is specific to today: **an
index is a copy of your data.** `CREATE INDEX ix_email ON members(email)`
writes every address into a second sorted structure in the same file, so
scrubbing a column is not enough if an index over it survives, a partial
index is a tidy list of exactly the rows it covers, and an expression
index stores whatever the expression computed. Retention policies apply to
indexes. Beyond that: values as parameters, never string-built SQL;
parameters cannot name identifiers, so validate any runtime column name
against an allow-list; and never let untrusted input trigger a `CREATE
INDEX`. This lab needs no credential, opens no port, reaches no network
and needs no `sudo`.

## Extension exercises

1. **Find the crossover.** At what table size does the index stop being
   worth measuring? Run `lookup.py` down through 1,000, 5,000 and 10,000
   rows and find the size at which the difference disappears into the
   spread. Write down that number and what it tells you about optimising
   small tables.
2. **Make the planner refuse a perfectly good index.** Build an index on
   `status`, which has three distinct values, and query `WHERE status =
   'ok'`. Run `ANALYZE`, look at `sqlite_stat1`, then explain in one
   sentence why reading the whole table is genuinely the cheaper plan —
   and find the selectivity at which the planner changes its mind by
   editing the data rather than the query.
3. **Widen an index until it covers.** Take a query the plan answers with
   `SEARCH events USING INDEX`, add columns to the index one at a time, and
   find the moment the plan says `COVERING INDEX`. Then measure what that
   cost you in pages and in insert time. Is it worth it? Show your working.
4. **Break the leftmost-prefix rule on purpose.** Build `(status, run_id)`
   instead of `(run_id, status)` and re-run the four queries from
   `composite.py`. Two plans should swap. Predict which two before you run
   it.
5. **Index the wrong thing and pay for it.** Add eight indexes to the
   table, none of which any query uses, then re-run `write_cost.py`-style
   timings. You now have a number for the cost of an index nobody asked
   for — the cost that never appears in the timings people look at.
6. **Take on a leading wildcard properly.** `WHERE trace_id LIKE '%072'`
   cannot use an ordinary index. Build a generated or manually maintained
   column holding the reversed string, index that, and rewrite the query
   against it. Measure. Then read about FTS5 and write a paragraph on when
   you would use it instead.
7. **Test a measurement badly, on purpose.** Add a check to a copy of
   `run_tests.sh` that asserts the indexed lookup takes under 0.05 ms. Run
   it while compiling something large in another window. Watch it fail for
   a reason that has nothing to do with the lab. Then delete it, and you
   will never write one again.

## Navigation

- **Previous day:** Day 88 — inserting, updating and schema design
  (`labs/sections/programming-with-python/day-088-inserting-updating-and-schema-design/`).
  The write cost measured today is the cost of the statements from that
  lab.
- **Next day:** Day 90 — the week's closing work
  (`labs/sections/programming-with-python/`).
- **This week:** Week 13, SQL and Relational Databases. Day 85 previewed
  one `EXPLAIN QUERY PLAN` output and promised an explanation; this is it.
