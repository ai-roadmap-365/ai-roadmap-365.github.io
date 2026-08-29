"""Runs your `db.py` and names the next unfinished exercise.

    python3 smoke.py

Exits 1 until all nine are written, on purpose: an unfinished lab should not
be able to look finished. Every database it builds lives in a temporary
directory that is removed on the way out.
"""

from __future__ import annotations

import ast
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

import db
from domain import Book, BookNotFound, DuplicateTitle, Member

STEPS: list[tuple[int, str, str]] = [
    (1, "connect()", "a configured connection: row factory, foreign keys on"),
    (2, "transaction()", "begin, commit on success, roll back on anything"),
    (3, "row_to_book()", "one row becomes one Book, addressed by column name"),
    (4, "BookRepository.get()", "one bound parameter, and BookNotFound when there is no row"),
    (5, "BookRepository.find_by_author()", "a hostile value bound, not interpolated"),
    (6, "BookRepository.published_between()", "named placeholders take a mapping"),
    (7, "BookRepository.stream_all()", "iterate the cursor, never fetchall"),
    (8, "BookRepository.add()", "lastrowid, and IntegrityError translated to DuplicateTitle"),
    (9, "BookRepository.add_many()", "executemany, one prepared statement"),
]

SAMPLE = [
    Book(title="The Mythical Man-Month", author="Fred Brooks", year=1975, copies=1),
    Book(title="A Discipline of Programming", author="Edsger Dijkstra", year=1976, copies=2),
    Book(title="Programming Pearls", author="Jon Bentley", year=1986, copies=1),
]


def calls_fetchall(function_name: str) -> bool:
    """Look at the code of one function in db.py, ignoring its docstring.

    Parsed with `ast` rather than searched as text, so a mention of
    "fetchall" in a comment or docstring does not count as a call to it.
    """
    tree = ast.parse(Path(db.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return any(
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr == "fetchall"
                for inner in ast.walk(node)
            )
    return False


def announce(number: int, detail: str = "") -> None:
    _, name, hint = STEPS[number - 1]
    print(f"\nEXERCISE {number} — {name}")
    print(f"  what it must do: {hint}")
    if detail:
        print(f"  what happened:   {detail}")
    print(f"  open db.py, find 'EXERCISE {number}', and write it. Then run this again.")


def main() -> int:
    sandbox = Path(tempfile.mkdtemp(prefix="day090-smoke-"))
    try:
        return run(sandbox)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def run(sandbox: Path) -> int:
    path = sandbox / "mine.db"
    done = 0

    # ---- 1 --------------------------------------------------------------
    try:
        connection = db.connect(path)
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1, (
            "connected, but PRAGMA foreign_keys is off on this connection"
        )
        db.apply_schema(connection)
        row = connection.execute("SELECT 1 AS one").fetchone()
        assert row["one"] == 1, "connected, but rows are not addressable by name"
    except NotImplementedError:
        announce(1)
        return summary(done)
    except (AssertionError, sqlite3.Error) as error:
        announce(1, str(error))
        return summary(done)
    done = 1
    print("  ok: 1. connect() — foreign keys on, rows by name")

    books = db.BookRepository(connection)
    loans = db.LoanRepository(connection)

    # ---- 2 --------------------------------------------------------------
    try:
        with db.transaction(connection):
            connection.execute(
                "INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)",
                ("Temporary", "Nobody", 1999, 1),
            )
            raise RuntimeError("deliberate")
    except NotImplementedError:
        announce(2)
        return summary(done)
    except RuntimeError:
        pass
    left = connection.execute("SELECT count(*) FROM books").fetchone()[0]
    if left != 0:
        announce(2, f"the failed block left {left} row(s) behind — it did not roll back")
        return summary(done)
    done = 2
    print("  ok: 2. transaction() — a failure left nothing behind")

    # seed, using only the given pieces
    try:
        with db.transaction(connection):
            for book in SAMPLE:
                connection.execute(
                    "INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)",
                    (book.title, book.author, book.year, book.copies),
                )
            loans.add_member(Member(name="Ada Lovelace", email="ada@example.invalid"))
    except sqlite3.Error as error:
        announce(2, f"seeding failed: {error}")
        return summary(done)

    # ---- 3 --------------------------------------------------------------
    row = connection.execute(
        "SELECT book_id, title, author, year, copies FROM books WHERE book_id = 1"
    ).fetchone()
    try:
        book = db.row_to_book(row)
        assert isinstance(book, Book), "row_to_book did not return a Book"
        assert book.title == "The Mythical Man-Month", f"got title {book.title!r}"
        assert book.book_id == 1, f"book_id should be 1, got {book.book_id!r}"
    except NotImplementedError:
        announce(3)
        return summary(done)
    except AssertionError as error:
        announce(3, str(error))
        return summary(done)
    done = 3
    print("  ok: 3. row_to_book() — a row became a domain object")

    # ---- 4 --------------------------------------------------------------
    try:
        assert books.get(2).title == "A Discipline of Programming"
        try:
            books.get(4242)
        except BookNotFound:
            pass
        else:
            raise AssertionError("get(4242) returned something instead of raising BookNotFound")
    except NotImplementedError:
        announce(4)
        return summary(done)
    except (AssertionError, sqlite3.Error) as error:
        announce(4, str(error))
        return summary(done)
    done = 4
    print("  ok: 4. get() — found one, and raised BookNotFound for a missing id")

    # ---- 5 --------------------------------------------------------------
    hostile = "Fred Brooks' OR '1'='1"
    try:
        assert [b.title for b in books.find_by_author("Fred Brooks")] == [
            "The Mythical Man-Month"
        ], "the ordinary lookup did not find the one book by Fred Brooks"
        assert books.find_by_author(hostile) == [], (
            "the crafted value returned rows — the value is being interpolated, not bound"
        )
        assert books.count() == 3, "the crafted value changed the table"
    except NotImplementedError:
        announce(5)
        return summary(done)
    except (AssertionError, sqlite3.Error) as error:
        announce(5, str(error))
        return summary(done)
    done = 5
    print("  ok: 5. find_by_author() — the crafted value was treated as data")

    # ---- 6 --------------------------------------------------------------
    try:
        years = [b.year for b in books.published_between(1975, 1980)]
        assert years == [1975, 1976], f"expected [1975, 1976], got {years}"
    except NotImplementedError:
        announce(6)
        return summary(done)
    except (AssertionError, sqlite3.Error) as error:
        announce(6, str(error))
        return summary(done)
    done = 6
    print("  ok: 6. published_between() — named placeholders, in year order")

    # ---- 7 --------------------------------------------------------------
    try:
        streamed = list(books.stream_all())
        assert len(streamed) == 3, f"expected 3 books, got {len(streamed)}"
        assert all(isinstance(b, Book) for b in streamed), "stream_all yielded something else"
        assert not calls_fetchall("stream_all"), (
            "stream_all calls fetchall; iterate the cursor instead"
        )
    except NotImplementedError:
        announce(7)
        return summary(done)
    except (AssertionError, sqlite3.Error, IndexError) as error:
        announce(7, str(error))
        return summary(done)
    done = 7
    print("  ok: 7. stream_all() — three books, one row at a time")

    # ---- 8 --------------------------------------------------------------
    try:
        stored = books.add(Book(title="Compilers", author="Alfred Aho", year=1986, copies=1))
        assert stored.book_id is not None, "add() returned a Book with no book_id"
        assert books.get(stored.book_id).title == "Compilers"
        try:
            books.add(Book(title="Compilers", author="Alfred Aho", year=1986, copies=1))
        except DuplicateTitle:
            pass
        except sqlite3.IntegrityError:
            raise AssertionError(
                "the duplicate raised sqlite3.IntegrityError — translate it to DuplicateTitle"
            ) from None
        else:
            raise AssertionError("the duplicate title was accepted")
    except NotImplementedError:
        announce(8)
        return summary(done)
    except (AssertionError, sqlite3.Error) as error:
        announce(8, str(error))
        return summary(done)
    done = 8
    print("  ok: 8. add() — id assigned, duplicate translated to DuplicateTitle")

    # ---- 9 --------------------------------------------------------------
    try:
        before = books.count()
        extra = [
            Book(title=f"Volume {n}", author="Anon", year=1990, copies=1) for n in range(50)
        ]
        with db.transaction(connection):
            written = books.add_many(extra)
        assert written == 50, f"add_many reported {written} rows, expected 50"
        assert books.count() == before + 50, "the rows are not in the table"
    except NotImplementedError:
        announce(9)
        return summary(done)
    except (AssertionError, sqlite3.Error) as error:
        announce(9, str(error))
        return summary(done)
    done = 9
    print("  ok: 9. add_many() — fifty rows, one prepared statement")

    connection.close()
    return summary(done)


def summary(done: int) -> int:
    print()
    print(f"{done} of {len(STEPS)} exercises finished.")
    if done == len(STEPS):
        print("All nine. Now run the real suite:  python3 ../examples/test_repository.py")
        print("(or, from the lab directory, bash tests/run_tests.sh)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
