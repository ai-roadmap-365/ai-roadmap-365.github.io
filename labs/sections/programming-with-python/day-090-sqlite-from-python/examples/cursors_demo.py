"""Cursors, the four ways to get rows out, and row factories.

Run it:  python3 cursors_demo.py

Everything happens in a database built inside a temporary directory, which
is removed on the way out.
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
import tracemalloc
from contextlib import closing
from pathlib import Path

from db import BookRepository, apply_schema, connect, dict_factory, transaction
from domain import Book


def rule(text: str) -> None:
    print()
    print(text)
    print("-" * len(text))


def main() -> int:
    sandbox = Path(tempfile.mkdtemp(prefix="day090-cursors-"))
    try:
        return run(sandbox)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def run(sandbox: Path) -> int:
    import seed

    path = sandbox / "library.db"

    # `closing` is the idiom for "close this when the block ends". Note that
    # `with connection:` would NOT close it — that form manages a
    # transaction, not the connection's lifetime.
    with closing(seed.build(path)) as connection:
        books = BookRepository(connection)

        rule("1. execute returns a cursor, and the cursor is the result")
        cursor = connection.execute("SELECT book_id, title, year FROM books ORDER BY year")
        print(f"    type(connection.execute(...)) -> {type(cursor).__name__}")
        print(f"    cursor.description names the columns: "
              f"{[column[0] for column in cursor.description]}")
        print("    cursor.rowcount for a SELECT ->", cursor.rowcount,
              "(SQLite cannot know how many rows a query will yield until it has run it)")
        print("    the same cursor, reused for a second statement, forgets the first.")

        rule("2. fetchone, fetchmany, fetchall, and iteration")
        cursor = connection.execute("SELECT title, year FROM books ORDER BY year")
        first = cursor.fetchone()
        print(f"    fetchone()      -> {tuple(first)}")
        batch = cursor.fetchmany(3)
        print(f"    fetchmany(3)    -> {[row['title'] for row in batch]}")
        rest = cursor.fetchall()
        print(f"    fetchall()      -> {len(rest)} remaining rows: {[row['title'] for row in rest]}")
        print(f"    fetchone() now  -> {cursor.fetchone()}   (the cursor is exhausted)")
        print()
        print("    iterating the cursor instead, which is the memory-safe default:")
        for book in books.stream_all():
            print(f"      {book.book_id}: {book.label}")

        rule("3. what fetchall actually costs, measured")
        # 40,000 rows in a second table, so the difference is visible.
        connection.execute("CREATE TABLE wide (n INTEGER, payload TEXT) STRICT")
        with transaction(connection):
            connection.executemany(
                "INSERT INTO wide (n, payload) VALUES (?, ?)",
                [(n, "x" * 200) for n in range(40_000)],
            )

        tracemalloc.start()
        rows = connection.execute("SELECT n, payload FROM wide").fetchall()
        fetchall_peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        del rows

        tracemalloc.start()
        total = 0
        for row in connection.execute("SELECT n, payload FROM wide"):
            total += row["n"]
        iterate_peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()

        print(f"    40,000 rows of about 200 bytes each")
        print(f"    fetchall()        peak traced memory: {fetchall_peak:>10,} bytes")
        print(f"    iterating cursor  peak traced memory: {iterate_peak:>10,} bytes")
        print(f"    ratio: {fetchall_peak / max(iterate_peak, 1):.0f}x")
        print(f"    (both computed the same sum: {total:,})")
        print("    fetchall builds the whole list first. Iteration holds one row.")

        rule("4. row factories: tuple, sqlite3.Row, and a dict")
        plain = sqlite3.connect(path)
        row = plain.execute("SELECT title, year FROM books ORDER BY year").fetchone()
        print(f"    default (no factory) -> {row!r}   — addressed by position only")

        plain.row_factory = sqlite3.Row
        row = plain.execute("SELECT title, year FROM books ORDER BY year").fetchone()
        print(f"    sqlite3.Row          -> row['title'] = {row['title']!r}, row[0] = {row[0]!r}")
        print(f"                            row.keys() = {row.keys()}")
        print(f"                            isinstance(row, dict) = {isinstance(row, dict)}"
              "   — it is NOT a dict; it has no .get and json.dumps refuses it")
        print(f"                            dict(row) = {dict(row)}")

        plain.row_factory = dict_factory
        row = plain.execute("SELECT title, year FROM books ORDER BY year").fetchone()
        print(f"    dict_factory         -> {row}   type: {type(row).__name__}")
        plain.close()

        rule("5. a cursor of your own, when you want two open at once")
        outer = connection.cursor()
        inner = connection.cursor()
        outer.execute("SELECT book_id, title FROM books ORDER BY book_id")
        for book_row in outer.fetchmany(2):
            inner.execute(
                "SELECT count(*) AS n FROM loans WHERE book_id = ?", (book_row["book_id"],)
            )
            print(f"    {book_row['title']:<36} loans: {inner.fetchone()['n']}")
        print("    Two cursors on one connection: independent positions, one transaction.")

    print()
    print("connection closed by contextlib.closing; sandbox removed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
