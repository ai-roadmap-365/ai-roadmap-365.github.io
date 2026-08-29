# What this lab needs, and where it comes from

Nothing to install. Same as Day 85: SQLite is not a service you run, it is
a library already inside the tools you have.

## The two things you need

| Thing | Where it comes from | Cost | How to check |
| --- | --- | --- | --- |
| The `sqlite3` command-line shell | Preinstalled on macOS. On Debian or Ubuntu, `sudo apt install sqlite3`; on Fedora, `sudo dnf install sqlite`. On Windows, use WSL, or download the precompiled shell from the SQLite website | Free; public domain | `sqlite3 --version` |
| The `sqlite3` Python module | Part of the Python standard library since Python 2.5. You already have it | Free; part of Python | `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"` |

Python **3.11 or newer** is what the captures were taken on (3.14.0).
Nothing here needs a feature newer than that.

## Two SQLite versions on one machine is normal

```bash
sqlite3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

On the authoring machine these print **3.51.0** and **3.53.3**. The shell
is a program that links its own copy of SQLite; the Python module is a
different program that links its own. Both read and write the same file
format. `tests/run_tests.sh` reports both and asserts only that each is
readable — it deliberately does not require them to be equal.

It matters slightly more today than it did on Day 85. The query planner is
part of the library, so two versions can legitimately choose two different
plans for the same query on the same data. If a plan in
`expected-output/` differs from yours, check which SQLite you are running
before assuming anything is wrong.

## What the lab deliberately does not use

- **No benchmarking framework.** `timeit`, `pytest-benchmark` and the rest
  are good tools, and all of them would put a layer between you and the
  thing being measured. `examples/timing.py` is thirty lines you can read
  in a minute: run it seven times, report best, median and spread.
- **No third-party package at all.** `tests/run_tests.sh` greps every
  Python file for an import of `requests`, `httpx`, `urllib3`, `pandas`,
  `numpy` or `sqlalchemy` and fails if it finds one. On a lab about
  timings, an unexpected import is an unexpected variable.
- **No network.** The same suite fails if any executable lab file contains
  a URL. There is nothing to download.
- **No ORM.** You need to see the SQL to see the plan.

## Disk and time

`generate.py` builds a 400,000-row table of about **30 MB**. The write-cost
experiment builds several smaller databases, the largest about **35 MB**,
all inside a temporary directory that is removed when it finishes. The
full test suite took about **12 seconds** on the authoring machine and
leaves nothing behind.

If disk space is genuinely tight, every script takes a row count:

```bash
python3 generate.py events.db 100000
```

The shapes still show at 100,000 rows. Below about 50,000 the differences
start hiding inside the noise, which is itself worth seeing once.

## If the shell is missing

Everything except `plans.sql` and `starter/indexes.sql` can be done from
Python alone, because the module carries its own copy of the engine.
`tests/run_tests.sh` needs the shell and says so rather than silently
skipping checks; point it at one you have with
`SQLITE=/path/to/sqlite3 bash tests/run_tests.sh`.
