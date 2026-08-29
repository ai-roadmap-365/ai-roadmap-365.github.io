# Dependencies

There are none to install. That is not laziness; it is the point of the week.

| Tool | Version verified here | Why this lab needs it | Licence |
| --- | --- | --- | --- |
| `sqlite3` (the shell) | 3.51.0 | Runs every query in `examples/queries/`, the seed, and the whole test harness | Public domain |
| `python3` | 3.14.0 | Runs `examples/groupby_from_scratch.py`, which builds GROUP BY out of a dictionary of accumulators and then checks SQL agrees | Python Software Foundation License |
| `bash` | 3.2.57 | Runs `tests/run_tests.sh`, `examples/build_db.sh` and `starter/check.sh` | GPL-3.0 |
| `sqlite3` (the Python module) | Standard library | The comparison script's connection to the same database file | Python Software Foundation License |

All four are free, and three of the four are already on any macOS or Linux
machine you would be reading this on.

## Installing the one that might be missing

macOS ships the `sqlite3` shell. On Debian and Ubuntu the shell is packaged
separately from the library, so it is possible to have a perfectly working
`import sqlite3` in Python and no `sqlite3` command at all:

```bash
sudo apt install sqlite3      # Debian, Ubuntu
sudo dnf install sqlite       # Fedora
```

`tests/run_tests.sh` checks for the command before it does anything else and
stops with that instruction rather than failing halfway through a run.

## What is deliberately absent

**No ORM.** Not SQLAlchemy, not Django's, not Peewee. Every one of them is a
good tool and you will meet them later. Today the whole subject is the shape of
a SELECT and the order its clauses run in, and an ORM's job is to hide exactly
that. Learning the abstraction before the thing it abstracts is how people end
up unable to explain why their query is slow.

**No pandas.** The Alternatives section of the lesson covers it honestly as the
dataframe answer to the same questions, including where it wins and where it
loses. It is not installed here, and the lesson says so rather than showing
output that was never produced.

**No database server.** SQLite is a library and a file. There is no daemon to
start, no port to open, no user to create, and nothing to uninstall afterwards
except one file you can delete with `rm`.

**No seed data from the internet.** `examples/seed.sql` is 45 loans, 24 books
and 12 members written by hand, chosen so that every number in the tests can be
checked by reading the file. The whole lab runs with the network switched off.
