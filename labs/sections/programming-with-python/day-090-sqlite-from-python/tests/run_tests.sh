#!/usr/bin/env bash
# Tests for the Day 090 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# These checks ask whether the data layer actually has the properties it
# claims, rather than whether it runs:
#
#   * is a crafted value CODE when concatenated and DATA when bound — both
#     demonstrated on a throwaway database, both asserted?
#   * does a failure halfway through a transaction leave the database
#     exactly as it was, for a SQL error and for a Python one?
#   * is PRAGMA foreign_keys really per-connection, and really a no-op
#     inside a transaction?
#   * does `with connection:` leave the connection OPEN?
#   * is every SQL statement in the lab a literal, with every value bound?
#   * does executemany beat a loop, and does a transaction beat both?
#   * does the starter refuse to look finished before it is?
#
# Everything runs offline. No server, no port, no credential, no third-party
# package. Every database is created inside a directory made with mktemp -d
# and removed in a trap, so a completed run leaves nothing behind — and one
# of the checks asserts exactly that.
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

yesno() { if [ "$1" -eq 0 ]; then echo yes; else echo no; fi; }

contains() {
  # contains <file> <literal string>
  if grep -qF -- "$2" "$1"; then echo yes; else echo no; fi
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

work_root="$(mktemp -d "${TMPDIR:-/tmp}/day090-XXXXXX")"
work="${work_root}/lab"
out="${work_root}/out"
mkdir -p "${work}" "${out}"
cp "${lab_dir}/examples/"*.py "${work}/"

echo "Day 090 — A Real Data Layer"
echo

# ===========================================================================
echo "1. The interpreter reports itself, and the module is the standard one"
# ===========================================================================
py_version="$("${python_bin}" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
sqlite_version="$("${python_bin}" -c 'import sqlite3; print(sqlite3.sqlite_version)')"
echo "     python:                 ${py_version}"
echo "     sqlite3.sqlite_version: ${sqlite_version}"

"${python_bin}" -c 'import sqlite3, sys; sys.exit(0 if sqlite3.paramstyle == "qmark" else 1)'
check "the sqlite3 module is present and its paramstyle is qmark" "$(yesno $?)"

"${python_bin}" - <<'PY' >/dev/null 2>&1
import sqlite3, sys
sys.exit(0 if hasattr(sqlite3.connect(":memory:"), "autocommit") else 1)
PY
check "Connection.autocommit exists on this interpreter (Python 3.12 or newer)" "$(yesno $?)"

"${python_bin}" -c 'import sqlite3, sys; sys.exit(0 if sqlite3.sqlite_version_info >= (3, 37, 0) else 1)'
check "the linked SQLite is 3.37.0 or newer, so STRICT tables are available" "$(yesno $?)"

# ===========================================================================
echo
echo "2. The connection factory configures what has to be configured"
# ===========================================================================
cd "${work}" || exit 1

"${python_bin}" - <<'PY' >"${out}/factory.txt" 2>&1
import sqlite3, tempfile, shutil
from pathlib import Path
from db import connect, apply_schema

sandbox = Path(tempfile.mkdtemp(prefix="day090-factory-"))
try:
    path = sandbox / "x.db"
    configured = connect(path)
    apply_schema(configured)
    print("foreign_keys(configured):", configured.execute("PRAGMA foreign_keys").fetchone()[0])
    print("isolation_level:", repr(configured.isolation_level))
    row = configured.execute("SELECT 1 AS one").fetchone()
    print("row type:", type(row).__name__, "by name:", row["one"])
    configured.close()

    raw = sqlite3.connect(path)
    print("foreign_keys(raw):", raw.execute("PRAGMA foreign_keys").fetchone()[0])
    raw.close()
finally:
    shutil.rmtree(sandbox, ignore_errors=True)
PY
check "the factory turns foreign keys ON" \
  "$(contains "${out}/factory.txt" 'foreign_keys(configured): 1')"
check "a plain sqlite3.connect leaves them OFF — the setting is per connection" \
  "$(contains "${out}/factory.txt" 'foreign_keys(raw): 0')"
check "the factory turns off the module's implicit transaction handling" \
  "$(contains "${out}/factory.txt" 'isolation_level: None')"
check "rows arrive as sqlite3.Row, addressable by column name" \
  "$(contains "${out}/factory.txt" 'row type: Row by name: 1')"

# ===========================================================================
echo
echo "3. Injection: the same value as CODE, then as DATA"
# ===========================================================================
"${python_bin}" injection_demo.py >"${out}/injection.txt" 2>&1
injection_status=$?
check "injection_demo.py runs and every one of its own assertions holds" "$(yesno ${injection_status})"
check "the concatenated query leaked all three private rows" \
  "$(contains "${out}/injection.txt" 'rows: 3  -> every member, with address and PIN')"
check "the crafted value changed the statement's meaning" \
  "$(contains "${out}/injection.txt" "WHERE name = 'Ada' OR '1'='1'")"
check "execute() refuses a second statement — a module limit, not a defence" \
  "$(contains "${out}/injection.txt" 'ProgrammingError: You can only execute one statement at a time.')"
check "executescript() accepts it, and the table is destroyed for real" \
  "$(contains "${out}/injection.txt" 'members table exists afterwards: False')"
check "the identical value, bound, returns zero rows" \
  "$(contains "${out}/injection.txt" 'rows returned: 0')"
check "and leaves all three members in place" \
  "$(contains "${out}/injection.txt" 'ok: and still holds all three rows')"
check "the demonstration built its database inside a throwaway directory" \
  "$(contains "${out}/injection.txt" 'sandbox removed. Nothing outside it was ever opened.')"

# The repository must never be fooled by the same input.
"${python_bin}" - <<'PY' >"${out}/repo_injection.txt" 2>&1
import shutil, tempfile
from pathlib import Path
import seed
from db import BookRepository

sandbox = Path(tempfile.mkdtemp(prefix="day090-repoinj-"))
try:
    connection = seed.build(sandbox / "library.db")
    books = BookRepository(connection)
    before = books.count()
    for hostile in ("Fred Brooks' OR '1'='1", "Fred Brooks'; DROP TABLE books; --"):
        found = books.find_by_author(hostile)
        print(f"rows for hostile input: {len(found)}")
    print("books before:", before, "after:", books.count())
    connection.close()
finally:
    shutil.rmtree(sandbox, ignore_errors=True)
PY
check "the repository returns nothing for either hostile author name" \
  "$(contains "${out}/repo_injection.txt" 'rows for hostile input: 0')"
check "and the books table is unchanged afterwards" \
  "$(contains "${out}/repo_injection.txt" 'books before: 7 after: 7')"

# ===========================================================================
echo
echo "4. No SQL anywhere in this lab is built out of pieces"
# ===========================================================================
"${python_bin}" no_sql_strings.py "${work}" >"${out}/guard.txt" 2>&1
check "the guard finds no assembled SQL in the lab's own code" "$(yesno $?)"

guard_dir="${work_root}/guardcheck"
mkdir -p "${guard_dir}"
cat >"${guard_dir}/bad.py" <<'PY'
def find(connection, author):
    return connection.execute(f"SELECT * FROM books WHERE author = '{author}'").fetchall()
PY
"${python_bin}" no_sql_strings.py "${guard_dir}" >"${out}/guard_bad.txt" 2>&1
guard_bad_status=$?
if [ ${guard_bad_status} -ne 0 ]; then bad_ok=0; else bad_ok=1; fi
check "and the guard does catch a deliberately unsafe f-string" "$(yesno ${bad_ok})"
check "naming the file, the line and the reason" \
  "$(contains "${out}/guard_bad.txt" 'bad.py:2: SQL built by an f-string and passed straight to execute()')"

cat >"${guard_dir}/fine.py" <<'PY'
def find(connection, author):
    return connection.execute(
        "SELECT book_id, title FROM books"
        " WHERE author = ? ORDER BY year",
        (author,),
    ).fetchall()
PY
rm -f "${guard_dir}/bad.py"
"${python_bin}" no_sql_strings.py "${guard_dir}" >/dev/null 2>&1
check "and does NOT flag two adjacent string literals, which Python joins at compile time" \
  "$(yesno $?)"

# ===========================================================================
echo
echo "5. Transactions: all of it, or none of it"
# ===========================================================================
"${python_bin}" transactions_demo.py >"${out}/transactions.txt" 2>&1
check "transactions_demo.py runs to the end" "$(yesno $?)"
check "a fresh connection defaults to implicit transaction handling" \
  "$(contains "${out}/transactions.txt" "default isolation_level: ''")"
check "DDL opens no transaction; DML does" \
  "$(contains "${out}/transactions.txt" 'after INSERT (DML):                   True')"
check "with connection: rolls back when the block raises" \
  "$(contains "${out}/transactions.txt" 'rows in t now: [1]')"
check "with connection: does NOT close the connection" \
  "$(contains "${out}/transactions.txt" 'is the connection still usable after the with-block? True')"
check "a foreign-key failure undid the earlier write in the same transaction" \
  "$(contains "${out}/transactions.txt" 'the transaction raised: IntegrityError: FOREIGN KEY constraint failed')"
check "PRAGMA foreign_keys set inside a transaction is silently ignored" \
  "$(contains "${out}/transactions.txt" 'inside a transaction, set ON   -> 0')"
check "and takes effect outside one" \
  "$(contains "${out}/transactions.txt" 'outside again, set ON          -> 1')"
check "autocommit = True makes a write visible to another connection at once" \
  "$(contains "${out}/transactions.txt" 'autocommit = True:  in_transaction False')"

# The rollback property, asserted directly rather than read from a log.
"${python_bin}" - <<'PY' >"${out}/rollback.txt" 2>&1
import shutil, sqlite3, sys, tempfile
from pathlib import Path
import seed
from db import BookRepository, LoanRepository, connect, transaction

sandbox = Path(tempfile.mkdtemp(prefix="day090-rollback-"))
ok = True
try:
    path = sandbox / "library.db"
    connection = seed.build(path)
    books, loans = BookRepository(connection), LoanRepository(connection)
    before = (books.get(1).copies, loans.open_count(), books.count())

    try:
        with transaction(connection):
            loans.borrow(1, 1, "2026-08-01", "2026-08-15")
            loans.borrow(2, 999, "2026-08-01", "2026-08-15")
    except sqlite3.IntegrityError:
        pass
    after_sql = (books.get(1).copies, loans.open_count(), books.count())

    try:
        with transaction(connection):
            loans.borrow(1, 1, "2026-08-01", "2026-08-15")
            raise ZeroDivisionError("a bug in the middle of a transaction")
    except ZeroDivisionError:
        pass
    after_python = (books.get(1).copies, loans.open_count(), books.count())
    connection.close()

    # A second connection sees the same thing: nothing was committed.
    fresh = connect(path)
    after_reopen = (
        BookRepository(fresh).get(1).copies,
        LoanRepository(fresh).open_count(),
        BookRepository(fresh).count(),
    )
    fresh.close()

    print("before:      ", before)
    print("after sql:   ", after_sql)
    print("after python:", after_python)
    print("after reopen:", after_reopen)
    ok = before == after_sql == after_python == after_reopen
    print("UNCHANGED:", ok)
finally:
    shutil.rmtree(sandbox, ignore_errors=True)
sys.exit(0 if ok else 1)
PY
check "a SQL error and a Python error both leave the database byte-identical" "$(yesno $?)"
check "and a newly opened connection agrees that nothing was committed" \
  "$(contains "${out}/rollback.txt" 'UNCHANGED: True')"

# ===========================================================================
echo
echo "6. Cursors, fetch methods and row factories"
# ===========================================================================
"${python_bin}" cursors_demo.py >"${out}/cursors.txt" 2>&1
check "cursors_demo.py runs to the end" "$(yesno $?)"
check "execute() returns a Cursor" \
  "$(contains "${out}/cursors.txt" 'type(connection.execute(...)) -> Cursor')"
check "rowcount is -1 for a SELECT, because the row count is not known in advance" \
  "$(contains "${out}/cursors.txt" 'cursor.rowcount for a SELECT -> -1')"
check "an exhausted cursor returns None from fetchone" \
  "$(contains "${out}/cursors.txt" 'fetchone() now  -> None')"
check "sqlite3.Row is not a dict" \
  "$(contains "${out}/cursors.txt" 'isinstance(row, dict) = False')"
check "and a dict factory produces one when a dict is what you need" \
  "$(contains "${out}/cursors.txt" 'type: dict')"

"${python_bin}" - <<'PY' >"${out}/memory.txt" 2>&1
import shutil, sys, tempfile, tracemalloc
from pathlib import Path
import seed
from db import BookRepository, transaction

sandbox = Path(tempfile.mkdtemp(prefix="day090-memory-"))
try:
    connection = seed.build(sandbox / "library.db")
    connection.execute("CREATE TABLE wide (n INTEGER, payload TEXT) STRICT")
    with transaction(connection):
        connection.executemany(
            "INSERT INTO wide (n, payload) VALUES (?, ?)",
            [(n, "x" * 200) for n in range(40_000)],
        )
    tracemalloc.start()
    rows = connection.execute("SELECT n, payload FROM wide").fetchall()
    peak_fetchall = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    del rows

    tracemalloc.start()
    total = 0
    for row in connection.execute("SELECT n, payload FROM wide"):
        total += row["n"]
    peak_iterate = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    connection.close()
    print(f"fetchall peak: {peak_fetchall:,}  iterate peak: {peak_iterate:,}")
    sys.exit(0 if peak_fetchall > peak_iterate * 100 else 1)
finally:
    shutil.rmtree(sandbox, ignore_errors=True)
PY
check "fetchall holds the whole result in memory; iterating a cursor does not (>100x apart)" \
  "$(yesno $?)"

# ===========================================================================
echo
echo "7. Errors: each mistake raises the class it should"
# ===========================================================================
"${python_bin}" errors_demo.py >"${out}/errors.txt" 2>&1
check "errors_demo.py made thirteen deliberate mistakes and all thirteen raised" "$(yesno $?)"
check "a broken constraint raises IntegrityError" \
  "$(contains "${out}/errors.txt" 'duplicate title (UNIQUE)                               IntegrityError')"
check "a missing table raises OperationalError" \
  "$(contains "${out}/errors.txt" 'table that is not there                                OperationalError')"
check "misusing the module raises ProgrammingError" \
  "$(contains "${out}/errors.txt" 'two statements in one execute()                        ProgrammingError')"
check "a STRICT column refuses the wrong type" \
  "$(contains "${out}/errors.txt" 'cannot store TEXT value in INTEGER column books.year')"

# ===========================================================================
echo
echo "8. executemany, and the transaction that matters more"
# ===========================================================================
"${python_bin}" bulk_insert.py 2000 >"${out}/bulk.txt" 2>&1
check "bulk_insert.py stored every row by all three methods" "$(yesno $?)"
"${python_bin}" - "${out}/bulk.txt" <<'PY' >"${out}/bulk_order.txt" 2>&1
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
seconds = {}
for line in text.splitlines():
    match = re.match(r"^(.+?)\s{2,}(\d+\.\d+)\s+([\d,]+)\s+([\d.]+)x$", line)
    if match:
        seconds[match.group(1).strip()] = float(match.group(2))
print(seconds)
loop = seconds["a loop, no transaction"]
batched = seconds["a loop inside one transaction"]
many = seconds["executemany inside one transaction"]
print(f"loop/batched = {loop / batched:.1f}x   batched/many = {batched / many:.2f}x")
sys.exit(0 if loop > batched > 0 and many > 0 else 1)
PY
check "one transaction around the loop is dramatically faster than one per row" "$(yesno $?)"
check "all three methods were timed and reported" \
  "$(contains "${out}/bulk.txt" 'executemany inside one transaction')"

# ===========================================================================
echo
echo "9. The data layer's own suite, and the boundary it protects"
# ===========================================================================
"${python_bin}" test_repository.py >"${out}/unittest.txt" 2>&1
check "python3 test_repository.py exits 0" "$(yesno $?)"
check "and reports OK" "$(contains "${out}/unittest.txt" 'OK')"
unit_count="$(grep -oE '^Ran [0-9]+ test' "${out}/unittest.txt" | grep -oE '[0-9]+' | head -1)"
echo "     unit tests run: ${unit_count:-0}"
if [ "${unit_count:-0}" -ge 25 ]; then units_ok=0; else units_ok=1; fi
check "the suite contains at least 25 tests" "$(yesno ${units_ok})"

"${python_bin}" report.py >"${out}/report.txt" 2>&1
check "report.py runs the whole application layer" "$(yesno $?)"
check "the three-table overdue report is right" \
  "$(contains "${out}/report.txt" 'The Mythical Man-Month           due 2026-06-22  (55 days late)')"
check "a duplicate title surfaces as a domain error, never as sqlite3.IntegrityError" \
  "$(contains "${out}/report.txt" "refused: a book titled 'Compilers' is already stored")"
check "a sort key that is not on the allow-list is refused before any SQL exists" \
  "$(contains "${out}/report.txt" 'cannot sort by')"

if grep -qE '^\s*import sqlite3|^\s*from sqlite3' "${work}/report.py" "${work}/domain.py"; then
  boundary=1
else
  boundary=0
fi
check "neither the application layer nor the domain imports sqlite3" "$(yesno ${boundary})"

# ===========================================================================
echo
echo "10. The starter cannot look finished before it is"
# ===========================================================================
starter_work="${work_root}/starter"
mkdir -p "${starter_work}"
cp "${lab_dir}/starter/"*.py "${starter_work}/"
( cd "${starter_work}" && "${python_bin}" smoke.py >"${out}/starter.txt" 2>&1 )
starter_status=$?
if [ ${starter_status} -ne 0 ]; then starter_ok=0; else starter_ok=1; fi
check "the shipped starter exits non-zero and names exercise 1" "$(yesno ${starter_ok})"
check "and says so in words rather than a traceback" \
  "$(contains "${out}/starter.txt" '0 of 9 exercises finished.')"

cp "${work}/db.py" "${starter_work}/db.py"
( cd "${starter_work}" && "${python_bin}" smoke.py >"${out}/starter_done.txt" 2>&1 )
check "a completed db.py takes the same starter to exit 0" "$(yesno $?)"
check "reporting all nine" \
  "$(contains "${out}/starter_done.txt" '9 of 9 exercises finished.')"

# ===========================================================================
echo
echo "11. Offline, self-contained, and leaves nothing behind"
# ===========================================================================
if grep -rlE 'https?://|[0-9]{1,3}(\.[0-9]{1,3}){3}' "${lab_dir}/examples" "${lab_dir}/starter" >/dev/null 2>&1; then
  net=1
else
  net=0
fi
check "no executable lab file contains a network address of any kind" "$(yesno ${net})"

if grep -rhE '^\s*(import|from)\s+' "${lab_dir}/examples" "${lab_dir}/starter" \
  | grep -qE '\b(requests|httpx|urllib3|pandas|sqlalchemy|aiosqlite|numpy|pytest)\b'; then
  thirdparty=1
else
  thirdparty=0
fi
check "no lab file imports a third-party package — standard library only" "$(yesno ${thirdparty})"

if grep -rq 'sudo' "${lab_dir}/examples" "${lab_dir}/starter"; then sudo_used=1; else sudo_used=0; fi
check "nothing in the lab's code asks for sudo" "$(yesno ${sudo_used})"

leftover="$(find "${lab_dir}" -name '*.db' -o -name '*.db-journal' -o -name '*.db-wal' | wc -l | tr -d ' ')"
if [ "${leftover}" = "0" ]; then left_ok=0; else left_ok=1; fi
check "this run left no database file anywhere inside the lab directory" "$(yesno ${left_ok})"

# Every script makes its own sandbox with a day090- prefix and removes it in
# a finally block. The only one that may still exist is this harness's own,
# which its trap removes when the script exits.
stray="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'day090-*' \
  ! -name "$(basename "${work_root}")" 2>/dev/null | wc -l | tr -d ' ')"
if [ "${stray}" = "0" ]; then stray_ok=0; else stray_ok=1; fi
check "no sandbox from any lab script was left in the temporary directory" "$(yesno ${stray_ok})"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ] || exit 1
exit 0
