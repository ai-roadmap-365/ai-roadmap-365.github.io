# Dependencies

**None.** This lab installs nothing, and `requirements.txt` is deliberately
empty of packages. The whole point of the day is that a schema and the queries
over it are the deliverable; no library is needed to produce either.

| Tool | Version used here | Where it comes from | Licence |
| --- | --- | --- | --- |
| `python3` | 3.14.0 | Whatever Python you installed on Day 43. Only the standard library is used, and only the `sqlite3`, `sys` and `pathlib` modules from it | PSF licence |
| `sqlite3` (the shell) | 3.51.0 | Preinstalled on macOS at `/usr/bin/sqlite3`; `apt install sqlite3` or the equivalent on Linux | Public domain |

Python's `sqlite3` module wraps a copy of the SQLite library compiled into your
Python. It is often a **different version** from the `sqlite3` shell on your
`PATH` — on the authoring machine the shell reported 3.51.0 while Python
reported 3.53.3. That does not matter for anything in this lab, but it is worth
knowing that they are two separate copies, because one day a feature will exist
in one and not the other.

Check what you have:

```bash
python3 --version
sqlite3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

## Minimum versions, and why these two in particular

**Python 3.11 or newer** — the type hints in `examples/05_report.py` use the
`str | Path` syntax.

**SQLite 3.25.0 (2018) or newer**, for window functions. Questions 6, 7 and 8
use `ROW_NUMBER`, `RANK` and `SUM ... OVER`, and without them those three
answers cannot be written at all in the shape this lab uses. `tests/run_tests.sh`
runs `SELECT row_number() OVER ()` as its very first check so that an old shell
fails with one clear line rather than a wall of syntax errors.

**SQLite 3.8.3 (2014) or newer**, for `WITH RECURSIVE`. Question 9 walks the
category tree and cannot be answered by any fixed number of joins.

Confirm both in one line:

```bash
sqlite3 :memory: "SELECT sqlite_version(); SELECT row_number() OVER (); WITH RECURSIVE c(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM c WHERE n<3) SELECT count(*) FROM c;"
```

## If the tools are somewhere unusual

Both scripts take overrides rather than guessing:

```bash
PYTHON=/path/to/python3 SQLITE3=/path/to/sqlite3 bash tests/run_tests.sh
SQLITE3=/path/to/sqlite3 bash starter/03_check.sh
```

They fail loudly with that instruction if they cannot find either one, rather
than quietly skipping the checks that need them.

## What is deliberately absent

**No modelling tool.** Draw the entity diagram on paper, or in whichever
diagramming tool you already have. The lesson's Alternatives section covers the
dedicated tools honestly, including what they buy on a team and what they cost
you when the diagram and the database drift apart. Nothing here needs one.

**No ORM.** SQLAlchemy, Django's ORM and Peewee would all generate a version of
this schema from Python classes, and Day 93 covers that. Doing it in that order
would mean meeting the abstraction before the thing it abstracts, and the first
time a generated migration did something surprising you would have no way in.

**No database server.** PostgreSQL is covered in the lesson's Alternatives
section, with the type differences that actually change the design — a real
`date`, a real `boolean`, a native `enum`, and `numeric` for money. Installing
one would turn this lab from thirty-five minutes of schema design into an
afternoon of administration, and nothing in today's material needs it.
