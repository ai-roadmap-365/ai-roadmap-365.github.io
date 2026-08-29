#!/usr/bin/env python3
"""Day 091 — the monthly report for the Fenwick Road brief.

    python3 examples/05_report.py library.db

This is the last stage of the pipeline the lesson describes: requirements in
English became entities, entities became a schema, and the schema answers the
questions. Here the answers become something a trustee would actually read.

Two things are on purpose.

The SQL lives in a repository class, one method per question, exactly as on
Day 90. Nothing outside ``LibraryRepository`` knows that SQLite exists, so the
formatting code below cannot accidentally build a query out of string
concatenation, and every query has one place to be fixed.

The report instant is a *parameter with a default*, not ``datetime.now()``.
A report whose answer changes depending on when it runs cannot be tested,
cannot be reproduced, and cannot be compared with last month's copy.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPORT_INSTANT = "2026-08-16T09:00:00Z"


class LibraryRepository:
    """Every question the report asks, and nothing else.

    The connection is opened with ``PRAGMA foreign_keys = ON`` as the first
    statement, before any transaction can be open — the pragma is a documented
    no-op inside one (Day 87), and it is per connection, every connection.
    """

    def __init__(self, path: str | Path) -> None:
        self.connection = sqlite3.connect(str(path))
        self.connection.execute("PRAGMA foreign_keys = ON")
        # Rows arrive as mappings, so the report reads row["title"] rather than
        # row[2] and stays correct when a column is added to a SELECT.
        self.connection.row_factory = sqlite3.Row

    def __enter__(self) -> "LibraryRepository":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()

    def _rows(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        # Every value that varies is bound, never interpolated. The report
        # instant below is data, and data goes through a placeholder.
        return self.connection.execute(sql, params).fetchall()

    # -- Question 1 ---------------------------------------------------------
    def collection_summary(self) -> sqlite3.Row:
        return self._rows(
            """
            SELECT (SELECT count(*) FROM books WHERE withdrawn_at IS NULL) AS in_collection,
                   (SELECT count(*) FROM loans WHERE returned_at IS NULL)  AS on_loan_now,
                   (SELECT count(*) FROM books WHERE withdrawn_at IS NOT NULL) AS withdrawn
            """
        )[0]

    # -- Question 2 ---------------------------------------------------------
    def members_who_never_borrowed(self) -> list[sqlite3.Row]:
        return self._rows(
            """
            SELECT m.full_name, m.tier
              FROM members AS m
             WHERE m.left_at IS NULL
               AND NOT EXISTS (SELECT 1 FROM loans AS l WHERE l.member_id = m.member_id)
             ORDER BY m.full_name
            """
        )

    # -- Question 3 ---------------------------------------------------------
    def multi_author_books(self) -> list[sqlite3.Row]:
        return self._rows(
            """
            SELECT b.title,
                   count(*)                   AS author_count,
                   group_concat(a.name, ', ') AS credited_order
              FROM books        AS b
              JOIN book_authors AS ba ON ba.book_id  = b.book_id
              JOIN authors      AS a  ON a.author_id = ba.author_id
             GROUP BY b.book_id, b.title
            HAVING count(*) > 1
             ORDER BY author_count DESC, b.title
            """
        )

    # -- Question 4 ---------------------------------------------------------
    def overdue_loans(self, now: str) -> list[sqlite3.Row]:
        return self._rows(
            """
            SELECT m.full_name,
                   b.title,
                   l.due_at,
                   CAST(julianday(?) - julianday(l.due_at) AS INTEGER) AS days_overdue
              FROM loans   AS l
              JOIN members AS m ON m.member_id = l.member_id
              JOIN books   AS b ON b.book_id   = l.book_id
             WHERE l.returned_at IS NULL
               AND l.due_at < ?
             ORDER BY days_overdue DESC
            """,
            (now, now),
        )

    # -- Question 5 ---------------------------------------------------------
    def fines_owed(self) -> list[sqlite3.Row]:
        # sum() stays in pence. The division by 100 happens in the formatter,
        # once, at the edge.
        return self._rows(
            """
            SELECT m.full_name,
                   CASE WHEN m.left_at IS NULL THEN 'current' ELSE 'left' END AS standing,
                   sum(l.fine_pence) AS fine_pence
              FROM members AS m
              JOIN loans   AS l ON l.member_id = m.member_id
             GROUP BY m.member_id, m.full_name
            HAVING sum(l.fine_pence) > 0
             ORDER BY fine_pence DESC
            """
        )

    # -- Question 6 ---------------------------------------------------------
    def top_borrowers_per_tier(self, limit: int) -> list[sqlite3.Row]:
        return self._rows(
            """
            WITH per_member AS (
              SELECT m.member_id, m.full_name, m.tier, count(l.loan_id) AS loan_count
                FROM members AS m
                LEFT JOIN loans AS l ON l.member_id = m.member_id
               WHERE m.left_at IS NULL
               GROUP BY m.member_id, m.full_name, m.tier
            ),
            ranked AS (
              SELECT tier, full_name, loan_count,
                     ROW_NUMBER() OVER (PARTITION BY tier
                                        ORDER BY loan_count DESC, full_name) AS position
                FROM per_member
            )
            SELECT tier, position, full_name, loan_count
              FROM ranked
             WHERE position <= ?
             ORDER BY tier, position
            """,
            (limit,),
        )

    # -- Question 7 ---------------------------------------------------------
    def reservation_queues(self) -> list[sqlite3.Row]:
        return self._rows(
            """
            SELECT b.title,
                   ROW_NUMBER() OVER (PARTITION BY r.book_id
                                      ORDER BY r.reserved_at) AS queue_position,
                   m.full_name
              FROM reservations AS r
              JOIN books        AS b ON b.book_id   = r.book_id
              JOIN members      AS m ON m.member_id = r.member_id
             WHERE r.status = 'waiting'
             ORDER BY b.title, queue_position
            """
        )

    # -- Question 8 ---------------------------------------------------------
    def loans_per_month(self) -> list[sqlite3.Row]:
        return self._rows(
            """
            WITH monthly AS (
              SELECT strftime('%Y-%m', borrowed_at) AS month, count(*) AS loans_started
                FROM loans
               GROUP BY month
            )
            SELECT month, loans_started,
                   sum(loans_started) OVER (ORDER BY month) AS running_total
              FROM monthly
             ORDER BY month
            """
        )

    # -- Question 9 ---------------------------------------------------------
    def category_subtree(self, root: str) -> list[sqlite3.Row]:
        return self._rows(
            """
            WITH RECURSIVE subtree(category_id, name, depth) AS (
                  SELECT category_id, name, 0 FROM categories WHERE name = ?
              UNION ALL
                  SELECT c.category_id, c.name, s.depth + 1
                    FROM categories AS c
                    JOIN subtree    AS s ON c.parent_id = s.category_id
            )
            SELECT s.depth, s.name AS category, count(b.book_id) AS books_in_collection
              FROM subtree AS s
              LEFT JOIN books AS b
                     ON b.category_id  = s.category_id
                    AND b.withdrawn_at IS NULL
             GROUP BY s.category_id, s.depth, s.name
             ORDER BY s.depth, s.name
            """,
            (root,),
        )

    # -- Question 10 --------------------------------------------------------
    def never_borrowed_authors(self) -> list[sqlite3.Row]:
        return self._rows(
            """
            SELECT a.name
              FROM authors AS a
             WHERE NOT EXISTS (
                     SELECT 1
                       FROM book_authors AS ba
                       JOIN loans        AS l ON l.book_id = ba.book_id
                      WHERE ba.author_id = a.author_id
                   )
             ORDER BY a.name
            """
        )


def pounds(pence: int) -> str:
    """Integer pence to a display string. The only place money divides."""
    return f"GBP {pence // 100}.{pence % 100:02d}"


def plural(count: int, singular: str) -> str:
    """English, not `book(s)`. A report a person reads is written for a person."""
    return singular if count == 1 else singular + "s"


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def render(repo: LibraryRepository, now: str) -> None:
    print("=" * 64)
    print("FENWICK ROAD COMMUNITY LIBRARY — collection and lending report")
    print(f"as of {now}   (all figures invented for this exercise)")
    print("=" * 64)

    summary = repo.collection_summary()
    rule("1. The collection")
    print(f"  {summary['in_collection']} books on the shelves, "
          f"{summary['on_loan_now']} of them out on loan.")
    print(f"  {summary['withdrawn']} {plural(summary['withdrawn'], 'withdrawn book')} "
          f"kept in the record so old loans still resolve.")

    rule("2. Current members who have never borrowed")
    for row in repo.members_who_never_borrowed():
        print(f"  {row['full_name']:<16} ({row['tier']})")

    rule("3. Books with more than one author")
    for row in repo.multi_author_books():
        print(f"  {row['title']}")
        print(f"      {row['author_count']} authors: {row['credited_order']}")

    rule("4. Overdue loans")
    for row in repo.overdue_loans(now):
        print(f"  {row['days_overdue']:>3} days  {row['full_name']:<16} {row['title']}")
        print(f"            was due {row['due_at']}")

    rule("5. Fines outstanding")
    total = 0
    for row in repo.fines_owed():
        total += row["fine_pence"]
        print(f"  {pounds(row['fine_pence']):>10}  {row['full_name']:<16} ({row['standing']})")
    print(f"  {pounds(total):>10}  TOTAL")

    rule("6. Most active borrowers in each tier")
    current_tier = None
    for row in repo.top_borrowers_per_tier(limit=2):
        if row["tier"] != current_tier:
            current_tier = row["tier"]
            print(f"  {current_tier}:")
        loans = row["loan_count"]
        print(f"      {row['position']}. {row['full_name']:<16} {loans} {plural(loans, 'loan')}")

    rule("7. Reservation queues")
    current_title = None
    for row in repo.reservation_queues():
        if row["title"] != current_title:
            current_title = row["title"]
            print(f"  {current_title}:")
        print(f"      {row['queue_position']}. {row['full_name']}")

    rule("8. Loans started per month")
    for row in repo.loans_per_month():
        bar = "#" * row["loans_started"]
        print(f"  {row['month']}  {row['loans_started']:>2} {bar:<4}  running total {row['running_total']:>2}")

    rule("9. The Fiction shelves, at every depth")
    for row in repo.category_subtree("Fiction"):
        indent = "    " * row["depth"]
        count = row["books_in_collection"]
        print(f"  {indent}{row['category']}  ({count} {plural(count, 'book')})")

    rule("10. Authors never borrowed")
    for row in repo.never_borrowed_authors():
        print(f"  {row['name']}")

    print()
    print("=" * 64)
    print("end of report")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: python3 05_report.py <database> [report-instant]", file=sys.stderr)
        return 2
    database = Path(argv[1])
    if not database.exists():
        print(f"no such database: {database}", file=sys.stderr)
        print("build it first with 01_schema.sql and 02_seed.sql", file=sys.stderr)
        return 1
    now = argv[2] if len(argv) > 2 else REPORT_INSTANT
    with LibraryRepository(database) as repo:
        render(repo, now)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
