"""demo_toy.py — the hundred-line ORM, doing the four things an ORM does.

Run it:  python3 examples/demo_toy.py

It generates DDL from class attributes, inserts objects, reads rows back as
objects, and proves the identity map both by object identity and by the number
of statements it did NOT send.
"""

from __future__ import annotations

import sqlite3

from tiny_orm import Column, Model, Session


class Member(Model):
    __table__ = "members"
    id = Column("INTEGER", primary_key=True)
    name = Column("TEXT")
    email = Column("TEXT")


class Book(Model):
    __table__ = "books"
    id = Column("INTEGER", primary_key=True)
    title = Column("TEXT")
    author = Column("TEXT")
    copies = Column("INTEGER")


def rule(label: str) -> None:
    print()
    print(label)
    print("-" * len(label))


def main() -> None:
    connection = sqlite3.connect(":memory:")
    session = Session(connection)

    rule("1. The class declaration IS the schema")
    print(Member.create_table_sql())
    print(Book.create_table_sql())
    session.create_all(Member, Book)

    rule("2. add() makes an object pending — no SQL yet")
    ada = Member(name="Ada Okonkwo", email="ada@library.test")
    bruno = Member(name="Bruno Sartori", email="bruno@library.test")
    session.add(ada)
    session.add(bruno)
    session.add(Book(title="The C Programming Language", author="Kernighan and Ritchie", copies=3))
    session.add(Book(title="Design Patterns", author="Gamma and others", copies=2))
    before = len(session.statements)
    print(f"objects pending: {len(session.pending)}")
    print(f"statements emitted so far: {before} (the two CREATE TABLEs above)")
    print(f"ada.id before flush: {ada.id}")

    rule("3. flush() turns pending objects into INSERTs")
    session.flush()
    for statement in session.statements[before:]:
        print(f"    {statement}")
    print(f"ada.id after flush: {ada.id}  <- the database decided this, not you")
    session.commit()

    rule("4. Rows map back into objects")
    everyone = session.select(Member)
    for member in everyone:
        print(f"    {member}")

    rule("5. The identity map: the same row is the same object")
    before = len(session.statements)
    first = session.get(Member, 1)
    second = session.get(Member, 1)
    print(f"first is second      : {first is second}")
    print(f"first is ada         : {first is ada}")
    print(f"statements emitted   : {len(session.statements) - before}")
    print("Both lookups were answered from the identity map, so no SELECT was sent.")

    rule("6. Why the identity map matters")
    first.name = "Ada O."
    print(f"changed via `first`, read via `second`: {second.name}")
    print("Without an identity map these would be two objects and one of the")
    print("two edits would be silently thrown away on the next write.")

    rule("7. Every statement this session sent")
    for number, statement in enumerate(session.statements, start=1):
        print(f"    {number:>2}. {statement}")

    connection.close()


if __name__ == "__main__":
    main()
