"""executemany against a loop, and the transaction that dwarfs both.

The point of this script is not a benchmark figure — those move with the
machine, the filesystem and what else is running. The point is the SHAPE:
which of three choices actually matters, and by roughly how much.

Run it:  python3 bulk_insert.py [row_count]
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path

from db import transaction

CREATE = "CREATE TABLE rows_in (n INTEGER NOT NULL, payload TEXT NOT NULL) STRICT"
INSERT = "INSERT INTO rows_in (n, payload) VALUES (?, ?)"


def make_rows(count: int) -> list[tuple[int, str]]:
    return [(n, f"payload-for-row-{n}") for n in range(count)]


def timed(label: str, path: Path, rows: list[tuple[int, str]], body) -> float:
    with closing(sqlite3.connect(path, isolation_level=None)) as connection:
        connection.execute(CREATE)
        start = time.perf_counter()
        body(connection, rows)
        elapsed = time.perf_counter() - start
        stored = connection.execute("SELECT count(*) FROM rows_in").fetchone()[0]
    assert stored == len(rows), f"{label}: stored {stored}, expected {len(rows)}"
    return elapsed


def loop_no_transaction(connection: sqlite3.Connection, rows) -> None:
    """One statement, one transaction, one fsync — per row. The slow one."""
    for row in rows:
        connection.execute(INSERT, row)


def loop_in_transaction(connection: sqlite3.Connection, rows) -> None:
    """The same loop, wrapped once. This is where nearly all the win is."""
    with transaction(connection):
        for row in rows:
            connection.execute(INSERT, row)


def execute_many(connection: sqlite3.Connection, rows) -> None:
    """One prepared statement, stepped once per row, inside one transaction."""
    with transaction(connection):
        connection.executemany(INSERT, rows)


def main() -> int:
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20_000
    rows = make_rows(count)
    sandbox = Path(tempfile.mkdtemp(prefix="day090-bulk-"))
    try:
        print(f"Inserting {count:,} rows, three ways, into a fresh file each time.")
        print()
        results = {
            "a loop, no transaction": timed(
                "loop", sandbox / "a.db", rows, loop_no_transaction),
            "a loop inside one transaction": timed(
                "loop-txn", sandbox / "b.db", rows, loop_in_transaction),
            "executemany inside one transaction": timed(
                "many", sandbox / "c.db", rows, execute_many),
        }
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    slowest = max(results.values())
    width = max(len(label) for label in results)
    print(f"{'method':<{width}}  {'seconds':>9}  {'rows/second':>13}  relative")
    print(f"{'-' * width}  {'-' * 9}  {'-' * 13}  {'-' * 8}")
    for label, elapsed in results.items():
        print(f"{label:<{width}}  {elapsed:>9.4f}  {count / elapsed:>13,.0f}  "
              f"{slowest / elapsed:>6.1f}x")

    print()
    print("Read it in this order:")
    print("  * The first row pays a COMMIT — and on a durable filesystem an")
    print("    fsync — once per row. That is the cost that dominates, and it")
    print("    is the reason a bulk load in a loop feels broken.")
    print("  * Wrapping the same loop in one transaction removes almost all of")
    print("    it. Batching your writes matters more than which method you use.")
    print("  * executemany then saves the remaining per-row cost of going")
    print("    through the module: it prepares the statement once and steps it")
    print("    once per row, binding new values each time.")
    print()
    print("These numbers are from one run on one machine and will differ on")
    print("yours. The ORDER is the durable fact, not the figures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
