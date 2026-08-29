"""YOUR data layer. Nine numbered exercises.

`domain.py` and `seed.py` beside this file are finished and need no changes.
Everything you write goes here.

How to work:

    python3 smoke.py          # names the next unfinished exercise, exits 1
    python3 smoke.py          # ...until it exits 0
    python3 test_repository.py    # then the real suite, from examples/

Every exercise says exactly which call to use. None of them needs more than
about five lines. The one rule that applies to all nine: **no value ever
goes into a SQL string.** Statements are literals; values are bound.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path

from domain import Book, BookNotFound, DuplicateTitle, Loan, Member

# Given: the schema. Read it before you start — every exercise below is
# constrained by something written here.
SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    book_id  INTEGER PRIMARY KEY,
    title    TEXT    NOT NULL UNIQUE,
    author   TEXT    NOT NULL,
    year     INTEGER NOT NULL CHECK (year BETWEEN 1400 AND 2100),
    copies   INTEGER NOT NULL CHECK (copies >= 0)
) STRICT;

CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE
) STRICT;

CREATE TABLE IF NOT EXISTS loans (
    loan_id     INTEGER PRIMARY KEY,
    book_id     INTEGER NOT NULL REFERENCES books(book_id),
    member_id   INTEGER NOT NULL REFERENCES members(member_id),
    borrowed_on TEXT NOT NULL,
    due_on      TEXT NOT NULL,
    returned_on TEXT,
    CHECK (due_on >= borrowed_on)
) STRICT;

CREATE INDEX IF NOT EXISTS loans_open ON loans(due_on) WHERE returned_on IS NULL;
"""


# ===========================================================================
# EXERCISE 1 — the connection factory
# ===========================================================================
def connect(path: str | Path) -> sqlite3.Connection:
    """Open a connection and configure it.

    Do four things, in this order:

      1. `sqlite3.connect(str(path), isolation_level=None, timeout=5.0)`
         — isolation_level=None turns off the module's implicit transaction
         handling, so `transaction()` below is the only thing that opens one.
      2. set `connection.row_factory = sqlite3.Row` so rows are addressable
         by column name.
      3. `connection.execute("PRAGMA foreign_keys = ON")` — foreign keys are
         OFF by default, per connection. Do it here, before anything can
         start a transaction: the pragma is a silent no-op inside one.
      4. return the connection.

    Checked by: smoke.py step 1, and
    TestConnectionFactory in examples/test_repository.py.
    """
    raise NotImplementedError("exercise 1: connect()")


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    """Given, as a worked model of what a row factory actually is.

    A row factory is any callable taking (cursor, row) and returning
    whatever you want a row to be. `cursor.description` is a 7-tuple per
    column of which sqlite3 fills in only the first item, the name.
    """
    return {column[0]: value for column, value in zip(cursor.description, row)}


def apply_schema(connection: sqlite3.Connection) -> None:
    """Given. Note that `executescript` takes no parameters at all, and
    issues an implicit COMMIT before it runs — so it can never be nested
    inside a transaction."""
    connection.executescript(SCHEMA)


# ===========================================================================
# EXERCISE 2 — the transaction context manager
# ===========================================================================
@contextmanager
def transaction(connection: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Begin, then commit on success and roll back on anything at all.

      1. if `connection.in_transaction` is already True, raise RuntimeError
         with a message saying SQLite has no nested transactions.
      2. `connection.execute("BEGIN")`.
      3. `yield connection` inside a try.
      4. `except BaseException:` roll back and re-raise. BaseException, not
         Exception: a KeyboardInterrupt halfway through a two-statement
         change must roll back too.
      5. `else:` commit.

    Checked by: smoke.py step 2, TestTransactions.
    """
    raise NotImplementedError("exercise 2: transaction()")


# ===========================================================================
# EXERCISE 3 — row-to-object mapping
# ===========================================================================
def row_to_book(row: sqlite3.Row) -> Book:
    """Build one Book from one row, addressing columns BY NAME.

    Use `row["book_id"]`, not `row[0]`. Positional access is a bug waiting
    for somebody to add a column to the SELECT list.

    Checked by: smoke.py step 3, TestMapping.
    """
    raise NotImplementedError("exercise 3: row_to_book()")


def row_to_member(row: sqlite3.Row) -> Member:
    """Given, as the model for exercise 3."""
    return Member(member_id=row["member_id"], name=row["name"], email=row["email"])


def row_to_loan(row: sqlite3.Row) -> Loan:
    """Given."""
    return Loan(
        loan_id=row["loan_id"],
        book_id=row["book_id"],
        member_id=row["member_id"],
        borrowed_on=row["borrowed_on"],
        due_on=row["due_on"],
        returned_on=row["returned_on"],
    )


# Given: sorting has to vary at runtime, and a placeholder cannot stand in
# for an identifier — `ORDER BY ?` binds a VALUE. The safe form is an
# allow-list of whole statements you wrote.
SORTED_QUERIES = {
    "title": "SELECT book_id, title, author, year, copies FROM books ORDER BY title",
    "author": "SELECT book_id, title, author, year, copies FROM books ORDER BY author",
    "year": "SELECT book_id, title, author, year, copies FROM books ORDER BY year",
}


class BookRepository:
    """Every SQL statement about books lives in this class, and nothing else does."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    # =======================================================================
    # EXERCISE 4 — a read with one bound parameter
    # =======================================================================
    def get(self, book_id: int) -> Book:
        """SELECT one book by id.

        `connection.execute("SELECT ... WHERE book_id = ?", (book_id,))`,
        then `.fetchone()`. If the result is None, raise BookNotFound —
        never return None, because a caller will forget to check it.
        Otherwise return `row_to_book(row)`.

        Note the trailing comma in `(book_id,)`. Without it that is not a
        tuple, and you get a ProgrammingError about bindings.

        Checked by: smoke.py step 4, TestMapping.
        """
        raise NotImplementedError("exercise 4: BookRepository.get()")

    # =======================================================================
    # EXERCISE 5 — the query the attacker aims at
    # =======================================================================
    def find_by_author(self, author: str) -> list[Book]:
        """SELECT every book by one author, ORDER BY year.

        `author` comes from outside the program. Bind it. Return a list of
        Book objects built by iterating the cursor:

            cursor = self._connection.execute("SELECT ... WHERE author = ?"
                                              " ORDER BY year", (author,))
            return [row_to_book(row) for row in cursor]

        Two adjacent string literals like that are joined by Python at
        compile time — no runtime value can enter, so it is the right way to
        wrap a long statement. An f-string is not.

        Checked by: smoke.py step 5, TestParameterBinding.
        """
        raise NotImplementedError("exercise 5: BookRepository.find_by_author()")

    # =======================================================================
    # EXERCISE 6 — named placeholders
    # =======================================================================
    def published_between(self, first: int, last: int) -> list[Book]:
        """SELECT books with year BETWEEN :first AND :last, ORDER BY year.

        Named style takes a MAPPING: `{"first": first, "last": last}`.
        Passing a tuple to named placeholders raises ProgrammingError —
        try it once on purpose so you recognise the message.

        Checked by: smoke.py step 6, TestParameterBinding.
        """
        raise NotImplementedError("exercise 6: BookRepository.published_between()")

    def all_sorted(self, sort_key: str = "title") -> list[Book]:
        """Given, as the model for handling an identifier chosen at runtime."""
        try:
            statement = SORTED_QUERIES[sort_key]
        except KeyError:
            raise ValueError(
                f"cannot sort by {sort_key!r}; choose from {sorted(SORTED_QUERIES)}"
            ) from None
        return [row_to_book(row) for row in self._connection.execute(statement)]

    # =======================================================================
    # EXERCISE 7 — streaming instead of fetching everything
    # =======================================================================
    def stream_all(self) -> Iterator[Book]:
        """Yield every book, one row at a time, without building a list.

        Execute the SELECT, then `for row in cursor: yield row_to_book(row)`.
        Do NOT call fetchall(). On a large table fetchall builds the whole
        result in memory; iterating holds one row.

        Checked by: smoke.py step 7, TestBulkAndStreaming.
        """
        raise NotImplementedError("exercise 7: BookRepository.stream_all()")

    def count(self) -> int:
        """Given."""
        return self._connection.execute("SELECT count(*) AS n FROM books").fetchone()["n"]

    # =======================================================================
    # EXERCISE 8 — a write, its assigned id, and the error translated
    # =======================================================================
    def add(self, book: Book) -> Book:
        """INSERT one book; return it with the id the database assigned.

          * `cursor = self._connection.execute("INSERT INTO books (title,
            author, year, copies) VALUES (?, ?, ?, ?)", (book.title,
            book.author, book.year, book.copies))`
          * the new id is `cursor.lastrowid` — which is why keeping the
            cursor that execute() returned is worth doing.
          * wrap it in `try / except sqlite3.IntegrityError as error:` and,
            when `"books.title" in str(error)`, raise
            `DuplicateTitle(...) from error`. Anything else, re-raise.
            That translation is the boundary doing its job: nothing above
            this line should have to import sqlite3 to learn that a title
            was taken.
          * return a NEW Book with book_id filled in. Book is frozen, so you
            build one rather than assigning to a field.

        Checked by: smoke.py step 8, TestMapping.
        """
        raise NotImplementedError("exercise 8: BookRepository.add()")

    # =======================================================================
    # EXERCISE 9 — the bulk write
    # =======================================================================
    def add_many(self, books: Sequence[Book]) -> int:
        """INSERT many books with ONE prepared statement.

        `cursor = self._connection.executemany(statement, sequence_of_tuples)`
        where the sequence is `[(b.title, b.author, b.year, b.copies) for b
        in books]`. Return `cursor.rowcount`.

        Call it inside `transaction()`; `examples/bulk_insert.py` measures
        why that matters more than executemany itself does.

        Checked by: smoke.py step 9, TestBulkAndStreaming.
        """
        raise NotImplementedError("exercise 9: BookRepository.add_many()")

    def set_copies(self, book_id: int, copies: int) -> None:
        """Given. Note `cursor.rowcount` here: for UPDATE and DELETE it is
        the number of rows changed, which is how you tell "updated nothing"
        from "updated something"."""
        cursor = self._connection.execute(
            "UPDATE books SET copies = ? WHERE book_id = ?", (copies, book_id)
        )
        if cursor.rowcount == 0:
            raise BookNotFound(f"no book with id {book_id}")

    def delete(self, book_id: int) -> None:
        """Given."""
        cursor = self._connection.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        if cursor.rowcount == 0:
            raise BookNotFound(f"no book with id {book_id}")


class LoanRepository:
    """Given in full. Read `borrow` — it is the reason transactions exist."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add_member(self, member: Member) -> Member:
        cursor = self._connection.execute(
            "INSERT INTO members (name, email) VALUES (?, ?)", (member.name, member.email)
        )
        return Member(member_id=cursor.lastrowid, name=member.name, email=member.email)

    def borrow(self, book_id: int, member_id: int, borrowed_on: str, due_on: str) -> Loan:
        cursor = self._connection.execute(
            "INSERT INTO loans (book_id, member_id, borrowed_on, due_on) VALUES (?, ?, ?, ?)",
            (book_id, member_id, borrowed_on, due_on),
        )
        self._connection.execute(
            "UPDATE books SET copies = copies - 1 WHERE book_id = ?", (book_id,)
        )
        return Loan(
            loan_id=cursor.lastrowid,
            book_id=book_id,
            member_id=member_id,
            borrowed_on=borrowed_on,
            due_on=due_on,
        )

    def overdue(self, as_of: str) -> list[dict]:
        cursor = self._connection.execute(
            """
            SELECT   members.name AS borrower,
                     books.title  AS book,
                     loans.due_on AS due,
                     julianday(:as_of) - julianday(loans.due_on) AS days_late
            FROM     loans
            JOIN     books   ON books.book_id     = loans.book_id
            JOIN     members ON members.member_id = loans.member_id
            WHERE    loans.returned_on IS NULL
              AND    loans.due_on < :as_of
            ORDER BY days_late DESC
            """,
            {"as_of": as_of},
        )
        return [
            {
                "borrower": row["borrower"],
                "book": row["book"],
                "due": row["due"],
                "days_late": int(row["days_late"]),
            }
            for row in cursor
        ]

    def open_count(self) -> int:
        return self._connection.execute(
            "SELECT count(*) AS n FROM loans WHERE returned_on IS NULL"
        ).fetchone()["n"]
