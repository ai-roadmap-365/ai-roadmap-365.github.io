"""Composite indexes, the leftmost prefix, covering, ORDER BY, partial.

    python3 composite.py events.db

Five experiments, each of which answers one question with a plan and a
measurement rather than a rule of thumb.

  1. LEFTMOST PREFIX. One index on (run_id, status). Four queries: both
     columns, the leading column alone, the trailing column alone, and
     the two conditions written in the other order. Two of those four can
     use the index for a seek and two cannot, and which two is not
     negotiable — it follows from the index being sorted by run_id first.

  2. COVERING. A query whose columns all appear in the index never has to
     open the table at all. The planner says so in one word: COVERING.

  3. ORDER BY. An index is sorted, so a query that wants rows in that
     order can take them straight off it. Watch USE TEMP B-TREE FOR ORDER
     BY disappear.

  4. PARTIAL. An index with a WHERE clause covers only the rows that
     match it. It is smaller, cheaper to maintain, and usable only by
     queries the planner can prove fall inside it.

  5. ANALYZE. Statistics in sqlite_stat1 are how the planner knows which
     of two usable indexes is the more selective one.

Every experiment starts by dropping every index, so no result here
depends on the order you ran things in.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from timing import drop_all_indexes, file_pages, fmt, plan, time_query

RULE = "-" * 78


def verdict(plan_text: str) -> str:
    """The one word that decides everything.

    If any step of the plan says SCAN, something is being walked end to
    end — the table, or an index used as a narrower table. Only SEARCH
    means the engine descended a tree to the rows it wanted.
    """
    return "SCAN" if "SCAN" in plan_text else "SEEK"


def section(title: str) -> None:
    print()
    print(RULE)
    print(title)
    print(RULE)


def show(connection, label, sql, params=()):
    plan_text = plan(connection, sql, params)
    measurement = time_query(connection, sql, params)
    print(f"  {label}")
    print(f"    plan : [{verdict(plan_text)}] {plan_text}")
    print(f"    time : {fmt(measurement)}")
    return plan_text, measurement


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("events.db")
    if not path.exists():
        print(f"{path} does not exist. Run: python3 generate.py {path}", file=sys.stderr)
        return 2

    connection = sqlite3.connect(path)
    total = connection.execute("SELECT count(*) FROM events").fetchone()[0]
    print(f"{path.name}: {total:,} rows")

    # ---------------------------------------------------------------- 1
    section("1. The leftmost-prefix rule: one index on (run_id, status)")
    drop_all_indexes(connection)
    connection.execute("CREATE INDEX ix_run_status ON events(run_id, status)")
    print("  The index holds every row's (run_id, status) pair, sorted by")
    print("  run_id first and by status only within one run_id.")
    print()
    show(
        connection,
        "a) both columns, leading first  WHERE run_id = ? AND status = ?",
        "SELECT count(*) FROM events WHERE run_id = ? AND status = ?",
        (200, "failed"),
    )
    show(
        connection,
        "b) the leading column alone     WHERE run_id = ?",
        "SELECT count(*) FROM events WHERE run_id = ?",
        (200,),
    )
    show(
        connection,
        "c) the trailing column alone    WHERE status = ?",
        "SELECT count(*) FROM events WHERE status = ?",
        ("failed",),
    )
    show(
        connection,
        "d) both columns, order swapped  WHERE status = ? AND run_id = ?",
        "SELECT count(*) FROM events WHERE status = ? AND run_id = ?",
        ("failed", 200),
    )
    print()
    print("  (a), (b) and (d) seek. (c) cannot.")
    print("  The order you write conditions in WHERE does not matter — (d)")
    print("  is (a) rearranged and gets the same plan. The order of COLUMNS")
    print("  IN THE INDEX is what decides, because a sorted list of pairs is")
    print("  only sorted by the second value inside one value of the first.")
    print("  A phone book sorted by surname then forename cannot find every")
    print("  Ada without reading all of it.")

    # ---------------------------------------------------------------- 2
    section("2. Covering: the index answers, and the table is never opened")
    drop_all_indexes(connection)
    query = "SELECT score FROM events WHERE run_id = ?"
    connection.execute("CREATE INDEX ix_run ON events(run_id)")
    show(connection, "index on (run_id) — seek, then fetch the row for score", query, (200,))
    connection.execute("DROP INDEX ix_run")
    connection.execute("CREATE INDEX ix_run_score ON events(run_id, score)")
    show(connection, "index on (run_id, score) — score is already in the index", query, (200,))
    print()
    print("  The second plan says COVERING INDEX. Every column the query")
    print("  named is in the index, so there is no reason to touch the table.")
    print("  This is the fastest an index gets — and the reason to widen an")
    print("  index is sometimes the columns you SELECT, not the ones you filter.")

    # ---------------------------------------------------------------- 3
    section("3. ORDER BY: an index is already sorted, so the sort disappears")
    drop_all_indexes(connection)
    ordered = "SELECT event_id, created_on FROM events ORDER BY created_on LIMIT 20"
    show(connection, "no index on created_on", ordered)
    connection.execute("CREATE INDEX ix_created ON events(created_on)")
    show(connection, "with an index on created_on", ordered)
    print()
    print("  USE TEMP B-TREE FOR ORDER BY means SQLite built a throwaway tree")
    print("  to sort 400,000 rows so it could hand back the first 20. With the")
    print("  index it walks the first 20 entries and stops. Nothing was sorted.")

    # ---------------------------------------------------------------- 4
    section("4. Partial: index only the rows anybody asks about")
    drop_all_indexes(connection)
    failures = (
        "SELECT count(*) FROM events"
        " WHERE status = 'failed' AND created_on >= '2025-06-01'"
    )
    show(connection, "no index at all", failures)

    pages_before, page_size = file_pages(connection)
    connection.execute("CREATE INDEX ix_created_full ON events(created_on)")
    pages_full, _ = file_pages(connection)
    connection.execute("DROP INDEX ix_created_full")

    pages_reset, _ = file_pages(connection)
    connection.execute(
        "CREATE INDEX ix_failed_created ON events(created_on) WHERE status = 'failed'"
    )
    pages_partial, _ = file_pages(connection)
    show(connection, "with a partial index, WHERE status = 'failed'", failures)

    failed_rows = connection.execute(
        "SELECT count(*) FROM events WHERE status = 'failed'"
    ).fetchone()[0]
    print()
    print(f"  rows in the table        : {total:,}")
    print(f"  rows the partial covers  : {failed_rows:,}"
          f" ({failed_rows / total * 100:.1f}%)")
    print(f"  a full index on created_on costs {pages_full - pages_before:,} pages"
          f" ({(pages_full - pages_before) * page_size:,} bytes)")
    print(f"  the partial index costs          {pages_partial - pages_reset:,} pages"
          f" ({(pages_partial - pages_reset) * page_size:,} bytes)")
    print()
    print("  The catch: the planner will only use it for a query it can prove")
    print("  falls inside the WHERE clause. Drop `status = 'failed'` from the")
    print("  query and this index becomes unusable, not merely unhelpful:")
    show(
        connection,
        "the same date range without status = 'failed'",
        "SELECT count(*) FROM events WHERE created_on >= '2025-06-01'",
    )

    # ---------------------------------------------------------------- 5
    section("5. ANALYZE: what the planner knows about your data")
    drop_all_indexes(connection)
    connection.execute("CREATE INDEX ix_run ON events(run_id)")
    connection.execute("CREATE INDEX ix_status ON events(status)")
    both = "SELECT count(*) FROM events WHERE run_id = ? AND status = ?"
    before_plan, _ = show(connection, "two usable indexes, no statistics", both, (200, "failed"))
    connection.execute("ANALYZE")
    after_plan, _ = show(connection, "the same query after ANALYZE", both, (200, "failed"))
    print()
    print("  sqlite_stat1 — one row per index, written by ANALYZE:")
    for row in connection.execute(
        "SELECT tbl, idx, stat FROM sqlite_stat1 WHERE idx IS NOT NULL ORDER BY idx"
    ):
        rows_in_index, average_per_key = row[2].split()[:2]
        print(
            f"    {row[1]:<12} {int(rows_in_index):>9,} rows,"
            f" about {int(average_per_key):>7,} rows per distinct value"
        )
    print()
    print("  That second number is SELECTIVITY: how many rows the average")
    print("  distinct value matches. An index whose average key matches 100")
    print("  rows is worth seeking; one whose average key matches 130,000 is")
    print("  usually worse than reading the table, because every match costs")
    print("  a jump back into the table for the rest of the row.")
    print()
    if before_plan == after_plan:
        print("  Note what did NOT happen here: the plan is unchanged.")
        print("  SQLite's built-in guess had already picked the more selective")
        print("  of the two indexes on this data, and ANALYZE only replaced the")
        print("  guess with a measured number. That is the usual outcome on a")
        print("  small, evenly distributed table, and pretending otherwise would")
        print("  be inventing a result. ANALYZE earns its keep on skewed data")
        print("  and on tables that changed shape after the index was built —")
        print("  so run it after a big load, and check whether anything moved.")
    else:
        print("  The plan CHANGED once the planner had real numbers:")
        print(f"    before : {before_plan}")
        print(f"    after  : {after_plan}")

    drop_all_indexes(connection)
    connection.execute("ANALYZE")
    connection.commit()
    connection.close()
    print()
    print(RULE)
    print("Indexes dropped. The table is back to how generate.py left it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
