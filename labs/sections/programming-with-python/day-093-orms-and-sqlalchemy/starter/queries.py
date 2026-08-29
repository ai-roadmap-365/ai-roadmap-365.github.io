"""Your ORM work — a working skeleton with nine exercises.

This file RUNS right now, and every function in it returns the right answer.
That is the point. **None of the exercises below are about correctness.** They
are about what the ORM sent to the database to get there, which you cannot
see by reading the Python and which the tests measure for you.

Prove the baseline before you change anything. From the lab directory:

    python3 -m venv .venv
    .venv/bin/pip install -r requirements/requirements.txt
    .venv/bin/pytest starter -q

You should see one test pass and nine skipped. Each skipped test names the
exercise that makes it pass. Work through them in order; after each one,
rerun the command above and delete the `@pytest.mark.skip` line from the test
you just satisfied.

What is here already is deliberately the version somebody writes on their
first afternoon with an ORM:

  * filtering and joining in Python, because the objects are right there;
  * touching a relationship inside a loop, which is the N+1 problem written
    in a way that looks completely innocent;
  * reading attributes after the session closed, which raises;
  * changing rows one object at a time when a single statement would do.

Every one of those runs. Every one of those returns the correct answer. The
tests fail on the STATEMENT COUNT, not on the values — which is the habit this
whole lab exists to build.

The reference implementations live in `examples/`. Run them whenever you want
to see where you are heading:

    .venv/bin/python3 examples/demo_n_plus_one.py
    .venv/bin/python3 examples/demo_unit_of_work.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from counting import QueryCounter
from library import build_engine
from models import Book, Loan, Member


# ---------------------------------------------------------------------------
# EXERCISE 1 — filter in the database, not in Python
# ---------------------------------------------------------------------------
def books_with_at_least(session: Session, copies: int) -> list[str]:
    """Titles of every book with at least `copies` copies, alphabetically.

    Right answer, wrong query. This pulls the whole books table across the
    wire and then throws most of it away in Python. On eight books nobody
    notices. On eight million it is the outage.

    EXERCISE 1: rewrite the body as ONE `select()` that does the filtering
                and the ordering in SQL. The shape you want is

                    select(Book.title).where(Book.copies >= copies)
                                      .order_by(Book.title)

                and then `session.scalars(...).all()` to run it.

                The test asserts that exactly one statement is emitted and
                that the emitted SQL contains both WHERE and ORDER BY.
    """
    everything = session.scalars(select(Book)).all()
    matching = [book.title for book in everything if book.copies >= copies]
    return sorted(matching)


# ---------------------------------------------------------------------------
# EXERCISE 2 — let the database do the join and the counting
# ---------------------------------------------------------------------------
def open_loan_counts(session: Session) -> list[tuple[str, int]]:
    """(member name, number of unreturned loans), busiest first, then by name.

    EXERCISE 2: replace the two queries and the Python bookkeeping with ONE
                `select()` that joins members to loans, filters on
                `Loan.returned.is_(False)`, groups by `Member.id`, and orders
                by the count descending then the name. You will want
                `func.count` — import it with `from sqlalchemy import func`.

                Careful: a plain JOIN drops members with no open loans. This
                naive version keeps them at zero, and the test checks that all
                six members appear. Use `outerjoin` and count `Loan.id`, which
                counts non-NULL values and therefore gives 0 rather than 1 for
                a member with no matching loan row.

                The test asserts exactly one statement and all six members.
    """
    members = session.scalars(select(Member).order_by(Member.id)).all()
    loans = session.scalars(select(Loan).where(Loan.returned.is_(False))).all()
    tally: dict[int, int] = {member.id: 0 for member in members}
    for loan in loans:
        tally[loan.member_id] += 1
    named = [(member.name, tally[member.id]) for member in members]
    return sorted(named, key=lambda pair: (-pair[1], pair[0]))


# ---------------------------------------------------------------------------
# EXERCISE 3 — the N+1, fixed with selectinload
# ---------------------------------------------------------------------------
def member_loan_totals(session: Session) -> list[tuple[str, int]]:
    """(member name, total loans ever), in id order.

    This is the N+1 problem, and notice how ordinary it looks. `member.loans`
    reads like a list attribute. It is a SELECT, issued the first time you
    touch it, once per member.

    EXERCISE 3: keep the loop — the loop is fine and readable — and change
                only the query that feeds it, so the relationship is loaded up
                front:

                    from sqlalchemy.orm import selectinload
                    select(Member).options(selectinload(Member.loans))
                                  .order_by(Member.id)

                The test asserts EXACTLY 2 statements: one for the members,
                one for all their loans. Not 7. And not 1 — selectinload
                deliberately uses a second query rather than a join.
    """
    members = session.scalars(select(Member).order_by(Member.id)).all()
    return [(member.name, len(member.loans)) for member in members]


# ---------------------------------------------------------------------------
# EXERCISE 4 — the many-to-one N+1, fixed with joinedload
# ---------------------------------------------------------------------------
def loan_titles(session: Session) -> list[str]:
    """The book title for every loan, in loan id order.

    Same defect, different relationship. `loan.book` is many-to-one: every
    loan has exactly one book, so a JOIN cannot multiply the rows, which makes
    this the case joinedload was designed for.

    EXERCISE 4: load the relationship with `joinedload(Loan.book)`:

                    from sqlalchemy.orm import joinedload
                    select(Loan).options(joinedload(Loan.book)).order_by(Loan.id)

                The test asserts EXACTLY 1 statement. Note you do NOT need
                `.unique()` here, because a many-to-one join returns one row
                per loan. Exercise 3's collection would have needed it.
    """
    loans = session.scalars(select(Loan).order_by(Loan.id)).all()
    return [loan.book.title for loan in loans]


# ---------------------------------------------------------------------------
# EXERCISE 5 — flush is not commit
# ---------------------------------------------------------------------------
def flush_then_commit(path: Path) -> tuple[int, int, int]:
    """Add one member; report what a SEPARATE connection can see at each step.

    Returns (before_flush, after_flush, after_commit) — three row counts, each
    read through `peek(path)`, which opens its own sqlite3 connection that
    SQLAlchemy knows nothing about.

    This version calls `commit()` straight away, so it never shows the
    interesting middle state.

    EXERCISE 5: split the write into an explicit `session.flush()` and then a
                `session.commit()`, taking a `peek(path)` reading between
                them. The result should be (6, 6, 7): the INSERT really was
                sent at the flush, and the other connection really could not
                see it until the commit, because it was inside an open
                transaction.

                The test asserts that triple exactly.
    """
    engine = build_engine(f"sqlite:///{path}")
    try:
        before = peek(path)
        with Session(engine) as session:
            session.add(Member(name="Grace Mensah", email="grace@library.test"))
            session.commit()
            after_flush = peek(path)
        after_commit = peek(path)
        return (before, after_flush, after_commit)
    finally:
        engine.dispose()


def peek(path: Path) -> int:
    """How many members a connection outside SQLAlchemy's control can see."""
    connection = sqlite3.connect(path)
    try:
        return connection.execute("SELECT count(*) FROM members").fetchone()[0]
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# EXERCISE 6 — the four object states
# ---------------------------------------------------------------------------
def state_sequence(engine: Engine) -> list[str]:
    """The state of one Member after construct, add, flush and close.

    Nearly every confusing ORM error is a question about which of these an
    object is in, so being able to name them on demand is worth the five
    minutes.

    EXERCISE 6: return the four state names as strings, in order, by asking
                SQLAlchemy rather than by hard-coding them:

                    from sqlalchemy import inspect
                    inspect(member).transient / .pending / .persistent / .detached

                Write a small helper that returns the name of whichever flag
                is True. The expected answer is
                ["transient", "pending", "persistent", "detached"] — but the
                test also checks you did not simply return that literal list,
                by running the same helper against an object it manipulates
                itself.
    """
    session = Session(engine)
    member = Member(name="Hana Ito", email="hana@library.test")
    session.add(member)
    session.flush()
    session.commit()
    session.close()
    return ["unknown", "unknown", "unknown", "unknown"]


def state_of(instance: object) -> str:
    """Name the state of one mapped object.

    EXERCISE 6 (part two): implement this. `state_sequence` should call it
    four times, and the test calls it directly on objects of its own.
    """
    return "unknown"


# ---------------------------------------------------------------------------
# EXERCISE 7 — DetachedInstanceError, fixed by not expiring
# ---------------------------------------------------------------------------
def name_after_close(engine: Engine) -> str:
    """Read a member's name AFTER the session that loaded it has closed.

    Run this as it stands and it raises DetachedInstanceError. That is not a
    bug being demonstrated for fun — it is the single most common wall a
    beginner hits, and it has a precise cause: `commit()` expires every loaded
    attribute so the next read will be fresh, and `close()` then takes away
    the connection that read would have used.

    EXERCISE 7: fix it WITHOUT loading anything extra, by telling the session
                not to expire attributes on commit:

                    with Session(engine, expire_on_commit=False) as session:

                Then `member.name` is still readable afterwards, because the
                value that was already loaded was never thrown away.

                The test asserts the name comes back as 'Ada Okonkwo' and no
                exception escapes.
    """
    with Session(engine) as session:
        member = session.get(Member, 1)
        session.commit()
    return member.name


# ---------------------------------------------------------------------------
# EXERCISE 8 — DetachedInstanceError, fixed by eager loading
# ---------------------------------------------------------------------------
def loan_count_after_close(engine: Engine) -> int:
    """How many loans member 1 has, counted AFTER the session closed.

    This raises too, and for a related but genuinely different reason: a lazy
    relationship is a SELECT waiting to happen, and the session it was waiting
    for is gone. `expire_on_commit=False` would NOT save you here, because the
    relationship was never loaded in the first place — there is nothing to
    keep.

    EXERCISE 8: fix it by deciding in advance that you need the loans, and
                loading them while the session is open:

                    select(Member).options(selectinload(Member.loans))
                                  .where(Member.id == 1)

                then `session.scalars(...).one()`.

                The test asserts the answer is 4, and — the part that matters —
                that ZERO statements are emitted after the session closes,
                because there is no session left to emit them.
    """
    with Session(engine) as session:
        member = session.get(Member, 1)
    return len(member.loans)


# ---------------------------------------------------------------------------
# EXERCISE 9 — when to stop using the ORM
# ---------------------------------------------------------------------------
def close_all_open_loans(session: Session) -> int:
    """Mark every unreturned loan as returned. Return the number changed.

    The ORM way below is correct and it is readable, and it does something you
    may not want: it SELECTs every matching row and builds a Python object for
    each one, purely so it can set a flag. With thirteen rows that is nothing.
    With a million it is a memory incident.

    EXERCISE 9: replace the body with one Core UPDATE:

                    from sqlalchemy import update
                    result = session.execute(
                        update(Loan).where(Loan.returned.is_(False))
                                    .values(returned=True)
                    )
                    return result.rowcount

                The test asserts exactly ONE cursor execution and a rowcount
                of 13. Read `examples/demo_bulk.py` afterwards for the price
                you just paid: nothing you wrote in Python runs for those
                rows, because no object was ever created.
    """
    changed = 0
    for loan in session.scalars(select(Loan).where(Loan.returned.is_(False))):
        loan.returned = True
        changed += 1
    session.flush()
    return changed


__all__ = [
    "QueryCounter",
    "books_with_at_least",
    "build_engine",
    "close_all_open_loans",
    "flush_then_commit",
    "loan_count_after_close",
    "loan_titles",
    "member_loan_totals",
    "name_after_close",
    "open_loan_counts",
    "peek",
    "state_of",
    "state_sequence",
]
