# What this lab needs, and where it comes from

Nothing to install. That is unusual enough in a programming course to be worth
a page of its own, because it is a fact about databases rather than a
convenience: SQLite is not a service you run, it is a library that is already
inside the tools you have.

## The two things you need

| Thing | Where it comes from | Cost | How to check |
| --- | --- | --- | --- |
| The `sqlite3` command-line shell | Preinstalled on macOS. On Debian or Ubuntu, `sudo apt install sqlite3`; on Fedora, `sudo dnf install sqlite`. On Windows, use WSL, or download the precompiled shell from the SQLite website | Free; public domain | `sqlite3 --version` |
| The `sqlite3` Python module | Part of the Python standard library since Python 2.5. You already have it | Free; part of Python | `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"` |

Python **3.11 or newer** is what the captures were taken on. Nothing in the lab
requires a feature newer than that; the type-hint syntax used in the starter
(`Path | None`) needs 3.10 or newer.

## Run those two commands now, and read both numbers

```bash
sqlite3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

On the authoring machine they print **3.51.0** and **3.53.3** — two different
SQLite libraries on one computer. That is not a misconfiguration and there is
nothing to fix. The shell is a program that links its own copy of SQLite; the
Python module is a different program that links its own. Both read and write
the same file format, and a database written by one is read by the other
without conversion, which is precisely the guarantee the file format exists to
give.

The number that matters is whichever belongs to the program you are running at
the time. If a `STRICT` table works in the shell and fails in Python, the
question to ask is not "what version is installed" but "what version is
*this* program using".

`tests/run_tests.sh` reports both and asserts neither is missing. It
deliberately does not assert they are equal.

## What the lab deliberately does not use

- **No ORM.** SQLAlchemy and Django's ORM are excellent, and both hide exactly
  the thing this lesson is about. You write the SQL here.
- **No database server.** Nothing to start, nothing to stop, no port, no
  password, no `sudo`. This is the difference between an embedded database and
  a client-server one, and feeling it is part of the lesson.
- **No third-party package at all.** `tests/run_tests.sh` checks this
  mechanically: it greps every Python file in the lab for an import of
  `requests`, `httpx`, `urllib3`, `pandas` or `sqlalchemy` and fails if it
  finds one.
- **No network.** The same suite fails if any executable lab file contains a
  URL. There is nothing to download and nothing to reach.

## If the shell is missing

Everything except the dot-command walkthrough can be done from Python alone,
because the module carries its own copy of the engine. `tests/run_tests.sh`
needs the shell and will tell you so rather than silently skipping the checks
that use it; point it at one you have with
`SQLITE=/path/to/sqlite3 bash tests/run_tests.sh`.
