"""The data layer, built from first principles.

Five pieces, and nothing else:

  1. `SCHEMA`             — the tables, as one script.
  2. `connect()`          — a connection factory that sets the four things
                            every connection in this program must have.
  3. `transaction()`      — a context manager that begins, commits, and rolls
                            back explicitly.
  4. `row_to_book()`      — one function that turns a database row into a
                            domain object, so mapping lives in one place.
  5. `BookRepository`     — every SQL statement in the program, and nothing
                            but SQL statements.

The rule this file exists to enforce: **SQL lives here and only here.** No
other module in the lab imports `sqlite3`. Grep for it and see —
`tests/run_tests.sh` does exactly that and fails if it finds one.

Every statement below is parameterised. There is not one f-string, one `%`
and one `+` anywhere near a SQL string in this file, and the test suite
proves that mechanically rather than trusting the author.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path

from domain import Book, BookNotFound, DuplicateTitle, Loan, Member

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


# ---------------------------------------------------------------------------
# 1. The connection factory
# ---------------------------------------------------------------------------

def connect(path: str | Path) -> sqlite3.Connection:
    """Open a connection configured the way this program needs it.

    Four decisions, each of which is per-connection and would otherwise have
    to be remembered at every call site:

    * `isolation_level=None` — turn OFF the module's implicit transaction
      handling. Nothing begins a transaction behind our back; `transaction()`
      below is the only thing that opens one, which is what makes the
      transaction boundaries visible in the code rather than implied.
    * `PRAGMA foreign_keys = ON` — foreign keys are OFF by default in SQLite,
      per connection. Without this line every REFERENCES clause in SCHEMA is
      a comment. It is executed here, outside any transaction, because the
      pragma is a silent no-op inside one.
    * `row_factory = sqlite3.Row` — rows arrive addressable by column name
      instead of by position, so `row["title"]` survives a change to the
      SELECT list that `row[1]` would not.
    * a busy timeout — if another connection holds the write lock, wait
      rather than raising immediately.

    The caller owns the connection and must close it. `contextlib.closing`
    is the tidy way; see `report.py`.
    """
    connection = sqlite3.connect(str(path), isolation_level=None, timeout=5.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    """An alternative row factory: plain dicts instead of sqlite3.Row.

    `sqlite3.Row` is not a dict — it has no `.get`, it is immutable, and
    `json.dumps` refuses it. When a row has to leave the data layer as JSON,
    this is the three-line answer. `cursor.description` is a 7-tuple per
    column of which only the first item, the name, is populated by sqlite3.
    """
    return {column[0]: value for column, value in zip(cursor.description, row)}


def apply_schema(connection: sqlite3.Connection) -> None:
    """Create the tables.

    `executescript` is the right tool for a multi-statement script and the
    wrong tool for anything containing a value: it takes no parameters at
    all, so anything variable would have to be pasted into the string. It
    also issues an implicit COMMIT before it runs, which means it cannot be
    nested inside `transaction()`.
    """
    connection.executescript(SCHEMA)


# ---------------------------------------------------------------------------
# 2. The transaction context manager
# ---------------------------------------------------------------------------

@contextmanager
def transaction(connection: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Run a block of writes as one indivisible act.

    Commits if the block finishes, rolls back if anything at all is raised,
    and re-raises. `BaseException` rather than `Exception` on purpose: a
    KeyboardInterrupt in the middle of a two-statement change must roll back
    too, and `except Exception` would let it through with the transaction
    still open.

    This is not the same thing as `with connection:`. That form commits or
    rolls back a transaction the module opened implicitly, and it does NOT
    close the connection — a genuinely common misreading. This function is
    explicit about both ends, which is why the connection factory turns the
    implicit machinery off.
    """
    if connection.in_transaction:
        raise RuntimeError(
            "a transaction is already open on this connection; "
            "SQLite has no nested transactions, only SAVEPOINTs"
        )
    connection.execute("BEGIN")
    try:
        yield connection
    except BaseException:
        connection.rollback()
        raise
    else:
        connection.commit()


# ---------------------------------------------------------------------------
# 3. Row-to-object mapping — in one place, on purpose
# ---------------------------------------------------------------------------

def row_to_book(row: sqlite3.Row) -> Book:
    """Turn one database row into one domain object.

    Every SELECT in the repository returns these five columns in this order
    and hands the row here. When a column is renamed, this function is the
    only thing that changes.
    """
    return Book(
        book_id=row["book_id"],
        title=row["title"],
        author=row["author"],
        year=row["year"],
        copies=row["copies"],
    )


def row_to_member(row: sqlite3.Row) -> Member:
    return Member(member_id=row["member_id"], name=row["name"], email=row["email"])


def row_to_loan(row: sqlite3.Row) -> Loan:
    return Loan(
        loan_id=row["loan_id"],
        book_id=row["book_id"],
        member_id=row["member_id"],
        borrowed_on=row["borrowed_on"],
        due_on=row["due_on"],
        returned_on=row["returned_on"],
    )


# ---------------------------------------------------------------------------
# 4. The repository
# ---------------------------------------------------------------------------

# Sorting has to vary at runtime, and a placeholder cannot stand in for an
# identifier: `ORDER BY ?` binds a VALUE, and ordering every row by the same
# constant is not ordering at all. The safe form is an allow-list — and the
# safest allow-list holds whole statements you wrote, so that no SQL string
# in this file is ever built out of pieces.
SORTED_QUERIES = {
    "title": "SELECT book_id, title, author, year, copies FROM books ORDER BY title",
    "author": "SELECT book_id, title, author, year, copies FROM books ORDER BY author",
    "year": "SELECT book_id, title, author, year, copies FROM books ORDER BY year",
}


class BookRepository:
    """Every SQL statement about books, and no statement about anything else.

    The repository takes a connection rather than a path. That one decision
    is what makes it testable: the suite hands it a connection to a database
    in a temporary directory, and nothing in the class knows the difference.
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    # -- reads ------------------------------------------------------------

    def get(self, book_id: int) -> Book:
        row = self._connection.execute(
            "SELECT book_id, title, author, year, copies FROM books WHERE book_id = ?",
            (book_id,),
        ).fetchone()
        if row is None:
            raise BookNotFound(f"no book with id {book_id}")
        return row_to_book(row)

    def find_by_author(self, author: str) -> list[Book]:
        """The query the injection demonstration attacks.

        `author` arrives from outside this program. It is bound, so the
        engine compares it to a column and never parses it.
        """
        cursor = self._connection.execute(
            "SELECT book_id, title, author, year, copies FROM books"
            " WHERE author = ? ORDER BY year",
            (author,),
        )
        return [row_to_book(row) for row in cursor]

    def published_between(self, first: int, last: int) -> list[Book]:
        """Named placeholders, which read better as soon as there are three.

        Named style takes a mapping; qmark style takes a sequence. Mixing
        them raises sqlite3.ProgrammingError rather than doing something
        surprising.
        """
        cursor = self._connection.execute(
            "SELECT book_id, title, author, year, copies FROM books"
            " WHERE year BETWEEN :first AND :last ORDER BY year",
            {"first": first, "last": last},
        )
        return [row_to_book(row) for row in cursor]

    def all_sorted(self, sort_key: str = "title") -> list[Book]:
        """Sorting by a column chosen at runtime, done safely.

        The key selects a whole statement from SORTED_QUERIES. An unknown
        key raises before any SQL exists at all. This is the only correct
        way to vary an identifier: an allow-list you wrote, never a value
        you received — and note that no string is assembled even here.
        """
        try:
            statement = SORTED_QUERIES[sort_key]
        except KeyError:
            raise ValueError(
                f"cannot sort by {sort_key!r}; choose from {sorted(SORTED_QUERIES)}"
            ) from None
        return [row_to_book(row) for row in self._connection.execute(statement)]

    def stream_all(self) -> Iterator[Book]:
        """Iterate the cursor instead of fetching everything.

        `fetchall()` on a ten-million-row table builds a ten-million-item
        list in memory. Iterating a cursor asks the virtual machine for one
        row per step, so memory stays flat however large the table is. This
        is the default worth reaching for; `fetchall` is the special case.
        """
        cursor = self._connection.execute(
            "SELECT book_id, title, author, year, copies FROM books ORDER BY book_id"
        )
        for row in cursor:
            yield row_to_book(row)

    def count(self) -> int:
        return self._connection.execute("SELECT count(*) AS n FROM books").fetchone()["n"]

    # -- writes -----------------------------------------------------------

    def add(self, book: Book) -> Book:
        """Insert one book and return it with the id the database assigned.

        `cursor.lastrowid` is the rowid of the last successful INSERT on
        THAT cursor — which is why the cursor returned by `execute` is worth
        keeping rather than discarding.
        """
        try:
            cursor = self._connection.execute(
                "INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)",
                (book.title, book.author, book.year, book.copies),
            )
        except sqlite3.IntegrityError as error:
            # Translate the storage error into a domain error at the boundary.
            # Nothing above this line should ever have to import sqlite3 to
            # find out that a title was taken.
            if "books.title" in str(error):
                raise DuplicateTitle(f"a book titled {book.title!r} is already stored") from error
            raise
        return Book(
            book_id=cursor.lastrowid,
            title=book.title,
            author=book.author,
            year=book.year,
            copies=book.copies,
        )

    def add_many(self, books: Sequence[Book]) -> int:
        """Bulk insert with one prepared statement and many bindings.

        `executemany` compiles the statement once and steps it once per row.
        The loop version compiles it once per row as well, and pays the
        round trip through the module each time. `bulk_insert.py` measures
        the difference rather than asserting it.
        """
        cursor = self._connection.executemany(
            "INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)",
            [(b.title, b.author, b.year, b.copies) for b in books],
        )
        return cursor.rowcount

    def set_copies(self, book_id: int, copies: int) -> None:
        cursor = self._connection.execute(
            "UPDATE books SET copies = ? WHERE book_id = ?",
            (copies, book_id),
        )
        if cursor.rowcount == 0:
            raise BookNotFound(f"no book with id {book_id}")

    def delete(self, book_id: int) -> None:
        cursor = self._connection.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        if cursor.rowcount == 0:
            raise BookNotFound(f"no book with id {book_id}")


class LoanRepository:
    """The loans half, kept separate so each class stays readable."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add_member(self, member: Member) -> Member:
        cursor = self._connection.execute(
            "INSERT INTO members (name, email) VALUES (?, ?)",
            (member.name, member.email),
        )
        return Member(member_id=cursor.lastrowid, name=member.name, email=member.email)

    def borrow(self, book_id: int, member_id: int, borrowed_on: str, due_on: str) -> Loan:
        """Two writes that are only true together — the reason transactions exist.

        A loan row appears and the shelf count drops. Call this inside
        `transaction()`; if the second statement fails, the first must not
        survive, and `test_repository.py` proves that it does not.
        """
        cursor = self._connection.execute(
            "INSERT INTO loans (book_id, member_id, borrowed_on, due_on)"
            " VALUES (?, ?, ?, ?)",
            (book_id, member_id, borrowed_on, due_on),
        )
        self._connection.execute(
            "UPDATE books SET copies = copies - 1 WHERE book_id = ?",
            (book_id,),
        )
        return Loan(
            loan_id=cursor.lastrowid,
            book_id=book_id,
            member_id=member_id,
            borrowed_on=borrowed_on,
            due_on=due_on,
        )

    def overdue(self, as_of: str) -> list[dict]:
        """The three-table question, answered in one statement.

        The returned rows are dicts rather than domain objects because this
        is a report, not an entity: nothing here has an identity to preserve.
        """
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
