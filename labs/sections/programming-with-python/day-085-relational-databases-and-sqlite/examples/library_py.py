#!/usr/bin/env python3
"""The same database from Python, with the three habits that matter.

  1. Turn foreign keys ON. SQLite leaves them off for backward compatibility,
     and the sqlite3 module does not turn them on for you. A REFERENCES clause
     with foreign_keys OFF is a comment.
  2. Pass values as PARAMETERS, never by building a string. This is the whole
     of SQL injection defence and it is one character of extra typing.
  3. Use row_factory so a row is something you can read, not a tuple you have
     to count along.

Run it:  python3 library_py.py library.db
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

TODAY = "2026-08-16"


def connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def overdue(connection: sqlite3.Connection, as_of: str) -> list[sqlite3.Row]:
    """The overdue question, with the date supplied as a parameter."""
    return connection.execute(
        """
        SELECT m.name AS borrower, b.title AS book, l.due_on AS due
          FROM loans   AS l
          JOIN members AS m ON m.member_id = l.member_id
          JOIN books   AS b ON b.book_id   = l.book_id
         WHERE l.returned_on IS NULL
           AND l.due_on < ?
         ORDER BY l.due_on
        """,
        (as_of,),
    ).fetchall()


def main(argv: list[str]) -> int:
    database = Path(argv[1]) if len(argv) > 1 else Path("library.db")
    if not database.exists():
        print(f"no such database: {database}", file=sys.stderr)
        return 1

    # The two versions this machine reports. They are allowed to differ: the
    # sqlite3 command-line shell and the Python module each link their own
    # copy of the SQLite library, and neither is wrong.
    print(f"SQLite library linked into Python: {sqlite3.sqlite_version}")
    print("Compare that with `sqlite3 --version` in your shell. On many")
    print("machines the two numbers differ, and neither is wrong: the shell")
    print("and the Python module are separate programs, each carrying its own")
    print("copy of the library. Check the one you are actually running.")
    print()

    connection = connect(database)
    try:
        print(f"foreign_keys = {connection.execute('PRAGMA foreign_keys').fetchone()[0]}")
        print()

        print(f"overdue as of {TODAY}:")
        for row in overdue(connection, TODAY):
            print(f"  {row['due']}  {row['borrower']:<14} {row['book']}")
        print()

        # ------------------------------------------------------------------
        # Parameters, and why. The value below is hostile on purpose.
        # ------------------------------------------------------------------
        hostile = "Ada'; DROP TABLE loans; --"
        print("looking up a member whose name is an attempted injection:")
        print(f"  value: {hostile!r}")
        found = connection.execute(
            "SELECT member_id, name FROM members WHERE name = ?", (hostile,)
        ).fetchall()
        print(f"  rows returned: {len(found)}")
        still_there = connection.execute("SELECT count(*) FROM loans").fetchone()[0]
        print(f"  loans table still has {still_there} rows")
        print("  The value was never parsed as SQL. It was a string, and the")
        print("  engine compared it to a column. That is all a parameter is.")
        print()
        print("  The dangerous version, which this file deliberately does not run:")
        print('      f"SELECT ... WHERE name = \'{name}\'"')
        print("  Build a statement out of a value once and you have handed the")
        print("  value the ability to be a statement.")
        print()

        # ------------------------------------------------------------------
        # A transaction that is all or nothing.
        # ------------------------------------------------------------------
        before = connection.execute("SELECT count(*) FROM loans").fetchone()[0]
        try:
            with connection:  # commits on success, rolls back on any exception
                connection.execute(
                    "INSERT INTO loans"
                    " (loan_id, book_id, member_id, borrowed_on, due_on)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (60, 1, 2, TODAY, "2026-09-06"),
                )
                # A second write that cannot succeed: member 999 does not exist.
                connection.execute(
                    "INSERT INTO loans"
                    " (loan_id, book_id, member_id, borrowed_on, due_on)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (61, 1, 999, TODAY, "2026-09-06"),
                )
        except sqlite3.IntegrityError as error:
            print(f"transaction refused: {error}")
        after = connection.execute("SELECT count(*) FROM loans").fetchone()[0]
        print(f"loans before: {before}, after: {after}")
        print("The first INSERT succeeded and was then undone with the second.")
        print("Atomicity is not 'each statement works'; it is 'the group did'.")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
