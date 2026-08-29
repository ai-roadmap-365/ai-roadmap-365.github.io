"""Fixed sample data, and one function that builds a database from it.

Every date here is a literal. Nothing calls `date.today()`, because a
fixture that moves makes today's captured output stop matching tomorrow's
run for no reason anybody can debug.
"""

from __future__ import annotations

from pathlib import Path

from db import BookRepository, LoanRepository, apply_schema, connect, transaction
from domain import Book, Member

BOOKS = [
    Book(title="The Art of Computer Programming", author="Donald Knuth", year=1968, copies=2),
    Book(title="A Relational Model of Data", author="Edgar Codd", year=1970, copies=3),
    Book(title="The Mythical Man-Month", author="Fred Brooks", year=1975, copies=1),
    Book(title="A Discipline of Programming", author="Edsger Dijkstra", year=1976, copies=2),
    Book(title="Structure and Interpretation", author="Harold Abelson", year=1985, copies=4),
    Book(title="The Practice of Programming", author="Brian Kernighan", year=1999, copies=2),
    Book(title="Programming Pearls", author="Jon Bentley", year=1986, copies=1),
]

MEMBERS = [
    Member(name="Ada Lovelace", email="ada@example.invalid"),
    Member(name="Grace Hopper", email="grace@example.invalid"),
    Member(name="Alan Turing", email="alan@example.invalid"),
]

# (book_id, member_id, borrowed_on, due_on)
LOANS = [
    (3, 1, "2026-06-08", "2026-06-22"),
    (4, 2, "2026-07-12", "2026-07-26"),
    (5, 1, "2026-07-27", "2026-08-10"),
    (1, 3, "2026-08-14", "2026-08-28"),
]

AS_OF = "2026-08-16"


def build(path: str | Path):
    """Create and populate a database, and hand back an open connection.

    The whole seed happens inside one transaction: either every row lands or
    none does. A half-seeded fixture is worse than no fixture.
    """
    connection = connect(path)
    apply_schema(connection)
    books = BookRepository(connection)
    loans = LoanRepository(connection)
    with transaction(connection):
        books.add_many(BOOKS)
        for member in MEMBERS:
            loans.add_member(member)
        for book_id, member_id, borrowed_on, due_on in LOANS:
            loans.borrow(book_id, member_id, borrowed_on, due_on)
    return connection
