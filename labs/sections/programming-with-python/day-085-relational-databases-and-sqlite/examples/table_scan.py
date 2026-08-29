#!/usr/bin/env python3
"""A query engine in about sixty lines, so you can see what SQL replaces.

This is the from-scratch half of Day 085. A table here is a list of dicts —
the same shape you have been writing to JSON since Day 65 — and the three
operations below are the three that almost every SELECT is made of:

    project (the column list)  ->  restrict (WHERE)  ->  sort (ORDER BY)

Relational algebra, which Codd published in 1970, calls the first two
PROJECTION and RESTRICTION (usually "selection"). SQL's SELECT statement is
a surface syntax over exactly these. Writing them by hand once is the point:
after this, `SELECT title FROM books WHERE year < 1980 ORDER BY year` is not
magic, it is a request for the loop you just wrote.

Run it:  python3 table_scan.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

Row = dict[str, Any]
Table = list[Row]


# --------------------------------------------------------------------------
# The three operators.
# --------------------------------------------------------------------------
def restrict(rows: Iterable[Row], predicate: Callable[[Row], bool]) -> Table:
    """WHERE. Keep the rows the predicate accepts. One full pass, every row.

    Note what this does NOT do: it does not look at an index, because there
    is no index. Every WHERE over a plain list is a full table scan, and the
    cost is exactly len(rows) predicate calls whether one row matches or all
    of them do.
    """
    kept: Table = []
    for row in rows:
        if predicate(row):
            kept.append(row)
    return kept


def project(rows: Iterable[Row], columns: Sequence[str]) -> Table:
    """The column list after SELECT. Keep only the named fields, in order."""
    return [{column: row[column] for column in columns} for row in rows]


def order_by(rows: Table, key: str, descending: bool = False) -> Table:
    """ORDER BY. A sort, which is why it costs more than the scan it follows.

    NULL has to be decided rather than assumed: Python refuses to compare
    None with an int, so we sort NULLs last and say so out loud. SQLite's own
    default is NULLs FIRST for ascending order; the difference is a real one
    and pretending otherwise is how two "identical" queries disagree.
    """
    return sorted(
        rows,
        key=lambda row: (row[key] is None, row[key] if row[key] is not None else 0),
        reverse=descending,
    )


def scan(
    rows: Table,
    where: Callable[[Row], bool],
    columns: Sequence[str],
    sort_key: str,
    descending: bool = False,
) -> Table:
    """The whole pipeline, in the order an engine would run it.

    Restrict first, then project, then sort. The order matters for cost, not
    for the answer: sorting six rows after filtering is cheaper than sorting
    fifty thousand before it. Choosing that order is precisely the job you
    hand to the query planner when you write SQL instead.
    """
    return order_by(project(restrict(rows, where), columns), sort_key, descending)


# --------------------------------------------------------------------------
# The same data the database holds, as plain Python.
# --------------------------------------------------------------------------
def load_books(path: Path | None = None) -> Table:
    """Read books.json — the pre-database version of the books table."""
    source = path or Path(__file__).with_name("books.json")
    return json.loads(source.read_text(encoding="utf-8"))["books"]


def main() -> int:
    books = load_books()
    print(f"loaded {len(books)} rows from books.json")
    print()

    print("hand-written scan: books published before 1980, oldest first")
    result = scan(
        books,
        where=lambda row: row["year"] is not None and row["year"] < 1980,
        columns=["title", "author", "year"],
        sort_key="year",
    )
    for row in result:
        print(f"  {row['year']}  {row['title']:<34} {row['author']}")
    print()
    print(f"{len(result)} row(s); {len(books)} predicate calls to find them")
    print()
    print("the SQL that replaces every line of this:")
    print("  SELECT title, author, year FROM books")
    print("   WHERE year IS NOT NULL AND year < 1980")
    print("   ORDER BY year;")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
