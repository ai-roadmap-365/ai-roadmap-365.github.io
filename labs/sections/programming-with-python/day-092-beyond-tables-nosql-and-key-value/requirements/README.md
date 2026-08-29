# Dependencies

**None.** This lab installs nothing, and `requirements.txt` is deliberately
empty of packages. The point of the day is the trade-off between storage
shapes, and you can feel every one of those trade-offs with two stores that are
already on your machine.

| Tool | Version used here | Where it comes from | Licence |
| --- | --- | --- | --- |
| `python3` | 3.14.0 | Whatever Python you installed on Day 43. Standard library only: `sqlite3`, `dbm`, `json`, `re`, `sys`, `time`, `tempfile`, `pathlib` | PSF licence |
| `sqlite3` (the shell) | 3.51.0 | Preinstalled on macOS at `/usr/bin/sqlite3`; `apt install sqlite3` or the equivalent on Linux | Public domain |

Python's `sqlite3` module wraps a copy of the SQLite library compiled into your
Python. It is often a **different version** from the `sqlite3` shell on your
`PATH` — on the authoring machine the shell reported 3.51.0 while Python
reported 3.53.3. Both are far past this lab's floor, but it is worth knowing
they are two separate copies.

Check what you have:

```bash
python3 --version
sqlite3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

## The one version floor, and why it exists

**SQLite 3.38.0 (2022) or newer.** That release made the JSON functions part of
the default build instead of an optional compile-time extension, and it added
the `->` and `->>` operators. Half this lab is about querying inside a document
from a relational engine, and without `json_extract`, `json_each` and an index
on an extracted expression, that half cannot be run at all.

Confirm all of it in one line:

```bash
sqlite3 :memory: "SELECT sqlite_version(), json_extract('{\"a\":1}','\$.a'), '{\"a\":2}' ->> '\$.a', (SELECT count(*) FROM json_each('[1,2,3]'));"
```

You should see your version followed by `1|2|3`. `tests/run_tests.sh` runs the
same three probes as its first checks so an old shell fails with one clear line.

**Python 3.11 or newer**, for the `dict | None` return annotations in the
example modules.

## `dbm` is a real key-value store, and it is already installed

`dbm` is not a toy standing in for the real thing. It is a genuine key-value
store — bytes in, bytes out, addressed by one key — and it is the reason this
lab can measure the key-value trade-off rather than describe it.

Python chooses a backend when it creates the file and tells you which through
`dbm.whichdb()`. On the authoring machine that was `dbm.sqlite3`, the default
since Python 3.13; on many Linux boxes it is `dbm.gnu`. Nothing in this lab
depends on which one you get. Check yours:

```bash
python3 -c "import dbm; print(dbm.whichdb.__module__)"
```

## If the tools are somewhere unusual

The test suite takes overrides rather than guessing:

```bash
PYTHON=/path/to/python3 SQLITE3=/path/to/sqlite3 bash tests/run_tests.sh
```

It fails loudly with that instruction if it cannot find either one, rather than
quietly skipping the checks that need them.

## What is deliberately absent, and this is the important section

**No Redis, MongoDB, Cassandra or DynamoDB.** The lesson covers all four
honestly, from their published documentation, with the commands you would run
against each. It shows **no transcript from any of them**, because none was
installed on the authoring machine and no server was available. Fabricating a
`redis-cli` session would have been easy and would have taught you a fiction.

That absence costs you less than it sounds. Redis at its core is `SET key
value` / `GET key`, which is exactly what `examples/02_key_value_dbm.py` does
with `dbm`; the interesting part — that a question about anything except the
key becomes a scan you write yourself — is identical in both, and here you can
measure it. MongoDB's `find({shelf: "A3"})` is
`examples/04_docstore.py`'s `find("shelf", "A3")`, and building it yourself is
the fastest way to stop treating a document database as magic.

**No client libraries.** `redis-py`, `pymongo` and `cassandra-driver` are all
excellent and all pointless without a server to talk to. Installing them would
give you an import that connects to nothing.

**No Docker.** Running a Redis or MongoDB container is a reasonable way to
explore these stores and the lesson's extension exercises point at it. It is
not a prerequisite here, because a lab that needs a container daemon is a lab
that fails on somebody's locked-down laptop for reasons that have nothing to do
with databases.

**No ORM and no ODM.** SQLAlchemy is Day 93's subject. Meeting the abstraction
before the thing it abstracts is the wrong order, and it is doubly wrong today,
when the whole lesson is about what each shape gives up.
