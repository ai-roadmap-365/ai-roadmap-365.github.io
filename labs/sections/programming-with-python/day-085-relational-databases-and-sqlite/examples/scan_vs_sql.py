#!/usr/bin/env python3
"""Run the hand-written scan and the SQL, and prove they agree.

This is the assertion the lesson rests on: SQL is not a different kind of
answer, it is the same answer with the loop written by somebody else. If the
two disagree by a single row, one of them is wrong, and the script exits
non-zero rather than printing a comforting summary.

Run it:  python3 scan_vs_sql.py library.db
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from table_scan import load_books, scan

QUERY = """
SELECT title, author, year
  FROM books
 WHERE year IS NOT NULL AND year < 1980
 ORDER BY year
"""


def by_hand() -> list[tuple[object, ...]]:
    rows = scan(
        load_books(),
        where=lambda row: row["year"] is not None and row["year"] < 1980,
        columns=["title", "author", "year"],
        sort_key="year",
    )
    return [tuple(row.values()) for row in rows]


def by_sql(database: Path) -> list[tuple[object, ...]]:
    connection = sqlite3.connect(database)
    try:
        return [tuple(row) for row in connection.execute(QUERY)]
    finally:
        connection.close()


def main(argv: list[str]) -> int:
    database = Path(argv[1]) if len(argv) > 1 else Path("library.db")
    if not database.exists():
        print(f"no such database: {database}", file=sys.stderr)
        print("build it first: sqlite3 library.db < schema.sql", file=sys.stderr)
        return 1

    manual = by_hand()
    engine = by_sql(database)

    print(f"sqlite3 module reports SQLite library {sqlite3.sqlite_version}")
    print()
    print(f"{'by hand (table_scan.py)':<44} | {'by SQL (SELECT ...)':<44}")
    print("-" * 44 + "-+-" + "-" * 44)
    for left, right in zip(manual, engine):
        print(f"{left[2]}  {left[0]:<38} | {right[2]}  {right[0]:<38}")
    print()

    if manual == engine:
        print(f"IDENTICAL: {len(manual)} rows, same values, same order.")
        print("The engine ran your loop. That is the whole trick.")
        return 0

    print("DIFFERENT — one of these is wrong:", file=sys.stderr)
    print(f"  by hand: {manual}", file=sys.stderr)
    print(f"  by SQL : {engine}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
