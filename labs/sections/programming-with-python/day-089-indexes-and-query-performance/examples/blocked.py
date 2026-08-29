"""When the index is there and the planner will not touch it.

    python3 blocked.py events.db

This is the part people get wrong, because the index exists, the column
is indexed, the query mentions the column, and the query is still slow.
An index is a sorted copy of the COLUMN'S VALUES. Anything that asks a
question about something other than those exact values — a function
applied to them, a match that does not start at the beginning, a
condition the index cannot bracket — puts the answer outside what the
sorted order can find.

Five cases, each with the fix where a fix exists:

  1. A function wrapping the column          -> an expression index
  2. An expression on the column             -> store or index the expression
  3. LIKE with a leading wildcard            -> no fix; a different tool
  4. LIKE with a trailing wildcard           -> a range, or case_sensitive_like
  5. OR across two columns                   -> index both, or write UNION

Watch the plan line, not just the milliseconds. `SCAN events USING
COVERING INDEX ...` still contains the word SCAN, and that is the word
that matters: the planner decided the index was a cheaper thing to walk
end-to-end than the table, which is not the same as finding anything.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from timing import drop_all_indexes, fmt, plan, time_query

RULE = "-" * 78


def verdict(plan_text: str) -> str:
    """The one word that decides everything.

    If any step of the plan says SCAN, something is being walked end to
    end — the table, or an index used as a narrower table. Only SEARCH
    means the engine descended a tree to the rows it wanted.
    """
    return "SCAN" if "SCAN" in plan_text else "SEEK"


def show(connection, label, sql, params=()):
    plan_text = plan(connection, sql, params)
    measurement = time_query(connection, sql, params)
    print(f"  {label}")
    print(f"    plan : [{verdict(plan_text)}] {plan_text}")
    print(f"    time : {fmt(measurement)}   rows: {len(measurement['result']):,}")
    return plan_text, measurement


def section(title: str) -> None:
    print()
    print(RULE)
    print(title)
    print(RULE)


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("events.db")
    if not path.exists():
        print(f"{path} does not exist. Run: python3 generate.py {path}", file=sys.stderr)
        return 2

    connection = sqlite3.connect(path)
    drop_all_indexes(connection)
    connection.execute("CREATE INDEX ix_trace ON events(trace_id)")
    connection.execute("CREATE INDEX ix_run ON events(run_id)")

    total = connection.execute("SELECT count(*) FROM events").fetchone()[0]
    trace = connection.execute(
        "SELECT trace_id FROM events WHERE event_id = 123456"
    ).fetchone()[0]
    print(f"{path.name}: {total:,} rows")
    print("Indexes present for all of the below: ix_trace(trace_id), ix_run(run_id)")
    print(f"The value being looked for: trace_id = {trace!r}")

    # ---------------------------------------------------------------- 0
    section("0. The baseline: plain equality on an indexed column")
    baseline = show(
        connection,
        "WHERE trace_id = ?",
        "SELECT event_id FROM events WHERE trace_id = ?",
        (trace,),
    )[1]

    # ---------------------------------------------------------------- 1
    section("1. A function wrapping the column")
    show(
        connection,
        "WHERE lower(trace_id) = ?   — the index holds trace_id, not lower(trace_id)",
        "SELECT event_id FROM events WHERE lower(trace_id) = ?",
        (trace.lower(),),
    )
    connection.execute("CREATE INDEX ix_lower_trace ON events(lower(trace_id))")
    show(
        connection,
        "the fix: CREATE INDEX ix_lower_trace ON events(lower(trace_id))",
        "SELECT event_id FROM events WHERE lower(trace_id) = ?",
        (trace.lower(),),
    )
    connection.execute("DROP INDEX ix_lower_trace")
    print()
    print("  An expression index stores the answer to lower(trace_id) for every")
    print("  row and sorts THAT. The rule is exact: the expression in the query")
    print("  must match the expression in the index, character for character in")
    print("  meaning. upper() will not use an index built on lower().")

    # ---------------------------------------------------------------- 2
    section("2. An expression on the column")
    show(
        connection,
        "WHERE substr(trace_id, 4) = ?   — asking about part of the value",
        "SELECT event_id FROM events WHERE substr(trace_id, 4) = ?",
        (trace[3:],),
    )
    print()
    print("  Same cause, and the same two fixes: an expression index, or —")
    print("  usually better — store the part you actually query as its own")
    print("  column. If you keep asking half a question, keep half a column.")

    # ---------------------------------------------------------------- 3
    section("3. LIKE with a leading wildcard")
    show(
        connection,
        f"WHERE trace_id LIKE '%{trace[-6:]}'",
        "SELECT event_id FROM events WHERE trace_id LIKE ?",
        (f"%{trace[-6:]}",),
    )
    print()
    print("  There is no fix, and that is worth saying plainly. A B-tree finds")
    print("  things by their beginning; '%abc' says the beginning is unknown.")
    print("  If you genuinely need it: index a reversed copy of the column when")
    print("  the wildcard is always leading, or reach for full-text search —")
    print("  SQLite ships FTS5 for exactly this. Do not add an ordinary index")
    print("  and hope.")

    # ---------------------------------------------------------------- 4
    section("4. LIKE with a trailing wildcard")
    prefix = trace[:8]
    show(
        connection,
        f"WHERE trace_id LIKE '{prefix}%'   — a prefix, which a B-tree could find",
        "SELECT event_id FROM events WHERE trace_id LIKE ?",
        (f"{prefix}%",),
    )
    upper_bound = prefix[:-1] + chr(ord(prefix[-1]) + 1)
    show(
        connection,
        f"the rewrite: WHERE trace_id >= '{prefix}' AND trace_id < '{upper_bound}'",
        "SELECT event_id FROM events WHERE trace_id >= ? AND trace_id < ?",
        (prefix, upper_bound),
    )
    connection.execute("PRAGMA case_sensitive_like = ON")
    show(
        connection,
        "or: PRAGMA case_sensitive_like = ON, then the same LIKE",
        "SELECT event_id FROM events WHERE trace_id LIKE ?",
        (f"{prefix}%",),
    )
    connection.execute("PRAGMA case_sensitive_like = OFF")
    print()
    print("  This one surprises people, so read the three plans above together.")
    print("  A prefix LIKE is bracketable in principle, but SQLite's LIKE is")
    print("  case-insensitive by default while the index is sorted in binary")
    print("  order — and a case-insensitive match cannot be answered from a")
    print("  case-sensitive ordering. Turn LIKE case-sensitive and the planner")
    print("  rewrites it into exactly the range shown above, all by itself.")

    # ---------------------------------------------------------------- 5
    section("5. OR across different columns")
    show(
        connection,
        "WHERE run_id = ? OR trace_id = ?   — BOTH columns indexed",
        "SELECT event_id FROM events WHERE run_id = ? OR trace_id = ?",
        (200, trace),
    )
    show(
        connection,
        "WHERE run_id = ? OR score > ?      — score has no index",
        "SELECT event_id FROM events WHERE run_id = ? OR score > ?",
        (200, 0.999999),
    )
    show(
        connection,
        "the rewrite: UNION of two indexed halves",
        "SELECT event_id FROM events WHERE run_id = ?"
        " UNION SELECT event_id FROM events WHERE trace_id = ?",
        (200, trace),
    )
    print()
    print("  The honest version of the folklore: OR is not automatically fatal.")
    print("  When EVERY branch has an index, SQLite runs each one and merges —")
    print("  that is the MULTI-INDEX OR plan above. One unindexed branch and the")
    print("  whole thing collapses to a scan, because a row failing the indexed")
    print("  test might still pass the other one. An OR is only as indexed as")
    print("  its worst branch.")

    # ---------------------------------------------------------------- end
    section("What the five cases have in common")
    print("  In every failing case the index was present and the column was")
    print("  named. What was missing was that the query asked about something")
    print("  the sorted order does not contain: a transformed value, a match")
    print("  with an unknown beginning, or a condition that cannot be bracketed.")
    print()
    print(f"  For scale, the plain indexed lookup at the top: {fmt(baseline)}")
    print("  Everything in sections 1 to 3 was hundreds of times slower than")
    print("  that, with the index sitting right there unused.")

    drop_all_indexes(connection)
    connection.commit()
    connection.close()
    print()
    print(RULE)
    print("Indexes dropped. The table is back to how generate.py left it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
