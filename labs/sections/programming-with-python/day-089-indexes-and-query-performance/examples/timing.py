"""Timing helpers shared by every measuring script in the Day 089 lab.

One number is not a measurement. A single run of a query on a real machine
competes with your browser, your editor, the operating system's own
housekeeping and whatever the page cache happens to be holding, so the
first number you see is worth roughly nothing on its own.

Everything here therefore runs the same work several times and reports
three figures:

  * BEST     — the fastest run. The closest you get to "the work itself",
               because it is the run that was interrupted least.
  * MEDIAN   — the middle run. What you would typically wait.
  * SPREAD   — worst minus best. How noisy the machine was while you asked.

Read best and median together. If they are close, the number means
something. If the spread is larger than the difference you are trying to
demonstrate, you have not demonstrated anything and you need more rows,
not more repeats.

Nothing here is a benchmark suite. It is the smallest honest thing.
"""

from __future__ import annotations

import statistics
import time

REPEATS = 7
"""Odd, so the median is a real sample rather than an average of two."""


def time_call(work, repeats=REPEATS):
    """Run `work` `repeats` times and report best, median, worst and spread.

    `work` must be callable with no arguments. Its return value from the
    LAST run is kept, so a caller can both time a query and use its rows.
    """
    samples = []
    result = None
    for _ in range(repeats):
        started = time.perf_counter()
        result = work()
        samples.append((time.perf_counter() - started) * 1000.0)
    return {
        "best_ms": min(samples),
        "median_ms": statistics.median(samples),
        "worst_ms": max(samples),
        "spread_ms": max(samples) - min(samples),
        "repeats": repeats,
        "result": result,
    }


def time_query(connection, sql, params=()):
    """Time a query, fetching every row.

    fetchall() matters. Without it you would time only how long SQLite
    takes to PREPARE the statement and produce the first row, which for a
    scan is misleadingly quick — the work happens as you step through.
    """
    return time_call(lambda: connection.execute(sql, params).fetchall())


def fmt(measurement):
    """One aligned line: best, median and how noisy the machine was."""
    return (
        f"best {measurement['best_ms']:9.3f} ms"
        f" | median {measurement['median_ms']:9.3f} ms"
        f" | spread {measurement['spread_ms']:7.3f} ms"
    )


def plan(connection, sql, params=()):
    """The planner's own description of how it intends to answer.

    EXPLAIN QUERY PLAN returns one row per step. The last column is the
    human-readable detail — "SCAN events", "SEARCH events USING INDEX ...".
    Joined with " / " so a multi-step plan fits on one line.
    """
    rows = connection.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return " / ".join(str(row[-1]) for row in rows)


def drop_all_indexes(connection):
    """Remove every index you created, leaving the implicit ones alone.

    `sql IS NULL` in sqlite_schema marks an index SQLite made for itself —
    the one behind a UNIQUE or PRIMARY KEY constraint. Those cannot be
    dropped and should not be. Everything with a `sql` value is one
    somebody typed, and this lab types a lot of them.

    Every measuring script calls this first, so each one starts from the
    same bare table no matter what the previous script left behind.
    """
    names = [
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_schema WHERE type = 'index' AND sql IS NOT NULL"
        ).fetchall()
    ]
    for name in names:
        connection.execute(f'DROP INDEX "{name}"')
    return names


def file_pages(connection):
    """Pages actually in use, and the page size, so index cost can be
    reported in bytes.

    `page_count` alone would lie after a DROP INDEX: the pages are handed
    to the database's free list and the file does not shrink. Subtracting
    `freelist_count` gives the pages holding real data, which is the
    figure that goes back up when you create the next index.
    """
    page_size = connection.execute("PRAGMA page_size").fetchone()[0]
    page_count = connection.execute("PRAGMA page_count").fetchone()[0]
    free = connection.execute("PRAGMA freelist_count").fetchone()[0]
    return page_count - free, page_size


def ratio(slow, fast):
    """How many times faster, on the best-of-N figure. Never divide by zero."""
    if fast["best_ms"] <= 0:
        return float("inf")
    return slow["best_ms"] / fast["best_ms"]
