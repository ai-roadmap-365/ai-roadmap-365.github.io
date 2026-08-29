# What this lab needs, and where it comes from

Nothing to install. Every import in every file is standard library.

## The one thing you need

| Thing | Where it comes from | Cost | How to check |
| --- | --- | --- | --- |
| Python 3.12 or newer, with `sqlite3` | Part of Python since 2.5. You already have it | Free; part of Python | `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"` |
| `bash`, for the test harness | Preinstalled on macOS and Linux; WSL or Git Bash on Windows | Free | `bash --version` |

Captures were taken on **Python 3.14.0** with the module linked against
**SQLite 3.53.3**.

## Why 3.12 rather than 3.11

Two things in this lab are newer than 3.11 and both are checked by the test
suite rather than assumed:

- **`Connection.autocommit`** arrived in Python 3.12. `transactions_demo.py`
  demonstrates it directly, and section 1 of the harness asserts the
  attribute exists. On 3.11 that check fails honestly rather than the demo
  crashing halfway through.
- **The default date and timestamp adapters are deprecated as of Python
  3.12.** The lesson reports the exact deprecation message this interpreter
  produces. Nothing in the lab relies on those adapters — every date is
  stored as an ISO-8601 `TEXT` string, which is what the deprecation notes
  recommend you do instead.

`STRICT` tables need **SQLite 3.37.0 or newer**, which the harness also
checks. That is the library linked into Python, not a separate install.

## Two SQLite version numbers on one machine

If you also have the `sqlite3` command-line shell, `sqlite3 --version` may
print a different number from `python3 -c "import sqlite3;
print(sqlite3.sqlite_version)"`. That is normal: two programs, each linking
its own copy of the library, both reading and writing the same file format.
This lab needs only the Python one. Day 85's lab covers the shell.

## What the lab deliberately does not use

- **No ORM.** SQLAlchemy Core and the SQLAlchemy ORM are excellent, and Day
  93 covers them properly. Today you write the layer they would replace, so
  that when you do reach for one you know what it is doing for you.
- **No `pytest`.** `unittest` is in the standard library and does everything
  this suite needs. `tests/run_tests.sh` is a bash harness that runs it.
- **No `aiosqlite`, no `pandas`.** Both appear in the lesson's Alternatives
  section, described rather than demonstrated. Neither is installed for this
  lab, and no output from either is claimed anywhere.
- **No network, asserted mechanically.** The harness fails if any file under
  `examples/` or `starter/` contains a URL or an IP address.
- **No `sudo`, no server, no port, no credential.**
