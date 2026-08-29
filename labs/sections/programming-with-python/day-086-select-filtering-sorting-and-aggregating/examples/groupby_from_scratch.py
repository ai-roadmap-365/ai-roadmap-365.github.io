#!/usr/bin/env python3
"""Build GROUP BY and the aggregates by hand, then check SQL agrees.

Run from the lab directory, after `bash examples/build_db.sh`:

    python3 examples/groupby_from_scratch.py

An explicit database path may be passed as the one optional argument, which is
how tests/run_tests.sh points it at a throwaway copy.

The point is not that the Python is better. It is that after you have written
the accumulator loop once, the one-line SQL stops being magic: you know exactly
which dictionary it is filling in, and you know exactly why AVG skips NULLs —
because you had to decide that yourself, on line 60-ish, and there was no other
sensible choice available.

Nothing here imports anything outside the standard library.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
DB_PATH = LAB_DIR / "examples" / "library.db"


# --------------------------------------------------------------------------
# Step 1 — FROM. Pull the raw rows out, and do nothing else to them.
# --------------------------------------------------------------------------
def load_rows(conn: sqlite3.Connection) -> list[dict]:
    """The FROM clause: every row, every column, no filtering yet."""
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT genre, rating, pages, published_year FROM books")
    return [dict(r) for r in cur.fetchall()]


# --------------------------------------------------------------------------
# Step 2 — WHERE. Keep a row only when the predicate is TRUE.
#
# This is where three-valued logic shows up in plain Python: a comparison
# against None cannot be True, so the row is dropped. SQL does exactly this,
# and the reason it feels surprising is that SQL does it silently.
# --------------------------------------------------------------------------
def where(rows: list[dict]) -> list[dict]:
    """WHERE published_year >= 2000 — rows with a NULL year cannot qualify."""
    kept = []
    for row in rows:
        year = row["published_year"]
        if year is None:
            continue  # UNKNOWN, and UNKNOWN is not TRUE
        if year >= 2000:
            kept.append(row)
    return kept


# --------------------------------------------------------------------------
# Step 3 — GROUP BY. One accumulator per distinct key.
#
# The grouping key here is `genre`, and None is a legitimate key: GROUP BY is
# the one place in SQL where all the NULLs are treated as equal to each other
# and land in a single bucket.
# --------------------------------------------------------------------------
def group_by_genre(rows: list[dict]) -> dict:
    """Fold the rows into one accumulator per genre."""
    buckets: dict = {}
    for row in rows:
        key = row["genre"]  # None is a real key, not an error
        acc = buckets.get(key)
        if acc is None:
            acc = {
                "rows": 0,  # COUNT(*)      — every row
                "rating_n": 0,  # COUNT(rating) — non-NULL ratings only
                "rating_sum": 0.0,  # SUM(rating)
                "rating_min": None,  # MIN(rating)
                "rating_max": None,  # MAX(rating)
                "pages_n": 0,
                "pages_sum": 0,
            }
            buckets[key] = acc

        acc["rows"] += 1  # COUNT(*) counts the ROW

        rating = row["rating"]
        if rating is not None:  # every other aggregate SKIPS NULL
            acc["rating_n"] += 1
            acc["rating_sum"] += rating
            if acc["rating_min"] is None or rating < acc["rating_min"]:
                acc["rating_min"] = rating
            if acc["rating_max"] is None or rating > acc["rating_max"]:
                acc["rating_max"] = rating

        pages = row["pages"]
        if pages is not None:
            acc["pages_n"] += 1
            acc["pages_sum"] += pages

    return buckets


# --------------------------------------------------------------------------
# Step 4 — HAVING, then SELECT, then ORDER BY.
# --------------------------------------------------------------------------
def finish(buckets: dict) -> list[tuple]:
    """HAVING COUNT(*) >= 3, project the columns, then sort."""
    out = []
    for key, acc in buckets.items():
        if acc["rows"] < 3:  # HAVING — filters BUCKETS, not rows
            continue

        # SELECT — the projection. AVG is SUM over the NON-NULL count, and it
        # is NULL (not 0) when nothing in the bucket had a value at all.
        avg_rating = (
            round(acc["rating_sum"] / acc["rating_n"], 6) if acc["rating_n"] else None
        )
        avg_pages = round(acc["pages_sum"] / acc["pages_n"], 6) if acc["pages_n"] else None
        label = key if key is not None else "(unclassified)"
        out.append(
            (
                label,
                acc["rows"],
                acc["rating_n"],
                avg_rating,
                acc["rating_min"],
                acc["rating_max"],
                avg_pages,
            )
        )

    # ORDER BY books DESC, genre_label ASC — last of all, on the projected rows.
    out.sort(key=lambda r: (-r[1], r[0]))
    return out


# --------------------------------------------------------------------------
# The one-line replacement. Written in the order you TYPE a SELECT, executed
# in the order the functions above are called.
# --------------------------------------------------------------------------
SQL = """
SELECT IFNULL(genre, '(unclassified)') AS genre_label,
       COUNT(*)                        AS books,
       COUNT(rating)                   AS rated,
       ROUND(AVG(rating), 6)           AS avg_rating,
       MIN(rating)                     AS min_rating,
       MAX(rating)                     AS max_rating,
       ROUND(AVG(pages), 6)            AS avg_pages
FROM books
WHERE published_year >= 2000
GROUP BY genre
HAVING COUNT(*) >= 3
ORDER BY books DESC, genre_label ASC
"""

HEADER = ("genre_label", "books", "rated", "avg_rating", "min_rating", "max_rating", "avg_pages")


def render(rows: list[tuple]) -> str:
    widths = [max(len(str(r[i])) for r in ([HEADER] + rows)) for i in range(len(HEADER))]
    lines = ["  ".join(str(h).ljust(widths[i]) for i, h in enumerate(HEADER))]
    lines.append("  ".join("-" * w for w in widths))
    for r in rows:
        lines.append("  ".join(str(v).ljust(widths[i]) for i, v in enumerate(r)))
    return "\n".join(lines)


def main() -> int:
    db_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DB_PATH
    if not db_path.exists():
        print(f"error: {db_path} does not exist — run: bash examples/build_db.sh", file=sys.stderr)
        return 1

    with sqlite3.connect(db_path) as conn:
        rows = load_rows(conn)
        kept = where(rows)
        buckets = group_by_genre(kept)
        by_hand = finish(buckets)

        cur = conn.execute(SQL)
        by_sql = [tuple(r) for r in cur.fetchall()]

    print("The 20 lines of Python:")
    print(f"  FROM      -> {len(rows)} rows")
    print(f"  WHERE     -> {len(kept)} rows survive")
    print(f"  GROUP BY  -> {len(buckets)} buckets")
    print(f"  HAVING    -> {len(by_hand)} buckets survive")
    print()
    print(render(by_hand))
    print()
    print("The one SQL statement:")
    print()
    print(render(by_sql))
    print()

    if by_hand == by_sql:
        print(f"IDENTICAL: {len(by_hand)} rows match exactly.")
        return 0

    print("MISMATCH", file=sys.stderr)
    for hand, sql in zip(by_hand, by_sql):
        if hand != sql:
            print(f"  by hand: {hand}", file=sys.stderr)
            print(f"  by sql : {sql}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
