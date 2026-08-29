"""Day 087 · Step 7 — the same foreign-key proof from Python, plus the trap
that makes people think the pragma does not work.

The pragma is per-connection, and SQLite documents it as a no-op inside an
open transaction. Python's sqlite3 module opens transactions for you, so a
pragma issued after your first INSERT can be silently ignored. This script
shows both the failure and the fix, on a throwaway in-memory database.

Run with:  python3 examples/07_foreign_keys_python.py
"""

from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE members (member_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE loans (
  loan_id   INTEGER PRIMARY KEY,
  member_id INTEGER NOT NULL REFERENCES members(member_id)
);
"""


def read_pragma(connection: sqlite3.Connection) -> int:
    return connection.execute("PRAGMA foreign_keys").fetchone()[0]


def part_one_default_is_off() -> None:
    print("--- 1. a fresh connection does not enforce foreign keys ---")
    connection = sqlite3.connect(":memory:")
    connection.executescript(SCHEMA)
    print(f"PRAGMA foreign_keys on a new connection: {read_pragma(connection)}")

    connection.execute("INSERT INTO loans (loan_id, member_id) VALUES (1, 999)")
    orphans = connection.execute("SELECT count(*) FROM loans").fetchone()[0]
    print(f"orphan loan pointing at member 999 inserted: {orphans} row")
    connection.close()


def part_two_the_trap() -> None:
    print()
    print("--- 2. the trap: the pragma is a no-op inside an open transaction ---")
    connection = sqlite3.connect(":memory:")
    connection.executescript(SCHEMA)
    connection.execute("INSERT INTO loans (loan_id, member_id) VALUES (1, 999)")
    print(f"connection.in_transaction: {connection.in_transaction}")

    connection.execute("PRAGMA foreign_keys = ON")
    print(f"pragma set, but it reads back as: {read_pragma(connection)}")

    connection.commit()
    connection.execute("PRAGMA foreign_keys = ON")
    print(f"after commit(), setting it again reads back as: {read_pragma(connection)}")

    try:
        connection.execute("INSERT INTO loans (loan_id, member_id) VALUES (2, 999)")
    except sqlite3.IntegrityError as error:
        print(f"the same insert now raises {type(error).__name__}: {error}")
    connection.close()


def part_three_the_habit() -> None:
    print()
    print("--- 3. the habit: set it first, before anything else ---")
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    print(f"PRAGMA foreign_keys: {read_pragma(connection)}")
    connection.executescript(SCHEMA)
    try:
        connection.execute("INSERT INTO loans (loan_id, member_id) VALUES (1, 999)")
    except sqlite3.IntegrityError as error:
        print(f"orphan insert refused: {type(error).__name__}: {error}")
    connection.execute("INSERT INTO members (member_id, name) VALUES (999, 'Real Member')")
    connection.execute("INSERT INTO loans (loan_id, member_id) VALUES (1, 999)")
    good = connection.execute("SELECT count(*) FROM loans").fetchone()[0]
    print(f"with the parent row present, the same insert succeeds: {good} row")
    connection.close()


if __name__ == "__main__":
    part_one_default_is_off()
    part_two_the_trap()
    part_three_the_habit()
