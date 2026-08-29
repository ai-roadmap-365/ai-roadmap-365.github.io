"""The same lookup, before and after one CREATE INDEX, at four sizes.

    python3 lookup.py events.db

This is the measurement the whole lab is built on. One query —

    SELECT event_id, model, score FROM events WHERE run_id = ?

— is asked of tables of 25,000, 100,000, 200,000 and 400,000 rows, first
with no index on `run_id` and then with one. Every timing is a best-of-7
with the median printed beside it, and `EXPLAIN QUERY PLAN` is captured
in both states so you can see the planner change its mind.

The row counts are checked. The unindexed and indexed runs must return
exactly the same rows, and the script exits non-zero if they do not.

Two honest notes, because a measurement you cannot criticise is not a
measurement.

**These milliseconds are from one machine on one day.** Yours will
differ, possibly by a lot. What generalises is the SHAPE: the scan column
grows roughly in proportion to the table, and the seek column barely
moves. Read the columns, not the digits.

**The indexed run has an advantage the scan did not.** By the time it
runs, the pages it needs are already in the operating system's cache
because the scan just read them. That makes this comparison friendly to
the index rather than hostile — so the script drops the index and
re-measures the scan at the end, and reports whether the scan came back
to where it started.
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

from generate import build
from timing import drop_all_indexes, file_pages, fmt, plan, ratio, time_query

SIZES = [25_000, 100_000, 200_000, 400_000]
QUERY = "SELECT event_id, model, score FROM events WHERE run_id = ?"
TARGET_RUN = 200  # exists at every size above: 25,000 rows / 100 = 250 runs


def measure_one(path: Path, size: int) -> dict:
    connection = sqlite3.connect(path)
    drop_all_indexes(connection)

    pages_before, page_size = file_pages(connection)
    scanned = time_query(connection, QUERY, (TARGET_RUN,))
    scan_plan = plan(connection, QUERY, (TARGET_RUN,))

    connection.execute("CREATE INDEX ix_events_run ON events(run_id)")
    pages_after, _ = file_pages(connection)
    sought = time_query(connection, QUERY, (TARGET_RUN,))
    seek_plan = plan(connection, QUERY, (TARGET_RUN,))

    if sorted(scanned["result"]) != sorted(sought["result"]):
        raise AssertionError("the index changed the answer — that must never happen")

    connection.execute("DROP INDEX ix_events_run")
    rescanned = time_query(connection, QUERY, (TARGET_RUN,))
    connection.close()

    return {
        "size": size,
        "rows": len(scanned["result"]),
        "scan": scanned,
        "seek": sought,
        "rescan": rescanned,
        "scan_plan": scan_plan,
        "seek_plan": seek_plan,
        "index_pages": pages_after - pages_before,
        "page_size": page_size,
        "table_pages": pages_before,
    }


def main(argv: list[str]) -> int:
    source = Path(argv[1]) if len(argv) > 1 else Path("events.db")
    if not source.exists():
        print(f"{source} does not exist. Run: python3 generate.py {source}", file=sys.stderr)
        return 2

    workspace = Path(tempfile.mkdtemp(prefix="day089-lookup-"))
    results = []
    try:
        print("One lookup, with and without an index on run_id.")
        print(f"Query: {QUERY}   (run_id = {TARGET_RUN})")
        print("Every figure is milliseconds, best and median of 7 runs.")
        print()
        header = (
            f"{'rows':>9} | {'scan best':>10} | {'seek best':>10} | {'faster':>8} |"
            f" {'scan median':>12} | {'seek median':>12} | {'matched':>7}"
        )
        print(header)
        print("-" * len(header))

        for size in SIZES:
            path = workspace / f"events-{size}.db"
            if size == 400_000 and source.exists():
                shutil.copyfile(source, path)
            else:
                build_quiet(path, size)
            row = measure_one(path, size)
            results.append(row)
            print(
                f"{row['size']:>9,} | {row['scan']['best_ms']:>10.2f} |"
                f" {row['seek']['best_ms']:>10.3f} |"
                f" {ratio(row['scan'], row['seek']):>7.0f}x |"
                f" {row['scan']['median_ms']:>12.2f} |"
                f" {row['seek']['median_ms']:>12.3f} |"
                f" {row['rows']:>7,}"
            )

        biggest = results[-1]
        print()
        print("The planner's own words, on the largest table:")
        print(f"  without the index : {biggest['scan_plan']}")
        print(f"  with the index    : {biggest['seek_plan']}")
        print()
        print("SCAN means every row. SEARCH means a descent to the rows that match.")
        print("That one word is the whole difference, and it costs nothing to check.")
        print()
        print("What the index cost, on the largest table:")
        print(
            f"  table pages before : {biggest['table_pages']:,}"
            f" ({biggest['table_pages'] * biggest['page_size']:,} bytes)"
        )
        print(
            f"  index added        : {biggest['index_pages']:,} pages"
            f" ({biggest['index_pages'] * biggest['page_size']:,} bytes,"
            f" {biggest['index_pages'] / biggest['table_pages'] * 100:.0f}% of the table)"
        )
        print()
        print("And the scan, re-measured after the index was dropped again:")
        for row in results:
            print(
                f"  {row['size']:>9,} rows: first {row['scan']['best_ms']:>8.2f} ms"
                f" | after dropping the index {row['rescan']['best_ms']:>8.2f} ms"
            )
        print()
        print("If those two columns are close, the scan figures were not a")
        print("cold-cache artefact and the comparison above is a fair one.")
        print()
        print("Same rows every time. Only the work changed.")
        return 0
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def build_quiet(path: Path, size: int) -> None:
    """generate.build prints a report; here only the file is wanted."""
    import contextlib
    import io

    with contextlib.redirect_stdout(io.StringIO()):
        build(path, size)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
