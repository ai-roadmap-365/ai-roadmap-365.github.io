"""The application layer. Look at what it does not import.

There is no `sqlite3` here, no SQL string, and no connection object built by
hand. This module asks a repository for domain objects and prints them. It
would work unchanged against a repository backed by a different database, a
file, or a fake built for a test — which is the argument Day 74 made about
boundaries, now cashed in.

Run it:  python3 report.py
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from contextlib import closing
from pathlib import Path

import seed
from db import BookRepository, LoanRepository
from domain import Book, BookNotFound, DuplicateTitle, LibraryError


def shelf_report(books: BookRepository) -> list[str]:
    """Pure formatting over domain objects. Nothing here can fail on I/O."""
    lines = ["Shelf, by year:"]
    for book in sorted(books.all_sorted("year"), key=lambda b: b.year):
        status = "on the shelf" if book.copies else "all copies out"
        lines.append(f"  {book.year}  {book.title:<34} {book.copies} × ({status})")
    return lines


def overdue_report(loans: LoanRepository, as_of: str) -> list[str]:
    lines = [f"Overdue as of {as_of}:"]
    rows = loans.overdue(as_of)
    if not rows:
        lines.append("  nothing is overdue")
    for row in rows:
        lines.append(
            f"  {row['borrower']:<14} {row['book']:<32} due {row['due']}"
            f"  ({row['days_late']} days late)"
        )
    return lines


def add_with_domain_errors(books: BookRepository, book: Book) -> str:
    """Show the boundary translating storage errors into domain errors.

    The caller never sees an sqlite3 exception. It sees DuplicateTitle,
    which is a sentence about the library rather than about the engine.
    """
    try:
        stored = books.add(book)
    except DuplicateTitle as error:
        return f"  refused: {error}"
    return f"  stored as book_id {stored.book_id}: {stored.label}"


def main() -> int:
    sandbox = Path(tempfile.mkdtemp(prefix="day090-report-"))
    try:
        with closing(seed.build(sandbox / "library.db")) as connection:
            books = BookRepository(connection)
            loans = LoanRepository(connection)

            for line in shelf_report(books):
                print(line)
            print()
            for line in overdue_report(loans, seed.AS_OF):
                print(line)

            print()
            print("Adding books through the repository:")
            print(add_with_domain_errors(
                books, Book(title="Compilers", author="Alfred Aho", year=1986, copies=1)))
            print(add_with_domain_errors(
                books, Book(title="Compilers", author="Alfred Aho", year=1986, copies=1)))

            print()
            print("Looking one up that is not there:")
            try:
                books.get(4242)
            except LibraryError as error:
                print(f"  {type(error).__name__}: {error}")

            print()
            print("Sorting by a key chosen at runtime:")
            for key in ("author", "nonsense; DROP TABLE books"):
                try:
                    first = books.all_sorted(key)[0]
                    print(f"  sort_key={key!r:<32} first row: {first.title}")
                except ValueError as error:
                    print(f"  sort_key={key!r:<32} {error}")

            print()
            print("Streaming every book without building a list:")
            titles = [book.title for book in books.stream_all()]
            print(f"  {len(titles)} titles, one row held at a time")
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
