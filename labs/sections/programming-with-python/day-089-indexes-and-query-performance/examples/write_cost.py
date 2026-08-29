"""The other half of the trade: what indexes cost on the way in.

    python3 write_cost.py

Every lesson about indexes shows the read getting faster. This is the
half that decides whether you should have added it.

An index is a second sorted structure holding the same values. Every
INSERT has to put a new entry in the right place in every one of them.
Every DELETE has to take one out of each. Every UPDATE that changes an
indexed column has to do both. None of that work exists on a table with
no indexes.

The experiment: build two identical tables of 100,000 rows in a temporary
directory. Give one of them five indexes. Insert the same further 100,000
rows into each and time it, three times per configuration so the numbers
are not a single sample. Report the time and the space.

The rows are the deterministic ones from generate.py, so this is the same
data every run, on any machine.
"""

from __future__ import annotations

import shutil
import sqlite3
import statistics
import sys
import tempfile
import time
from pathlib import Path

from generate import SCHEMA, rows
from timing import file_pages

BASE_ROWS = 100_000
ADDED_ROWS = 100_000
TRIALS = 3

INSERT = (
    "INSERT INTO events"
    " (event_id, run_id, trace_id, model, status, score, created_on, note)"
    " VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
)

INDEXES = [
    "CREATE INDEX ix_run ON events(run_id)",
    "CREATE INDEX ix_trace ON events(trace_id)",
    "CREATE INDEX ix_created ON events(created_on)",
    "CREATE INDEX ix_model_status ON events(model, status)",
    "CREATE INDEX ix_status_score ON events(status, score)",
]


def one_trial(directory: Path, label: str, index_sql: list[str], base, extra):
    path = directory / f"{label}.db"
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA)
    with connection:
        connection.executemany(INSERT, base)
    for statement in index_sql:
        connection.execute(statement)
    connection.commit()

    pages_before, page_size = file_pages(connection)

    started = time.perf_counter()
    with connection:
        connection.executemany(INSERT, extra)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    pages_after, _ = file_pages(connection)
    connection.close()
    path.unlink()
    return {
        "ms": elapsed_ms,
        "pages_before": pages_before,
        "pages_after": pages_after,
        "page_size": page_size,
    }


def run(directory: Path, label: str, index_sql: list[str], base, extra):
    trials = [one_trial(directory, label, index_sql, base, extra) for _ in range(TRIALS)]
    times = [trial["ms"] for trial in trials]
    last = trials[-1]
    return {
        "label": label,
        "indexes": len(index_sql),
        "best_ms": min(times),
        "median_ms": statistics.median(times),
        "worst_ms": max(times),
        "pages_before": last["pages_before"],
        "pages_after": last["pages_after"],
        "page_size": last["page_size"],
    }


def main() -> int:
    print("What indexes cost on the way in.")
    print(
        f"Each configuration: build {BASE_ROWS:,} rows, add the indexes,"
        f" then insert {ADDED_ROWS:,} more."
    )
    print(f"{TRIALS} trials each, in a temporary directory. Same rows every time.")
    print()

    batch = list(rows(BASE_ROWS + ADDED_ROWS))
    base, extra = batch[:BASE_ROWS], batch[BASE_ROWS:]

    workspace = Path(tempfile.mkdtemp(prefix="day089-write-"))
    try:
        bare = run(workspace, "bare", [], base, extra)
        indexed = run(workspace, "indexed", INDEXES, base, extra)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    header = (
        f"{'configuration':<16} | {'indexes':>7} | {'best ms':>9} |"
        f" {'median ms':>10} | {'worst ms':>9}"
    )
    print(header)
    print("-" * len(header))
    for result in (bare, indexed):
        print(
            f"{result['label']:<16} | {result['indexes']:>7} |"
            f" {result['best_ms']:>9.1f} | {result['median_ms']:>10.1f} |"
            f" {result['worst_ms']:>9.1f}"
        )

    slowdown = indexed["best_ms"] / bare["best_ms"]
    print()
    print(
        f"Inserting the same {ADDED_ROWS:,} rows took {slowdown:.1f}x longer"
        " with five indexes."
    )
    print(
        f"Per row: {bare['best_ms'] / ADDED_ROWS * 1000:.2f} microseconds bare,"
        f" {indexed['best_ms'] / ADDED_ROWS * 1000:.2f} microseconds indexed."
    )
    print()

    for result in (bare, indexed):
        page_size = result["page_size"]
        print(
            f"{result['label']:<16} pages {result['pages_before']:>7,}"
            f" -> {result['pages_after']:>7,}"
            f"  ({result['pages_after'] * page_size:>12,} bytes on disk)"
        )
    space = indexed["pages_after"] / bare["pages_after"]
    print()
    print(f"The indexed database is {space:.1f}x the size of the bare one for the")
    print("same rows. Five indexes are five more sorted copies of five more")
    print("column sets, and they live in the same file.")
    print()
    print("Read this next to the read measurements, not instead of them. An")
    print("index that turns a 9 ms scan into a 0.03 ms seek on a query you run")
    print("a thousand times an hour is obviously worth a slower insert. An")
    print("index nothing queries is pure cost, paid on every single write,")
    print("forever, and it will not show up in any timing you are looking at.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
