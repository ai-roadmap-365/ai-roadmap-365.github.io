"""Your exercise suite. One test passes now; nine are waiting for you.

Run it from the lab directory:

    .venv/bin/pytest starter -q

Each skipped test names the exercise in `queries.py` that makes it pass. Do
the exercise, delete that test's `@pytest.mark.skip(...)` line, rerun. When
all nine are green, you have written the ORM code the lesson argues for and
you have proved it by counting statements rather than by trusting the output.

**Read this before you start, because it is the transferable lesson:** almost
every assertion below is on a COUNT of statements, never on a duration. A
timing assertion is a flake waiting for a loaded machine, and it names no
cause — "this took 240 ms" is a mood. A count is deterministic, identical on
every machine, and it names the defect directly: "this loop issued seven
queries where two would do" is a bug report you can act on.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from counting import QueryCounter
from library import build_engine
from queries import (
    books_with_at_least,
    close_all_open_loans,
    flush_then_commit,
    loan_count_after_close,
    loan_titles,
    member_loan_totals,
    name_after_close,
    open_loan_counts,
    state_of,
    state_sequence,
)
from sqlalchemy.orm import Session


@pytest.fixture
def engine():
    made = build_engine()
    yield made
    made.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as opened:
        yield opened


def test_the_seed_is_what_we_think_it_is(session) -> None:
    """This one passes already. It is your green baseline: if it ever fails,
    the problem is your setup rather than your code."""
    from models import Book, Loan, Member, Tag
    from sqlalchemy import func, select

    counts = {
        "members": session.scalar(select(func.count()).select_from(Member)),
        "books": session.scalar(select(func.count()).select_from(Book)),
        "tags": session.scalar(select(func.count()).select_from(Tag)),
        "loans": session.scalar(select(func.count()).select_from(Loan)),
    }
    assert counts == {"members": 6, "books": 8, "tags": 4, "loans": 24}


@pytest.mark.skip(reason="Exercise 1: filter in the database, not in Python")
def test_books_with_at_least_filters_in_sql(engine, session) -> None:
    with QueryCounter(engine) as counted:
        titles = books_with_at_least(session, 3)

    assert titles == [
        "Clean Code",
        "Introduction to Algorithms",
        "The C Programming Language",
    ]
    assert len(counted) == 1, f"expected one statement, got {len(counted)}"
    emitted = counted.statements[0].upper()
    assert "WHERE" in emitted, "the filter is still happening in Python"
    assert "ORDER BY" in emitted, "the sort is still happening in Python"


@pytest.mark.skip(reason="Exercise 2: one grouped outer join instead of two queries")
def test_open_loan_counts_is_one_grouped_query(engine, session) -> None:
    with QueryCounter(engine) as counted:
        rows = open_loan_counts(session)

    assert len(counted) == 1, f"expected one statement, got {len(counted)}"
    assert len(rows) == 6, "every member must appear, including any with none open"
    assert rows[0] == ("Ada Okonkwo", 3)
    assert sum(count for _, count in rows) == 13
    emitted = counted.statements[0].upper()
    assert "GROUP BY" in emitted, "the grouping is still happening in Python"
    assert "JOIN" in emitted, "the join is still happening in Python"


@pytest.mark.skip(reason="Exercise 3: fix the N+1 with selectinload")
def test_member_loan_totals_is_exactly_two_statements(engine, session) -> None:
    with QueryCounter(engine) as counted:
        rows = member_loan_totals(session)

    assert rows == [
        ("Ada Okonkwo", 4),
        ("Bruno Sartori", 3),
        ("Chen Wei", 4),
        ("Divya Ramanan", 4),
        ("Emeka Balogun", 4),
        ("Farida Haddad", 5),
    ]
    assert len(counted) == 2, (
        f"expected exactly 2 statements, got {len(counted)}. "
        "7 means the relationship is still lazy; 1 means you used joinedload, "
        "which works but is not what selectinload does."
    )


@pytest.mark.skip(reason="Exercise 4: fix the many-to-one N+1 with joinedload")
def test_loan_titles_is_exactly_one_statement(engine, session) -> None:
    with QueryCounter(engine) as counted:
        titles = loan_titles(session)

    assert len(titles) == 24
    assert titles[0] == "The C Programming Language"
    assert len(set(titles)) == 8
    assert len(counted) == 1, (
        f"expected exactly 1 statement, got {len(counted)}. A many-to-one "
        "joinedload cannot multiply rows, so one query is the whole job."
    )


@pytest.mark.skip(reason="Exercise 5: separate the flush from the commit")
def test_flush_is_not_commit() -> None:
    workdir = Path(tempfile.mkdtemp(prefix="day093-starter-"))
    try:
        result = flush_then_commit(workdir / "library.db")
    finally:
        for leftover in sorted(workdir.glob("library.db*")):
            leftover.unlink()
        workdir.rmdir()

    assert result == (6, 6, 7), (
        f"expected (6, 6, 7), got {result}. The middle number is the point: "
        "the INSERT had been sent, and an outside connection still could not "
        "see it, because the transaction was open."
    )


@pytest.mark.skip(reason="Exercise 6: name the four object states")
def test_state_sequence_and_state_of(engine) -> None:
    assert state_sequence(engine) == [
        "transient",
        "pending",
        "persistent",
        "detached",
    ]

    # And prove `state_of` really inspects, rather than returning a script.
    from models import Member

    fresh = Member(name="Ivan Petrov", email="ivan@library.test")
    assert state_of(fresh) == "transient"
    with Session(engine) as opened:
        opened.add(fresh)
        assert state_of(fresh) == "pending"
        opened.flush()
        assert state_of(fresh) == "persistent"
        opened.rollback()


@pytest.mark.skip(reason="Exercise 7: fix the detached read with expire_on_commit")
def test_name_readable_after_close(engine) -> None:
    assert name_after_close(engine) == "Ada Okonkwo"


@pytest.mark.skip(reason="Exercise 8: fix the detached relationship with selectinload")
def test_loans_readable_after_close(engine) -> None:
    with QueryCounter(engine) as counted:
        total = loan_count_after_close(engine)
        emitted_inside = len(counted)

    assert total == 4
    # Everything must have been loaded before the session closed. If the
    # relationship were still lazy this would have raised rather than counted.
    assert emitted_inside == 2, (
        f"expected 2 statements (members, then their loans), got {emitted_inside}"
    )


@pytest.mark.skip(reason="Exercise 9: one Core UPDATE instead of an object loop")
def test_close_all_open_loans_is_one_statement(engine, session) -> None:
    with QueryCounter(engine) as counted:
        changed = close_all_open_loans(session)
    session.rollback()

    assert changed == 13
    assert len(counted) == 1, (
        f"expected exactly 1 cursor execution, got {len(counted)}. Two means "
        "you are still SELECTing the rows in order to change them."
    )
    assert counted.statements[0].upper().startswith("UPDATE")
