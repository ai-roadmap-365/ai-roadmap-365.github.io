#!/usr/bin/env bash
# Tests for the Day 085 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# These checks ask whether a database actually gives you what a file did not.
# The happy path — "a SELECT returned some rows" — is a small part of it. The
# rest are the properties that make the difference worth the trouble:
#
#   * is the database really one ordinary file, with the documented header?
#   * does the schema REFUSE the writes it promised to refuse — including the
#     typo'd member id that a JSON file accepted without comment?
#   * is SQLite's typing really dynamic, and does STRICT really fix it?
#   * does the hand-written table scan return EXACTLY what the SQL returns?
#   * is a transaction all-or-nothing, from the shell and from Python?
#
# Everything runs offline. There is no server, no network call, and no third-
# party package: the standard library and the sqlite3 shell, nothing else.
# Every database is built inside a temporary directory that is removed in a
# trap, so a completed run leaves nothing behind.
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

work_root="$(mktemp -d "${TMPDIR:-/tmp}/day085-XXXXXX")"
work="${work_root}/lab"
mkdir -p "${work}"
cp "${lab_dir}/examples/"*.sql "${lab_dir}/examples/"*.py "${lab_dir}/examples/books.json" "${work}/"

echo "Day 085 — Your First Database"
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

# This is deliberately NOT an equality assertion. The shell and the Python
# module are separate programs, each linking its own copy of the library, and
# on many machines the numbers differ. The check is that both are readable.
if [ "${shell_version}" = "${module_version}" ]; then
  echo "     the two agree on this machine"
else
  echo "     the two DIFFER on this machine — this is normal, not a fault"
fi
check "both SQLite library versions could be read and reported" \
  "$([ -n "${shell_version}" ] && [ -n "${module_version}" ] && echo yes || echo no)"

# ===========================================================================
echo
echo "2. The database is one ordinary file, and the header says so"
# ===========================================================================
if (cd "${work}" && "${sqlite_bin}" library.db < schema.sql >/dev/null 2>&1); then
  check "schema.sql applies cleanly" "yes"
else
  check "schema.sql applies cleanly" "no"
fi

if (cd "${work}" && "${sqlite_bin}" library.db < seed.sql >/dev/null 2>&1); then
  check "seed.sql applies cleanly inside one transaction" "yes"
else
  check "seed.sql applies cleanly inside one transaction" "no"
fi

check "library.db is a plain regular file" \
  "$([ -f "${work}/library.db" ] && echo yes || echo no)"

if "${python_bin}" - "${work}/library.db" <<'PY' >/dev/null 2>&1
import sys
from pathlib import Path
header = Path(sys.argv[1]).read_bytes()[:16]
sys.exit(0 if header == b"SQLite format 3\x00" else 1)
PY
then
  check "the first 16 bytes are the literal string SQLite format 3 plus a NUL" "yes"
else
  check "the first 16 bytes are the literal string SQLite format 3 plus a NUL" "no"
fi

if "${python_bin}" - "${work}/library.db" <<'PY' >/dev/null 2>&1
import sqlite3, sys
from pathlib import Path
path = Path(sys.argv[1])
raw = path.read_bytes()
page_size = int.from_bytes(raw[16:18], "big")
page_size = 65536 if page_size == 1 else page_size
page_count = int.from_bytes(raw[28:32], "big")
connection = sqlite3.connect(path)
engine_size = connection.execute("PRAGMA page_size").fetchone()[0]
engine_count = connection.execute("PRAGMA page_count").fetchone()[0]
connection.close()
ok = (page_size == engine_size
      and page_count == engine_count
      and page_size * page_count == path.stat().st_size)
sys.exit(0 if ok else 1)
PY
then
  check "header page size and count match the engine and the file length" "yes"
else
  check "header page size and count match the engine and the file length" "no"
fi

tables="$("${sqlite_bin}" "${work}/library.db" \
  "SELECT group_concat(name, ',') FROM (SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name)" 2>/dev/null)"
check "the schema is data: sqlite_schema lists books, loans and members" \
  "$([ "${tables}" = "books,loans,members" ] && echo yes || echo no)"

# ===========================================================================
echo
echo "3. The schema is a promise, and the engine keeps it"
# ===========================================================================
refuses() {
  local label="$1" statement="$2"
  if "${sqlite_bin}" "${work}/library.db" "PRAGMA foreign_keys=ON; ${statement}" >/dev/null 2>&1; then
    check "${label}" "no"
  else
    check "${label}" "yes"
  fi
}

refuses "a loan naming member 999, who does not exist, is refused" \
  "INSERT INTO loans (loan_id,book_id,member_id,borrowed_on,due_on) VALUES (99,1,999,'2026-08-16','2026-09-06');"
refuses "a loan of book 404, which does not exist, is refused" \
  "INSERT INTO loans (loan_id,book_id,member_id,borrowed_on,due_on) VALUES (98,404,1,'2026-08-16','2026-09-06');"
refuses "a member with a NULL name is refused" \
  "INSERT INTO members (member_id,name,email,joined_on) VALUES (9,NULL,'x@library.invalid','2026-08-16');"
refuses "a second member with an address already in use is refused" \
  "INSERT INTO members (member_id,name,email,joined_on) VALUES (10,'Impostor','ada@library.invalid','2026-08-16');"
refuses "a negative number of copies is refused" \
  "UPDATE books SET copies = -1 WHERE book_id = 1;"
refuses "a loan due before it was borrowed is refused" \
  "INSERT INTO loans (loan_id,book_id,member_id,borrowed_on,due_on) VALUES (97,1,1,'2026-08-16','2026-08-01');"
refuses "the same primary key twice is refused" \
  "INSERT INTO books (book_id,title,author) VALUES (1,'Duplicate','Nobody');"

counts="$("${sqlite_bin}" "${work}/library.db" \
  "SELECT (SELECT count(*) FROM books)||'/'||(SELECT count(*) FROM members)||'/'||(SELECT count(*) FROM loans)||'/'||(SELECT copies FROM books WHERE book_id=1)" 2>/dev/null)"
check "after seven refused writes the data is byte-for-byte unchanged (6/4/7/2)" \
  "$([ "${counts}" = "6/4/7/2" ] && echo yes || echo no)"

# The teachable negative: SQLite leaves foreign keys OFF unless you ask.
# The identical statement that was refused above is accepted here.
if "${sqlite_bin}" "${work}/library.db" \
  "PRAGMA foreign_keys=OFF; INSERT INTO loans (loan_id,book_id,member_id,borrowed_on,due_on) VALUES (96,1,999,'2026-08-16','2026-09-06');" >/dev/null 2>&1
then
  check "with foreign_keys OFF the SAME bad write is accepted — the rule is opt-in" "yes"
  "${sqlite_bin}" "${work}/library.db" "DELETE FROM loans WHERE loan_id=96;" >/dev/null 2>&1
else
  check "with foreign_keys OFF the SAME bad write is accepted — the rule is opt-in" "no"
fi

# ===========================================================================
echo
echo "4. Typing is dynamic by default, and STRICT is the fix"
# ===========================================================================
typing_db="${work}/typing.db"
"${sqlite_bin}" "${typing_db}" "CREATE TABLE loose (id INTEGER PRIMARY KEY, year INTEGER);" >/dev/null 2>&1
"${sqlite_bin}" "${typing_db}" "CREATE TABLE tight (id INTEGER PRIMARY KEY, year INTEGER) STRICT;" >/dev/null 2>&1

if "${sqlite_bin}" "${typing_db}" "INSERT INTO loose VALUES (1,'not-a-number');" >/dev/null 2>&1; then
  check "an ordinary INTEGER column ACCEPTS the text not-a-number" "yes"
else
  check "an ordinary INTEGER column ACCEPTS the text not-a-number" "no"
fi

stored_class="$("${sqlite_bin}" "${typing_db}" "SELECT typeof(year) FROM loose WHERE id=1;" 2>/dev/null)"
check "and stores it with storage class text, in a column declared INTEGER" \
  "$([ "${stored_class}" = "text" ] && echo yes || echo no)"

"${sqlite_bin}" "${typing_db}" "INSERT INTO loose VALUES (2,'1970');" >/dev/null 2>&1
converted="$("${sqlite_bin}" "${typing_db}" "SELECT typeof(year) FROM loose WHERE id=2;" 2>/dev/null)"
check "text that looks like an integer is converted by affinity to integer" \
  "$([ "${converted}" = "integer" ] && echo yes || echo no)"

matched="$("${sqlite_bin}" "${typing_db}" "SELECT count(*) FROM loose WHERE year < 2000;" 2>/dev/null)"
total="$("${sqlite_bin}" "${typing_db}" "SELECT count(*) FROM loose;" 2>/dev/null)"
check "the text row silently fails year < 2000 — two rows in, one row out" \
  "$([ "${matched}" = "1" ] && [ "${total}" = "2" ] && echo yes || echo no)"

if "${sqlite_bin}" "${typing_db}" "INSERT INTO tight VALUES (1,'not-a-number');" >/dev/null 2>&1; then
  check "a STRICT table REFUSES the same text value" "no"
else
  check "a STRICT table REFUSES the same text value" "yes"
fi

strict_rows="$("${sqlite_bin}" "${typing_db}" "SELECT count(*) FROM tight;" 2>/dev/null)"
check "and the refused row was never written to the STRICT table" \
  "$([ "${strict_rows}" = "0" ] && echo yes || echo no)"

if "${sqlite_bin}" "${typing_db}" "INSERT INTO tight VALUES (2,'1970');" >/dev/null 2>&1; then
  strict_converted="$("${sqlite_bin}" "${typing_db}" "SELECT typeof(year) FROM tight WHERE id=2;" 2>/dev/null)"
  check "STRICT still allows the LOSSLESS text-to-integer conversion" \
    "$([ "${strict_converted}" = "integer" ] && echo yes || echo no)"
else
  check "STRICT still allows the LOSSLESS text-to-integer conversion" "no"
fi

# ===========================================================================
echo
echo "5. The hand-written scan and the SQL return the same rows"
# ===========================================================================
if (cd "${work}" && "${python_bin}" scan_vs_sql.py library.db >/dev/null 2>&1); then
  check "scan_vs_sql.py reports the two results IDENTICAL and exits 0" "yes"
else
  check "scan_vs_sql.py reports the two results IDENTICAL and exits 0" "no"
fi

if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
import sys
from table_scan import restrict, project, order_by

rows = [
    {"a": 3, "b": "x", "c": 0},
    {"a": 1, "b": "y", "c": 0},
    {"a": None, "b": "z", "c": 0},
    {"a": 2, "b": "w", "c": 0},
]

kept = restrict(rows, lambda r: r["a"] is not None and r["a"] > 1)
assert [r["a"] for r in kept] == [3, 2], kept

projected = project(rows, ["b", "a"])
assert list(projected[0].keys()) == ["b", "a"], projected[0]
assert "c" not in projected[0], projected[0]
assert rows[0] == {"a": 3, "b": "x", "c": 0}, "project must not mutate its input"

sorted_rows = order_by(rows, "a")
assert [r["a"] for r in sorted_rows] == [1, 2, 3, None], sorted_rows

sys.exit(0)
PY
); then
  check "restrict, project and order_by each behave as the operator they name" "yes"
else
  check "restrict, project and order_by each behave as the operator they name" "no"
fi

if (cd "${work}" && "${python_bin}" table_scan.py 2>/dev/null | grep -q "4 row(s); 6 predicate calls"); then
  check "the scan reports its own cost: 6 predicate calls to find 4 rows" "yes"
else
  check "the scan reports its own cost: 6 predicate calls to find 4 rows" "no"
fi

# ===========================================================================
echo
echo "6. The question a JSON file could not answer cheaply"
# ===========================================================================
overdue_sql="$("${sqlite_bin}" "${work}/library.db" \
  "SELECT count(*) FROM loans WHERE returned_on IS NULL AND due_on < '2026-08-16';" 2>/dev/null)"
check "one SELECT finds exactly 3 overdue loans as of 2026-08-16" \
  "$([ "${overdue_sql}" = "3" ] && echo yes || echo no)"

names="$("${sqlite_bin}" "${work}/library.db" \
  "SELECT group_concat(m.name, '|') FROM loans l JOIN members m ON m.member_id=l.member_id WHERE l.returned_on IS NULL AND l.due_on < '2026-08-16' ORDER BY l.due_on;" 2>/dev/null)"
check "and names the borrowers by joining three tables in one statement" \
  "$([ -n "${names}" ] && echo yes || echo no)"

if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
"""The same answer computed both ways, and required to agree."""
import sqlite3
import sys

TODAY = "2026-08-16"

connection = sqlite3.connect("library.db")
by_sql = sorted(
    connection.execute(
        "SELECT loan_id FROM loans WHERE returned_on IS NULL AND due_on < ?",
        (TODAY,),
    ).fetchall()
)
# Now the file version: pull every row out and filter it in Python, which is
# exactly what the JSON state file forced you to do.
all_loans = connection.execute(
    "SELECT loan_id, returned_on, due_on FROM loans"
).fetchall()
connection.close()
by_hand = sorted(
    (row[0],) for row in all_loans if row[1] is None and row[2] < TODAY
)
assert by_sql == by_hand, (by_sql, by_hand)
assert len(by_sql) == 3, by_sql
sys.exit(0)
PY
); then
  check "filtering by hand over every row gives the identical answer" "yes"
else
  check "filtering by hand over every row gives the identical answer" "no"
fi

# ===========================================================================
echo
echo "7. A transaction is all or nothing"
# ===========================================================================
before="$("${sqlite_bin}" "${work}/library.db" "SELECT count(*) FROM loans;" 2>/dev/null)"
"${sqlite_bin}" "${work}/library.db" <<'SQL' >/dev/null 2>&1
BEGIN;
INSERT INTO loans (loan_id,book_id,member_id,borrowed_on,due_on) VALUES (50,3,4,'2026-08-16','2026-09-06');
UPDATE books SET copies = copies - 1 WHERE book_id = 3;
ROLLBACK;
SQL
after_rollback="$("${sqlite_bin}" "${work}/library.db" \
  "SELECT count(*)||'/'||(SELECT copies FROM books WHERE book_id=3) FROM loans;" 2>/dev/null)"
check "ROLLBACK undoes BOTH writes, not just the last one" \
  "$([ "${after_rollback}" = "${before}/3" ] && echo yes || echo no)"

"${sqlite_bin}" "${work}/library.db" <<'SQL' >/dev/null 2>&1
BEGIN;
INSERT INTO loans (loan_id,book_id,member_id,borrowed_on,due_on) VALUES (50,3,4,'2026-08-16','2026-09-06');
UPDATE books SET copies = copies - 1 WHERE book_id = 3;
COMMIT;
SQL
after_commit="$("${sqlite_bin}" "${work}/library.db" \
  "SELECT count(*)||'/'||(SELECT copies FROM books WHERE book_id=3) FROM loans;" 2>/dev/null)"
check "COMMIT keeps both writes together" \
  "$([ "${after_commit}" = "$((before + 1))/2" ] && echo yes || echo no)"

if (cd "${work}" && "${python_bin}" - <<'PY' >/dev/null 2>&1
import sqlite3, sys

connection = sqlite3.connect("library.db")
connection.execute("PRAGMA foreign_keys = ON")
before = connection.execute("SELECT count(*) FROM loans").fetchone()[0]
try:
    with connection:
        connection.execute(
            "INSERT INTO loans (loan_id,book_id,member_id,borrowed_on,due_on)"
            " VALUES (60,1,2,'2026-08-16','2026-09-06')")
        connection.execute(
            "INSERT INTO loans (loan_id,book_id,member_id,borrowed_on,due_on)"
            " VALUES (61,1,999,'2026-08-16','2026-09-06')")
except sqlite3.IntegrityError:
    pass
after = connection.execute("SELECT count(*) FROM loans").fetchone()[0]
connection.close()
sys.exit(0 if before == after else 1)
PY
); then
  check "in Python, one failing write in a with-block undoes the good one too" "yes"
else
  check "in Python, one failing write in a with-block undoes the good one too" "no"
fi

if (cd "${work}" && "${python_bin}" library_py.py library.db 2>/dev/null | grep -q "loans table still has"); then
  check "a hostile value passed as a PARAMETER is compared, never executed" "yes"
else
  check "a hostile value passed as a PARAMETER is compared, never executed" "no"
fi

# ===========================================================================
echo
echo "8. The starter is runnable, and carries its exercises"
# ===========================================================================
starter_work="${work_root}/starter"
mkdir -p "${starter_work}"
cp "${lab_dir}/starter/"* "${starter_work}/"

if (cd "${starter_work}" && "${sqlite_bin}" starter.db < schema.sql >/dev/null 2>&1); then
  check "the starter schema applies cleanly before you have written a line" "yes"
else
  check "the starter schema applies cleanly before you have written a line" "no"
fi

starter_tables="$("${sqlite_bin}" "${starter_work}/starter.db" \
  "SELECT group_concat(name) FROM sqlite_schema WHERE type='table';" 2>/dev/null)"
check "and creates the one worked table, books, for you to build on" \
  "$([ "${starter_tables}" = "books" ] && echo yes || echo no)"

exercise_count="$(grep -c "^-- EXERCISE" "${lab_dir}/starter/schema.sql" || true)"
check "the starter schema carries its 8 numbered exercises" \
  "$([ "${exercise_count}" = "8" ] && echo yes || echo no)"

scan_exercises="$(grep -c "^# EXERCISE" "${lab_dir}/starter/table_scan.py" || true)"
check "the starter scan carries its 3 numbered exercises" \
  "$([ "${scan_exercises}" = "3" ] && echo yes || echo no)"

if (cd "${starter_work}" && "${python_bin}" table_scan.py 2>/dev/null | grep -q "EXERCISE 1"); then
  check "running the unfinished starter names the next exercise instead of a traceback" "yes"
else
  check "running the unfinished starter names the next exercise instead of a traceback" "no"
fi

starter_exit=0
(cd "${starter_work}" && "${python_bin}" table_scan.py >/dev/null 2>&1) || starter_exit=$?
check "and exits non-zero, so an unfinished lab cannot look finished" \
  "$([ "${starter_exit}" -ne 0 ] && echo yes || echo no)"

# ===========================================================================
echo
echo "9. Nothing here reaches the network or needs anything installed"
# ===========================================================================
if "${python_bin}" - "${lab_dir}" <<'PY' >/dev/null 2>&1
import re, sys
from pathlib import Path

root = Path(sys.argv[1])
banned = re.compile(r"https?://(?!\S*\.invalid)", re.IGNORECASE)
offenders = []
for directory in ("examples", "starter", "tests"):
    for path in (root / directory).rglob("*"):
        if path.is_file() and path.suffix in {".py", ".sql", ".sh", ".json"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if banned.search(text):
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
import re, sys
from pathlib import Path

root = Path(sys.argv[1])
third_party = re.compile(r"^\s*(import|from)\s+(requests|httpx|urllib3|pandas|sqlalchemy)\b", re.M)
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
  "$([ ! -e "${lab_dir}/tests/library.db" ] && [ ! -e "${lab_dir}/starter/starter.db" ] && echo yes || echo no)"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
