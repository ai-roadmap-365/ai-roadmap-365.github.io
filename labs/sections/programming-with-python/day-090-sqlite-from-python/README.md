# Day 090 lab — A Real Data Layer

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** SQLite from Python
- **Day number:** 90 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-090-sqlite-from-python
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-090-sqlite-from-python` when the site is running.
<!-- generated-links:end -->

## Purpose

For five days the database has been a place you visited with a shell. Today
it moves inside a program, and two things start to go wrong that the shell
never let you get wrong: **SQL built out of strings**, and **transactions
you thought you understood**.

So this lab does not describe either. It demonstrates both, and then makes
you build the layer that prevents them.

You will do four things, in this order:

1. **Break a database on purpose.** `injection_demo.py` builds a throwaway
   database in a temporary directory, hands the same crafted value to a
   concatenated query and to a bound one, and prints both results. The first
   returns every member's address and PIN and then destroys a table. The
   second returns nothing and changes nothing. Same value, same schema, one
   character of difference in the code.
2. **Build the data layer from first principles.** A connection factory, a
   transaction context manager, row-to-object mapping, and a repository
   whose every statement is a literal with every value bound. Nine numbered
   exercises in `starter/db.py`, each naming the check that confirms it.
3. **Prove the properties rather than assume them.** A failure halfway
   through a transaction leaves the database unchanged — for a SQL error and
   for a Python one, checked from a second connection. `PRAGMA foreign_keys`
   is per-connection, and is a silent no-op inside a transaction. `with
   connection:` does not close the connection. `executemany` beats a loop,
   and one transaction beats both by more.
4. **Make the guard mechanical.** `no_sql_strings.py` parses every file with
   `ast` and fails if any statement reaching `execute` was built from parts
   — and the test suite feeds it a deliberately unsafe file to prove it
   still catches one.

All 64 checks run offline. No server, no port, no credential, no third-party
package: the standard library and bash, nothing else. The suite asserts that
mechanically.

## Learning objectives

- Open a connection deliberately: turn foreign keys on, choose a row
  factory, decide who controls transactions, and know why each of those is
  per-connection.
- Bind every value, in both qmark and named styles, and know why escaping is
  not an equivalent fix and why parameters cannot stand in for identifiers.
- See a crafted input arrive as **code** and then as **data**, in the same
  program, against the same schema.
- Write a transaction context manager and prove it undoes a partial change,
  whether the failure came from SQL or from Python.
- Choose between `fetchone`, `fetchmany`, `fetchall` and iterating a cursor,
  with the memory difference measured rather than asserted.
- Map rows to domain objects in one place, and translate storage errors into
  domain errors at the boundary.
- Tell `IntegrityError`, `OperationalError` and `ProgrammingError` apart by
  making each of them happen.
- Keep SQL out of the rest of the program — and check that mechanically
  rather than by reading.

## Prerequisites

- The Day 90 lesson (read it first).
- Days 85–89: the relational model, `SELECT`, joins, writing and schema
  design, and indexes. Everything you learned at the shell prompt is what
  the repository sends over the wire today.
- Day 70: modelling a domain with objects. `domain.py` here is that model,
  unchanged, and `db.py` is the repository it always implied.
- Day 74: mocking and testing boundaries. The argument that fakes beat mocks
  and that the best move is to relocate the boundary is what makes
  `test_repository.py` look the way it does.
- A terminal and a text editor. Nothing to install.

## Supported operating systems

- **macOS** — fully supported. Captures taken on macOS 26.5.1 (Apple
  Silicon, arm64), Python 3.14.0, bash 3.2.57, SQLite 3.53.3 as linked into
  Python.
- **Linux** — fully supported on any distribution with Python 3.12+ and
  bash.
- **Windows** — use WSL and follow the Linux path. On native Windows,
  `tests/run_tests.sh` is a bash script and will not run; every Python file
  works unchanged, because paths go through `pathlib` and `tempfile` rather
  than being hard-coded. `expected-output/FIELDS.md` records what may
  legitimately differ rather than inventing captures never taken.

## Hardware requirements

Any computer that runs Python 3.12 or newer. No GPU, no special memory. The
largest thing created is a temporary database of 40,000 short rows used to
measure `fetchall` against cursor iteration, and it is deleted before the
script returns. The whole harness finishes in a few seconds.

`examples/bulk_insert.py`, run on its own with its default of 20,000 rows,
takes about fifteen seconds — because its first method commits once per row,
which is the finding rather than a fault. The test suite runs it with 2,000.

## Required software

- `python3`, **3.12 or newer** (captures on 3.14.0), with the
  standard-library `sqlite3` module — already there.
- `bash` for the test harness — preinstalled on macOS and Linux.

**No packages to install.** See
[`requirements/README.md`](requirements/README.md), which explains why 3.12
rather than 3.11.

## Free and open-source options

Everything here is free. Python and its `sqlite3` module are free under the
Python Software Foundation License; SQLite's source code is in the **public
domain**; bash is free under the GPL. There is no paid tier, no account and
nothing to sign up for.

The lesson's Alternatives section covers `sqlite3` itself, SQLAlchemy Core,
the SQLAlchemy ORM, a hand-rolled repository, `pandas.read_sql` and
`aiosqlite` — with when to choose each and free versus paid stated plainly.
None of them is installed for this lab, and no output from any of them is
claimed anywhere.

## Installation

```bash
cd labs/sections/programming-with-python/day-090-sqlite-from-python
python3 -c "import sqlite3, sys; print(sys.version.split()[0], sqlite3.sqlite_version)"
```

That is the installation. Both numbers printed on one line: the Python
version, then the SQLite library linked into it.

If your `python3` is older than 3.12, point the harness at a newer one:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## File structure

```text
day-090-sqlite-from-python/
├── README.md                    ← you are here
├── metadata.yml
├── examples/                    ← the finished work, all runnable
│   ├── domain.py                ← Day 70's objects. Note: no sqlite3 import
│   ├── db.py                    ← THE DATA LAYER: connect, transaction,
│   │                              mapping, BookRepository, LoanRepository
│   ├── seed.py                  ← fixed sample data; every date a literal
│   ├── injection_demo.py        ← the same value as code, then as data
│   ├── cursors_demo.py          ← fetch methods, row factories, memory
│   ├── transactions_demo.py     ← implicit, with-block, explicit, autocommit
│   ├── errors_demo.py           ← 13 deliberate mistakes and their classes
│   ├── bulk_insert.py           ← loop vs transaction vs executemany
│   ├── report.py                ← the application layer. No SQL anywhere
│   ├── test_repository.py       ← 29 tests against a real temporary database
│   └── no_sql_strings.py        ← the ast guard: no assembled SQL
├── starter/                     ← YOUR work
│   ├── db.py                    ← 9 numbered exercises
│   ├── domain.py                ← given, unchanged
│   ├── seed.py                  ← given, unchanged
│   └── smoke.py                 ← names the next exercise; exits 1 until done
├── tests/
│   └── run_tests.sh             ← 64 behavioural checks, one exit code
├── expected-output/
│   ├── test-run.txt             ← the full harness run
│   ├── injection.txt            ← the four acts, with the leaked rows
│   ├── transactions.txt         ← every transaction fact, on this interpreter
│   ├── cursors.txt              ← fetch methods, factories, the memory ratio
│   ├── errors.txt               ← the exception table, produced by erring
│   ├── bulk-insert.txt          ← the three timings
│   ├── report.txt               ← the application layer's output
│   ├── unit-tests.txt           ← unittest, verbose
│   ├── no-sql-strings.txt       ← the guard passing
│   ├── starter-smoke.txt        ← the starter refusing to look finished
│   └── FIELDS.md                ← what must match, what may differ
├── requirements/
│   ├── requirements.txt         ← deliberately empty; the note says why
│   └── README.md
├── troubleshooting.md
└── security.md
```

## How to run

Everything below runs from this directory. Nothing needs a scratch copy:
every script creates its own database inside a temporary directory and
removes it before it returns.

```bash
# 1. Watch the attack, then watch it fail. Read this one's output slowly.
python3 examples/injection_demo.py

# 2. The transaction model, on the interpreter you are actually running.
python3 examples/transactions_demo.py

# 3. Cursors, the four ways to get rows, and what fetchall costs.
python3 examples/cursors_demo.py

# 4. Thirteen deliberate mistakes, and the class each one raises.
python3 examples/errors_demo.py

# 5. A loop, a batched loop, and executemany. Takes about 15 seconds.
python3 examples/bulk_insert.py
python3 examples/bulk_insert.py 2000        # or a smaller number

# 6. The application layer. Open it and note what it does not import.
python3 examples/report.py

# 7. The data layer's own suite, against a real database in a temp file.
python3 examples/test_repository.py -v

# 8. The guard. Then break something and watch it complain.
python3 examples/no_sql_strings.py examples

# 9. YOUR TASK. Nine exercises; the smoke test names the next one.
cd starter
python3 smoke.py
# ... write exercise 1 in db.py, run it again, repeat ...
cd ..
```

And the whole thing behind one command:

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

## What the commands do

- `python3 examples/injection_demo.py` — builds a members table with
  addresses and PINs inside a fresh temporary directory. Act 1 concatenates
  the value `Ada' OR '1'='1` into a query and prints the three rows it
  should never have returned. Act 2 aims a `DROP TABLE` through the same
  hole and meets `execute`'s one-statement limit — a limit of the module,
  not a defence. Act 3 hands the identical string to `executescript`, which
  accepts it, and the table is gone. Act 4 binds both values as parameters:
  zero rows, no error, nothing changed. The directory is removed in a
  `finally:` block.
- `python3 examples/transactions_demo.py` — prints what *this* interpreter
  does: the default `isolation_level`, `autocommit`, whether DDL opens a
  transaction, what `with connection:` commits and what it leaves open, a
  two-write transaction undone by a foreign-key failure, `PRAGMA
  foreign_keys` being silently ignored inside a transaction, and
  `connection.autocommit` set both ways with a second connection watching.
- `python3 examples/cursors_demo.py` — `execute` returning a cursor,
  `description`, `rowcount` being `-1` for a `SELECT`, the four fetch
  methods on one cursor, then `tracemalloc` measuring `fetchall` against
  iteration, then three row factories side by side, then two cursors open on
  one connection.
- `python3 examples/errors_demo.py` — prints the exception hierarchy from
  the module itself, then makes thirteen deliberate mistakes and tabulates
  the class and message each produced. It exits non-zero if any of them
  fails to raise.
- `python3 examples/bulk_insert.py [n]` — inserts n rows three ways into a
  fresh file each time and reports seconds, rows per second and the ratio.
  The order is the durable fact; the figures are not.
- `python3 examples/report.py` — the application layer: a shelf report, the
  three-table overdue query, a duplicate title surfacing as `DuplicateTitle`
  rather than `sqlite3.IntegrityError`, a missing id as `BookNotFound`, a
  runtime sort key checked against an allow-list, and a streamed read.
- `python3 examples/test_repository.py` — 29 tests in five classes against a
  real database file in a temporary directory, torn down per test.
- `python3 examples/no_sql_strings.py [dir]` — parses every `.py` file with
  `ast` and fails on any statement reaching `execute`, `executemany` or
  `executescript` that was built with an f-string, `+`, `%` or `.format`.
- `python3 starter/smoke.py` — runs your `db.py` and names the first
  exercise that is missing or wrong. Exits 1 until all nine pass.
- `bash tests/run_tests.sh` — all 64 checks, in eleven sections, on copies
  made in a temporary directory. Exits 0 on success, non-zero on any
  failure.

## Expected output

The harness ends like this — a real captured run; see
[`expected-output/test-run.txt`](expected-output/test-run.txt) for all of it:

```text
11. Offline, self-contained, and leaves nothing behind
  ok: no executable lab file contains a network address of any kind
  ok: no lab file imports a third-party package — standard library only
  ok: nothing in the lab's code asks for sudo
  ok: this run left no database file anywhere inside the lab directory
  ok: no sandbox from any lab script was left in the temporary directory

64 checks, 0 failure(s).
```

The moment the whole lab exists for
([`expected-output/injection.txt`](expected-output/injection.txt)):

```text
  the crafted case, input = "Ada' OR '1'='1"
    statement: SELECT name, email, pin FROM members WHERE name = 'Ada' OR '1'='1'
                                                                    ^ the apostrophe inside the value closed the string early
    rows: 3  -> every member, with address and PIN:
      ('Ada Lovelace', 'ada@example.invalid', '4417')
      ('Grace Hopper', 'grace@example.invalid', '9021')
      ('Alan Turing', 'alan@example.invalid', '1912')
```

And the same value, bound:

```text
    leak attempt     value = "Ada' OR '1'='1"
                     statement: SELECT name, email, pin FROM members WHERE name = ?
                     rows returned: 0
```

The misreading this lab exists partly to correct
([`expected-output/transactions.txt`](expected-output/transactions.txt)):

```text
    is the connection still usable after the with-block? True
```

The pragma trap, in two lines:

```text
    inside a transaction, set ON   -> 0   (silently ignored — no error, no warning)
    outside again, set ON          -> 1
```

What `fetchall` costs
([`expected-output/cursors.txt`](expected-output/cursors.txt)) — figures
vary, the gap does not:

```text
    fetchall()        peak traced memory: 15,612,096 bytes
    iterating cursor  peak traced memory:        826 bytes
```

And the bulk insert
([`expected-output/bulk-insert.txt`](expected-output/bulk-insert.txt)):

```text
a loop, no transaction                13.3531          1,498     1.0x
a loop inside one transaction          0.0095      2,113,318  1411.0x
executemany inside one transaction     0.0054      3,677,372  2455.2x
```

[`expected-output/FIELDS.md`](expected-output/FIELDS.md) states exactly which
of these values must be identical on your machine and which are expected to
differ, and what a difference would actually mean.

## Validation steps

1. `bash tests/run_tests.sh` ends with `64 checks, 0 failure(s).` and exits 0.
2. `python3 examples/injection_demo.py` prints three leaked rows in act 1,
   `members table exists afterwards: False` in act 3, and `rows returned: 0`
   twice in act 4 — then exits 0.
3. The same hostile strings passed to `BookRepository.find_by_author` return
   an empty list and leave all seven books in place.
4. `python3 examples/no_sql_strings.py examples` exits 0. Add an f-string
   query to any file and it exits 1, naming the file and line. Try it, then
   put it back.
5. `transactions_demo.py` prints `is the connection still usable after the
   with-block? True`.
6. It also prints `inside a transaction, set ON   -> 0` and then `outside
   again, set ON          -> 1`.
7. A failed transaction leaves `copies`, the open-loan count and the book
   count exactly as they were — checked again from a freshly opened
   connection, so it is the file that is unchanged and not just the cache.
8. `python3 examples/errors_demo.py` reports `13 deliberate mistakes, 0 of
   which raised nothing.`
9. `python3 examples/test_repository.py` reports `Ran 29 tests` and `OK`.
10. `python3 examples/report.py` shows `55`, `21` and `6` days late, and
    refuses a duplicate title with a domain error.
11. `grep -n "import sqlite3" examples/report.py examples/domain.py` finds
    nothing.
12. `starter/smoke.py` exits 1 as shipped and 0 once all nine exercises are
    written.
13. After any run, `find . -name "*.db"` inside the lab finds nothing.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `64 checks, 0 failure(s).` The command exits 0 on
success and non-zero on any failure.

Three sections are worth reading before you run it.

**Section 3** is the injection demonstration, and it asserts both halves.
A suite that only checked the safe path would pass against code that was
never unsafe in the first place, and would tell you nothing.

**Section 4** tests the guard rather than trusting it: it writes a file
containing a deliberately unsafe f-string query, requires the guard to
reject it with the right file and line, then writes a file using adjacent
string literals and requires the guard to accept it. A check nobody has
watched fail is a check you are guessing about.

**Section 10** runs the shipped starter and requires it to **fail**, then
drops the finished `db.py` in and requires the same script to pass. That is
how you know the exercises are really being checked rather than merely being
present.

## Cleanup

There is nothing to clean up, which is the point: every script builds its
database inside a directory made with `tempfile.mkdtemp()` and removes it in
a `finally:` block. Two checks in section 11 assert that no `.db` file
remains in the lab and no sandbox remains in the temporary directory.

If a script was interrupted before its cleanup ran:

```bash
find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'day090-*'      # look first
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
git checkout -- starter/          # optional: reset your work
```

Delete only what that first command lists, and only after checking it.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md). The five you are most likely
to meet: `Incorrect number of bindings supplied`, which is a missing comma
in `(value,)`; a `PRAGMA` that runs without error and changes nothing, which
means you are inside a transaction; `Cannot operate on a closed database`,
which usually follows from believing `with connection:` closes it; writes
that vanish at exit, which means nothing committed them; and
`OperationalError: no such table`, which usually means a relative path
created an empty database next door.

## Security notes

See [security.md](security.md). Short version: `examples/injection_demo.py`
performs a real attack and drops a real table, entirely inside a temporary
directory it created and removes — it never opens a file you own. The habit
the lab is teaching is one character wide: bind every value, never build a
statement out of a string, and check that mechanically rather than by
reading. Turn `PRAGMA foreign_keys` on when you connect, because it is off
by default, per connection, and silently ignored inside a transaction. And
translate storage errors at the repository boundary, because a raw database
error leaks your schema to whoever provoked it.

This lab needs no credential, opens no port, reaches no network and needs no
`sudo`.

## Extension exercises

1. **Add a second backend behind the same repository.** Write
   `InMemoryBookRepository` with the same methods, backed by a dict, and run
   `report.py` against it unchanged. The moment it works, you have proved
   the boundary is real — and you have the fake that Day 74 argued beats a
   mock.
2. **Make the guard stricter, then live with it.** Extend
   `no_sql_strings.py` to also flag a statement passed to `execute` as a
   bare `Name` whose assignment it cannot see. Run it over the lab. Decide
   whether the false positives are worth the coverage, and write down why —
   that trade is what every real linter rule is.
3. **Measure the busy timeout.** Open two connections, `BEGIN IMMEDIATE` on
   one, and try to write from the other. Time how long it waits before
   `database is locked`. Then set `timeout=0.5` and repeat. Then turn on
   `PRAGMA journal_mode = WAL` and find out precisely which of the two
   operations stops blocking.
4. **Register an adapter and a converter, explicitly.** Store
   `datetime.date` objects using `sqlite3.register_adapter` and read them
   back with `register_converter` plus `detect_types`. Then compare against
   this lab's approach of storing ISO-8601 text. Note which one still sorts
   correctly in SQL, which one survives being read by another language, and
   which one the deprecation notes in Python 3.12 are steering you away
   from.
5. **Break each property on purpose, one at a time.** Remove the `PRAGMA`
   from `connect()`. Change `except BaseException` to `except Exception` in
   `transaction()`. Make `find_by_author` use an f-string. Make
   `stream_all` call `fetchall`. Run the harness after each. Four defects,
   and you now know rather than hope that each property is genuinely
   asserted.
6. **Take the repository to a real dataset.** Point it at something you own
   — a reading list, a music library, an export from an app — write a
   migration that reads the old format and inserts through the repository,
   and keep the list of rows it refuses. That list is the argument for
   constraints, written by your own data.
7. **Add a connection-per-thread factory.** SQLite connections are not
   shared between threads by default. Write a `threading.local` factory that
   gives each thread its own connection, run four threads writing
   concurrently, and record what actually happens: how often `database is
   locked` appears, and whether WAL changes it. Then say in one sentence
   when you would use threads with SQLite at all.

## Navigation

- **Previous day:** Day 89 — indexes and query performance
  (`labs/sections/programming-with-python/`).
- **Next day:** Day 91 — designing and querying a real schema
  (`labs/sections/programming-with-python/`).
- **This week:** Week 13, SQL and Relational Databases. Day 85 built the
  first database and Day 89 made it fast; today it moves inside a program,
  and Day 93 introduces the ORM that would have written this layer for you.
