"""Which mistake raises which exception — produced by making each mistake.

The table this prints is not copied from documentation. Each row is one
deliberate error, caught, and reported with the class the interpreter
actually raised.

Run it:  python3 errors_demo.py
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

from db import apply_schema, connect
from domain import Book

SETUP = [
    ("INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)",
     ("The Mythical Man-Month", "Fred Brooks", 1975, 1)),
    ("INSERT INTO members (name, email) VALUES (?, ?)",
     ("Ada Lovelace", "ada@example.invalid")),
]


def attempt(connection: sqlite3.Connection, label: str, call) -> tuple[str, str, str]:
    """Run one deliberate mistake and report what came back."""
    try:
        call()
    except sqlite3.Error as error:
        return (label, type(error).__name__, str(error))
    except Exception as error:  # noqa: BLE001 - we want to see anything else too
        return (label, type(error).__name__ + " (not a sqlite3.Error)", str(error))
    return (label, "nothing raised", "")


def main() -> int:
    sandbox = Path(tempfile.mkdtemp(prefix="day090-errors-"))
    try:
        return run(sandbox)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def run(sandbox: Path) -> int:
    print("The sqlite3 exception hierarchy, as this interpreter defines it:")
    for cls in (
        sqlite3.Warning,
        sqlite3.Error,
        sqlite3.InterfaceError,
        sqlite3.DatabaseError,
        sqlite3.DataError,
        sqlite3.OperationalError,
        sqlite3.IntegrityError,
        sqlite3.InternalError,
        sqlite3.ProgrammingError,
        sqlite3.NotSupportedError,
    ):
        parents = " <- ".join(base.__name__ for base in cls.__mro__[1:-1])
        print(f"    sqlite3.{cls.__name__:<18} {parents}")
    print()
    print("    Everything except Warning descends from sqlite3.Error, which is")
    print("    the one class a data layer should catch at its outer edge.")
    print()

    with closing(connect(sandbox / "errors.db")) as connection:
        apply_schema(connection)
        for statement, values in SETUP:
            connection.execute(statement, values)
        connection.commit()

        results = [
            attempt(connection, "duplicate title (UNIQUE)",
                    lambda: connection.execute(
                        "INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)",
                        ("The Mythical Man-Month", "Fred Brooks", 1975, 1))),
            attempt(connection, "missing required column (NOT NULL)",
                    lambda: connection.execute(
                        "INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)",
                        (None, "Fred Brooks", 1975, 1))),
            attempt(connection, "value fails a CHECK",
                    lambda: connection.execute(
                        "INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)",
                        ("Negative Copies", "Nobody", 1975, -1))),
            attempt(connection, "loan naming a member who does not exist (FOREIGN KEY)",
                    lambda: connection.execute(
                        "INSERT INTO loans (book_id, member_id, borrowed_on, due_on)"
                        " VALUES (?, ?, ?, ?)",
                        (1, 999, "2026-08-01", "2026-08-15"))),
            attempt(connection, "wrong type into a STRICT column",
                    lambda: connection.execute(
                        "INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)",
                        ("Bad Year", "Nobody", "nineteen seventy", 1))),
            attempt(connection, "table that is not there",
                    lambda: connection.execute("SELECT * FROM shelves")),
            attempt(connection, "column that is not there",
                    lambda: connection.execute("SELECT isbn FROM books")),
            attempt(connection, "SQL that is not SQL",
                    lambda: connection.execute("SELEKT * FROM books")),
            attempt(connection, "too many bindings for the placeholders",
                    lambda: connection.execute(
                        "SELECT * FROM books WHERE book_id = ?", (1, 2))),
            attempt(connection, "named placeholders given a sequence",
                    lambda: connection.execute(
                        "SELECT * FROM books WHERE book_id = :book_id", (1,))),
            attempt(connection, "two statements in one execute()",
                    lambda: connection.execute("SELECT 1; SELECT 2;")),
            attempt(connection, "binding a Python type SQLite has no column for",
                    lambda: connection.execute(
                        "INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)",
                        ({"title": "a dict"}, "Nobody", 1975, 1))),
            attempt(connection, "using a connection after close()",
                    lambda: use_closed(sandbox)),
        ]

    width_label = max(len(row[0]) for row in results)
    width_class = max(len(row[1]) for row in results)
    print(f"{'the mistake':<{width_label}}  {'raises':<{width_class}}  message")
    print(f"{'-' * width_label}  {'-' * width_class}  {'-' * 46}")
    for label, cls, message in results:
        print(f"{label:<{width_label}}  {cls:<{width_class}}  {message}")

    print()
    print("Read the pattern rather than the rows:")
    print("  IntegrityError    — the DATA broke a rule you wrote in the schema.")
    print("  OperationalError  — the DATABASE could not do it: no such table,")
    print("                      bad syntax, file locked, disk full.")
    print("  ProgrammingError  — YOUR CODE misused the module: wrong number of")
    print("                      bindings, two statements, a closed connection.")
    print("  The first is a fact about the user's input. The third is a bug.")

    failures = [row for row in results if row[1] == "nothing raised"]
    print()
    print(f"{len(results)} deliberate mistakes, {len(failures)} of which raised nothing.")
    return 1 if failures else 0


def use_closed(sandbox: Path) -> None:
    connection = sqlite3.connect(sandbox / "closed.db")
    connection.close()
    connection.execute("SELECT 1")


if __name__ == "__main__":
    sys.exit(main())
