"""The domain objects — Day 70's model, unchanged and unaware of storage.

Read the imports at the top of this file. There is no `sqlite3` here, and
there never will be. That absence is the whole architectural claim of this
lab: the objects that carry your program's meaning do not know that a
database exists, which is exactly what makes them testable without one
(Day 74) and replaceable without rewriting them.

Everything that knows about SQL lives in `db.py`. Everything that knows
about the problem lives here.
"""

from __future__ import annotations

from dataclasses import dataclass


class LibraryError(Exception):
    """Base class for every error this domain raises.

    The outer layer catches this one class and can say something a human can
    act on, instead of leaking an `sqlite3.IntegrityError` from three layers
    down into a user interface.
    """


class InvalidBook(LibraryError):
    """A Book was asked to exist in a state the domain forbids."""


class BookNotFound(LibraryError):
    """A lookup by identity found nothing."""


class DuplicateTitle(LibraryError):
    """A write would have created a second book with an existing title."""


@dataclass(frozen=True)
class Book:
    """One book. Frozen, because a book's identity does not change.

    `book_id` is `None` for a book that has been built in memory but never
    stored. The repository fills it in when the database assigns one, by
    returning a new Book rather than mutating this one.
    """

    title: str
    author: str
    year: int
    copies: int
    book_id: int | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise InvalidBook("a book must have a title")
        if not self.author.strip():
            raise InvalidBook("a book must have an author")
        if not isinstance(self.year, int) or not (1400 <= self.year <= 2100):
            raise InvalidBook(f"year out of range: {self.year!r}")
        if not isinstance(self.copies, int) or self.copies < 0:
            raise InvalidBook(f"copies must be a non-negative integer: {self.copies!r}")

    @property
    def label(self) -> str:
        """How a book prints in a report. Presentation, not persistence."""
        return f"{self.title} ({self.author}, {self.year})"


@dataclass(frozen=True)
class Member:
    """One library member."""

    name: str
    email: str
    member_id: int | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise LibraryError("a member must have a name")
        if "@" not in self.email:
            raise LibraryError(f"not an address: {self.email!r}")


@dataclass(frozen=True)
class Loan:
    """One book, out with one member, due on one date.

    `returned_on` is None while the book is still out. That is the one place
    in this model where None means something specific rather than "missing".
    """

    book_id: int
    member_id: int
    borrowed_on: str
    due_on: str
    returned_on: str | None = None
    loan_id: int | None = None

    @property
    def is_open(self) -> bool:
        return self.returned_on is None
