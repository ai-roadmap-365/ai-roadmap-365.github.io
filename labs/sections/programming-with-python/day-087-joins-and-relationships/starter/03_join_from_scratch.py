"""Day 087 starter — exercises 7, 8 and 9: build the join yourself.

This file runs as it stands. It builds the same data, calls your three
functions, compares them with what SQLite says, and prints a pass or fail line
for each. Right now all three fail, because all three are unfinished in one
specific, named way.

    bash starter/01_build.sh
    python3 starter/03_join_from_scratch.py

Finish the three functions marked EXERCISE. Do not change anything below the
line that says so - that part is the referee.
"""

from __future__ import annotations

import sqlite3
import sys
from collections import defaultdict
from pathlib import Path


# ============================================================================
# EXERCISE 7 — the nested-loop join.
#
# Unfinished how: the inner comparison is missing, so every left row is paired
# with every right row. That is a cartesian product: 30 pairs instead of 6.
# Change: only append the pair when left_row[left_key] == right_row[right_key].
# Also count one comparison per pair examined, so the cost is visible.
# Correct result: 6 pairs, 30 comparisons (6 loans x 5 members).
# Checked by: "exercise 7: nested-loop join matches SQL"
# ============================================================================
def nested_loop_join(
    left: list[dict], right: list[dict], left_key: str, right_key: str
) -> tuple[list[tuple[dict, dict]], int]:
    """For every left row, scan every right row. O(n * m)."""
    pairs: list[tuple[dict, dict]] = []
    comparisons = 0
    for left_row in left:
        for right_row in right:
            comparisons += 1
            pairs.append((left_row, right_row))  # <- exercise 7 goes here
    return pairs, comparisons


# ============================================================================
# EXERCISE 8 — the hash join.
#
# Unfinished how: the build phase is written for you. The probe phase is not,
# so no pairs come out at all.
# Change: for each left row, look its key up in `index` and append one pair per
# matching right row. Count one operation per left row probed, so the total
# comes to 11 rather than 30.
# Correct result: the same 6 pairs as exercise 7, in 11 operations (6 + 5).
# Checked by: "exercise 8: hash join matches SQL"
# ============================================================================
def hash_join(
    left: list[dict], right: list[dict], left_key: str, right_key: str
) -> tuple[list[tuple[dict, dict]], int]:
    """Index the right side once, then look each left row up. O(n + m)."""
    index: dict[object, list[dict]] = defaultdict(list)
    operations = 0
    for right_row in right:  # build phase - complete, leave it alone
        operations += 1
        index[right_row[right_key]].append(right_row)

    pairs: list[tuple[dict, dict]] = []
    for left_row in left:  # probe phase - exercise 8 goes here
        operations += 1
    return pairs, operations


# ============================================================================
# EXERCISE 9 — the LEFT OUTER version of the hash join.
#
# Unfinished how: it behaves exactly like an inner join, so a left row with no
# match is dropped instead of surviving.
# Change: when `matches` is empty, still append one pair - (left_row, None).
# None is what SQL calls NULL: the row survives, the right-hand columns do not.
# Correct result: 7 pairs from 5 members and 6 loans, and Eli Nakamura is the
# one member paired with None.
# Checked by: "exercise 9: left outer join keeps the unmatched row"
# ============================================================================
def left_outer_hash_join(
    left: list[dict], right: list[dict], left_key: str, right_key: str
) -> list[tuple[dict, dict | None]]:
    """Every left row comes through, matched or not."""
    index: dict[object, list[dict]] = defaultdict(list)
    for right_row in right:
        index[right_row[right_key]].append(right_row)

    pairs: list[tuple[dict, dict | None]] = []
    for left_row in left:
        matches = index.get(left_row[left_key], [])
        if matches:
            pairs.extend((left_row, match) for match in matches)
        # exercise 9: the missing `else` goes here
    return pairs


# ===================== do not change anything below here =====================


def rows_from(connection: sqlite3.Connection, table: str) -> list[dict]:
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(f"SELECT * FROM {table}")]


def as_comparable(pairs) -> list[tuple]:
    result = []
    for loan, member in pairs:
        name = member["name"] if member is not None else None
        result.append((loan["loan_id"], name, loan["borrowed_on"]))
    return sorted(result, key=lambda row: row[0])


def report(label: str, passed: bool, detail: str = "") -> bool:
    print(f"  {'ok  ' if passed else 'FAIL'}: {label}{(' — ' + detail) if detail else ''}")
    return passed


def main(database: str) -> int:
    if not Path(database).exists():
        print(f"{database} does not exist. Run: bash starter/01_build.sh")
        return 1

    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys = ON")
    loans = rows_from(connection, "loans")
    members = rows_from(connection, "members")

    connection.row_factory = None
    sql_inner = sorted(
        (row[0], row[1], row[2])
        for row in connection.execute(
            "SELECT l.loan_id, m.name, l.borrowed_on FROM loans AS l"
            " JOIN members AS m ON m.member_id = l.member_id"
        )
    )
    sql_unmatched = [
        row[0]
        for row in connection.execute(
            "SELECT m.name FROM members AS m"
            " LEFT JOIN loans AS l ON l.member_id = m.member_id"
            " WHERE l.loan_id IS NULL ORDER BY m.name"
        )
    ]
    connection.close()

    nested_pairs, comparisons = nested_loop_join(loans, members, "member_id", "member_id")
    hashed_pairs, operations = hash_join(loans, members, "member_id", "member_id")
    outer_pairs = left_outer_hash_join(members, loans, "member_id", "member_id")
    unmatched = [member["name"] for member, loan in outer_pairs if loan is None]

    print(f"SQLite says the inner join has {len(sql_inner)} rows.")
    print()

    passed = [
        report(
            "exercise 7: nested-loop join matches SQL",
            as_comparable(nested_pairs) == sql_inner and comparisons == 30,
            f"{len(nested_pairs)} pairs in {comparisons} comparisons (want 6 in 30)",
        ),
        report(
            "exercise 8: hash join matches SQL",
            as_comparable(hashed_pairs) == sql_inner and operations == 11,
            f"{len(hashed_pairs)} pairs in {operations} operations (want 6 in 11)",
        ),
        report(
            "exercise 9: left outer join keeps the unmatched row",
            len(outer_pairs) == 7 and unmatched == sql_unmatched,
            f"{len(outer_pairs)} pairs, unmatched={unmatched} (want 7, ['Eli Nakamura'])",
        ),
    ]

    print()
    done = sum(passed)
    print(f"{done} of 3 exercises complete.")
    return 0 if done == 3 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "library.db")))
