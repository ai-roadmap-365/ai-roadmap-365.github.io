#!/usr/bin/env bash
# Tests for the Day 089 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This suite is about measurements, which makes writing it a lesson in
# itself. There is exactly one rule and it is worth stating before the
# first check:
#
#   NO CHECK HERE ASSERTS A MILLISECOND FIGURE.
#
# A test that says "the indexed lookup takes under 0.05 ms" passes on the
# machine it was written on and fails on a busy laptop, a slower disk, a
# continuous-integration container or the same machine next year. It would
# not be measuring the lab; it would be measuring the computer. Every
# check below asserts a SHAPE instead:
#
#   * the plan changed from SCAN to SEARCH
#   * the two results contain exactly the same rows
#   * the indexed lookup is at least 20x faster than the scan
#   * inserting with five indexes is at least 1.5x slower than without
#   * a composite index serves these query shapes and cannot serve that one
#
# The two ratio thresholds are deliberately far below what the authoring
# machine measured — 20x against roughly 300x, and 1.5x against roughly
# 12x — so that a slow or noisy machine still passes while a genuinely
# broken lab still fails. That gap is the whole craft of testing around a
# measurement: assert the direction and an order of magnitude, never the
# number.
#
# Everything runs offline. No server, no network call, no third-party
# package: the standard library and the sqlite3 shell. Every database is
# built inside a temporary directory removed by a trap, so a completed run
# leaves nothing behind.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0
work_root=""

check() {
  local label="$1" ok="$2"
  checks=$((checks + 1))
  if [ "${ok}" = "yes" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    failures=$((failures + 1))
  fi
}

cleanup() {
  [ -n "${work_root}" ] && [ -d "${work_root}" ] && rm -rf "${work_root}"
}
trap cleanup EXIT INT TERM

resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

python_bin="$(resolve_tool python3 "${PYTHON:-}")" || {
  echo "FAIL: python3 not found on PATH." >&2
  echo "  Install Python 3.11 or newer and try again." >&2
  exit 1
}
sqlite_bin="$(resolve_tool sqlite3 "${SQLITE:-}")" || {
  echo "FAIL: the sqlite3 shell was not found on PATH." >&2
  echo "  macOS ships it. On Debian or Ubuntu: sudo apt install sqlite3" >&2
  echo "  Or point this suite at one: SQLITE=/path/to/sqlite3 bash tests/run_tests.sh" >&2
  exit 1
}

work_root="$(mktemp -d "${TMPDIR:-/tmp}/day089-XXXXXX")"
work="${work_root}/lab"
mkdir -p "${work}"
cp "${lab_dir}/examples/"*.py "${lab_dir}/examples/"*.sql "${work}/"

echo "Day 089 — Make It Fast"
echo

# ===========================================================================
echo "1. The tools report themselves, and they do not have to agree"
# ===========================================================================
shell_version="$("${sqlite_bin}" --version 2>/dev/null | awk '{print $1}')"
module_version="$("${python_bin}" -c 'import sqlite3; print(sqlite3.sqlite_version)' 2>/dev/null)"
echo "     sqlite3 shell library:  ${shell_version:-unknown}"
echo "     python3 module library: ${module_version:-unknown}"
case "${shell_version}" in
  3.*) check "the sqlite3 shell reports a SQLite 3 library version" "yes" ;;
  *)   check "the sqlite3 shell reports a SQLite 3 library version" "no" ;;
esac
case "${module_version}" in
  3.*) check "python3 can import sqlite3 and report its library version" "yes" ;;
  *)   check "python3 can import sqlite3 and report its library version" "no" ;;
esac
# Deliberately not an equality assertion: two programs, two copies of the
# library. On the authoring machine they differ, and that is not a fault.
if [ "${shell_version}" = "${module_version}" ]; then
  echo "     the two agree on this machine"
else
  echo "     the two DIFFER on this machine — this is normal, not a fault"
fi

# ===========================================================================
echo
echo "2. The table is built the same way every time"
# ===========================================================================
if (cd "${work}" && "${python_bin}" generate.py events.db 400000 >/dev/null 2>&1); then
  check "generate.py builds a 400,000-row table" "yes"
else
  check "generate.py builds a 400,000-row table" "no"
fi

rows="$("${sqlite_bin}" "${work}/events.db" "SELECT count(*) FROM events;" 2>/dev/null)"
check "the table holds exactly 400,000 rows" \
  "$([ "${rows}" = "400000" ] && echo yes || echo no)"

named="$("${sqlite_bin}" "${work}/events.db" \
  "SELECT count(*) FROM sqlite_schema WHERE type='index' AND sql IS NOT NULL;" 2>/dev/null)"
check "and no indexes of its own — every one in this lab is added by you" \
  "$([ "${named}" = "0" ] && echo yes || echo no)"

fingerprint="$("${sqlite_bin}" "${work}/events.db" \
  "SELECT trace_id||'|'||model||'|'||status||'|'||score FROM events WHERE event_id=123456;" 2>/dev/null)"
echo "     row 123456: ${fingerprint}"
if (cd "${work}" && "${python_bin}" generate.py again.db 5000 >/dev/null 2>&1 \
    && "${python_bin}" generate.py again2.db 5000 >/dev/null 2>&1); then
  sum_a="$("${sqlite_bin}" "${work}/again.db" "SELECT sum(score), sum(run_id), group_concat(trace_id) FROM events;" 2>/dev/null)"
  sum_b="$("${sqlite_bin}" "${work}/again2.db" "SELECT sum(score), sum(run_id), group_concat(trace_id) FROM events;" 2>/dev/null)"
  check "two builds of the same size are identical — the data is seeded" \
    "$([ -n "${sum_a}" ] && [ "${sum_a}" = "${sum_b}" ] && echo yes || echo no)"
else
  check "two builds of the same size are identical — the data is seeded" "no"
fi
rm -f "${work}/again.db" "${work}/again2.db"

# ===========================================================================
echo
echo "3. The idea in plain Python: a scan grows with n, a search does not"
# ===========================================================================
if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
import sys
sys.argv = ["scan_vs_bisect.py"]
from scan_vs_bisect import measure

small = measure(1_000, 200)
large = measure(100_000, 50)

# Answers must be identical — that is asserted inside measure(), which
# raises if the two ever disagree.
scan_growth = large["scan_steps"] / small["scan_steps"]
seek_growth = large["seek_steps"] / small["seek_steps"]

# 100x the data. A linear walk must cost far more; a binary search must
# cost barely more. Generous bounds: the shape, not the number.
assert scan_growth > 20, scan_growth
assert seek_growth < 3, seek_growth
assert small["seek_steps"] <= 12, small["seek_steps"]
assert large["seek_steps"] <= 20, large["seek_steps"]
sys.exit(0)
PY
); then
  check "100x the data costs the scan far more steps and bisect barely any" "yes"
else
  check "100x the data costs the scan far more steps and bisect barely any" "no"
fi

if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
import sys
from scan_vs_bisect import scan, seek, seek_steps

data = list(range(0, 3_000, 3))
for target in (0, 3, 1_500, 2_997, 1, 4_000, -1):
    assert scan(data, target) == seek(data, target), target
# A binary search over 1,000 sorted values takes at most 10 comparisons.
assert seek_steps(data, 1_500) <= 10
sys.exit(0)
PY
); then
  check "the hand-written scan and the binary search never disagree" "yes"
else
  check "the hand-written scan and the binary search never disagree" "no"
fi

if (cd "${work}" && "${python_bin}" scan_vs_bisect.py 2>/dev/null | grep -q "This is O(log n)"); then
  check "scan_vs_bisect.py runs end to end and reports both growth shapes" "yes"
else
  check "scan_vs_bisect.py runs end to end and reports both growth shapes" "no"
fi

# ===========================================================================
echo
echo "4. One CREATE INDEX: same rows, different plan, far less work"
# ===========================================================================
scan_plan="$("${sqlite_bin}" "${work}/events.db" \
  "EXPLAIN QUERY PLAN SELECT event_id, model, score FROM events WHERE run_id = 200;" 2>/dev/null)"
echo "     before: ${scan_plan}"
case "${scan_plan}" in
  *SCAN*) check "with no index the planner reports SCAN" "yes" ;;
  *)      check "with no index the planner reports SCAN" "no" ;;
esac

"${sqlite_bin}" "${work}/events.db" "CREATE INDEX ix_run ON events(run_id);" >/dev/null 2>&1
seek_plan="$("${sqlite_bin}" "${work}/events.db" \
  "EXPLAIN QUERY PLAN SELECT event_id, model, score FROM events WHERE run_id = 200;" 2>/dev/null)"
echo "     after:  ${seek_plan}"
case "${seek_plan}" in
  *"SEARCH events USING INDEX ix_run"*)
    check "with the index it reports SEARCH ... USING INDEX ix_run" "yes" ;;
  *)
    check "with the index it reports SEARCH ... USING INDEX ix_run" "no" ;;
esac
"${sqlite_bin}" "${work}/events.db" "DROP INDEX ix_run;" >/dev/null 2>&1

if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
"""Same rows, and a margin big enough to survive a slow machine."""
import sqlite3
import sys

from timing import drop_all_indexes, ratio, time_query

QUERY = "SELECT event_id, model, score FROM events WHERE run_id = ?"
MINIMUM_SPEEDUP = 20  # measured about 300x here; 20 leaves room for anything

connection = sqlite3.connect("events.db")
drop_all_indexes(connection)

scanned = time_query(connection, QUERY, (200,))
connection.execute("CREATE INDEX ix_run ON events(run_id)")
sought = time_query(connection, QUERY, (200,))

assert sorted(scanned["result"]) == sorted(sought["result"]), "the index changed the answer"
assert len(sought["result"]) == 100, len(sought["result"])
speedup = ratio(scanned, sought)
assert speedup >= MINIMUM_SPEEDUP, f"only {speedup:.1f}x faster"

drop_all_indexes(connection)
connection.commit()
connection.close()
sys.exit(0)
PY
); then
  check "the indexed lookup returns identical rows and is at least 20x faster" "yes"
else
  check "the indexed lookup returns identical rows and is at least 20x faster" "no"
fi

if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
"""The scan must grow with the table. That is the shape being taught."""
import sqlite3
import sys
import tempfile
from pathlib import Path

from generate import build
from timing import time_query

QUERY = "SELECT event_id, model, score FROM events WHERE run_id = ?"

with tempfile.TemporaryDirectory() as directory:
    timings = {}
    for size in (50_000, 400_000):
        path = Path(directory) / f"s{size}.db"
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            build(path, size)
        connection = sqlite3.connect(path)
        timings[size] = time_query(connection, QUERY, (200,))["best_ms"]
        connection.close()

# 8x the rows. A scan should cost several times more. Asserting "more than
# 3x" rather than "8x" leaves room for cache effects and a noisy machine
# while still failing if the cost stopped growing at all.
growth = timings[400_000] / timings[50_000]
assert growth > 3, f"a scan of 8x the table was only {growth:.1f}x the cost"
sys.exit(0)
PY
); then
  check "8x the rows costs the scan several times more — the cost grows with n" "yes"
else
  check "8x the rows costs the scan several times more — the cost grows with n" "no"
fi

# ===========================================================================
echo
echo "5. The leftmost-prefix rule, query shape by query shape"
# ===========================================================================
"${sqlite_bin}" "${work}/events.db" "CREATE INDEX ix_run_status ON events(run_id, status);" >/dev/null 2>&1

prefix_plan() {
  "${sqlite_bin}" "${work}/events.db" "EXPLAIN QUERY PLAN $1" 2>/dev/null | tr '\n' ' '
}

both="$(prefix_plan "SELECT count(*) FROM events WHERE run_id = 200 AND status = 'failed';")"
lead="$(prefix_plan "SELECT count(*) FROM events WHERE run_id = 200;")"
trail="$(prefix_plan "SELECT count(*) FROM events WHERE status = 'failed';")"
swapped="$(prefix_plan "SELECT count(*) FROM events WHERE status = 'failed' AND run_id = 200;")"

case "${both}" in *SEARCH*ix_run_status*) a=yes ;; *) a=no ;; esac
check "an index on (run_id, status) serves WHERE run_id = ? AND status = ?" "${a}"
case "${lead}" in *SEARCH*ix_run_status*) a=yes ;; *) a=no ;; esac
check "and serves the leading column alone" "${a}"
case "${trail}" in *SEARCH*) a=no ;; *SCAN*) a=yes ;; *) a=no ;; esac
check "and CANNOT seek on the trailing column alone — this is the rule" "${a}"
case "${swapped}" in *SEARCH*ix_run_status*) a=yes ;; *) a=no ;; esac
check "the order of conditions in WHERE is irrelevant; column order in the index is not" "${a}"
"${sqlite_bin}" "${work}/events.db" "DROP INDEX ix_run_status;" >/dev/null 2>&1

# ===========================================================================
echo
echo "6. Covering, ORDER BY and partial indexes"
# ===========================================================================
"${sqlite_bin}" "${work}/events.db" "CREATE INDEX ix_run_score ON events(run_id, score);" >/dev/null 2>&1
covering="$(prefix_plan "SELECT score FROM events WHERE run_id = 200;")"
case "${covering}" in
  *"COVERING INDEX ix_run_score"*) a=yes ;; *) a=no ;;
esac
check "a query whose columns are all in the index reports COVERING INDEX" "${a}"
"${sqlite_bin}" "${work}/events.db" "DROP INDEX ix_run_score;" >/dev/null 2>&1

order_before="$(prefix_plan "SELECT event_id, created_on FROM events ORDER BY created_on LIMIT 20;")"
case "${order_before}" in
  *"USE TEMP B-TREE FOR ORDER BY"*) a=yes ;; *) a=no ;;
esac
check "ORDER BY with no usable index builds a temporary B-tree" "${a}"

"${sqlite_bin}" "${work}/events.db" "CREATE INDEX ix_created ON events(created_on);" >/dev/null 2>&1
order_after="$(prefix_plan "SELECT event_id, created_on FROM events ORDER BY created_on LIMIT 20;")"
case "${order_after}" in
  *"USE TEMP B-TREE"*) a=no ;; *ix_created*) a=yes ;; *) a=no ;;
esac
check "and the temporary B-tree disappears once an index supplies the order" "${a}"
"${sqlite_bin}" "${work}/events.db" "DROP INDEX ix_created;" >/dev/null 2>&1

if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
"""A partial index is usable only where the planner can prove it applies,
and it costs a fraction of the pages a full one would."""
import sqlite3
import sys

from timing import drop_all_indexes, file_pages, plan

FAILURES = ("SELECT count(*) FROM events"
            " WHERE status = 'failed' AND created_on >= '2025-06-01'")
DATES_ONLY = "SELECT count(*) FROM events WHERE created_on >= '2025-06-01'"

connection = sqlite3.connect("events.db")
drop_all_indexes(connection)

before, _ = file_pages(connection)
connection.execute("CREATE INDEX ix_full ON events(created_on)")
full, _ = file_pages(connection)
connection.execute("DROP INDEX ix_full")

reset, _ = file_pages(connection)
connection.execute(
    "CREATE INDEX ix_failed_created ON events(created_on) WHERE status = 'failed'")
partial, _ = file_pages(connection)

assert "SEARCH" in plan(connection, FAILURES), plan(connection, FAILURES)
assert "SEARCH" not in plan(connection, DATES_ONLY), plan(connection, DATES_ONLY)

full_pages = full - before
partial_pages = partial - reset
assert full_pages > 0 and partial_pages > 0, (full_pages, partial_pages)
assert partial_pages * 3 < full_pages, (partial_pages, full_pages)

drop_all_indexes(connection)
connection.commit()
connection.close()
sys.exit(0)
PY
); then
  check "a partial index serves the query it covers, refuses the one it does not, and costs far fewer pages" "yes"
else
  check "a partial index serves the query it covers, refuses the one it does not, and costs far fewer pages" "no"
fi

# ===========================================================================
echo
echo "7. When an index is present and the planner will not use it"
# ===========================================================================
if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
import sqlite3
import sys

from timing import drop_all_indexes, plan

connection = sqlite3.connect("events.db")
drop_all_indexes(connection)
connection.execute("CREATE INDEX ix_trace ON events(trace_id)")
trace = connection.execute(
    "SELECT trace_id FROM events WHERE event_id = 123456").fetchone()[0]

plain = plan(connection, "SELECT event_id FROM events WHERE trace_id = ?", (trace,))
wrapped = plan(connection,
               "SELECT event_id FROM events WHERE lower(trace_id) = ?",
               (trace.lower(),))
assert "SEARCH" in plain, plain
assert "SCAN" in wrapped, wrapped

connection.execute("CREATE INDEX ix_lower_trace ON events(lower(trace_id))")
rescued = plan(connection,
               "SELECT event_id FROM events WHERE lower(trace_id) = ?",
               (trace.lower(),))
assert "SEARCH" in rescued, rescued

drop_all_indexes(connection)
connection.commit()
connection.close()
sys.exit(0)
PY
); then
  check "a function around the column forces a scan; an expression index fixes it" "yes"
else
  check "a function around the column forces a scan; an expression index fixes it" "no"
fi

if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
import sqlite3
import sys

from timing import drop_all_indexes, plan

connection = sqlite3.connect("events.db")
drop_all_indexes(connection)
connection.execute("CREATE INDEX ix_trace ON events(trace_id)")
trace = connection.execute(
    "SELECT trace_id FROM events WHERE event_id = 123456").fetchone()[0]

leading = plan(connection, "SELECT event_id FROM events WHERE trace_id LIKE ?",
               (f"%{trace[-6:]}",))
assert "SCAN" in leading, leading

prefix = trace[:8]
upper = prefix[:-1] + chr(ord(prefix[-1]) + 1)
ranged = plan(connection,
              "SELECT event_id FROM events WHERE trace_id >= ? AND trace_id < ?",
              (prefix, upper))
assert "SEARCH" in ranged, ranged

# And the rewrite must not change the answer.
by_like = sorted(connection.execute(
    "SELECT event_id FROM events WHERE trace_id LIKE ?", (f"{prefix}%",)).fetchall())
by_range = sorted(connection.execute(
    "SELECT event_id FROM events WHERE trace_id >= ? AND trace_id < ?",
    (prefix, upper)).fetchall())
assert by_like == by_range, (len(by_like), len(by_range))

drop_all_indexes(connection)
connection.commit()
connection.close()
sys.exit(0)
PY
); then
  check "a leading wildcard forces a scan; the range rewrite seeks and returns the same rows" "yes"
else
  check "a leading wildcard forces a scan; the range rewrite seeks and returns the same rows" "no"
fi

if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
import sqlite3
import sys

from timing import drop_all_indexes, plan

connection = sqlite3.connect("events.db")
drop_all_indexes(connection)
connection.execute("CREATE INDEX ix_trace ON events(trace_id)")
connection.execute("CREATE INDEX ix_run ON events(run_id)")
trace = connection.execute(
    "SELECT trace_id FROM events WHERE event_id = 123456").fetchone()[0]

both_indexed = plan(connection,
                    "SELECT event_id FROM events WHERE run_id = ? OR trace_id = ?",
                    (200, trace))
one_missing = plan(connection,
                   "SELECT event_id FROM events WHERE run_id = ? OR score > ?",
                   (200, 0.999999))
assert "SCAN" not in both_indexed, both_indexed
assert "SCAN" in one_missing, one_missing

drop_all_indexes(connection)
connection.commit()
connection.close()
sys.exit(0)
PY
); then
  check "an OR whose branches are all indexed avoids the scan; one bare branch does not" "yes"
else
  check "an OR whose branches are all indexed avoids the scan; one bare branch does not" "no"
fi

# ===========================================================================
echo
echo "8. The other half of the trade: what indexes cost to write"
# ===========================================================================
if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
"""Writes must get slower and the file must get bigger. Direction and a
loose ratio, never a millisecond figure."""
import shutil
import sys
import tempfile
from pathlib import Path

from generate import rows
from write_cost import ADDED_ROWS, BASE_ROWS, INDEXES, one_trial

MINIMUM_SLOWDOWN = 1.5  # measured about 12x here

batch = list(rows(BASE_ROWS + ADDED_ROWS))
base, extra = batch[:BASE_ROWS], batch[BASE_ROWS:]

directory = Path(tempfile.mkdtemp(prefix="day089-writetest-"))
try:
    bare = min(one_trial(directory, "bare", [], base, extra)["ms"] for _ in range(2))
    indexed_trial = one_trial(directory, "indexed", INDEXES, base, extra)
    indexed = min(indexed_trial["ms"],
                  one_trial(directory, "indexed", INDEXES, base, extra)["ms"])
finally:
    shutil.rmtree(directory, ignore_errors=True)

slowdown = indexed / bare
assert slowdown >= MINIMUM_SLOWDOWN, f"only {slowdown:.2f}x slower"
sys.exit(0)
PY
); then
  check "inserting the same rows with five indexes is at least 1.5x slower" "yes"
else
  check "inserting the same rows with five indexes is at least 1.5x slower" "no"
fi

if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
"""And it costs disk. An index is a second copy of the data it covers."""
import sqlite3
import sys

from timing import drop_all_indexes, file_pages

connection = sqlite3.connect("events.db")
drop_all_indexes(connection)
bare_pages, _ = file_pages(connection)
connection.execute("CREATE INDEX ix_trace ON events(trace_id)")
connection.execute("CREATE INDEX ix_run ON events(run_id)")
connection.execute("CREATE INDEX ix_created ON events(created_on)")
indexed_pages, _ = file_pages(connection)
drop_all_indexes(connection)
connection.commit()
connection.close()

assert indexed_pages > bare_pages, (bare_pages, indexed_pages)
# Three indexes over a table this shape cost a real fraction of it, not a
# rounding error. 10% is a floor, not a prediction.
assert (indexed_pages - bare_pages) > bare_pages * 0.10, (bare_pages, indexed_pages)
sys.exit(0)
PY
); then
  check "three indexes add a real fraction of the table's pages to the file" "yes"
else
  check "three indexes add a real fraction of the table's pages to the file" "no"
fi

# ===========================================================================
echo
echo "9. The examples all run, and the SQL walkthrough leaves nothing behind"
# ===========================================================================
if (cd "${work}" && "${python_bin}" lookup.py events.db 2>/dev/null | grep -q "Same rows every time"); then
  check "lookup.py measures four table sizes and finishes" "yes"
else
  check "lookup.py measures four table sizes and finishes" "no"
fi

if (cd "${work}" && "${python_bin}" composite.py events.db 2>/dev/null | grep -q "COVERING INDEX"); then
  check "composite.py demonstrates the leftmost prefix and a covering index" "yes"
else
  check "composite.py demonstrates the leftmost prefix and a covering index" "no"
fi

if (cd "${work}" && "${python_bin}" blocked.py events.db 2>/dev/null | grep -q "MULTI-INDEX OR"); then
  check "blocked.py reaches the OR case and reports a multi-index plan" "yes"
else
  check "blocked.py reaches the OR case and reports a multi-index plan" "no"
fi

if (cd "${work}" && "${python_bin}" write_cost.py 2>/dev/null | grep -q "longer with five indexes"); then
  check "write_cost.py measures the insert cost both ways" "yes"
else
  check "write_cost.py measures the insert cost both ways" "no"
fi

if (cd "${work}" && "${sqlite_bin}" events.db < plans.sql >/dev/null 2>&1); then
  check "plans.sql runs in the sqlite3 shell" "yes"
else
  check "plans.sql runs in the sqlite3 shell" "no"
fi

leftover="$("${sqlite_bin}" "${work}/events.db" \
  "SELECT count(*) FROM sqlite_schema WHERE type='index' AND sql IS NOT NULL;" 2>/dev/null)"
check "and every example puts the table back the way it found it — no indexes left" \
  "$([ "${leftover}" = "0" ] && echo yes || echo no)"

# ===========================================================================
echo
echo "10. The starter is runnable, and carries its exercises"
# ===========================================================================
starter_work="${work_root}/starter"
mkdir -p "${starter_work}"
cp "${lab_dir}/starter/"* "${starter_work}/"
cp "${lab_dir}/examples/generate.py" "${starter_work}/"
(cd "${starter_work}" && "${python_bin}" generate.py mine.db 25000 >/dev/null 2>&1)

if (cd "${starter_work}" && "${sqlite_bin}" mine.db < indexes.sql >/dev/null 2>&1); then
  check "the starter SQL applies as shipped, before you have written a line" "yes"
else
  check "the starter SQL applies as shipped, before you have written a line" "no"
fi

sql_exercises="$(grep -c "^-- EXERCISE" "${lab_dir}/starter/indexes.sql" || true)"
check "the starter SQL carries its 6 numbered exercises" \
  "$([ "${sql_exercises}" = "6" ] && echo yes || echo no)"

py_exercises="$(grep -c "^# EXERCISE\|^    # EXERCISE" "${lab_dir}/starter/measure.py" || true)"
check "the starter measuring tool carries its 5 numbered exercises" \
  "$([ "${py_exercises}" = "5" ] && echo yes || echo no)"

if (cd "${starter_work}" && "${python_bin}" measure.py mine.db 2>/dev/null | grep -q "EXERCISE 1"); then
  check "running the unfinished starter names the next exercise instead of a traceback" "yes"
else
  check "running the unfinished starter names the next exercise instead of a traceback" "no"
fi

starter_exit=0
(cd "${starter_work}" && "${python_bin}" measure.py mine.db >/dev/null 2>&1) || starter_exit=$?
check "and exits non-zero, so an unfinished lab cannot look finished" \
  "$([ "${starter_exit}" -ne 0 ] && echo yes || echo no)"

# ===========================================================================
echo
echo "11. Nothing here reaches the network or needs anything installed"
# ===========================================================================
if "${python_bin}" - "${lab_dir}" <<'PY' >/dev/null 2>&1
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
banned = re.compile(r"https?://(?!\S*\.invalid)", re.IGNORECASE)
offenders = []
for directory in ("examples", "starter", "tests"):
    for path in (root / directory).rglob("*"):
        if path.is_file() and path.suffix in {".py", ".sql", ".sh"}:
            if banned.search(path.read_text(encoding="utf-8", errors="ignore")):
                offenders.append(path.name)
for name in offenders:
    print(name, file=sys.stderr)
sys.exit(1 if offenders else 0)
PY
then
  check "no executable lab file contains a network address of any kind" "yes"
else
  check "no executable lab file contains a network address of any kind" "no"
fi

if "${python_bin}" - "${lab_dir}" <<'PY' >/dev/null 2>&1
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
third_party = re.compile(
    r"^\s*(import|from)\s+(requests|httpx|urllib3|pandas|numpy|sqlalchemy)\b", re.M)
offenders = []
for directory in ("examples", "starter", "tests"):
    for path in (root / directory).rglob("*.py"):
        if third_party.search(path.read_text(encoding="utf-8", errors="ignore")):
            offenders.append(path.name)
for name in offenders:
    print(name, file=sys.stderr)
sys.exit(1 if offenders else 0)
PY
then
  check "no lab file imports a third-party package — standard library only" "yes"
else
  check "no lab file imports a third-party package — standard library only" "no"
fi

check "every database this run created lives under a temporary directory" \
  "$([ ! -e "${lab_dir}/events.db" ] && [ ! -e "${lab_dir}/starter/mine.db" ] \
     && [ ! -e "${lab_dir}/tests/events.db" ] && echo yes || echo no)"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
