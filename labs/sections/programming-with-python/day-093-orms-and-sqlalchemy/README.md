# Day 093 lab — See What the ORM Does

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** ORMs and SQLAlchemy
- **Day number:** 93 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-093-orms-and-sqlalchemy
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-093-orms-and-sqlalchemy` when the site is running.
<!-- generated-links:end -->

## Purpose

You never take the ORM's word for anything in this lab. Every exercise is
validated by looking at the SQL it emitted.

That constraint is the whole design. An object-relational mapper's promise is
that you write Python and it writes SQL, and the only way to hold it to that
promise is to read the SQL. Two lines of Python that look identical can cost
one query or fifty-one, and nothing in the source hints at the difference. So
this lab hands you an instrument — a statement counter built on SQLAlchemy's
`before_cursor_execute` event — and every test asserts on what came out of it.

You build the mapper yourself first. `examples/tiny_orm.py` is a working ORM
in about a hundred and sixty lines: columns declared as class attributes, DDL
and DML generated from that declaration, rows mapped back into objects, and an
identity map so the same row fetched twice yields the *same* Python object.
Once you have written the toy, SQLAlchemy stops being magic and becomes a much
more careful version of code you already understand — and the Session stops
being a mystery, because you built one.

Then the same library domain from Week 13, mapped with SQLAlchemy 2.0
declarative models, and five things measured rather than asserted: the four
object states, flush against commit, the N+1 problem, `DetachedInstanceError`,
and where the ORM stops being the right tool.

**A note on what is being asserted.** Almost every check in this lab is on a
*count of statements*, never on a duration. That is a transferable testing
lesson and it is worth stating plainly: a timing assertion is a flake waiting
for a loaded machine, and it names no cause. "This took 240 milliseconds" is a
mood. "This loop issued seven queries where two would do" is a bug report you
can act on, it is identical on every machine, and it fails the moment somebody
reintroduces the defect.

An ORM is **not** a way to avoid learning SQL. This day only works because you
spent Week 13 writing SQL by hand — every emitted statement you are about to
read is a statement you could have written yourself, and knowing that is what
lets you judge whether the one the ORM chose was any good.

## Learning objectives

By the end of this lab you will be able to:

1. Build a minimal ORM from first principles — column descriptors, generated
   `CREATE TABLE`/`INSERT`/`SELECT`, row-to-object mapping, and an identity
   map — and explain what each piece is for.
2. Instrument a SQLAlchemy engine so that every statement it emits is
   recorded, and assert on the count in a test.
3. Declare SQLAlchemy 2.0 models with `DeclarativeBase`, `Mapped` and
   `mapped_column`, including a one-to-many and a many-to-many through a
   secondary table.
4. Name which of the four states — transient, pending, persistent, detached —
   a mapped object is in, by inspecting it rather than by guessing.
5. Distinguish `flush()` from `commit()` by observing when the INSERT is sent
   and when another connection can see the row.
6. Demonstrate the N+1 problem by counting queries, then fix it with
   `selectinload` and with `joinedload`, and say which to use when.
7. Provoke `DetachedInstanceError` on a column and on a relationship, and fix
   each with the right one of two different remedies.
8. Decide when to drop from the ORM to Core, and state the price you pay.

## Prerequisites

- **Day 85–91** — the relational model, `SELECT`, joins, constraints,
  indexes, SQLite from Python, and schema design. This lab's tables are the
  Day 91 library, and every emitted statement is one you could have written by
  hand.
- **Day 90** — parameter binding and the repository pattern. The ORM binds
  parameters by construction; you will recognise every `?` in the output.
- **Day 43** — `python3 -m venv`. The install below is the same pattern.
- **Days 71–74** — pytest. The starter exercises use it, pointed at statement
  counts instead of return values.
- **Day 60-ish object-oriented Python** — classes, class attributes, and
  `__set_name__` if you want to follow the toy ORM's descriptor trick closely
  (it is explained inline either way).

## Supported operating systems

- **macOS** — exercised here; every capture in `expected-output/` comes from
  macOS 26.5.2 on Apple Silicon.
- **Linux** — expected to behave identically with Python 3.11 or newer. Not
  run here, so no capture is claimed for it.
- **Windows** — use WSL and follow the Linux path. `tests/run_tests.sh` is a
  bash script and uses `mktemp -d`; it was not run on native Windows and no
  behaviour is claimed for it there. The Python files themselves use `pathlib`
  and `tempfile` and have no Unix dependency.

## Hardware requirements

Nothing notable. Every database is in memory or a few kilobytes in a temporary
directory. The largest thing this lab builds is a thousand rows, which SQLite
handles without noticing. No GPU, no minimum RAM worth stating.

## Required software

- `python3` 3.11 or newer (3.14.0 here).
- `SQLAlchemy` 2.0.51 and `pytest` 9.1.1, both pinned in
  `requirements/requirements.txt` and both installed into a lab-local `.venv`.
- `bash` for the test harness (3.2.57 here — the version macOS ships).

SQLite arrives with Python; there is nothing to install for it.

**Not used here:** Alembic, SQLAlchemy's migration tool, is not installed. The
lesson describes it from its documentation and says plainly that no output is
reproduced for it. Section 1 of the test suite checks the claim is still true.

## Free and open-source options

Everything in this lab is free and open source, and there is no paid tier of
anything to be aware of.

| Tool | Licence | Cost | Note |
| --- | --- | --- | --- |
| SQLAlchemy | MIT | Free | The library the day is about. Both Core and the ORM ship together; there is no commercial edition. |
| pytest | MIT | Free | The runner from Week 11. |
| SQLite | Public domain | Free | Arrives with Python. Nothing to install, no server to run. |
| Python | PSF licence | Free | 3.11 or newer. |

If you want to try the same models against a different database, PostgreSQL
and MySQL are both free and open source and both have SQLAlchemy dialects.
Nothing in this lab was run against either, so no behaviour is claimed for
them.

## Installation

```bash
cd labs/sections/programming-with-python/day-093-orms-and-sqlalchemy
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

Expect `2.0.51`. The install needs the network once. **Nothing after it
does** — see "Security notes" below, where the guard that enforces that is
described.

## File structure

```
day-093-orms-and-sqlalchemy/
├── README.md                      this file
├── metadata.yml                   lab metadata and the recorded run
├── security.md                    what this lab touches; SQL injection and an ORM
├── troubleshooting.md             every error you are likely to hit, by cause
├── requirements/
│   ├── README.md                  why each pin exists, and what is deliberately absent
│   └── requirements.txt           SQLAlchemy==2.0.51, pytest==9.1.1
├── examples/
│   ├── tiny_orm.py                a working ORM in ~160 lines — read this FIRST
│   ├── models.py                  the same domain in SQLAlchemy 2.0 declarative style
│   ├── library.py                 one engine, one schema, one fixed seed
│   ├── counting.py                the instrument: every statement, recorded
│   ├── demo_toy.py                the toy ORM doing the four things an ORM does
│   ├── demo_sqlalchemy.py         the same four operations, in the real library
│   ├── demo_unit_of_work.py       states, autoflush, flush vs commit, detached
│   ├── demo_n_plus_one.py         the N+1, counted, then fixed two ways
│   └── demo_bulk.py               where the ORM stops being the right tool
├── starter/
│   ├── queries.py                 your work: nine numbered exercises
│   ├── test_queries.py            1 passing, 9 skipped — each names its exercise
│   ├── conftest.py                import path plus the offline guard
│   └── pytest.ini                 SQLAlchemy warnings are errors here
├── tests/
│   └── run_tests.sh               87 checks — the harness
└── expected-output/
    ├── FIELDS.md                  what must match and what may differ
    ├── toy.txt                    captured from a real run
    ├── sqlalchemy.txt             captured from a real run
    ├── unit-of-work.txt           captured from a real run
    ├── n-plus-one.txt             captured from a real run
    └── bulk.txt                   captured from a real run
```

## How to run

Read and run them in this order. The order matters — the toy exists so the
real library's vocabulary is already familiar when you meet it.

```bash
cd labs/sections/programming-with-python/day-093-orms-and-sqlalchemy
export PYTHONPATH=examples

# 1. The ORM you could have written yourself
.venv/bin/python3 examples/demo_toy.py

# 2. The same four operations in SQLAlchemy 2.0
.venv/bin/python3 examples/demo_sqlalchemy.py

# 3. The Session as a unit of work: states, autoflush, flush vs commit, detached
.venv/bin/python3 examples/demo_unit_of_work.py

# 4. The N+1 problem, counted and then fixed
.venv/bin/python3 examples/demo_n_plus_one.py

# 5. Where the ORM stops being the right tool
.venv/bin/python3 examples/demo_bulk.py

# 6. Your turn
.venv/bin/pytest starter -q

# 7. The whole suite
bash tests/run_tests.sh
```

Then work through `starter/queries.py`. Nine exercises, each named by a
skipped test in `starter/test_queries.py`. Do the exercise, delete that test's
`@pytest.mark.skip` line, rerun.

## What the commands do

| Command | What it does | What to look at |
| --- | --- | --- |
| `demo_toy.py` | Builds a session, a schema and four objects using only `sqlite3` and about 160 lines of your own ORM | Step 5: two lookups of the same row return the *same object* and emit **zero** statements |
| `demo_sqlalchemy.py` | Repeats the toy's numbered steps in SQLAlchemy 2.0, printing every emitted statement beside the Python that produced it | Steps 6 and 7: the `select()` and the SQL it compiled to, side by side |
| `demo_unit_of_work.py` | Walks one object through four states, separates flush from commit using a second connection, provokes autoflush, and raises `DetachedInstanceError` twice | Step 2: the INSERT is sent, and an outside connection still sees 7 members until the commit |
| `demo_n_plus_one.py` | Counts the statements of a lazy loop, a `selectinload` and a `joinedload`, then shows why one statement is not automatically the winner | The scoreboard: **7**, **2**, **1** — and then the 24 rows the JOIN really returned |
| `demo_bulk.py` | Compares a flush per row, a batched flush, and Core, on both inserts and updates | Section 4, which contradicts the folklore, and section 6, which says where Core actually wins |
| `pytest starter -q` | Runs your exercise suite | `1 passed, 9 skipped` before you start |
| `bash tests/run_tests.sh` | Everything, including a byte-for-byte comparison against the captures | The final line |

## Expected output

Every file in `expected-output/` was captured from a real run on 2026-08-16
and is compared byte for byte by section 8 of the harness. The numbers that
carry the lesson:

**The identity map, from `toy.txt`:**

```
5. The identity map: the same row is the same object
----------------------------------------------------
first is second      : True
first is ada         : True
statements emitted   : 0
```

**Flush is not commit, from `unit-of-work.txt`:**

```
after flush, other connection sees : 7 members, last 'Grace Mensah'
  The INSERT was sent. The transaction is open. Nobody else can see it.
after commit, other connection sees: 8 members, last 'Hana Ito'
```

**The N+1 scoreboard, from `n-plus-one.txt`:**

```
    lazy (default)    7 statements   <- 1 + N
    selectinload      2 statements   <- 1 + 1, whatever N is
    joinedload        1 statement    <- 1, but wider rows
```

**And the number that contradicts the received wisdom, from `bulk.txt`:**

```
    add() + flush() per row    500 execution(s)    500 row(s)
    add_all() + one flush        1 execution(s)    500 row(s)
    Core insert(), one call      1 execution(s)    500 row(s)
```

A batched ORM insert costs the *same* number of cursor executions as Core on
this version. "Drop to Core for bulk inserts, it is far fewer queries" is not
what the counter shows. The dramatic gap is between the naive loop and
everything else, and it is entirely about whether the `flush()` is inside the
loop. `expected-output/FIELDS.md` and section 6 of the demo both say so at
length, and section 5 of the demo shows where Core *does* genuinely win: a
bulk `UPDATE`, where the ORM must build one Python object per matching row and
Core builds none.

The harness ends with:

```
87 checks, 0 failure(s).
```

## Validation steps

1. **The install is the version the lab claims.**
   `.venv/bin/python3 -c "import sqlalchemy; print(sqlalchemy.__version__)"`
   prints `2.0.51`, matching `requirements/requirements.txt`.
2. **Every demo exits 0.** Run all five from "How to run". Any traceback is a
   setup problem — see `troubleshooting.md`.
3. **The captures still match.** `bash tests/run_tests.sh` compares all five
   byte for byte. A diff means something changed in `examples/`.
4. **The starter baseline is green.** `.venv/bin/pytest starter -q` reports
   `1 passed, 9 skipped` before you have written anything.
5. **Your work is measured, not assumed.** Each exercise's test asserts a
   statement count. If it passes, the ORM really did what you think it did.
6. **The lab left nothing behind.** After the run, `find . -name '*.db' -not
   -path '*/.venv/*'` and `find . -type d -name __pycache__ -not -path
   '*/.venv/*'` are both empty. The harness checks this too.

## Tests

```bash
bash tests/run_tests.sh
```

87 checks in nine sections: the environment and the pinned version; the toy
ORM; SQLAlchemy's declarative models and emitted SQL; the Session as a unit of
work; the N+1 problem; bulk work; the starter skeleton; the captured output;
and hygiene.

The harness **resolves its tools** — `$PYTHON` and `$PYTEST` override first,
then `./.venv/bin/<tool>`, then whatever is on `PATH` — and **fails loudly
with install instructions rather than skipping silently** if SQLAlchemy is not
importable. A suite that quietly skips the only thing it was written to test
is worse than one that fails.

Two checks are worth knowing about because they are unusual:

- **Section 1 asserts that Alembic is *not* installed.** The lesson says
  plainly that no Alembic output is reproduced. If somebody installs it here,
  that statement stops being the whole truth, and the suite fails rather than
  letting the text go quietly stale.
- **Section 9 trips the network guard on purpose.** `starter/conftest.py`
  replaces `socket.create_connection`; the harness calls it and asserts the
  refusal, because a guard nobody tests is a guard nobody can trust.

This harness has been proved to fail. Removing the `selectinload` from
`examples/demo_n_plus_one.py` and rerunning reports:

```
  FAIL: selectinload costs exactly 2, whatever N is
  FAIL: expected-output/n-plus-one.txt differs from this run
87 checks, 2 failure(s).
```

with a non-zero exit status — caught twice, once by the count and once by the
capture.

## Cleanup

```bash
cd labs/sections/programming-with-python/day-093-orms-and-sqlalchemy
find . -type d -name '__pycache__' -not -path './.venv/*' -prune -exec rm -rf -- {} +
rm -rf starter/.pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: reset your exercise work
```

There is no database to delete. Every one this lab builds is either in memory
or inside a temporary directory that its own script removes —
`demo_unit_of_work.py` prints `temporary database removed: True` as proof
rather than as a promise.

## Troubleshooting

`troubleshooting.md` covers every error you are likely to hit, organised by
cause: the environment, the session, the query count, and the tests. The three
you are most likely to meet:

- **`DetachedInstanceError`** — read the rest of the message. "attribute
  refresh operation cannot proceed" and "lazy load operation of attribute"
  are two different problems needing two different fixes, and applying the
  wrong one is the classic wasted afternoon.
- **`InvalidRequestError: The unique() method must be invoked`** — you used
  `joinedload` on a collection. The JOIN really does return one row per child.
- **SQL appearing at a line where you wrote no query** — that is autoflush.

## Security notes

`security.md` has the full treatment. The short version:

- The lab needs the network exactly once, to install two packages. Nothing
  else does, and `starter/conftest.py` arms a guard that raises if anything
  tries — a guard the harness trips deliberately to prove it works.
- **The ORM parameterises everything you express through it.** Every `?` in
  the captured output is the proof. It does *not* protect `text()` with
  string-concatenated SQL, and it cannot bind an identifier — a user-chosen
  sort column must be validated against an allow-list you control.
- **The N+1 problem is a denial-of-service vector**, not only a performance
  bug: an endpoint that lazily loads per result lets a client control how many
  queries your database runs.
- **`echo=True` prints your data to the log.** Best learning tool in the
  library; never leave it on in a deployed service. The `QueryCounter` here
  records statement text and parameter *counts* only, never the values.
- Every name and email in the seed is invented and uses the reserved
  `library.test` domain, which can never resolve.

## Extension exercises

1. **Give the toy ORM an `update()`.** It can insert and select; it cannot yet
   write a change back. Track which attributes were modified since load and
   emit an `UPDATE` naming only those columns. You have just written dirty
   tracking, which is the part of the unit of work this lab did not build.
2. **Give the toy ORM a relationship.** A `loans` attribute on the toy
   `Member` that issues its own `SELECT` on first access — and then watch your
   own N+1 appear in the statement log. Fixing it teaches more than reading
   about `selectinload`.
3. **Break `joinedload` on purpose.** Give a member 200 loans and compare the
   bytes returned by `joinedload` against `selectinload` for the same result.
   The row multiplication the lesson describes becomes a number you measured.
4. **Count queries in a test you already have.** Take any Day 90 or Day 91
   code and wrap a `QueryCounter` around it. The habit — not the library — is
   the transferable skill.
5. **Turn `echo=True` on and read every line of `demo_n_plus_one.py`.** The
   lab counts statements; `echo` shows them in full with their parameters.
   Doing both once is how the counting stops feeling abstract.
6. **Try a different loader strategy.** `lazy="selectin"` on the
   `relationship()` itself makes eager loading the default for that
   relationship everywhere, instead of a per-query decision. Measure what that
   does to the counts, and form an opinion about which you would rather debug.

## Navigation

- **This lab:** Day 93 — ORMs and SQLAlchemy
  (`labs/sections/programming-with-python/day-093-orms-and-sqlalchemy/`).
- **Previous day:** Day 92 — Beyond Tables: NoSQL and Key-Value Stores
  (`labs/sections/programming-with-python/day-092-beyond-tables-nosql-and-key-value/`).
- **Next day:** Day 94
  (`labs/sections/programming-with-python/`), which continues Week 14's work on
  data formats and pipelines.
- **Week 14 — Data Formats and Pipelines**, inside Programming with Python →
  Data and Databases. The tables mapped here are the schema designed on Day 91,
  which is why every emitted statement is one you could have written by hand.
