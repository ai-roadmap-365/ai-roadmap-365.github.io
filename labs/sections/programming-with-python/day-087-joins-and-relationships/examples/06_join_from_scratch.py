"""Day 087 · Step 6 — build the join yourself, two ways, and check both
against SQLite.

A join is not magic. It is one of two small algorithms, and the query planner
picks between them. Here they are, in plain Python over lists of dictionaries,
with no database involved until the final comparison.

    nested-loop join   for every left row, scan every right row     O(n * m)
    hash join          index the right side once, then look up      O(n + m)

Run with:  python3 examples/06_join_from_scratch.py library.db
"""

from __future__ import annotations

import sqlite3
import sys
from collections import defaultdict


def rows_from(connection: sqlite3.Connection, table: str) -> list[dict]:
    """Read a whole table as a list of plain dictionaries."""
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(f"SELECT * FROM {table}")]


def nested_loop_join(
    left: list[dict], right: list[dict], left_key: str, right_key: str
) -> tuple[list[tuple[dict, dict]], int]:
    """The obvious algorithm: compare everything with everything.

    Returns the matched pairs and the number of key comparisons performed, so
    the cost is a number you can look at rather than a claim you have to trust.
    """
    pairs: list[tuple[dict, dict]] = []
    comparisons = 0
    for left_row in left:
        for right_row in right:
            comparisons += 1
            if left_row[left_key] == right_row[right_key]:
                pairs.append((left_row, right_row))
    return pairs, comparisons


def hash_join(
    left: list[dict], right: list[dict], left_key: str, right_key: str
) -> tuple[list[tuple[dict, dict]], int]:
    """Build a dictionary from the smaller side, then probe it once per row.

    The build phase touches every right row once. The probe phase touches every
    left row once. Nothing is scanned repeatedly, which is the whole difference.
    """
    index: dict[object, list[dict]] = defaultdict(list)
    operations = 0
    for right_row in right:  # build phase
        operations += 1
        index[right_row[right_key]].append(right_row)

    pairs: list[tuple[dict, dict]] = []
    for left_row in left:  # probe phase
        operations += 1
        for right_row in index.get(left_row[left_key], ()):
            pairs.append((left_row, right_row))
    return pairs, operations


def left_outer_hash_join(
    left: list[dict], right: list[dict], left_key: str, right_key: str
) -> list[tuple[dict, dict | None]]:
    """The same probe, except a left row with no match still comes through —
    paired with None, which is exactly what SQL calls NULL."""
    index: dict[object, list[dict]] = defaultdict(list)
    for right_row in right:
        index[right_row[right_key]].append(right_row)

    pairs: list[tuple[dict, dict | None]] = []
    for left_row in left:
        matches = index.get(left_row[left_key], [])
        if matches:
            pairs.extend((left_row, match) for match in matches)
        else:
            pairs.append((left_row, None))
    return pairs


def as_comparable(pairs) -> list[tuple]:
    """Reduce join output to (loan_id, member name, borrowed_on) so it can be
    compared with the SQL result by value."""
    result = []
    for loan, member in pairs:
        name = member["name"] if member is not None else None
        result.append((loan["loan_id"], name, loan["borrowed_on"]))
    return sorted(result, key=lambda row: row[0])


def main(database: str) -> int:
    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys = ON")

    loans = rows_from(connection, "loans")
    members = rows_from(connection, "members")

    print(f"left side:  {len(loans)} loans")
    print(f"right side: {len(members)} members")
    print()

    nested_pairs, comparisons = nested_loop_join(loans, members, "member_id", "member_id")
    hashed_pairs, operations = hash_join(loans, members, "member_id", "member_id")

    print(f"nested-loop join: {len(nested_pairs)} rows, {comparisons} key comparisons")
    print(f"hash join:        {len(hashed_pairs)} rows, {operations} operations")
    print(f"  (6 x 5 = {6 * 5} against 6 + 5 = {6 + 5}; the gap widens as the square)")
    print()

    # The reference: let SQLite do the same join.
    connection.row_factory = None
    sql_rows = connection.execute(
        """
        SELECT l.loan_id, m.name, l.borrowed_on
          FROM loans   AS l
          JOIN members AS m ON m.member_id = l.member_id
         ORDER BY l.loan_id
        """
    ).fetchall()
    sql_result = sorted((row[0], row[1], row[2]) for row in sql_rows)

    nested_result = as_comparable(nested_pairs)
    hash_result = as_comparable(hashed_pairs)

    print("nested-loop == SQL:", nested_result == sql_result)
    print("hash        == SQL:", hash_result == sql_result)
    print("nested-loop == hash:", nested_result == hash_result)
    print()

    for loan_id, name, borrowed_on in sql_result:
        print(f"  loan {loan_id}  {name:<15} {borrowed_on}")
    print()

    # And the outer join, where the algorithms differ in what they keep.
    outer = left_outer_hash_join(
        rows_from(connection, "members"), rows_from(connection, "loans"),
        "member_id", "member_id",
    )
    unmatched = [member["name"] for member, loan in outer if loan is None]
    print(f"left outer join keeps {len(outer)} rows from 5 members and 6 loans")
    print(f"members surviving with NULL on the right: {unmatched}")

    sql_unmatched = [
        row[0]
        for row in connection.execute(
            """
            SELECT m.name
              FROM members AS m
              LEFT JOIN loans AS l ON l.member_id = m.member_id
             WHERE l.loan_id IS NULL
             ORDER BY m.name
            """
        )
    ]
    print(f"the same question in SQL:                {sql_unmatched}")
    print("outer join agrees with SQL:", unmatched == sql_unmatched)

    connection.close()

    everything_agrees = (
        nested_result == sql_result
        and hash_result == sql_result
        and unmatched == sql_unmatched
    )
    print()
    print("ALL THREE JOINS AGREE" if everything_agrees else "MISMATCH")
    return 0 if everything_agrees else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "library.db"))
