"""Day 087 · Step 8 — the N+1 query pattern, measured rather than asserted.

Looping in the application and asking the database one small question per row
is called the N+1 pattern: one query to get the list, then N more, one per item.
The alternative is one join.

This script builds a throwaway in-memory database, answers the same question
both ways, checks the two answers are identical, and reports the real query
count and the real elapsed time on THIS machine. Timings vary between machines
and between runs; the query counts do not.

Read https://www.sqlite.org/np1queryprob.html afterwards. SQLite's own
documentation argues that for an embedded database — where a query is a
function call into the same process, not a network round trip — N+1 is far less
costly than the usual advice implies. The measurement below is the honest
version of that argument, not a slogan in either direction.

Run with:  python3 examples/08_n_plus_one.py
"""

from __future__ import annotations

import sqlite3
import time

MEMBERS = 500
LOANS_PER_MEMBER = 4


def build() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE members (member_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE loans (
          loan_id   INTEGER PRIMARY KEY,
          member_id INTEGER NOT NULL REFERENCES members(member_id),
          title     TEXT NOT NULL
        );
        """
    )
    connection.executemany(
        "INSERT INTO members (member_id, name) VALUES (?, ?)",
        [(i, f"Member {i:04d}") for i in range(1, MEMBERS + 1)],
    )
    connection.executemany(
        "INSERT INTO loans (member_id, title) VALUES (?, ?)",
        [
            (member_id, f"Book {member_id:04d}-{n}")
            for member_id in range(1, MEMBERS + 1)
            for n in range(LOANS_PER_MEMBER)
        ],
    )
    connection.execute("CREATE INDEX idx_loans_member ON loans(member_id)")
    connection.commit()
    return connection


def n_plus_one(connection: sqlite3.Connection) -> tuple[list[tuple[str, int]], int]:
    """One query for the list, then one more per member. N+1 queries in total."""
    queries = 0
    members = connection.execute("SELECT member_id, name FROM members ORDER BY name").fetchall()
    queries += 1

    result = []
    for member_id, name in members:
        count = connection.execute(
            "SELECT count(*) FROM loans WHERE member_id = ?", (member_id,)
        ).fetchone()[0]
        queries += 1
        result.append((name, count))
    return result, queries


def one_join(connection: sqlite3.Connection) -> tuple[list[tuple[str, int]], int]:
    """The same answer, in one query, with the database doing the matching."""
    rows = connection.execute(
        """
        SELECT m.name, count(l.loan_id)
          FROM members AS m
          LEFT JOIN loans AS l ON l.member_id = m.member_id
         GROUP BY m.member_id, m.name
         ORDER BY m.name
        """
    ).fetchall()
    return [(name, count) for name, count in rows], 1


def timed(function, connection):
    started = time.perf_counter()
    result, queries = function(connection)
    return result, queries, time.perf_counter() - started


def main() -> int:
    connection = build()
    print(f"{MEMBERS} members, {MEMBERS * LOANS_PER_MEMBER} loans, in memory")
    print()

    loop_result, loop_queries, loop_seconds = timed(n_plus_one, connection)
    join_result, join_queries, join_seconds = timed(one_join, connection)

    print(f"N+1 loop: {loop_queries:>4} queries   {loop_seconds * 1000:7.2f} ms")
    print(f"one join: {join_queries:>4} queries   {join_seconds * 1000:7.2f} ms")
    print()
    print("same answer:", loop_result == join_result)
    print("first three rows:", join_result[:3])
    print()
    print("Timings differ between machines and between runs. The query counts do not:")
    print(f"  {loop_queries} against {join_queries}, for the same answer.")
    print()
    print("Across a network the difference is one round trip per query. In an")
    print("embedded database it is one function call, which is why SQLite's own")
    print("documentation treats N+1 as a much smaller problem than the usual advice.")

    connection.close()
    return 0 if loop_result == join_result else 1


if __name__ == "__main__":
    raise SystemExit(main())
