"""YOUR WORK — the measuring tool, built from nothing.

    python3 ../examples/generate.py events.db 200000
    python3 measure.py events.db

Five numbered exercises. The file runs as shipped: it will tell you which
exercise is next and exit non-zero, so an unfinished lab can never look
finished. Complete them in order and the last run prints a table of
measurements and exits 0.

The rule for this whole lab: you are not allowed to believe anything you
did not time. That includes believing that indexes help.

Each exercise names the check in tests/run_tests.sh that confirms it.
"""

from __future__ import annotations

import sqlite3
import statistics
import sys
import time
from pathlib import Path

REPEATS = 7
QUERY = "SELECT event_id, model, score FROM events WHERE run_id = ?"
TARGET_RUN = 200


def next_exercise(number: int, what: str):
    """Stop with the next exercise named, rather than with a traceback."""
    print(f"EXERCISE {number} is not done yet: {what}")
    print(f"Open {Path(__file__).name} and look for '# EXERCISE {number}'.")
    raise SystemExit(1)


# EXERCISE 1 — best and median.
#
# Given a list of durations in milliseconds, return a dict with keys
# "best_ms", "median_ms" and "spread_ms" (worst minus best).
#
# Why both: the BEST run is the closest you get to the work itself, because
# it is the run the operating system interrupted least. The MEDIAN is what
# you would typically wait. If they are far apart, the machine was busy and
# the number means less than it looks like it does.
#
# `statistics.median` is imported for you.
# Checked by: "best, median and spread are computed from the samples"
def summarise(samples):
    next_exercise(1, "compute best, median and spread from a list of durations")


# EXERCISE 2 — time a query properly.
#
# Run `connection.execute(sql, params).fetchall()` REPEATS times, timing
# each run with `time.perf_counter()`, and return summarise(...) of the
# durations in MILLISECONDS, plus the rows from the last run under the key
# "result".
#
# fetchall() is not optional. Without it you time how long SQLite takes to
# prepare the statement and produce the first row — which for a full scan
# is misleadingly fast, because the scanning happens as you step.
#
# Checked by: "the timing helper runs the query more than once"
def time_query(connection, sql, params=()):
    next_exercise(2, "run the query REPEATS times and summarise the durations")


# EXERCISE 3 — ask the planner what it intends to do.
#
# Run "EXPLAIN QUERY PLAN " + sql and return the last column of every row,
# joined with " / ". That last column is the human-readable detail:
# "SCAN events", "SEARCH events USING INDEX ix_run (run_id=?)", and so on.
#
# Checked by: "the plan helper returns the planner's own description"
def plan(connection, sql, params=()):
    next_exercise(3, "return EXPLAIN QUERY PLAN's detail column, joined with ' / '")


# EXERCISE 4 — the one word that decides everything.
#
# Return True if the plan text describes a seek, and False if anything in
# it is a scan.
#
# Be careful here, because this is the trap the lesson is about: a plan can
# name your index and still be a scan. "SCAN events USING COVERING INDEX
# ix_trace" means the engine walked every entry of the index instead of
# every row of the table — narrower, still linear, still not a seek. Only
# SEARCH means a descent to the matching rows.
#
# Checked by: "a plan naming an index is still a scan unless it says SEARCH"
def is_seek(plan_text):
    next_exercise(4, "return True only when no step of the plan is a SCAN")


def show(connection, label, sql, params=()):
    measurement = time_query(connection, sql, params)
    plan_text = plan(connection, sql, params)
    verdict = "SEEK" if is_seek(plan_text) else "SCAN"
    print(f"  {label}")
    print(f"    plan : [{verdict}] {plan_text}")
    print(
        f"    time : best {measurement['best_ms']:8.3f} ms"
        f" | median {measurement['median_ms']:8.3f} ms"
        f" | spread {measurement['spread_ms']:6.3f} ms"
        f" | rows {len(measurement['result']):,}"
    )
    return plan_text, measurement


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("events.db")
    if not path.exists():
        print(f"{path} does not exist. Build it first:", file=sys.stderr)
        print(f"  python3 ../examples/generate.py {path} 200000", file=sys.stderr)
        return 2

    connection = sqlite3.connect(path)
    for row in connection.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'index' AND sql IS NOT NULL"
    ).fetchall():
        connection.execute(f'DROP INDEX "{row[0]}"')

    # A one-line self-check, so the exercises are reported in the order you
    # are meant to build them rather than the order the code happens to
    # reach them.
    summarise([3.0, 1.0, 2.0])

    total = connection.execute("SELECT count(*) FROM events").fetchone()[0]
    print(f"{path.name}: {total:,} rows, no indexes of your own yet")
    print(f"Query: {QUERY}   (run_id = {TARGET_RUN})")
    print()

    before_plan, before = show(connection, "before any index", QUERY, (TARGET_RUN,))

    # EXERCISE 5 — create the index, then measure again.
    #
    # Create an index named ix_run on events(run_id), then delete the line
    # below. One statement. This is the entire intervention.
    #
    # Checked by: "the starter creates an index and re-measures"
    next_exercise(5, "CREATE INDEX ix_run ON events(run_id), then remove this line")

    after_plan, after = show(connection, "after CREATE INDEX", QUERY, (TARGET_RUN,))

    same = sorted(before["result"]) == sorted(after["result"])
    faster = before["best_ms"] / after["best_ms"]
    print()
    print(f"  same rows both times : {same}")
    print(f"  faster by            : {faster:.0f}x on the best-of-{REPEATS} figure")
    print(f"  plan changed         : {before_plan}  ->  {after_plan}")
    print()
    print("  Those milliseconds are yours, from this machine, today. The shape")
    print("  is what travels: one column grows with the table and one does not.")

    connection.execute("DROP INDEX ix_run")
    connection.commit()
    connection.close()

    if not same:
        print("FAIL: the index changed the answer. That must never happen.")
        return 1
    if not is_seek(after_plan):
        print("FAIL: the plan after CREATE INDEX is still a scan.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
