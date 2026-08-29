#!/usr/bin/env python3
"""Day 085 starter — write the query engine, then let SQL replace it.

Three functions, three exercises. Together they are the whole of
`SELECT columns FROM table WHERE condition ORDER BY column`, and writing them
once is the point: afterwards SQL is not magic, it is a request for the loop
you wrote here.

Run it at any time:  python3 table_scan.py

As shipped it stops at the first unwritten function and tells you which one.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

Row = dict[str, Any]
Table = list[Row]


# ===========================================================================
# EXERCISE 1 — restrict (this is WHERE).
#
# Return a new list holding only the rows for which predicate(row) is true.
# Keep the input order. One pass, every row, no cleverness.
#
# Then answer in a comment: how many times is predicate called when exactly
# one of fifty thousand rows matches?
#
# your answer:
#
# Checked by: "restrict keeps only matching rows, in order"
# ===========================================================================
def restrict(rows: Iterable[Row], predicate: Callable[[Row], bool]) -> Table:
    raise NotImplementedError("EXERCISE 1: implement restrict (WHERE)")


# ===========================================================================
# EXERCISE 2 — project (this is the column list after SELECT).
#
# Return a new list of dicts holding only the named columns, in the order
# they were named. Do not modify the input rows.
#
# Checked by: "project keeps only the named columns, in order"
# ===========================================================================
def project(rows: Iterable[Row], columns: Sequence[str]) -> Table:
    raise NotImplementedError("EXERCISE 2: implement project (the column list)")


# ===========================================================================
# EXERCISE 3 — order_by (this is ORDER BY).
#
# Sort the rows by row[key]. Some values are None, and Python refuses to
# compare None with an int, so you must DECIDE where NULLs go rather than
# letting the sort crash. Put them last, and say so in a comment.
#
# Hint: sorted(rows, key=lambda row: (row[key] is None, ...))
#
# Then answer in a comment: SQLite's own default puts NULLs FIRST in an
# ascending sort. Why does a difference like that matter?
#
# your answer:
#
# Checked by: "order_by sorts ascending and puts NULLs last"
# ===========================================================================
def order_by(rows: Table, key: str, descending: bool = False) -> Table:
    raise NotImplementedError("EXERCISE 3: implement order_by (ORDER BY)")


# ---------------------------------------------------------------------------
# Given to you: the pipeline. Restrict, then project, then sort.
# The order matters for cost, not for the answer — and choosing that order is
# exactly the job you hand to the query planner when you write SQL instead.
# ---------------------------------------------------------------------------
def scan(
    rows: Table,
    where: Callable[[Row], bool],
    columns: Sequence[str],
    sort_key: str,
    descending: bool = False,
) -> Table:
    return order_by(project(restrict(rows, where), columns), sort_key, descending)


def load_books(path: Path | None = None) -> Table:
    source = path or Path(__file__).with_name("books.json")
    return json.loads(source.read_text(encoding="utf-8"))["books"]


def main() -> int:
    books = load_books()
    print(f"loaded {len(books)} rows from books.json")
    try:
        result = scan(
            books,
            where=lambda row: row["year"] is not None and row["year"] < 1980,
            columns=["title", "author", "year"],
            sort_key="year",
        )
    except NotImplementedError as unwritten:
        print(f"not finished yet — {unwritten}")
        print("Write that function, then run this file again.")
        return 1

    for row in result:
        print(f"  {row['year']}  {row['title']:<34} {row['author']}")
    print()
    print(f"{len(result)} row(s); {len(books)} predicate calls to find them")
    print()
    print("EXERCISE 4 — now let the engine do it. Build library.db from")
    print("schema.sql, then run this and confirm it returns the same rows:")
    print("  SELECT title, author, year FROM books")
    print("   WHERE year IS NOT NULL AND year < 1980 ORDER BY year;")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
