"""demo_sqlalchemy.py — the same four operations, in SQLAlchemy 2.0.

Run it:  python3 examples/demo_sqlalchemy.py

Everything the toy did, the real library also does — with a great deal more
care. The section numbers here deliberately match `demo_toy.py`, so you can
read the two side by side.
"""

from __future__ import annotations

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable

from counting import QueryCounter
from library import build_engine
from models import Base, Book, Loan, Member, Tag


def rule(label: str) -> None:
    print()
    print(label)
    print("-" * len(label))


def main() -> None:
    import sqlalchemy

    rule("0. Versions actually in use")
    print(f"SQLAlchemy {sqlalchemy.__version__}")
    engine = create_engine("sqlite://")
    with engine.connect() as connection:
        print(f"SQLite      {connection.exec_driver_sql('select sqlite_version()').scalar_one()}")
    print(f"dialect     {engine.dialect.name}, driver {engine.dialect.driver}")
    print(f"pool        {type(engine.pool).__name__}")

    rule("1. The class declaration IS the schema")
    for table in Base.metadata.sorted_tables:
        print(str(CreateTable(table).compile(engine)).strip())

    rule("2. add() makes an object pending — no SQL yet")
    engine = build_engine()
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            member = Member(name="Grace Mensah", email="grace@library.test")
            session.add(member)
            from sqlalchemy import inspect

            state = inspect(member)
            print(f"statements emitted by add(): {len(counted)}")
            print(f"member.id                  : {member.id}   (nobody has decided it yet)")
            print(
                "state -> transient={} pending={} persistent={} detached={}".format(
                    state.transient, state.pending, state.persistent, state.detached
                )
            )

        rule("3. flush() emits the INSERT; commit() ends the transaction")
        with QueryCounter(engine) as counted:
            session.flush()
        print("after flush():")
        print(counted.report())
        print(f"member.id                  : {member.id}   (the database decided it)")
        state = inspect(member)
        print(
            "state -> transient={} pending={} persistent={} detached={}".format(
                state.transient, state.pending, state.persistent, state.detached
            )
        )
        with QueryCounter(engine) as counted:
            session.commit()
        print(f"statements emitted by commit(): {len(counted)}  (COMMIT is not a cursor execute)")

        rule("4. Rows map back into objects")
        with QueryCounter(engine) as counted:
            rows = session.scalars(select(Member).order_by(Member.id)).all()
        print(counted.report())
        for row in rows:
            print(f"    {row}")

        rule("5. The identity map: the same row is the same object")
        with QueryCounter(engine) as counted:
            first = session.get(Member, 1)
            second = session.get(Member, 1)
        print(f"first is second    : {first is second}")
        print(f"statements emitted : {len(counted)}   (already loaded in step 4)")

    rule("6. select(): filtering, ordering, joining, aggregating")
    with Session(engine) as session:
        statement = (
            select(Book.title, Book.author)
            .where(Book.copies >= 3)
            .order_by(Book.title)
        )
        print("Python:")
        print("    select(Book.title, Book.author).where(Book.copies >= 3).order_by(Book.title)")
        print("SQL:")
        print("    " + " ".join(str(statement.compile(engine)).split()))
        print("Rows:")
        for title, author in session.execute(statement):
            print(f"    {title} — {author}")

        rule("7. A join and an aggregate")
        statement = (
            select(Member.name, func.count(Loan.id).label("open_loans"))
            .join(Loan, Loan.member_id == Member.id)
            .where(Loan.returned.is_(False))
            .group_by(Member.id)
            .order_by(func.count(Loan.id).desc(), Member.name)
        )
        print("SQL:")
        print("    " + " ".join(str(statement.compile(engine)).split()))
        print("Rows:")
        for name, open_loans in session.execute(statement):
            print(f"    {name:<16} {open_loans}")

        rule("8. A many-to-many through the secondary table")
        craft = session.scalars(select(Tag).where(Tag.name == "craft")).one()
        print(f"tag: {craft}")
        for book in sorted(craft.books, key=lambda b: b.id):
            print(f"    {book}")

    engine.dispose()


if __name__ == "__main__":
    main()
