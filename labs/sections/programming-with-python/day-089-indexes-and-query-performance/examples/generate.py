"""Build the table this lab measures: 400,000 evaluation events.

    python3 generate.py events.db            # 400,000 rows, the default
    python3 generate.py small.db 25000       # any other size

Three properties matter more than the contents.

**It is deterministic.** Every value comes from `random.Random(SEED)` or
from arithmetic on the row number, so two runs of this script produce
byte-identical data. Reproducible numbers are the whole point of a lab
about measurement: if your rows differ from mine, your timings and mine
cannot be compared at all.

**It is big enough that the difference is unmistakable.** On fifty rows an
index and a scan are both instant and you will conclude, reasonably and
wrongly, that indexes do not matter. Four hundred thousand rows is the
smallest size at which a laptop stops hiding the difference.

**It is deliberately un-indexed.** The table is created with nothing but
its implicit rowid index. Every index in this lab is one you add, after
you have measured what life is like without it.

The shape is an evaluation log, because that is where you will meet this
problem in AI work: one row per model call, a run id grouping the calls of
one experiment, a trace id identifying a single call, a status, a score,
and a date.
"""

from __future__ import annotations

import random
import sqlite3
import sys
import time
from pathlib import Path

SEED = 20260816
DEFAULT_ROWS = 400_000
EVENTS_PER_RUN = 100

MODELS = [
    "atlas-7b",
    "atlas-13b",
    "beacon-3b",
    "beacon-9b",
    "cinder-1b",
    "cinder-4b",
    "delta-mini",
    "delta-large",
]
STATUSES = ["ok"] * 8 + ["failed", "timeout"]

SCHEMA = """
CREATE TABLE events (
    event_id   INTEGER PRIMARY KEY,
    run_id     INTEGER NOT NULL,
    trace_id   TEXT    NOT NULL,
    model      TEXT    NOT NULL,
    status     TEXT    NOT NULL,
    score      REAL    NOT NULL,
    created_on TEXT    NOT NULL,
    note       TEXT    NOT NULL
);
"""


def scramble(event_id: int) -> int:
    """Spread trace ids so they carry no hint of insertion order.

    Multiplying by a large odd constant and taking a modulus is the
    cheapest way to get a fixed, reproducible permutation. It is not a
    hash and it is not secret; it exists only so that trace_id order and
    rowid order are unrelated, the way they would be in a real system.
    """
    return (event_id * 2_654_435_761) % 999_983


def rows(count: int):
    """Yield `count` fully determined rows. One generator, no surprises."""
    rng = random.Random(SEED)
    for event_id in range(1, count + 1):
        run_id = (event_id - 1) // EVENTS_PER_RUN + 1
        day = 1 + (run_id * 7) % 28
        month = 1 + (run_id // 4) % 12
        year = 2024 + (run_id // 48) % 2
        yield (
            event_id,
            run_id,
            f"tr-{scramble(event_id):06d}-{event_id % 97:02d}",
            MODELS[event_id % len(MODELS)],
            STATUSES[rng.randrange(len(STATUSES))],
            round(rng.random(), 6),
            f"{year:04d}-{month:02d}-{day:02d}",
            f"run {run_id} step {(event_id - 1) % EVENTS_PER_RUN + 1}",
        )


def build(path: Path, count: int) -> None:
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA)
    started = time.perf_counter()
    with connection:
        connection.executemany(
            "INSERT INTO events"
            " (event_id, run_id, trace_id, model, status, score, created_on, note)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            rows(count),
        )
    elapsed = time.perf_counter() - started

    total = connection.execute("SELECT count(*) FROM events").fetchone()[0]
    distinct_runs = connection.execute(
        "SELECT count(DISTINCT run_id) FROM events"
    ).fetchone()[0]
    page_size = connection.execute("PRAGMA page_size").fetchone()[0]
    page_count = connection.execute("PRAGMA page_count").fetchone()[0]
    index_names = [
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_schema WHERE type = 'index' ORDER BY name"
        )
    ]
    connection.close()

    print(f"built {path.name}")
    print(f"  rows:            {total:,}")
    print(f"  distinct run_id: {distinct_runs:,} ({EVENTS_PER_RUN} events each)")
    print(f"  distinct model:  {len(MODELS)}")
    print(f"  page size:       {page_size:,} bytes")
    print(f"  pages:           {page_count:,}")
    print(f"  file size:       {path.stat().st_size:,} bytes")
    print(f"  named indexes:   {index_names if index_names else 'none — that is on purpose'}")
    print(f"  insert took:     {elapsed * 1000:,.0f} ms")
    print()
    print("A scan of this table has to read every one of those pages.")
    print("Nothing here is indexed yet except the implicit rowid B-tree.")


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("events.db")
    count = int(argv[2]) if len(argv) > 2 else DEFAULT_ROWS
    build(path, count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
