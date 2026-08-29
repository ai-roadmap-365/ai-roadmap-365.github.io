# Dependencies

**None.** This lab installs nothing, and `requirements.txt` is deliberately
empty of packages.

That is not laziness; it is the point of the day. Everything here runs on two
things you already have:

| Tool | Version used here | Where it comes from | Licence |
| --- | --- | --- | --- |
| `python3` | 3.14.0 | Whatever Python you installed on Day 43. Only the standard library is used, and only the `sqlite3`, `collections`, `time`, `sys` and `pathlib` modules from it | PSF licence |
| `sqlite3` (the shell) | 3.51.0 | Preinstalled on macOS at `/usr/bin/sqlite3`; `apt install sqlite3` or the equivalent on Linux | Public domain |

Python's `sqlite3` module is a wrapper around a copy of the SQLite library
compiled into your Python. It is often a *different version* from the `sqlite3`
shell on your `PATH` — on the authoring machine the shell reported 3.51.0 while
Python reported 3.53.3. Both behave identically for everything in this lab, but
it is worth knowing that they are two separate copies, because one day a
feature will exist in one and not the other.

Check what you have:

```bash
python3 --version
sqlite3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

**Minimum versions.** Python 3.11 or newer (the type-hint syntax in the Python
files uses `dict | None`). SQLite 3.16.0 or newer for the `pragma_table_info`
and `pragma_foreign_key_list` table-valued functions the test suite uses; any
SQLite shipped in the last several years is far past that.

## If the tools are somewhere unusual

The test harness takes overrides rather than guessing:

```bash
PYTHON=/path/to/python3 SQLITE3=/path/to/sqlite3 bash tests/run_tests.sh
```

It fails loudly with that instruction if it cannot find either one, rather than
quietly skipping the checks that need them.

## What is deliberately absent

**No ORM.** SQLAlchemy, Django's ORM and Peewee all generate the joins this lab
writes by hand, and all of them are worth using later. Learning them before you
can read the SQL they emit means that when a query is slow or wrong you have no
way in. Write the join first; let a library write it for you afterwards.

**No database server.** PostgreSQL and MySQL are covered in the lesson's
Alternatives section, with the syntax differences that actually matter. Neither
is installed here, because installing a server changes this lab from "twenty
minutes of joins" into "an afternoon of administration", and nothing in today's
material needs one.
