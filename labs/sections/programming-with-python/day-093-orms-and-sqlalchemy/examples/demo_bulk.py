"""demo_bulk.py — where the ORM stops being the right tool, measured honestly.

Run it:  python3 examples/demo_bulk.py

An ORM's job is to track individual objects through a unit of work. That is
the wrong shape for "change five hundred rows", and this script measures by
how much — but the measurement is more interesting than the folklore, so read
the numbers rather than the slogan.

Two numbers are recorded for every approach, and keeping them apart is the
whole lesson of this file:

  * **cursor executions** — how many times a statement was handed to the
    driver. This is the round-trip count, and it is what people mean when they
    say "number of queries".
  * **parameter sets** — how many rows those executions carried. One
    `executemany` call is ONE execution carrying five hundred rows.

Conflate the two and you will reach a conclusion the machine does not support.
"""

from __future__ import annotations

from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from counting import QueryCounter
from library import build_engine
from models import Loan

ROWS = 500


def rule(label: str) -> None:
    print()
    print(label)
    print("-" * len(label))


def new_loans(start_id: int, count: int = ROWS) -> list[dict]:
    return [
        {
            "id": start_id + offset,
            "book_id": (offset % 8) + 1,
            "member_id": (offset % 6) + 1,
            "borrowed_on": "2026-08-01",
            "due_on": "2026-08-22",
            "returned": False,
        }
        for offset in range(count)
    ]


def summarise(counted: QueryCounter) -> str:
    return (
        f"{len(counted)} cursor execution(s), "
        f"{counted.rows_sent()} parameter set(s), "
        f"{counted.executemany_count()} of them batched"
    )


def main() -> None:
    rule(f"1. Inserting {ROWS} rows the naive way: add() and flush() in the loop")
    engine = build_engine()
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            for row in new_loans(1001):
                session.add(Loan(**row))
                session.flush()
        session.rollback()
    naive = len(counted)
    print(summarise(counted))
    print(f"    {counted.statements[0]}")
    print(f"    ... and {naive - 1} more identical statements")
    print("  One round trip per row. This is the mistake, and it is a mistake")
    print("  about WHERE the flush goes, not about the ORM.")
    engine.dispose()

    rule(f"2. Inserting {ROWS} rows with add_all() and ONE flush")
    engine = build_engine()
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            session.add_all([Loan(**row) for row in new_loans(1001)])
            session.flush()
        session.rollback()
    batched = len(counted)
    batched_rows = counted.rows_sent()
    print(summarise(counted))
    print("  The unit of work sorted the pending objects by table and batched")
    print("  them into a single executemany. Still the ORM: every object is")
    print("  tracked, every identity registered, every default applied.")
    engine.dispose()

    rule(f"3. Inserting {ROWS} rows through Core")
    engine = build_engine()
    with engine.begin() as connection:
        with QueryCounter(engine) as counted:
            connection.execute(insert(Loan), new_loans(1001))
    core = len(counted)
    core_rows = counted.rows_sent()
    print(summarise(counted))
    print(f"    {counted.statements[0][:96]}...")
    engine.dispose()

    rule("4. What the insert numbers actually say")
    print(f"    add() + flush() per row   {naive:>4} execution(s)   {ROWS:>4} row(s)")
    print(f"    add_all() + one flush     {batched:>4} execution(s)   {batched_rows:>4} row(s)")
    print(f"    Core insert(), one call   {core:>4} execution(s)   {core_rows:>4} row(s)")
    print()
    print("  Read that carefully, because it contradicts the usual advice.")
    print("  On this version, batched ORM inserts and Core inserts issue the")
    print("  SAME number of cursor executions. The dramatic gap is between the")
    print("  naive loop and everything else — it is 500 against 1.")
    print()
    print("  So 'drop to Core for speed' is not what the execution count shows.")
    print("  What Core actually saves here is Python-side work the counter")
    print("  cannot see: no Loan instances are constructed, nothing enters the")
    print("  identity map, and the unit of work has no dependency graph to")
    print("  sort. That is real, and it is a memory and CPU argument rather")
    print("  than a round-trip argument. Measure it before you claim it.")

    rule("5. Updating every open loan — where Core genuinely wins")
    engine = build_engine()
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            loaded = 0
            for loan in session.scalars(select(Loan).where(Loan.returned.is_(False))):
                loan.returned = True
                loaded += 1
            session.flush()
        session.rollback()
    orm_update = len(counted)
    print(f"ORM, object by object : {summarise(counted)}")
    print(f"                        {loaded} Loan objects built in memory")
    print(counted.report())
    engine.dispose()

    engine = build_engine()
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            result = session.execute(
                update(Loan).where(Loan.returned.is_(False)).values(returned=True)
            )
            changed = result.rowcount
        session.rollback()
    core_update = len(counted)
    print(f"Core UPDATE           : {summarise(counted)}")
    print(f"                        0 Loan objects built, {changed} rows changed")
    print(counted.report())
    print("  Note the shape of the difference. The ORM had to SELECT the rows")
    print("  first, because it changes objects and it has no objects until it")
    print("  loads them. Core changes rows, so it never reads them.")
    engine.dispose()

    rule("6. That difference grows with the row count; the insert one does not")
    engine = build_engine()
    with Session(engine) as session:
        session.execute(insert(Loan), new_loans(2001, 1000))
        session.commit()
        with QueryCounter(engine) as counted:
            loaded = 0
            for loan in session.scalars(select(Loan).where(Loan.returned.is_(False))):
                loan.returned = True
                loaded += 1
            session.flush()
        session.rollback()
    print(f"ORM with ~1000 more open loans : {summarise(counted)}")
    print(f"                                 {loaded} Loan objects built in memory")
    engine.dispose()

    engine = build_engine()
    with Session(engine) as session:
        session.execute(insert(Loan), new_loans(2001, 1000))
        session.commit()
        with QueryCounter(engine) as counted:
            changed = session.execute(
                update(Loan).where(Loan.returned.is_(False)).values(returned=True)
            ).rowcount
        session.rollback()
    print(f"Core with the same rows        : {summarise(counted)}")
    print(f"                                 0 Loan objects built, {changed} rows changed")
    print("  The execution counts barely move. The object count moves by a")
    print("  thousand. THAT is the bulk-operation argument, stated in the")
    print("  units it is actually true in.")
    engine.dispose()

    rule("7. The honest summary")
    print("  * Never flush inside a loop. That is the only order-of-magnitude")
    print("    round-trip win available here, and it is free.")
    print("  * A batched ORM insert costs the same round trips as Core. Choose")
    print("    Core for it when you do not want the objects, not for the count.")
    print("  * A bulk UPDATE or DELETE is different: the ORM must load rows to")
    print("    change them and Core does not, so Core avoids work that scales")
    print("    with the number of matching rows.")
    print("  * The price of Core is that no Python-level default, validator or")
    print("    event of yours runs, because no object was ever created. That is")
    print("    a design decision, not an optimisation.")


if __name__ == "__main__":
    main()
