# Requirements for the Day 088 lab

## Nothing to install

This lab deliberately has no dependencies. `requirements.txt` lists none, and
running `pip install -r requirements/requirements.txt` would install nothing.

That is a teaching decision, not an oversight. Schema design and migrations are
the area where people reach for a framework earliest, and the reach is often
premature. Before you can judge whether Alembic or Django migrations is worth
its weight, you should have written the hundred and fifty lines it replaces and
seen exactly which problems those lines solve. That is what
`examples/migrate.py` is for.

## What must already be on your machine

| Tool | Why | Check it |
| --- | --- | --- |
| `sqlite3` | The shell every SQL demonstration runs in | `sqlite3 --version` |
| `python3` (3.9+) | The migration runner; standard library only | `python3 --version` |
| `bash` | The test harness | `bash --version` |
| `shasum` | The byte-for-byte rollback proof | `shasum --version` |

On macOS all four are preinstalled. On Debian or Ubuntu, `sqlite3` comes from
the `sqlite3` package and `shasum` from `perl` (or use `sha256sum`, which
`coreutils` provides).

If your tools live somewhere unusual, point the harness at them:

```bash
SQLITE=/opt/homebrew/bin/sqlite3 PYTHON=/usr/local/bin/python3 bash tests/run_tests.sh
```

## The two SQLite versions

`sqlite3` the shell and `python3`'s `sqlite3` module link *separate* copies of
the SQLite library, and they are frequently different versions. The harness
prints both in section 0. On the authoring machine they were 3.51.0 and 3.53.3
respectively — far enough apart that one accepts `ALTER TABLE ... ALTER COLUMN`
and the other rejects it as a syntax error.

Check yours before you rely on any capability:

```bash
sqlite3 :memory: 'SELECT sqlite_version();'
python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'
```

## Versions used for the captures

| Tool | Version | Verified |
| --- | --- | --- |
| macOS | 26.5.2 (Apple Silicon, arm64) | 2026-08-16 |
| `sqlite3` shell | 3.51.0 (`/usr/bin/sqlite3`) | 2026-08-16 |
| Python | 3.14.0, bundled SQLite 3.53.3 | 2026-08-16 |
| bash | 3.2.57 | 2026-08-16 |

Everything in `expected-output/` was produced by these. `expected-output/FIELDS.md`
records which values are fixed facts about SQL and which are properties of this
particular machine.
