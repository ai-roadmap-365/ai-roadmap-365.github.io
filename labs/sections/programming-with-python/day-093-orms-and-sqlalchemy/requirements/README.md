# Dependencies for the Day 093 lab

Two packages, both free and open source, both installed from the Python
Package Index with `pip`, both running entirely on your own machine.

| Package | Pinned version | Why this lab needs it |
| --- | --- | --- |
| `SQLAlchemy` | `2.0.51` | The library the lesson is about. It provides both layers the lesson separates: Core, an SQL expression language, and the ORM built on top of it. |
| `pytest` | `9.1.1` | The test runner from Days 071–074. Nothing new today except what it is pointed at — statement counts rather than return values. |

One package arrives that nobody asked for. `typing_extensions` (4.16.0 here)
is a SQLAlchemy dependency and is deliberately **not** pinned: SQLAlchemy
itself constrains which versions it accepts, and pinning a transitive
dependency separately is how you eventually get an unsolvable conflict.

The pinned numbers were read from the installed packages rather than assumed:

```bash
.venv/bin/python3 -c "from importlib.metadata import version; print(version('SQLAlchemy'), version('pytest'))"
```

On the authoring machine, on 16 August 2026, that printed `2.0.51 9.1.1`, and
section 1 of `tests/run_tests.sh` reprints the installed version and compares
it against `requirements.txt` — so a mismatch is reported at the top of the
run rather than discovered later as a mysterious count.

## What is deliberately absent

**Alembic**, SQLAlchemy's migration tool, is **not installed and not used
here.** The lesson describes what it does from its documentation and says
plainly that no output is reproduced for it. That is not an oversight — it is
a scope decision, because migrations are a Day 88 topic that deserves its own
treatment against a real ORM rather than a paragraph at the end of this one.

Section 1 of the test suite checks that Alembic is still absent. If somebody
installs it into this environment, the suite fails, because at that point the
lesson's honesty note would need rewriting rather than quietly becoming false.

**No database driver is installed either**, and none is needed. Every database
in this lab is SQLite, reached through `sqlite3` in the Python standard
library, which SQLAlchemy uses as its default driver for the `sqlite://` URL.
Nothing here talks to PostgreSQL or MySQL. Where the lesson mentions them, it
mentions them as documented behaviour and claims no measurement.

## Licences

SQLAlchemy is distributed under the MIT licence and pytest under the MIT
licence, each stated on the project's own documentation. Both are maintained
in the open, cost nothing, and need no account, no key and no signup —
personally or commercially.

## One-time install

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

Expect `2.0.51`. Day 43 covered `python3 -m venv` in full; this is the same
pattern. The environment lives in `.venv/` inside the lab, is already excluded
from version control, and can be deleted at any time with `rm -rf .venv`.

## Network

Installing needs the network, once. **Nothing else in this lab does.** Every
database here is either in memory (`sqlite://`) or a file in a temporary
directory that is deleted on the way out, and `starter/conftest.py` arms a
guard that raises if anything tries to open a socket. Section 9 of
`tests/run_tests.sh` proves that guard is armed by tripping it deliberately.

## Running without a lab-local environment

If you already have SQLAlchemy 2.x and pytest available in an environment you
have activated, the test runner will find them on your `PATH`. You can also
point it at specific binaries:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The runner checks that SQLAlchemy is importable from the interpreter it
resolved, and **stops with install instructions rather than skipping checks
quietly** if it is not. A test suite that silently skips the only thing it was
written to test is worse than one that fails.

## If your SQLAlchemy is a different version

Every statement count in `expected-output/` was captured on 2.0.51. The counts
in sections 2 to 5 of the harness are properties of how the ORM works and
should hold across 2.x. The **bulk** counts in section 6 are the ones most
likely to move, because how many rows SQLAlchemy packs into one `executemany`
is an implementation decision that has changed across releases and varies by
dialect. `expected-output/FIELDS.md` says exactly which numbers are structural
and which are version-specific.
