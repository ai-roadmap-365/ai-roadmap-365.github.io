#!/usr/bin/env bash
# Tests for the Day 092 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Every check below compares a REAL VALUE produced by one of the four shapes
# this lab models. The questions the suite asks are the ones the lesson claims
# answers to:
#
#   * does the relational baseline really refuse the misspelled column, at the
#     moment of the write, naming the field?
#   * does a key-value store really have to examine every key to answer a
#     question about anything except the key?
#   * does a hand-maintained secondary index really go stale with no error?
#   * do SQLite's JSON functions really let a relational engine query inside a
#     document, and does an index on an extracted field really change the plan
#     from SCAN to SEARCH?
#   * and the one that matters most: is the misspelled document ACCEPTED by
#     three of the four shapes, and INVISIBLE to the query in all of them?
#     Both halves are asserted. The silence is the lesson.
#
# Nothing here touches the network. Nothing needs sudo. Everything is built in
# a temporary directory removed by a trap, so a completed run leaves your lab
# directory exactly as it found it — no database and no __pycache__ behind.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work=""
checks=0
failures=0

cleanup() { [ -n "${work}" ] && [ -d "${work}" ] && rm -rf "${work}"; }
trap cleanup EXIT INT TERM

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

# check_eq LABEL EXPECTED ACTUAL — prints what it wanted when it does not match.
check_eq() {
  local label="$1" expected="$2" actual="$3"
  checks=$((checks + 1))
  if [ "${expected}" = "${actual}" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    echo "        expected: ${expected}"
    echo "        actual:   ${actual}"
    failures=$((failures + 1))
  fi
}

python_bin="${PYTHON:-$(command -v python3 || true)}"
sqlite_bin="${SQLITE3:-$(command -v sqlite3 || true)}"
if [ -z "${python_bin}" ] || [ ! -x "${python_bin}" ]; then
  echo "python3 was not found. Install Python 3.11+ or set PYTHON=/path/to/python3."
  exit 1
fi
if [ -z "${sqlite_bin}" ] || [ ! -x "${sqlite_bin}" ]; then
  echo "sqlite3 was not found. Install it or set SQLITE3=/path/to/sqlite3."
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
work="$(mktemp -d)"

echo "Day 092 — Beyond Tables: NoSQL and Key-Value Stores"
echo "python3: $("${python_bin}" -c 'import sys; print(sys.version.split()[0])')"
echo "sqlite3: $("${sqlite_bin}" --version | cut -d' ' -f1)"
echo "sqlite (python): $("${python_bin}" -c 'import sqlite3; print(sqlite3.sqlite_version)')"
echo "work:    a temporary directory, removed when this script exits"
echo

# ---------------------------------------------------------------------------
echo "0. The build has the JSON support this whole lab depends on"
# ---------------------------------------------------------------------------
# Check rather than assume. SQLite's JSON functions were an optional extension
# until 3.38.0 (2022) made them part of the core build, and the -> and ->>
# operators arrived in that same release.
check "the sqlite3 shell has json_extract() and json_valid()" \
  "$("${sqlite_bin}" :memory: "SELECT json_extract('{\"a\":1}','\$.a') + json_valid('{}')" 2>/dev/null | grep -q '^2$' && echo yes || echo no)"
check "the sqlite3 shell has the -> and ->> operators (3.38.0 or newer)" \
  "$("${sqlite_bin}" :memory: "SELECT ('{\"a\":2}' ->> '\$.a')" 2>/dev/null | grep -q '^2$' && echo yes || echo no)"
check "the sqlite3 shell has json_each()" \
  "$("${sqlite_bin}" :memory: "SELECT count(*) FROM json_each('[1,2,3]')" 2>/dev/null | grep -q '^3$' && echo yes || echo no)"
check "Python's own SQLite library has json_extract() too" \
  "$("${python_bin}" -c "import sqlite3; print(sqlite3.connect(':memory:').execute(\"select json_extract('{\\\"a\\\":1}','\$.a')\").fetchone()[0])" 2>/dev/null | grep -q '^1$' && echo yes || echo no)"
check "Python's dbm module can open a store on this machine" \
  "$("${python_bin}" -c 'import dbm; print(dbm)' >/dev/null 2>&1 && echo yes || echo no)"

echo
# ---------------------------------------------------------------------------
echo "1. Shape one: the relational baseline still enforces its schema"
# ---------------------------------------------------------------------------
rel_db="${work}/library.db"
"${sqlite_bin}" "${rel_db}" < "${lab_dir}/examples/01_relational.sql" \
  > "${work}/relational.txt" 2>&1
rel_status=$?

r() { "${sqlite_bin}" "${rel_db}" ".mode list" ".headers off" "$1"; }

check_eq "five tables exist: authors, books, book_authors, members, loans" "5" \
  "$(r "SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")"
check_eq "row counts: 6 authors, 4 books, 7 credits, 3 members, 4 loans" \
  "6|4|7|3|4" \
  "$(r "SELECT (SELECT count(*) FROM authors) || '|' || (SELECT count(*) FROM books) || '|' || (SELECT count(*) FROM book_authors) || '|' || (SELECT count(*) FROM members) || '|' || (SELECT count(*) FROM loans)")"
check_eq "a column holds one value, so the authors list needs a junction table" "2" \
  "$(r "SELECT count(*) FROM book_authors WHERE book_id = 101")"
check_eq "filtering on a non-key column is one statement" "101|102" \
  "$(r "SELECT group_concat(book_id, '|') FROM (SELECT book_id FROM books WHERE published_year < 1990 ORDER BY book_id)")"

# THE CHECK THIS WHOLE LAB TURNS ON. The misspelled column is refused, now,
# by name. Three shapes from now the same mistake will be accepted in silence.
check "the misspelled column is REFUSED, and the error names the field" \
  "$(grep -q 'no column named titel' "${work}/relational.txt" && echo yes || echo no)"
check_eq "the script therefore exits non-zero, on purpose" "refused" \
  "$([ "${rel_status}" -ne 0 ] && echo refused || echo "exit ${rel_status}")"
check_eq "and the bad row is not in the table: still 4 books" "4" \
  "$(r "SELECT count(*) FROM books")"

echo
# ---------------------------------------------------------------------------
echo "2. Shape two: a key-value store, and the cost of asking it anything else"
# ---------------------------------------------------------------------------
kv_dir="${work}/kv"
mkdir -p "${kv_dir}"
"${python_bin}" "${lab_dir}/examples/02_key_value_dbm.py" "${kv_dir}" \
  > "${work}/kv.txt" 2>&1
kv_status=$?
check_eq "02_key_value_dbm.py exits 0" "0" "${kv_status}"
check "a real dbm backend was chosen and named" \
  "$(grep -q '^backend chosen by Python: dbm\.' "${work}/kv.txt" && echo yes || echo no)"
check "the four books are stored under four keys" \
  "$(grep -q "keys: \['book:101', 'book:102', 'book:103', 'book:104'\]" "${work}/kv.txt" && echo yes || echo no)"
check "get by key examines exactly 1 key" \
  "$(grep -q '^keys examined: 1$' "${work}/kv.txt" && echo yes || echo no)"
check "the same question SQL answers with WHERE examines all 4 keys" \
  "$(grep -q '^keys examined: 4 of 4 (every key in the store)$' "${work}/kv.txt" && echo yes || echo no)"
check "every value is decoded on the way past, matching or not" \
  "$(grep -q '^json.loads calls: 4' "${work}/kv.txt" && echo yes || echo no)"
check "the hand-built secondary index cuts that to 3 key reads" \
  "$(grep -q '^keys examined: 3 (one index key, then one key per hit)$' "${work}/kv.txt" && echo yes || echo no)"
check "and deleting a book leaves the index pointing at a key that is gone" \
  "$(grep -q '^ids in that index with no book left in the store: \[102\]$' "${work}/kv.txt" && echo yes || echo no)"
check "with no error raised at any point" \
  "$(grep -q '^no error was raised at any point$' "${work}/kv.txt" && echo yes || echo no)"

# Independently: prove the store really is opaque — it never looked inside.
check_eq "the store holds bytes, not fields: the value is one blob" "bytes" \
  "$("${python_bin}" - "${kv_dir}" <<'PY'
import dbm, sys
from pathlib import Path
with dbm.open(str(Path(sys.argv[1]) / "library_kv"), "r") as store:
    print(type(store[b"book:101"]).__name__)
PY
)"

echo
# ---------------------------------------------------------------------------
echo "3. Shape three: JSON documents inside the relational engine"
# ---------------------------------------------------------------------------
json_db="${work}/docs.db"
"${sqlite_bin}" "${json_db}" < "${lab_dir}/examples/03_json_in_sqlite.sql" \
  > "${work}/json.txt" 2>&1
json_status=$?
j() { "${sqlite_bin}" "${json_db}" ".mode list" ".headers off" "$1"; }

check_eq "03_json_in_sqlite.sql exits 0" "0" "${json_status}"
check_eq "one table, one column of JSON, five documents" "documents|5" \
  "$(j "SELECT (SELECT name FROM sqlite_master WHERE type='table') || '|' || (SELECT count(*) FROM documents)")"
check_eq "json_extract reaches inside: doc 102 is The Mythical Man-Month" \
  "The Mythical Man-Month" "$(j "SELECT json_extract(body,'\$.title') FROM documents WHERE doc_id=102")"
check_eq "-> returns JSON text, ->> returns a typed SQL value" "text|integer" \
  "$(j "SELECT typeof(body -> '\$.published_year') || '|' || typeof(body ->> '\$.published_year') FROM documents WHERE doc_id=101")"
check_eq "json_each unrolls the array the relational model needed a table for" \
  "Brian W. Kernighan|2" \
  "$(j "SELECT a.value || '|' || count(*) FROM documents, json_each(documents.body,'\$.authors') AS a GROUP BY a.value ORDER BY count(*) DESC, a.value LIMIT 1")"
check "without an index the planner SCANs" \
  "$(grep -q '^\`--SCAN documents$' "${work}/json.txt" && echo yes || echo no)"
check "with an index on the extracted field it SEARCHes" \
  "$(grep -q 'SEARCH documents USING COVERING INDEX idx_documents_shelf' "${work}/json.txt" && echo yes || echo no)"
check_eq "the index survives in the database, not just in the transcript" "1" \
  "$(j "SELECT count(*) FROM sqlite_master WHERE type='index' AND name='idx_documents_shelf'")"
# The catch worth knowing: an expression index matches the EXPRESSION, not the
# question. Spell the same filter with ->> and the index does not apply.
check_eq "an index on json_extract(...) does not help a query written with ->>" \
  "SCAN documents" \
  "$(j "EXPLAIN QUERY PLAN SELECT doc_id FROM documents WHERE body ->> '\$.shelf' = 'A3'" | tail -1 | sed 's/^[^A-Z]*//')"

echo
# ---------------------------------------------------------------------------
echo "4. Shape four: the from-scratch document store"
# ---------------------------------------------------------------------------
doc_dir="${work}/docstore"
mkdir -p "${doc_dir}"
"${python_bin}" "${lab_dir}/examples/04_docstore.py" "${doc_dir}" \
  > "${work}/docstore.txt" 2>&1
doc_status=$?
check_eq "04_docstore.py exits 0" "0" "${doc_status}"
check "get() returns the whole document, nested list and all" \
  "$(grep -q "its authors field is a real list: \['Stuart J. Russell', 'Peter Norvig'\]" "${work}/docstore.txt" && echo yes || echo no)"
check "get() on a missing key returns None rather than raising" \
  "$(grep -q "^get('book:999') -> None$" "${work}/docstore.txt" && echo yes || echo no)"
check "delete() reports True the first time and False the second" \
  "$(grep -q "^delete('book:104') -> True$" "${work}/docstore.txt" \
     && grep -q "^delete('book:104') again -> False$" "${work}/docstore.txt" && echo yes || echo no)"
check "the store scales to 20,004 documents for the timing comparison" \
  "$(grep -q '^documents now in the store: 20004$' "${work}/docstore.txt" && echo yes || echo no)"
check "before the index the plan is a SCAN" \
  "$(grep -q '^plan without the index: SCAN documents$' "${work}/docstore.txt" && echo yes || echo no)"
check "after create_index() the plan is a SEARCH on the indexed expression" \
  "$(grep -q '^plan with the index: *SEARCH documents USING INDEX idx_docs_shelf' "${work}/docstore.txt" && echo yes || echo no)"
check "and the answer is identical before and after: an index changes speed, not results" \
  "$(grep -q 'returned 50 documents both times: True' "${work}/docstore.txt" && echo yes || echo no)"

# Timings differ per machine, so assert the SHAPE of the result: a large
# speedup, not a particular millisecond figure. On the authoring machine the
# ratio was around 95x; the floor below is deliberately far under that.
ratio="$(grep -o '^ratio: [0-9]*x' "${work}/docstore.txt" | tr -dc '0-9')"
check_eq "the indexed lookup is at least 5x faster (measured: ${ratio:-none}x)" "fast" \
  "$([ -n "${ratio}" ] && [ "${ratio}" -ge 5 ] 2>/dev/null && echo fast || echo "ratio=${ratio:-none}")"

check "(a) the misspelled document is accepted and stored" \
  "$(grep -q "get('book:105') -> \['authors', 'book_id', 'published_year', 'shelf', 'titel'\]" "${work}/docstore.txt" && echo yes || echo no)"
check "(b) a loan pointing at a book that does not exist is accepted" \
  "$(grep -q 'put a loan for book_id 999, which does not exist -> accepted' "${work}/docstore.txt" && echo yes || echo no)"
check "(c) the loan-to-book lookup returns None, and nothing warned about it" \
  "$(grep -q 'loan -> book lookup returned None' "${work}/docstore.txt" && echo yes || echo no)"
check "(d) an explicit transaction rolls the partial write back" \
  "$(grep -q "get('book:106') after the rollback -> None" "${work}/docstore.txt" && echo yes || echo no)"

# The field name is interpolated into SQL, so the allow-list is load-bearing.
check_eq "a field name that is not a plain identifier is refused before it reaches SQL" \
  "ValueError" \
  "$("${python_bin}" - "${lab_dir}" <<'PY'
import sys
from importlib import import_module
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "examples"))
store = import_module("04_docstore").DocumentStore(":memory:")
try:
    store.find("shelf'); DROP TABLE documents; --", "A3")
    print("ACCEPTED")
except ValueError:
    print("ValueError")
PY
)"

echo
# ---------------------------------------------------------------------------
echo "5. The punchline: one misspelled document, four shapes"
# ---------------------------------------------------------------------------
sor_dir="${work}/sor"
mkdir -p "${sor_dir}"
"${python_bin}" "${lab_dir}/examples/05_schema_on_read.py" "${sor_dir}" \
  > "${work}/sor.txt" 2>&1
sor_status=$?
check_eq "05_schema_on_read.py exits 0" "0" "${sor_status}"

summary() { grep -E "^${1} +" "${work}/sor.txt" | tail -1 | tr -s ' '; }
check_eq "relational: REFUSED, 4 books stored, query finds it: no" \
  "relational (books table) REFUSED 4 no" "$(summary 'relational \(books table\)')"
check_eq "key-value (dbm): ACCEPTED, 5 stored, query finds it: no" \
  "key-value (dbm) ACCEPTED 5 no" "$(summary 'key-value \(dbm\)')"
check_eq "JSON in SQLite: ACCEPTED, 5 stored, query finds it: no" \
  "JSON documents in SQLite ACCEPTED 5 no" "$(summary 'JSON documents in SQLite')"
check_eq "the from-scratch store: ACCEPTED, 5 stored, query finds it: no" \
  "the from-scratch document store ACCEPTED 5 no" "$(summary 'the from-scratch document store')"
check "only the relational store raised anything, and it named the field" \
  "$(grep -q 'OperationalError: table books has no column named titel' "${work}/sor.txt" && echo yes || echo no)"

# Both halves asserted directly, not read off a transcript: the document IS
# there, and the query CANNOT see it. Neither half alone is the lesson.
check_eq "asserted directly: stored=5, found_by_title=0, found_by_shelf=1" \
  "5|0|1" \
  "$("${python_bin}" - "${sor_dir}" <<'PY'
import json, sqlite3, sys
from pathlib import Path
connection = sqlite3.connect(str(Path(sys.argv[1]) / "json.db"))
wanted = "Compilers: Principles, Techniques, and Tools"
stored = connection.execute("SELECT count(*) FROM documents").fetchone()[0]
by_title = connection.execute(
    "SELECT count(*) FROM documents WHERE json_extract(body, '$.title') = ?", (wanted,)
).fetchone()[0]
by_shelf = connection.execute(
    "SELECT count(*) FROM documents WHERE json_extract(body, '$.shelf') = 'C1'"
).fetchone()[0]
print(f"{stored}|{by_title}|{by_shelf}")
PY
)"
check_eq "and the audit that would have caught it finds exactly one document" \
  "105" \
  "$("${python_bin}" - "${sor_dir}" <<'PY'
import sqlite3, sys
from pathlib import Path
connection = sqlite3.connect(str(Path(sys.argv[1]) / "json.db"))
rows = connection.execute(
    "SELECT doc_id FROM documents WHERE json_extract(body, '$.title') IS NULL ORDER BY doc_id"
).fetchall()
print(",".join(str(row[0]) for row in rows))
PY
)"

echo
# ---------------------------------------------------------------------------
echo "6. The starter reports honest progress"
# ---------------------------------------------------------------------------
before="$("${python_bin}" "${lab_dir}/starter/01_exercises.py" 2>&1)"
before_status=$?
check "the untouched starter reports 0 of 5 exercises complete" \
  "$(printf '%s' "${before}" | grep -q '^0 of 5 exercises complete\.$' && echo yes || echo no)"
check_eq "and exits non-zero, so it cannot be mistaken for finished" "incomplete" \
  "$([ "${before_status}" -ne 0 ] && echo incomplete || echo "exit ${before_status}")"
check "it runs rather than crashing: every exercise is a wrong answer, not a stub" \
  "$(printf '%s' "${before}" | grep -q 'the plan for find(.shelf., ...) is still: SCAN documents' && echo yes || echo no)"

# Solve the five marked lines, then confirm 5 of 5.
solver="${work}/solve.py"
cat > "${solver}" <<'PY'
import sys

SOLUTIONS = {
    "exercise-1": "        return None if row is None else json.loads(row[0])",
    "exercise-2": "        sql = f\"SELECT body FROM documents WHERE json_extract(body, '$.{field}') = ? ORDER BY key\"",
    "exercise-3": "        expression = f\"json_extract(body, '$.{field}')\"",
    "exercise-4": "    return [name for name in REQUIRED_FIELDS if name not in document]",
    "exercise-5": (
        "        rows = self.connection.execute(\n"
        "            \"SELECT key FROM documents WHERE json_extract(body, '$.title') IS NULL\"\n"
        "        )\n"
        "        return sorted(row[0] for row in rows)"
    ),
}

source, destination, break_marker = sys.argv[1], sys.argv[2], sys.argv[3]
out, replaced = [], 0
for line in open(source, encoding="utf-8").read().splitlines():
    for marker, answer in SOLUTIONS.items():
        if line.rstrip().endswith("# " + marker):
            if marker != break_marker:
                line = answer
                replaced += 1
            break
    out.append(line)
open(destination, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(replaced)
PY
replaced="$("${python_bin}" "${solver}" "${lab_dir}/starter/01_exercises.py" "${work}/solved.py" none)"
check_eq "all five exercise lines were found and replaced" "5" "${replaced}"
after="$("${python_bin}" "${work}/solved.py" 2>&1)"
after_status=$?
check "the solved starter reports 5 of 5 exercises complete" \
  "$(printf '%s' "${after}" | grep -q '^5 of 5 exercises complete\.$' && echo yes || echo no)"
check_eq "and exits 0" "0" "${after_status}"

# A checker that cannot fail proves nothing. Leave exercise 2 unsolved and the
# result must be 4 of 5, not 5 of 5.
"${python_bin}" "${solver}" "${lab_dir}/starter/01_exercises.py" "${work}/broken.py" exercise-2 >/dev/null
broken="$("${python_bin}" "${work}/broken.py" 2>&1)"
broken_status=$?
check "leaving one exercise unsolved is caught: 4 of 5, not 5 of 5" \
  "$(printf '%s' "${broken}" | grep -q '^4 of 5 exercises complete\.$' && echo yes || echo no)"
check_eq "and the checker still exits non-zero" "incomplete" \
  "$([ "${broken_status}" -ne 0 ] && echo incomplete || echo "exit ${broken_status}")"

echo
# ---------------------------------------------------------------------------
echo "7. Hygiene: offline, no sudo, no leaked paths, nothing left behind"
# ---------------------------------------------------------------------------
"${python_bin}" - "${lab_dir}" > "${work}/hygiene.txt" <<'PY'
import re, sys
from pathlib import Path

root = Path(sys.argv[1])
urls, sudo_lines = set(), []
comment = re.compile(r"^\s*(#|--)")
for path in sorted(root.rglob("*")):
    if not path.is_file() or path.suffix not in {".sql", ".py", ".sh"}:
        continue
    for number, line in enumerate(
        path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
    ):
        urls.update(re.findall(r"https?://[^\s\"')]+", line))
        if re.search(r"(^|[;|&(]\s*)sudo\s", line) and not comment.match(line):
            sudo_lines.append(f"{path.name}:{number}")
print("URLS " + " ".join(sorted(urls)))
print("SUDO " + " ".join(sudo_lines))
PY
check_eq "no URL appears anywhere in the lab's scripts" "URLS" \
  "$(grep '^URLS ' "${work}/hygiene.txt" | sed 's/ *$//')"
check_eq "no line in this lab would actually invoke sudo" "SUDO" \
  "$(grep '^SUDO ' "${work}/hygiene.txt" | sed 's/ *$//')"
check "nothing in this lab imports a networking module" \
  "$(grep -rlE '^\s*(import|from)\s+(socket|urllib|http|requests)' "${lab_dir}/examples" "${lab_dir}/starter" >/dev/null 2>&1 && echo no || echo yes)"
check "no captured output leaks an absolute home path" \
  "$(grep -rl '/Users/\|/home/' "${lab_dir}/expected-output" >/dev/null 2>&1 && echo no || echo yes)"
check "this suite created no database inside the lab directory" \
  "$([ -z "$(find "${lab_dir}" -maxdepth 2 -name '*.db' -print -quit)" ] && echo yes || echo no)"
check "and left no __pycache__ behind" \
  "$([ -z "$(find "${lab_dir}" -type d -name '__pycache__' -print -quit)" ] && echo yes || echo no)"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
