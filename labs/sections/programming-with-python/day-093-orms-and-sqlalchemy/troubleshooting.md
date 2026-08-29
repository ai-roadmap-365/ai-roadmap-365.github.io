# Troubleshooting — Day 093

Almost every problem on this day is one of three things: the environment is
not the one you think it is, the session is not open any more, or the query
count is not what you expected. This file is organised that way.

## The environment

### `ModuleNotFoundError: No module named 'sqlalchemy'`

The interpreter you ran is not the one the packages were installed into. From
the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

Then run everything with `.venv/bin/python3`, not with a bare `python3`.
`tests/run_tests.sh` resolves this for you — it prefers `.venv/bin/python3`
over whatever is on your `PATH` — but the demos do not, because they are meant
to be run by hand.

### `ModuleNotFoundError: No module named 'models'`

The demos import `models`, `library` and `counting` as plain modules, so
`examples/` has to be importable. Two ways, both fine:

```bash
PYTHONPATH=examples .venv/bin/python3 examples/demo_toy.py
```

or run from inside the directory:

```bash
cd examples && ../.venv/bin/python3 demo_toy.py
```

`starter/conftest.py` does this for you when you run pytest, which is why the
exercises need no such incantation.

### `FAIL: SQLAlchemy is not importable from ...` and the suite stops

That is the harness refusing to pretend. This lab is about SQLAlchemy, so
there is nothing to fall back on and skipping the checks would be a lie about
coverage. Install the pinned version, or point the suite at an interpreter
that already has it:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

### The version check fails at the top of the run

`requirements/requirements.txt` pins `SQLAlchemy==2.0.51` and the suite
compares that against what actually loaded. If you deliberately installed a
different 2.x version, expect the counts in section 6 (bulk) to be the ones
most likely to differ — see `expected-output/FIELDS.md`, which says which
numbers are structural and which are version-specific.

### The Alembic check fails

Section 1 asserts that Alembic is **not** installed, because the lesson says
plainly that no Alembic output is reproduced here. If you install Alembic into
this environment, that statement stops being the whole truth and the suite
fails rather than letting the text go quietly stale. Either use a separate
environment for your Alembic experiments, or accept that this one check will
fail and know exactly why.

## The session

### `DetachedInstanceError: Instance <X> is not bound to a Session`

This is the day's signature error and it has two distinct causes that need two
distinct fixes. Read the rest of the message, because it tells you which one
you have.

**"attribute refresh operation cannot proceed"** — you are reading a plain
column after the session closed. `commit()` expired every loaded attribute so
the next read would be fresh, and `close()` then removed the connection that
read needed. The value was there; it was thrown away deliberately.

Fix: `Session(engine, expire_on_commit=False)`. Now the loaded values survive
the commit, because nothing expires them.

**"lazy load operation of attribute 'loans' cannot proceed"** — you are
touching a relationship that was never loaded. `expire_on_commit=False` will
**not** help here, and this is the trap: there is nothing to keep, because the
relationship was always going to be a separate SELECT and that SELECT never
happened.

Fix: decide in advance that you need it, and load it while the session is
open:

```python
select(Member).options(selectinload(Member.loans)).where(Member.id == 1)
```

Section 4 and 5 of `examples/demo_unit_of_work.py` provoke both and fix both.

### SQL appears at a line where I never wrote a query

That is **autoflush**. Any query on a session with pending changes flushes
those changes first, so the query can see them. It is nearly always what you
want and it is occasionally very surprising — particularly inside a loop that
both reads and writes. Section 3 of `demo_unit_of_work.py` shows it happening.

If you genuinely need to query without flushing, `with session.no_autoflush:`
suspends it for a block. Reach for that rarely and comment why.

### My row is in the database but another connection cannot see it

You flushed; you did not commit. The INSERT really was sent, and it is sitting
inside an open transaction that nobody else can read. This is correct
behaviour and it is the entire point of section 2 of `demo_unit_of_work.py`.

`flush()` sends SQL. `commit()` ends the transaction. They are different verbs
and confusing them costs an afternoon exactly once.

### `sqlite3.OperationalError: database is locked`

Two connections want to write the same SQLite file at once. In this lab that
means you left a session open somewhere with an uncommitted transaction — most
likely by constructing a `Session(engine)` without `close()` instead of using
`with Session(engine) as session:`. Use the context manager; it closes on the
way out even when something raises.

## The query count

### I expected 2 statements and got 7

The relationship is still lazy. `selectinload` has to be attached to the query
that loads the parent objects, not to the loop that reads them:

```python
select(Member).options(selectinload(Member.loans)).order_by(Member.id)
```

If you attach it and still see 1 + N, check that you are counting around the
loop and not just around the query. The lazy loads happen when the attribute
is touched, which is later than you think.

### I expected 2 and got 1

You used `joinedload` where the test wanted `selectinload`. Both fix the N+1
and they fix it differently on purpose: `joinedload` adds an OUTER JOIN to the
one query, `selectinload` sends a second query with an `IN` clause. One
statement is not automatically better — see the next entry.

### `InvalidRequestError: The unique() method must be invoked on this Result`

You used `joinedload` on a **collection**. The JOIN really does return one row
per child, so the driver hands back 24 rows for 6 members, and SQLAlchemy
refuses to guess whether you wanted 6 objects or 24. Add `.unique()`:

```python
session.scalars(statement).unique().all()
```

You do not need it for a many-to-one (`joinedload(Loan.book)`), because each
loan has exactly one book and no multiplication can occur. Section 5 of
`demo_n_plus_one.py` provokes the error and shows the 24-against-6 arithmetic
behind it.

### My many-to-one N+1 is 9 statements, not 25

That is the identity map doing its job. 24 loans point at only 8 distinct
books, and once a book is loaded the second loan that references it is
answered from memory without SQL. So the cost of a lazy many-to-one is 1 plus
the number of **distinct** parents, not 1 plus the number of children. It is
still an N+1; it is just a smaller N than you feared.

### The bulk numbers on my machine are different

How many rows SQLAlchemy packs into a single `executemany` is an
implementation decision that has changed across 2.x releases and differs by
database dialect. The property the lab teaches — a flush per row is orders of
magnitude more round trips than one batched flush — holds anywhere. The exact
figure `1` does not. `expected-output/FIELDS.md` marks this explicitly as
version-specific.

## The tests

### `expected-output/<name>.txt differs from this run`

You changed something in `examples/`. That check is strict on purpose: the
lab's claim is that emitted SQL is stable and observable, and a capture
allowed to drift proves nothing. If the change was intended, re-capture:

```bash
PYTHONPATH=examples .venv/bin/python3 examples/demo_toy.py > expected-output/toy.txt 2>&1
```

and do the same for the other four. Then read the diff before you commit it —
a changed statement count is exactly the kind of regression this lab exists to
catch.

### `pytest starter` reports 1 passed, 9 skipped and I have done the work

Delete the `@pytest.mark.skip(...)` line above the test you just satisfied.
The skips are the ladder; removing them is part of the exercise.

### A test fails on the count but my answer is correct

That is the lab working. Every starter exercise already returns the right
value — the whole point is that correctness is not the thing being measured.
Read the failure message; each one says what count it wanted and what a wrong
count usually means.

## Platform

- **macOS and Linux** — everything here was written to run on both. Only macOS
  26.5.2 on Apple Silicon was actually exercised for the captures.
- **Windows** — use WSL and follow the Linux instructions. `tests/run_tests.sh`
  is bash and uses `mktemp -d`; it was not run on native Windows and no
  behaviour is claimed for it there. The Python files use `pathlib` and
  `tempfile` throughout and have no Unix dependency of their own.
- **bash 3.2**, which macOS still ships, mis-parses a `case` statement inside
  `$( )`. The harness avoids the construct and says so in a comment where it
  matters. If you extend the suite, avoid it too.
