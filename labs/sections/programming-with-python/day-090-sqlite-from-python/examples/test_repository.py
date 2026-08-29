"""The data layer's own test suite, against a real database in a temp file.

Two decisions are worth arguing with, because both are deliberate.

**A real database file, not a mock.** Day 74 said that fakes beat mocks and
that the best move is usually to relocate the boundary rather than patch
across it. That is exactly what a repository does. So these tests do not
mock `sqlite3` — mocking it would test that the code calls the functions the
author expected, which is a tautology. They open a real SQLite database in a
temporary directory, which costs a few milliseconds and tests the thing that
can actually be wrong: the SQL.

**A file, not `:memory:`.** An in-memory database is faster and cannot test
anything about files, paths or durability. Using a file in `tempfile` keeps
the tests honest and still leaves nothing behind, because `tearDown` removes
the directory.

Run it:  python3 test_repository.py          (verbose: -v)
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

import seed
from db import BookRepository, LoanRepository, apply_schema, connect, transaction
from domain import Book, BookNotFound, DuplicateTitle, InvalidBook, Member


class RepositoryTestCase(unittest.TestCase):
    """A fresh, seeded database per test. Tests never share state."""

    def setUp(self) -> None:
        self.sandbox = Path(tempfile.mkdtemp(prefix="day090-tests-"))
        self.path = self.sandbox / "library.db"
        self.connection = seed.build(self.path)
        self.books = BookRepository(self.connection)
        self.loans = LoanRepository(self.connection)

    def tearDown(self) -> None:
        self.connection.close()
        shutil.rmtree(self.sandbox, ignore_errors=True)


class TestConnectionFactory(RepositoryTestCase):
    def test_database_is_an_ordinary_file_where_we_asked(self) -> None:
        self.assertTrue(self.path.is_file())
        self.assertGreater(self.path.stat().st_size, 0)

    def test_foreign_keys_are_on_for_this_connection(self) -> None:
        self.assertEqual(self.connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_foreign_keys_are_off_on_a_connection_that_did_not_ask(self) -> None:
        """The pragma is per connection, not a property of the file."""
        raw = sqlite3.connect(self.path)
        try:
            self.assertEqual(raw.execute("PRAGMA foreign_keys").fetchone()[0], 0)
            # And the consequence: the same bad write is accepted.
            raw.execute(
                "INSERT INTO loans (book_id, member_id, borrowed_on, due_on)"
                " VALUES (?, ?, ?, ?)",
                (1, 999, "2026-08-01", "2026-08-15"),
            )
            raw.rollback()
        finally:
            raw.close()

    def test_the_configured_connection_refuses_that_same_write(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO loans (book_id, member_id, borrowed_on, due_on)"
                " VALUES (?, ?, ?, ?)",
                (1, 999, "2026-08-01", "2026-08-15"),
            )

    def test_rows_are_addressable_by_name(self) -> None:
        row = self.connection.execute("SELECT title, year FROM books LIMIT 1").fetchone()
        self.assertIsInstance(row, sqlite3.Row)
        self.assertEqual(row["title"], row[0])


class TestMapping(RepositoryTestCase):
    def test_rows_become_domain_objects(self) -> None:
        book = self.books.get(3)
        self.assertIsInstance(book, Book)
        self.assertEqual(book.title, "The Mythical Man-Month")
        self.assertEqual(book.year, 1975)
        self.assertEqual(book.label, "The Mythical Man-Month (Fred Brooks, 1975)")

    def test_missing_row_raises_a_domain_error_not_a_storage_one(self) -> None:
        with self.assertRaises(BookNotFound):
            self.books.get(4242)

    def test_add_returns_the_book_with_the_id_the_database_assigned(self) -> None:
        stored = self.books.add(Book(title="Compilers", author="Alfred Aho", year=1986, copies=1))
        self.assertIsNotNone(stored.book_id)
        self.assertEqual(self.books.get(stored.book_id).title, "Compilers")

    def test_duplicate_title_is_translated_at_the_boundary(self) -> None:
        with self.assertRaises(DuplicateTitle):
            self.books.add(
                Book(title="Programming Pearls", author="Jon Bentley", year=1986, copies=1)
            )

    def test_the_domain_refuses_a_bad_object_before_any_sql_runs(self) -> None:
        with self.assertRaises(InvalidBook):
            Book(title="Impossible", author="Nobody", year=1975, copies=-4)


class TestParameterBinding(RepositoryTestCase):
    HOSTILE = "Fred Brooks' OR '1'='1"
    DESTRUCTIVE = "Fred Brooks'; DROP TABLE books; --"

    def test_a_crafted_value_is_treated_as_ordinary_text(self) -> None:
        self.assertEqual(self.books.find_by_author(self.HOSTILE), [])
        self.assertEqual(self.books.find_by_author(self.DESTRUCTIVE), [])

    def test_the_tables_survive_it(self) -> None:
        self.books.find_by_author(self.DESTRUCTIVE)
        self.assertEqual(self.books.count(), len(seed.BOOKS))

    def test_an_ordinary_value_still_works(self) -> None:
        found = self.books.find_by_author("Fred Brooks")
        self.assertEqual([book.title for book in found], ["The Mythical Man-Month"])

    def test_named_placeholders(self) -> None:
        found = self.books.published_between(1968, 1976)
        self.assertEqual([book.year for book in found], [1968, 1970, 1975, 1976])

    def test_mixing_named_placeholders_with_a_sequence_is_an_error(self) -> None:
        with self.assertRaises(sqlite3.ProgrammingError):
            self.connection.execute("SELECT * FROM books WHERE year = :year", (1975,))

    def test_a_placeholder_cannot_stand_in_for_a_column_name(self) -> None:
        """ORDER BY ? binds a VALUE, so every row sorts by the same constant."""
        rows = self.connection.execute(
            "SELECT title FROM books ORDER BY ?", ("year",)
        ).fetchall()
        by_year = self.connection.execute("SELECT title FROM books ORDER BY year").fetchall()
        self.assertNotEqual([r["title"] for r in rows], [r["title"] for r in by_year])

    def test_sorting_uses_an_allow_list(self) -> None:
        self.assertEqual(self.books.all_sorted("year")[0].year, 1968)
        with self.assertRaises(ValueError):
            self.books.all_sorted("year; DROP TABLE books")


class TestTransactions(RepositoryTestCase):
    def test_a_failure_mid_transaction_leaves_the_database_unchanged(self) -> None:
        copies_before = self.books.get(1).copies
        loans_before = self.loans.open_count()

        with self.assertRaises(sqlite3.IntegrityError):
            with transaction(self.connection):
                self.loans.borrow(1, 1, "2026-08-01", "2026-08-15")
                self.loans.borrow(2, 999, "2026-08-01", "2026-08-15")  # no member 999

        self.assertEqual(self.books.get(1).copies, copies_before)
        self.assertEqual(self.loans.open_count(), loans_before)

    def test_a_python_error_rolls_back_just_as_a_sql_one_does(self) -> None:
        loans_before = self.loans.open_count()
        with self.assertRaises(ZeroDivisionError):
            with transaction(self.connection):
                self.loans.borrow(1, 1, "2026-08-01", "2026-08-15")
                _ = 1 / 0
        self.assertEqual(self.loans.open_count(), loans_before)

    def test_a_successful_transaction_is_visible_to_another_connection(self) -> None:
        with transaction(self.connection):
            self.loans.borrow(1, 1, "2026-08-01", "2026-08-15")
        other = connect(self.path)
        try:
            self.assertEqual(LoanRepository(other).open_count(), self.loans.open_count())
        finally:
            other.close()

    def test_the_transaction_closes_itself_either_way(self) -> None:
        self.assertFalse(self.connection.in_transaction)
        with transaction(self.connection):
            self.assertTrue(self.connection.in_transaction)
        self.assertFalse(self.connection.in_transaction)

    def test_nesting_is_refused_rather_than_silently_wrong(self) -> None:
        with transaction(self.connection):
            with self.assertRaises(RuntimeError):
                with transaction(self.connection):
                    pass

    def test_with_connection_does_not_close_the_connection(self) -> None:
        """The misreading this lab exists partly to correct."""
        with self.connection:
            self.connection.execute("SELECT 1")
        self.connection.execute("SELECT 1").fetchone()  # would raise if it were closed


class TestBulkAndStreaming(RepositoryTestCase):
    def test_executemany_stores_every_row(self) -> None:
        extra = [
            Book(title=f"Volume {n}", author="Anon", year=1990, copies=1)
            for n in range(500)
        ]
        with transaction(self.connection):
            written = self.books.add_many(extra)
        self.assertEqual(written, 500)
        self.assertEqual(self.books.count(), len(seed.BOOKS) + 500)

    def test_executemany_is_atomic_inside_a_transaction(self) -> None:
        before = self.books.count()
        clashing = [
            Book(title="Fresh Title", author="Anon", year=1990, copies=1),
            Book(title="Programming Pearls", author="Anon", year=1990, copies=1),  # taken
        ]
        with self.assertRaises(sqlite3.IntegrityError):
            with transaction(self.connection):
                self.books.add_many(clashing)
        self.assertEqual(self.books.count(), before)

    def test_streaming_yields_the_same_books_as_fetching_them_all(self) -> None:
        streamed = [book.title for book in self.books.stream_all()]
        fetched = [book.title for book in self.books.all_sorted("title")]
        self.assertEqual(sorted(streamed), sorted(fetched))
        self.assertEqual(len(streamed), len(seed.BOOKS))


class TestReports(RepositoryTestCase):
    def test_overdue_is_computed_from_the_date_we_pass_in(self) -> None:
        rows = self.loans.overdue(seed.AS_OF)
        self.assertEqual([row["days_late"] for row in rows], [55, 21, 6])

    def test_a_different_as_of_date_gives_a_different_answer(self) -> None:
        self.assertEqual(self.loans.overdue("2026-06-01"), [])

    def test_the_report_never_calls_todays_date(self) -> None:
        """A fixture that moves is a test that fails on a Tuesday."""
        source = Path(__file__).with_name("db.py").read_text(encoding="utf-8")
        for forbidden in ("date.today", "datetime.now", "date('now')", "CURRENT_DATE"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1)
