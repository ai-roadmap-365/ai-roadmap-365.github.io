"""demo_unit_of_work.py — object states, autoflush, flush versus commit.

Run it:  python3 examples/demo_unit_of_work.py

Almost every confusing ORM error is really a question about one of three
things: which state an object is in, when the flush happened, and whether the
session that loaded the object is still open. This script makes all three
visible, using a real file-backed database so that a genuinely separate
connection can be asked what it can see.

The database is created in a temporary directory and deleted on the way out.
"""

from __future__ import annotations

import re
import sqlite3
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.orm.exc import DetachedInstanceError

from counting import QueryCounter
from library import build_engine
from models import Member


def rule(label: str) -> None:
    print()
    print(label)
    print("-" * len(label))


def first_line(error: Exception) -> str:
    """The message, with the object's memory address replaced so output is stable."""
    return re.sub(r"0x[0-9a-f]+", "0xADDR", str(error).splitlines()[0])


def state_of(instance) -> str:
    state = inspect(instance)
    for name in ("transient", "pending", "persistent", "deleted", "detached"):
        if getattr(state, name):
            return name
    return "unknown"


def peek_with_a_second_connection(path: Path) -> list[str]:
    """Read the members table through a connection SQLAlchemy knows nothing about."""
    connection = sqlite3.connect(path)
    try:
        rows = connection.execute("SELECT name FROM members ORDER BY id").fetchall()
        return [row[0] for row in rows]
    finally:
        connection.close()


def main() -> None:
    workdir = Path(tempfile.mkdtemp(prefix="day093-"))
    path = workdir / "library.db"
    try:
        engine = build_engine(f"sqlite:///{path}")

        rule("1. The four states of a mapped object")
        session = Session(engine)
        member = Member(name="Grace Mensah", email="grace@library.test")
        print(f"just constructed          -> {state_of(member)}")
        session.add(member)
        print(f"after session.add()       -> {state_of(member)}")
        session.flush()
        print(f"after session.flush()     -> {state_of(member)}   id={member.id}")
        session.commit()
        print(f"after session.commit()    -> {state_of(member)}")
        session.close()
        print(f"after session.close()     -> {state_of(member)}")

        rule("2. flush is not commit — asked of a second, independent connection")
        session = Session(engine)
        session.add(Member(name="Hana Ito", email="hana@library.test"))
        print(f"before flush, other connection sees: {peek_with_a_second_connection(path)[-1]!r} last")
        with QueryCounter(engine) as counted:
            session.flush()
        print("flush emitted:")
        print(counted.report())
        seen = peek_with_a_second_connection(path)
        print(f"after flush, other connection sees : {len(seen)} members, last {seen[-1]!r}")
        print("  The INSERT was sent. The transaction is open. Nobody else can see it.")
        session.commit()
        seen = peek_with_a_second_connection(path)
        print(f"after commit, other connection sees: {len(seen)} members, last {seen[-1]!r}")
        session.close()

        rule("3. Autoflush — a query flushes your pending work first")
        session = Session(engine)
        session.add(Member(name="Ivan Petrov", email="ivan@library.test"))
        print("added one pending Member, then ran an unrelated SELECT:")
        with QueryCounter(engine) as counted:
            session.scalars(select(Member).where(Member.name.like("I%"))).all()
        print(counted.report())
        print("  The INSERT was emitted first, so the SELECT could see it.")
        print("  That is autoflush, and it is why SQL appears at lines you never wrote.")
        session.rollback()
        session.close()

        rule("4. DetachedInstanceError, provoked on a scalar attribute")
        session = Session(engine)
        ada = session.get(Member, 1)
        session.commit()
        session.close()
        try:
            print(ada.name)
        except DetachedInstanceError as error:
            print("raised DetachedInstanceError:")
            print(f"    {first_line(error)}")
        print("  commit() expired every attribute; close() removed the connection")
        print("  that would have refreshed them. Nothing is left to read.")

        print("  Fix A — tell the session not to expire on commit:")
        with Session(engine, expire_on_commit=False) as session:
            ada = session.get(Member, 1)
            session.commit()
        print(f"    ada.name after close: {ada.name!r}")

        rule("5. DetachedInstanceError, provoked on a relationship")
        with Session(engine) as session:
            ada = session.get(Member, 1)
        try:
            print(len(ada.loans))
        except DetachedInstanceError as error:
            print("raised DetachedInstanceError:")
            print(f"    {first_line(error)}")
        print("  A lazy relationship is a SELECT waiting to happen, and the session")
        print("  it was waiting for is gone.")

        print("  Fix B — load the relationship while the session is still open:")
        with Session(engine) as session:
            ada = session.scalars(
                select(Member).options(selectinload(Member.loans)).where(Member.id == 1)
            ).one()
        print(f"    len(ada.loans) after close: {len(ada.loans)}")
        print("  Fix A and Fix B answer different questions. A keeps loaded columns")
        print("  readable; B decides in advance which related rows you will need.")

        engine.dispose()
    finally:
        for leftover in sorted(workdir.glob("library.db*")):
            leftover.unlink()
        workdir.rmdir()
        print()
        print(f"temporary database removed: {not workdir.exists()}")


if __name__ == "__main__":
    main()
