# Day 085 lab — Your First Database

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Relational Databases and SQLite
- **Day number:** 85 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-085-relational-databases-and-sqlite
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-085-relational-databases-and-sqlite` when the site is running.
<!-- generated-links:end -->

## Purpose

Yesterday you shipped a toolkit that kept its state in a JSON file, written
atomically. That was the right call. In this lab you find out precisely where
it stops being the right call, by measuring it — and then you build the thing
that replaces it, from an empty directory to a working database, in one
sitting.

You will do four things, in this order:

1. **Make the file fail.** `json_pain.py` measures four costs on your own
   machine: the bytes rewritten to change one field, the typo'd member id that
   nothing rejects, two writers who both "succeed" while one update vanishes,
   and the full parse-and-scan that answering "which loans are overdue?" costs.
   Real numbers, not an argument.
2. **Build a database.** A schema for `books`, `members` and `loans`, seeded in
   one transaction, then proven to be one ordinary file — you read the first
   sixteen bytes of the header yourself and confirm they are the documented
   magic string.
3. **Write the query engine, then throw it away.** `table_scan.py` implements
   `WHERE`, the column list and `ORDER BY` by hand over a list of dicts. Then
   `scan_vs_sql.py` runs your loop and the equivalent `SELECT` and asserts the
   results are identical, row for row, in order. That assertion is the whole
   lesson: SQL is your loop, written by somebody else.
4. **Ask the question the file could not answer.** One `SELECT`, three tables,
   three overdue borrowers, and you never said how to find them.

Along the way you meet the two things about SQLite that surprise everybody:
its typing is dynamic (a `TEXT` value will sit happily in a column you declared
`INTEGER`, and no comparison will ever match it), and its foreign keys are off
until you turn them on.

All 44 checks run offline. There is no server, no port, no credential, and no
third-party package — the standard library and the `sqlite3` shell, nothing
else. The suite checks that mechanically.

## Learning objectives

- Measure, rather than assert, the four points at which a JSON file stops being
  an adequate store: whole-file rewrites, absent constraints, lost updates, and
  a question that costs a full scan.
- Write a schema as a promise the engine keeps, using `PRIMARY KEY`,
  `NOT NULL`, `UNIQUE`, `CHECK` and `REFERENCES`, and see each one refuse a
  bad write.
- Turn `PRAGMA foreign_keys` on, and see the identical write accepted when it
  is off — the rule is opt-in, per connection.
- Prove a database is one ordinary file by reading its header bytes and
  checking that page size times page count equals the file length.
- Implement `restrict`, `project` and `order_by` from first principles, and
  assert mechanically that the SQL returns exactly what they do.
- Demonstrate SQLite's dynamic typing and type affinity, then fix it with a
  `STRICT` table and watch the same insert be refused.
- See atomicity for yourself: `ROLLBACK` undoing both halves of a two-statement
  transaction, from the shell and from Python.
- Pass a hostile value as a parameter and understand why that ends SQL
  injection.
- Read both SQLite version numbers on your machine and explain why they are
  allowed to differ.

## Prerequisites

- The Day 85 lesson (read it first).
- Days 64–66: files, JSON, and an exception strategy. The JSON file this lab
  dismantles is the one you have been writing since then.
- Day 70: modelling a domain with objects. A table is that model, written down
  somewhere the engine can enforce it.
- Day 84: the automation toolkit and its JSON state file. This lab is the
  direct answer to that lab's fifth extension exercise.
- A terminal and a text editor. Nothing to install.

## Supported operating systems

- **macOS** — fully supported. Captures taken on macOS 26.5.1 (Apple Silicon,
  arm64), Python 3.14.0, bash 3.2.57, `sqlite3` shell 3.51.0.
- **Linux** — fully supported on any distribution with Python 3.11+, bash and
  the `sqlite3` shell (`sudo apt install sqlite3` on Debian or Ubuntu).
- **Windows** — use WSL and follow the Linux path. On native Windows,
  `tests/run_tests.sh` is a bash script and will not run; the SQL and Python
  files themselves work unchanged, and `expected-output/FIELDS.md` records what
  may legitimately differ rather than guessing at captures never taken.

## Hardware requirements

Any computer that runs Python 3.11 or newer. The database built here is 28,672
bytes — seven pages. The largest thing the lab creates is a temporary 8 MB JSON
file that `json_pain.py` deletes before it exits. No GPU, no special memory,
and the whole harness finishes in a few seconds.

## Required software

- `python3`, 3.11 or newer (captures on 3.14.0), with the standard-library
  `sqlite3` module — already there.
- The `sqlite3` command-line shell (captures on 3.51.0).
- `bash` for the test harness — preinstalled on macOS and Linux.

**No packages to install.** See
[`requirements/README.md`](requirements/README.md), which also explains why the
two SQLite version numbers on your machine may differ.

## Free and open-source options

Everything here is free, and SQLite is unusual even among free software:
**its source code is in the public domain**, not merely permissively licensed.
Python and its `sqlite3` module are free under the Python Software Foundation
License. bash is free under the GPL. There is no paid tier of any of it, no
account, and nothing to sign up for.

The lesson's Alternatives section covers PostgreSQL, MySQL/MariaDB, DuckDB and
the commercial tier honestly — including the case, which is common, where
SQLite is simply the right answer and reaching for a server is the expensive
mistake.

## Installation

```bash
cd labs/sections/programming-with-python/day-085-relational-databases-and-sqlite
sqlite3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

That is the installation. Read both numbers, and note whether they agree — on
the authoring machine they do not, and that is normal.

If the `sqlite3` shell is missing, install it (`sudo apt install sqlite3` on
Debian or Ubuntu) or point the harness at one you have:

```bash
SQLITE=/path/to/sqlite3 PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## File structure

```text
day-085-relational-databases-and-sqlite/
├── README.md                    ← you are here
├── metadata.yml
├── examples/                    ← the finished work, all runnable
│   ├── json_pain.py             ← why the JSON file stops paying — measured
│   ├── books.json               ← the books table before it was a table
│   ├── schema.sql               ← the promise: 3 tables, 7 kinds of refusal
│   ├── seed.sql                 ← fixed dates, one transaction
│   ├── queries.sql              ← the shell walkthrough and dot-commands
│   ├── constraints_demo.sql     ← 7 refused writes, then ROLLBACK vs COMMIT
│   ├── typing_demo.sql          ← dynamic typing, affinity, and STRICT
│   ├── file_facts.py            ← read the 16-byte header yourself
│   ├── table_scan.py            ← restrict / project / order_by, by hand
│   ├── scan_vs_sql.py           ← asserts the two agree, row for row
│   └── library_py.py            ← the module: parameters, row_factory, with
├── starter/                     ← YOUR work
│   ├── schema.sql               ← 8 numbered exercises; applies as shipped
│   ├── table_scan.py            ← 3 numbered exercises
│   └── books.json
├── tests/
│   └── run_tests.sh             ← 44 behavioural checks, one exit code
├── expected-output/
│   ├── test-run.txt             ← the full harness run
│   ├── first-database.txt       ← both versions, ls -l, the header bytes
│   ├── walkthrough.txt          ← queries.sql in .mode box
│   ├── constraints.txt          ← the seven refusals and the rollback
│   ├── typing-and-strict.txt    ← affinity, then STRICT refusing
│   ├── scan-vs-sql.txt          ← the identical-results proof
│   ├── json-pain.txt            ← the four measured costs
│   └── FIELDS.md                ← what must match, what may differ
├── requirements/
│   ├── requirements.txt         ← deliberately empty; the note says why
│   └── README.md
├── troubleshooting.md
└── security.md
```

## How to run

Everything below runs from this directory. Work in a scratch copy so your own
`library.db` is yours:

```bash
mkdir -p scratch && cp examples/* scratch/ && cd scratch
```

```bash
# 1. First, make the file fail. Real numbers on your machine.
python3 json_pain.py

# 2. Build the database from nothing.
sqlite3 library.db < schema.sql
sqlite3 library.db < seed.sql

# 3. It is one ordinary file. Prove it two ways.
ls -l library.db
python3 file_facts.py library.db

# 4. The shell walkthrough: dot-commands, then SQL.
sqlite3 library.db < queries.sql

# 5. Or drive it interactively. .quit or Ctrl-D to leave.
sqlite3 library.db
#   sqlite> .tables
#   sqlite> .schema loans
#   sqlite> .mode box
#   sqlite> .headers on
#   sqlite> SELECT title, year FROM books ORDER BY year;
#   sqlite> .quit

# 6. Watch the schema refuse seven bad writes, then a transaction undo itself.
#    EXPECT ERRORS. Exit code 1 here means it worked.
sqlite3 library.db < constraints_demo.sql; echo "exit: $?"

# 7. Dynamic typing, and STRICT as the fix.
sqlite3 typing.db < typing_demo.sql; echo "exit: $?"

# 8. The query engine you write by hand.
python3 table_scan.py

# 9. The assertion the whole lab is built on.
python3 scan_vs_sql.py library.db; echo "exit: $?"

# 10. The same database from Python: parameters, rows, transactions.
python3 library_py.py library.db

# 11. Your task. Build it yourself from the starter.
cd ../starter
sqlite3 mine.db < schema.sql        # applies as shipped; creates books
python3 table_scan.py               # names the next exercise
# ... complete exercises 1-8 in schema.sql and 1-3 in table_scan.py ...
```

And the whole thing behind one command, from the lab directory:

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

## What the commands do

- `python3 json_pain.py` — builds JSON loan files of 10, 1,000 and 50,000
  records in a temporary directory, changes one field in each, and reports the
  bytes read and written to do it. Then stores an impossible member id without
  complaint, races two writers over one file and loses an update, and finally
  parses 8.6 MB to answer one question. It cleans up after itself.
- `sqlite3 library.db < schema.sql` — creates the database. Note that the file
  did not exist a moment ago: SQLite creates it on first write, with no
  service, no port and no configuration anywhere else on the machine.
- `sqlite3 library.db < seed.sql` — inserts the rows inside one
  `BEGIN; ... COMMIT;`. Every date is a literal, never `date('now')`, so the
  captures stay true tomorrow.
- `python3 file_facts.py library.db` — opens the file in binary mode and reads
  bytes 0–15 (the magic string), 16–17 (page size) and 28–31 (page count), then
  asks the engine the same two questions with `PRAGMA` and checks they agree
  with each other and with the file's length.
- `sqlite3 library.db < queries.sql` — the walkthrough: `.tables`, `.schema`,
  `.mode box`, `.headers on`, `.nullvalue`, then real `SELECT`s, a
  `GROUP BY`, the three-table overdue query, and `EXPLAIN QUERY PLAN` showing
  which index the planner chose without being told.
- `sqlite3 library.db < constraints_demo.sql` — seven writes the schema
  refuses (a foreign key twice, `NOT NULL`, `UNIQUE`, two `CHECK`s, a duplicate
  primary key), a count proving nothing changed, then the same two-statement
  transaction rolled back and committed. **It exits 1 on purpose.**
- `sqlite3 typing.db < typing_demo.sql` — five inserts into an ordinary table
  showing what affinity does and does not convert, `typeof()` reporting the
  storage class actually used, a `WHERE` that silently drops a row, and then
  the same value refused by a `STRICT` table. **Also exits 1 on purpose.**
- `python3 table_scan.py` — the hand-written engine, and its own cost: six
  predicate calls to find four rows, because a list has no index.
- `python3 scan_vs_sql.py library.db` — runs both and exits non-zero if they
  differ by a single row. It prints them side by side so you can see they do
  not.
- `python3 library_py.py library.db` — the three habits: `PRAGMA foreign_keys`
  on, values passed as parameters (with a hostile one to prove the point), and
  `with connection:` as a transaction that rolls the whole group back.
- `bash tests/run_tests.sh` — all 44 checks, in nine sections, on copies made
  in a temporary directory. Exits 0 on success, non-zero on any failure.

## Expected output

The harness ends like this — a real captured run; see
[`expected-output/test-run.txt`](expected-output/test-run.txt) for all of it:

```text
9. Nothing here reaches the network or needs anything installed
  ok: no executable lab file contains a network address of any kind
  ok: no lab file imports a third-party package — standard library only
  ok: every database this run created lives under a temporary directory

44 checks, 0 failure(s).
```

The header, read off the disk
([`expected-output/first-database.txt`](expected-output/first-database.txt)):

```text
first 16 B:  b'SQLite format 3\x00'
hex:         53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00
matches the documented magic string: True

page size (header bytes 16-17):  4,096 bytes
page count (header bytes 28-31): 7
pages * page size:               28,672 bytes
```

The cost the JSON file was quietly paying
([`expected-output/json-pain.txt`](expected-output/json-pain.txt)):

```text
   50,000 loans: file 8,622,249 bytes | changed  27 bytes | read+wrote 17,244,490 bytes to do it
```

Seventeen megabytes moved to change twenty-seven bytes. The database rewrites
the 4,096-byte page holding that row.

Dynamic typing, caught in the act
([`expected-output/typing-and-strict.txt`](expected-output/typing-and-strict.txt)):

```text
│ 2  │ not-a-number │ text       │ stored as text          │ text        │
```

That row is in a column declared `INTEGER`. `SELECT count(*) ... WHERE year <
2000` then returns 4 out of 5 rows and says nothing about the one it dropped.
The `STRICT` version of the same table answers:

```text
Runtime error near line 71: cannot store TEXT value in INTEGER column tight.year (19)
```

And the assertion the lab is built on
([`expected-output/scan-vs-sql.txt`](expected-output/scan-vs-sql.txt)):

```text
IDENTICAL: 4 rows, same values, same order.
The engine ran your loop. That is the whole trick.
```

[`expected-output/FIELDS.md`](expected-output/FIELDS.md) states exactly which of
these values must be identical on your machine and which are expected to
differ — including the two SQLite version numbers, which the suite reports and
deliberately does not require to match.

## Validation steps

1. `bash tests/run_tests.sh` ends with `44 checks, 0 failure(s).` and exits 0.
2. `sqlite3 --version` and `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"`
   both print a `3.x` number. They need not be the same number.
3. `python3 file_facts.py library.db` prints
   `matches the documented magic string: True`, and page size times page count
   equals the size `ls -l` reports.
4. `sqlite3 library.db < constraints_demo.sql` produces seven `Runtime error`
   lines naming `FOREIGN KEY`, `NOT NULL`, `UNIQUE` and `CHECK`, then reports
   `6 / 4 / 7 / 2` — proof that a refused write changes nothing.
5. Re-running the same file with `PRAGMA foreign_keys = OFF` **accepts** the
   bad member id. The rule is per-connection and opt-in.
6. `sqlite3 typing.db < typing_demo.sql` shows `not-a-number` stored with
   `typeof` of `text` in an `INTEGER` column, a `WHERE year < 2000` matching 4
   of 5 rows, and the `STRICT` table refusing the same value with `cannot store
   TEXT value in INTEGER column`.
7. `python3 scan_vs_sql.py library.db` prints `IDENTICAL: 4 rows` and exits 0.
   Change one line of `table_scan.py` and it exits 1 — try it.
8. The overdue query returns exactly three rows, `days_late` of 55, 21 and 6.
9. `sqlite3 library.db "SELECT count(*) FROM loans"` is unchanged after a
   `ROLLBACK` of a two-statement transaction, and the `copies` column is back
   to its old value too.
10. `python3 library_py.py library.db` reports `loans before: 7, after: 7`
    after a `with connection:` block whose second write failed.
11. After the harness, `find . -name "*.db"` inside the lab finds nothing.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `44 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure.

Two sections are worth reading before you run it. **Section 3** proves the
schema's refusals and then does the opposite: it runs the identical rejected
write with `PRAGMA foreign_keys=OFF` and requires it to be **accepted**. A
suite that only ever checks the happy configuration would let you ship a
database with its most important rule switched off. **Section 5** is the
identical-results check; break any of `restrict`, `project` or `order_by` and
watch it go red, which is the fastest way to convince yourself the check is
real.

Section 1 is worth reading for what it deliberately does *not* assert: it
prints both SQLite library versions and requires only that each is readable.
On the authoring machine they differ, and writing the equality assertion would
have meant either a failing suite or a false claim.

## Cleanup

```bash
rm -rf scratch
rm -f starter/mine.db starter/starter.db
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
git checkout -- starter/          # optional: reset your work
```

A SQLite database is one ordinary file. Deleting it removes it completely —
there is no service to stop, no registry entry, no configuration elsewhere on
the machine. If you see `library.db-journal` or `library.db-wal` beside it,
those belong to the same database and go with it.

`tests/run_tests.sh` makes its own temporary directory with `mktemp -d` and
removes it in a `trap`, so a completed run leaves nothing behind and one of its
checks asserts exactly that.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md). The five you are most likely to
meet: the two SQLite versions disagreeing (normal, not a fault); `UNIQUE
constraint failed: books.book_id`, which means you applied `seed.sql` twice;
`FOREIGN KEY constraint failed`, which is the lab working — while the *same*
write being accepted means `PRAGMA foreign_keys` is off; a query returning
fewer rows than you expect, which is almost always type affinity and is
diagnosed with `typeof()`; and `no such table`, which usually means
`sqlite3.connect` created an empty database next door because the path was
relative.

## Security notes

See [security.md](security.md). Short version: pass values as parameters,
never build a statement out of a string — `examples/library_py.py` proves the
point with a hostile value and leaves the `loans` table intact. Turn foreign
keys on, because off they enforce nothing. And know what a database file is:
no users, no passwords, no encryption, so the filesystem permissions *are* the
access control, deleting a row does not scrub its bytes, and a `-wal` file
beside the database is part of it. This lab needs no credential, opens no port,
reaches no network and needs no `sudo`.

## Extension exercises

1. **Make the overdue query lie.** Insert a loan whose `due_on` was written as
   `'16/08/2026'` instead of `'2026-08-16'`. The `CHECK` catches that shape,
   so first work out what shape would pass it and still sort wrongly. Then fix
   it properly — and decide whether a `CHECK` is the right tool or whether you
   want the column typed differently.
2. **Add the missing table.** A library has copies, not just titles: one row
   per physical book, each belonging to a title, and a loan points at a copy.
   Redesign the schema, and note what the change does to the overdue query.
3. **Measure the index.** Load 100,000 loans, time the overdue query, drop
   `loans_open`, time it again, and put it back. Then run `EXPLAIN QUERY PLAN`
   in both states. Write down what changed and what did not — the answers must
   be identical, only the work differs.
4. **Convert the whole schema to STRICT.** Every column must then be declared
   `INT`, `INTEGER`, `REAL`, `TEXT`, `BLOB` or `ANY`. Find out which of your
   declarations were not really types at all.
5. **Turn WAL on.** `PRAGMA journal_mode = WAL;`, then look at the directory:
   there are now three files, and the mode persists in the database rather than
   in the connection. Open two shells and confirm one can read while the other
   holds a write transaction. Then confirm two writers still cannot.
6. **Replace Day 84's state file for real.** Take `feedkit`'s
   `feedkit-state.json` and design the two tables that hold the same
   information. Write down, before you start, what you gain — concurrent
   readers, a query, no whole-file rewrite — and what you lose: a file you
   could read with `cat`, and an atomic write you could explain in a paragraph.
7. **Break every check on purpose, one at a time.** Remove a `CHECK`, drop the
   `NOT NULL`, comment out `PRAGMA foreign_keys = ON`, return the wrong column
   order from `project`. Run the harness after each. Four defects, four red
   checks, and you now know rather than hope that each property is genuinely
   asserted.

## Navigation

- **Previous day:** Day 84 — shipping an automation toolkit
  (`labs/sections/programming-with-python/day-084-shipping-an-automation-toolkit/`).
  This lab is the direct answer to that one's fifth extension exercise.
- **Next day:** Day 86 — `SELECT`: filtering, sorting and aggregating
  (`labs/sections/programming-with-python/`).
- **This week:** Week 13, SQL and Relational Databases. Day 87 is joins, which
  today's overdue query previews on purpose.
