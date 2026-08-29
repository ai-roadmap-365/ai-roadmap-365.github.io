"""library.py — one engine, one schema, one fixed set of seed rows.

Every demo and every test in this lab builds its database from here, so every
number printed in `expected-output/` is reproducible: the same six members, the
same eight books, the same twenty-four loans, the same dates, every time.

The default URL is an in-memory SQLite database. Nothing is written to disk
unless you pass a path, which is why the lab leaves no database behind.
"""

from __future__ import annotations

from sqlalchemy import create_engine, insert
from sqlalchemy.engine import Engine

from models import Base, Book, Loan, Member, Tag, book_tags

MEMBERS = [
    (1, "Ada Okonkwo", "ada@library.test"),
    (2, "Bruno Sartori", "bruno@library.test"),
    (3, "Chen Wei", "chen@library.test"),
    (4, "Divya Ramanan", "divya@library.test"),
    (5, "Emeka Balogun", "emeka@library.test"),
    (6, "Farida Haddad", "farida@library.test"),
]

BOOKS = [
    (1, "978-0131103627", "The C Programming Language", "Kernighan and Ritchie", 3),
    (2, "978-0201633610", "Design Patterns", "Gamma and others", 2),
    (3, "978-0262033848", "Introduction to Algorithms", "Cormen and others", 4),
    (4, "978-1449355739", "Learning Python", "Mark Lutz", 2),
    (5, "978-0596007126", "Head First Design Patterns", "Freeman and Robson", 1),
    (6, "978-0132350884", "Clean Code", "Robert C. Martin", 3),
    (7, "978-0201616224", "The Pragmatic Programmer", "Hunt and Thomas", 2),
    (8, "978-0134685991", "Effective Java", "Joshua Bloch", 1),
]

TAGS = [(1, "classic"), (2, "python"), (3, "craft"), (4, "algorithms")]

BOOK_TAGS = [
    (1, 1),
    (2, 1),
    (2, 3),
    (3, 1),
    (3, 4),
    (4, 2),
    (5, 3),
    (6, 3),
    (7, 1),
    (7, 3),
    (8, 3),
]

# (id, book_id, member_id, borrowed_on, due_on, returned)
LOANS = [
    (1, 1, 1, "2026-05-04", "2026-05-25", True),
    (2, 2, 1, "2026-06-01", "2026-06-22", False),
    (3, 3, 1, "2026-06-08", "2026-06-29", False),
    (4, 1, 2, "2026-05-11", "2026-06-01", True),
    (5, 4, 2, "2026-06-15", "2026-07-06", False),
    (6, 5, 3, "2026-04-20", "2026-05-11", True),
    (7, 6, 3, "2026-05-18", "2026-06-08", True),
    (8, 7, 3, "2026-06-22", "2026-07-13", False),
    (9, 8, 3, "2026-07-01", "2026-07-22", False),
    (10, 2, 4, "2026-03-09", "2026-03-30", True),
    (11, 3, 4, "2026-04-13", "2026-05-04", True),
    (12, 6, 4, "2026-07-06", "2026-07-27", False),
    (13, 1, 5, "2026-02-16", "2026-03-09", True),
    (14, 4, 5, "2026-05-25", "2026-06-15", True),
    (15, 5, 5, "2026-06-29", "2026-07-20", False),
    (16, 7, 5, "2026-07-13", "2026-08-03", False),
    (17, 3, 6, "2026-01-19", "2026-02-09", True),
    (18, 8, 6, "2026-03-23", "2026-04-13", True),
    (19, 6, 6, "2026-05-04", "2026-05-25", True),
    (20, 2, 6, "2026-06-08", "2026-06-29", False),
    (21, 4, 6, "2026-07-20", "2026-08-10", False),
    (22, 5, 1, "2026-07-27", "2026-08-17", False),
    (23, 8, 2, "2026-08-03", "2026-08-24", False),
    (24, 7, 4, "2026-08-10", "2026-08-31", False),
]


def build_engine(url: str = "sqlite://", echo: bool = False) -> Engine:
    """Create the engine, create the schema, and load the fixed seed rows.

    The seed is loaded through Core `insert()` rather than the ORM on purpose:
    it keeps the setup out of every query count the demos take afterwards.
    """
    engine = create_engine(url, echo=echo)
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            insert(Member),
            [
                {"id": i, "name": n, "email": e}
                for i, n, e in MEMBERS
            ],
        )
        connection.execute(
            insert(Book),
            [
                {"id": i, "isbn": s, "title": t, "author": a, "copies": c}
                for i, s, t, a, c in BOOKS
            ],
        )
        connection.execute(
            insert(Tag), [{"id": i, "name": n} for i, n in TAGS]
        )
        connection.execute(
            insert(book_tags),
            [{"book_id": b, "tag_id": t} for b, t in BOOK_TAGS],
        )
        connection.execute(
            insert(Loan),
            [
                {
                    "id": i,
                    "book_id": b,
                    "member_id": m,
                    "borrowed_on": bo,
                    "due_on": d,
                    "returned": r,
                }
                for i, b, m, bo, d, r in LOANS
            ],
        )
    return engine
