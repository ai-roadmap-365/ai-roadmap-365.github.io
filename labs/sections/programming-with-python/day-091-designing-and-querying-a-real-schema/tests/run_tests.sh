#!/usr/bin/env bash
# Tests for the Day 091 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Every check below compares a REAL VALUE against the answer the brief asks
# for. The questions this suite asks are the ones the lesson claims answers to:
#
#   * does the schema actually enforce the decisions it claims to — the
#     junction table keyed on the pair, money as integers, the timestamp
#     format, the enumerations, the ordering constraints?
#   * do the ten reporting queries return the right rows, in the right order?
#   * does the design that stored a queue position really break, silently?
#   * does the report script print the numbers the lesson quotes?
#   * does the starter really report 0 of 16 before you start and 16 of 16
#     once the reference answers are in place?
#
# Nothing here touches the network. Nothing needs sudo. Everything is built in
# a temporary directory that is removed in a trap, so a completed run leaves
# your lab directory exactly as it found it — no database is left behind.
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
db="${work}/library.db"

# q SQL — one scalar or one column, no headers, no padding.
q() { "${sqlite_bin}" "${db}" ".mode list" ".headers off" "$1"; }
# rows SQL — pipe-separated rows.
rows() { "${sqlite_bin}" "${db}" ".mode list" ".separator '|'" ".headers off" "$1"; }

echo "Day 091 — Designing and Querying a Real Schema"
echo "python3: $("${python_bin}" -c 'import sys; print(sys.version.split()[0])')"
echo "sqlite3: $("${sqlite_bin}" --version | cut -d' ' -f1)"
echo "sqlite (python): $("${python_bin}" -c 'import sqlite3; print(sqlite3.sqlite_version)')"
echo "work:    a temporary directory, removed when this script exits"
echo

# Window functions need SQLite 3.25.0 and this lab uses them heavily. Fail
# loudly and early rather than producing a wall of syntax errors.
"${sqlite_bin}" :memory: "SELECT row_number() OVER ()" >/dev/null 2>&1
check "the sqlite3 shell supports window functions (3.25.0 or newer)" \
  "$([ $? -eq 0 ] && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
echo "1. The schema builds, and encodes the decisions it claims to"
# ---------------------------------------------------------------------------
"${sqlite_bin}" "${db}" < "${lab_dir}/examples/01_schema.sql" 2>"${work}/schema.err"
check "01_schema.sql runs without error" \
  "$([ ! -s "${work}/schema.err" ] && echo yes || echo no)"
"${sqlite_bin}" "${db}" < "${lab_dir}/examples/02_seed.sql" 2>"${work}/seed.err"
check "02_seed.sql runs without error" \
  "$([ ! -s "${work}/seed.err" ] && echo yes || echo no)"

check_eq "seven tables and two views exist" "7|2" \
  "$(q "SELECT (SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%') || '|' || (SELECT count(*) FROM sqlite_master WHERE type='view')")"
check_eq "row counts: 8 categories, 11 authors, 8 books, 12 credits, 6 members, 14 loans, 7 reservations" \
  "8|11|8|12|6|14|7" \
  "$(q "SELECT (SELECT count(*) FROM categories) || '|' || (SELECT count(*) FROM authors) || '|' || (SELECT count(*) FROM books) || '|' || (SELECT count(*) FROM book_authors) || '|' || (SELECT count(*) FROM members) || '|' || (SELECT count(*) FROM loans) || '|' || (SELECT count(*) FROM reservations)")"

# THE MANY-TO-MANY CHECK. If book_authors is not keyed on the pair — if the
# author ended up as a column on books, or the junction has its own surrogate
# id, or the credit order was left out — this is the check that fails.
check_eq "book_authors is keyed on the PAIR (book_id, author_id)" \
  "book_id,author_id" \
  "$(q "SELECT group_concat(name) FROM (SELECT name FROM pragma_table_info('book_authors') WHERE pk > 0 ORDER BY pk)")"
check_eq "the junction table carries the relationship's own attribute" \
  "author_position" \
  "$(q "SELECT name FROM pragma_table_info('book_authors') WHERE name='author_position'")"
check_eq "books has no author column: the relationship is not an attribute" "0" \
  "$(q "SELECT count(*) FROM pragma_table_info('books') WHERE name LIKE '%author%'")"
check_eq "book_authors references both parents" "authors,books" \
  "$(q "SELECT group_concat(t) FROM (SELECT \"table\" AS t FROM pragma_foreign_key_list('book_authors') ORDER BY t)")"

# Surrogate keys, and the natural keys kept as UNIQUE rather than as the key.
check_eq "isbn13 is UNIQUE but nullable, so the 1818 book can exist" "0" \
  "$(q "SELECT \"notnull\" FROM pragma_table_info('books') WHERE name='isbn13'")"
check_eq "exactly one book legitimately has no ISBN" "Frankenstein" \
  "$(q "SELECT title FROM books WHERE isbn13 IS NULL")"
check_eq "email is UNIQUE but is not the primary key" "member_id" \
  "$(q "SELECT name FROM pragma_table_info('members') WHERE pk = 1")"

# Money is integer minor units. A REAL column here would be the bug.
check_eq "fine_pence is declared INTEGER, not REAL" "INTEGER" \
  "$(q "SELECT type FROM pragma_table_info('loans') WHERE name='fine_pence'")"
check_eq "acquisition_cost_pence is declared INTEGER, not REAL" "INTEGER" \
  "$(q "SELECT type FROM pragma_table_info('books') WHERE name='acquisition_cost_pence'")"

# Indexes: a foreign key creates none, so these had to be written.
check_eq "nine explicit indexes, one per foreign key plus the two partial ones" "9" \
  "$(q "SELECT count(*) FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")"
check "the partial index on outstanding loans exists" \
  "$(q "SELECT count(*) FROM sqlite_master WHERE type='index' AND sql LIKE '%returned_at IS NULL%'" | grep -q '^1$' && echo yes || echo no)"

echo
# ---------------------------------------------------------------------------
echo "2. The constraints actually refuse the impossible rows"
# ---------------------------------------------------------------------------
# reject SQL — yes when the statement is refused, no when it succeeds.
reject() {
  "${sqlite_bin}" "${db}" "PRAGMA foreign_keys = ON; $1" >/dev/null 2>&1 && echo no || echo yes
}
check "a loan due before it was borrowed is refused" \
  "$(reject "INSERT INTO loans (loan_id, book_id, member_id, borrowed_at, due_at) VALUES (900, 101, 1, '2026-08-01T09:00:00Z', '2026-07-01T09:00:00Z')")"
check "a negative fine is refused" \
  "$(reject "INSERT INTO loans (loan_id, book_id, member_id, borrowed_at, due_at, fine_pence) VALUES (901, 101, 1, '2026-08-01T09:00:00Z', '2026-08-22T09:00:00Z', -1)")"
check "a timestamp that is not ISO 8601 UTC is refused" \
  "$(reject "INSERT INTO loans (loan_id, book_id, member_id, borrowed_at, due_at) VALUES (902, 101, 1, '01/08/2026', '2026-08-22T09:00:00Z')")"
check "a membership tier nobody has heard of is refused" \
  "$(reject "INSERT INTO members (member_id, email, full_name, tier, joined_at) VALUES (90, 'x@y.invalid', 'Test Person', 'platinum', '2026-01-01T00:00:00Z')")"
check "a reservation status outside the four documented values is refused" \
  "$(reject "INSERT INTO reservations (reservation_id, book_id, member_id, reserved_at, status) VALUES (90, 101, 1, '2026-08-01T09:00:00Z', 'pending')")"
check "a reservation against a book we do not own is refused" \
  "$(reject "INSERT INTO reservations (reservation_id, book_id, member_id, reserved_at) VALUES (91, 999, 1, '2026-08-01T09:00:00Z')")"
check "crediting the same author twice on one book is refused" \
  "$(reject "INSERT INTO book_authors (book_id, author_id, author_position) VALUES (101, 1, 3)")"
check "two authors credited second on the same book is refused" \
  "$(reject "INSERT INTO book_authors (book_id, author_id, author_position) VALUES (101, 7, 2)")"
check "a second WAITING reservation by the same member on the same book is refused" \
  "$(reject "INSERT INTO reservations (reservation_id, book_id, member_id, reserved_at, status) VALUES (92, 105, 1, '2026-08-12T09:00:00Z', 'waiting')")"
check "an ISBN that is not thirteen digits is refused" \
  "$(reject "INSERT INTO books (book_id, isbn13, title, category_id, acquisition_cost_pence) VALUES (900, '978-0131103627', 'Bad ISBN', 7, 100)")"
check "hard-deleting a book that has loan history is refused, so history survives" \
  "$(reject "DELETE FROM books WHERE book_id = 101")"
check_eq "and nothing above actually got in: the seed row counts are unchanged" \
  "8|12|6|14|7" \
  "$(q "SELECT (SELECT count(*) FROM books) || '|' || (SELECT count(*) FROM book_authors) || '|' || (SELECT count(*) FROM members) || '|' || (SELECT count(*) FROM loans) || '|' || (SELECT count(*) FROM reservations)")"

echo
# ---------------------------------------------------------------------------
echo "3. The ten reporting questions return the right answers"
# ---------------------------------------------------------------------------
"${sqlite_bin}" "${db}" < "${lab_dir}/examples/06_answers.sql" > "${work}/answers.txt" 2>&1
block() {
  awk -v want="### $1" '
    $0 == want { grab = 1; next }
    /^### /    { grab = 0 }
    grab       { print }
  ' "${work}/answers.txt"
}

check_eq "Q1: 7 books on the shelves, 4 of them out on loan" "7|4" "$(block 1)"
check_eq "Q1: the withdrawn book is excluded — 8 rows in books, 7 in the collection" \
  "8|7" "$(q "SELECT (SELECT count(*) FROM books) || '|' || (SELECT count(*) FROM current_collection)")"
check_eq "Q2: exactly one current member has never borrowed" "Eli Nakamura|student" "$(block 2)"
check_eq "Q3: three books have more than one author, names in credited order" \
"Structure and Interpretation of Computer Programs|3|Harold Abelson, Gerald Jay Sussman, Julie Sussman
The C Programming Language|2|Brian W. Kernighan, Dennis M. Ritchie
The Practice of Programming|2|Brian W. Kernighan, Rob Pike" "$(block 3)"
check_eq "Q4: two loans are overdue, by 10 and 5 whole days" \
"Bruno Salgado|The Left Hand of Darkness|10
Chandra Iyer|Neuromancer|5" "$(block 4)"
check_eq "Q5: fines are 4.10 and 3.00, and the member who left is still counted" \
"Ada Okafor|current|4.10
Farida Haddad|left|3.00" "$(block 5)"
check_eq "Q6: top two per tier, including the student who has borrowed nothing" \
"staff|1|Chandra Iyer|4
standard|1|Ada Okafor|3
standard|2|Dana Whitfield|2
student|1|Bruno Salgado|4
student|2|Eli Nakamura|0" "$(block 6)"
check_eq "Q7: the queues, with the cancelled reservation occupying no slot" \
"Neuromancer|1|Bruno Salgado
Neuromancer|2|Ada Okafor
The Left Hand of Darkness|1|Ada Okafor
The Left Hand of Darkness|2|Chandra Iyer
The Left Hand of Darkness|3|Dana Whitfield" "$(block 7)"
check_eq "Q8: eight months of loans, running total reaching 14" \
"2026-01|1|1
2026-02|1|2
2026-03|1|3
2026-04|1|4
2026-05|2|6
2026-06|3|9
2026-07|3|12
2026-08|2|14" "$(block 8)"
check_eq "Q9: the recursive walk finds Fiction and its three descendants, to depth 2" \
"0|Fiction|0
1|Gothic|1
1|Science Fiction|1
2|Cyberpunk|1" "$(block 9)"
check_eq "Q10: one author has never been borrowed" "Donald E. Knuth" "$(block 10)"

# The two failure modes the lesson names, demonstrated rather than asserted.
check_eq "forgetting the soft-delete filter reports 8 books instead of 7" "8" \
  "$(q "SELECT count(*) FROM books")"
check_eq "an INNER JOIN in Q6 would drop the member with no loans entirely" "4" \
  "$(q "SELECT count(*) FROM (SELECT m.member_id FROM members m JOIN loans l ON l.member_id = m.member_id WHERE m.left_at IS NULL GROUP BY m.member_id)")"
check_eq "count(*) instead of count(l.loan_id) reports 1 loan for Eli, not 0" "1" \
  "$(q "SELECT count(*) FROM members m LEFT JOIN loans l ON l.member_id = m.member_id WHERE m.full_name = 'Eli Nakamura'")"
check_eq "a GROUP BY alone cannot do top-2-per-tier: it collapses to 3 rows" "3" \
  "$(q "SELECT count(*) FROM (SELECT tier, max(c) FROM (SELECT m.tier AS tier, count(l.loan_id) AS c FROM members m LEFT JOIN loans l ON l.member_id = m.member_id WHERE m.left_at IS NULL GROUP BY m.member_id, m.tier) GROUP BY tier)")"
check_eq "EXISTS and the LEFT JOIN anti-join agree on Q2" "yes" \
  "$(q "SELECT CASE WHEN (SELECT count(*) FROM members m WHERE m.left_at IS NULL AND NOT EXISTS (SELECT 1 FROM loans l WHERE l.member_id = m.member_id)) = (SELECT count(*) FROM members m LEFT JOIN loans l ON l.member_id = m.member_id WHERE m.left_at IS NULL AND l.loan_id IS NULL) THEN 'yes' ELSE 'no' END")"
check_eq "money never leaves integer arithmetic: 410 + 300 pence is exactly 710" "710" \
  "$(q "SELECT sum(fine_pence) FROM loans")"
check_eq "and binary floating point is why: 0.1 + 0.2 is not 0.3 in SQLite either" "no" \
  "$(q "SELECT CASE WHEN 0.1 + 0.2 = 0.3 THEN 'yes' ELSE 'no' END")"

echo
# ---------------------------------------------------------------------------
echo "4. The rejected design really does break, silently"
# ---------------------------------------------------------------------------
rej="${work}/rejected.db"
"${sqlite_bin}" "${rej}" < "${lab_dir}/examples/04_rejected_design.sql" > "${work}/rejected.txt" 2>&1
rej_status=$?
check_eq "04_rejected_design.sql runs to completion with no error raised" "0" "${rej_status}"
check "the stored-position design ends with two members at the same position" \
  "$(grep -qE '^3 +2( |$)' "${work}/rejected.txt" && echo yes || echo no)"
check_eq "the v1 queue really does contain a duplicate position" "1" \
  "$("${sqlite_bin}" "${rej}" ".mode list" ".headers off" "SELECT count(*) FROM (SELECT queue_position FROM reservations_v1 WHERE status='waiting' GROUP BY queue_position HAVING count(*) > 1)")"
check_eq "the derived version renumbers itself correctly after a cancellation" "1,2" \
  "$("${sqlite_bin}" "${rej}" ".mode list" ".headers off" "SELECT group_concat(p) FROM (SELECT ROW_NUMBER() OVER (PARTITION BY book_id ORDER BY reserved_at) AS p FROM reservations_v2 WHERE status='waiting')")"

echo
# ---------------------------------------------------------------------------
echo "5. The report script prints the report"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/05_report.py" "${db}" > "${work}/report.txt" 2>&1
report_status=$?
check_eq "05_report.py exits 0" "0" "${report_status}"
check "the report states 7 books on the shelves and 4 out on loan" \
  "$(grep -q '7 books on the shelves, 4 of them out on loan' "${work}/report.txt" && echo yes || echo no)"
check "the report totals the fines at GBP 7.10" \
  "$(grep -q 'GBP 7.10  TOTAL' "${work}/report.txt" && echo yes || echo no)"
check "the report shows Eli Nakamura with 0 loans rather than omitting her" \
  "$(grep -q 'Eli Nakamura     0 loans' "${work}/report.txt" && echo yes || echo no)"
check "the report shows the three-deep queue for The Left Hand of Darkness" \
  "$(grep -q '3. Dana Whitfield' "${work}/report.txt" && echo yes || echo no)"
check "the report indents Cyberpunk two levels under Fiction" \
  "$(grep -q '^          Cyberpunk  (1 book)$' "${work}/report.txt" && echo yes || echo no)"
check "the report refuses to run against a database that does not exist" \
  "$("${python_bin}" "${lab_dir}/examples/05_report.py" "${work}/nothing.db" >/dev/null 2>&1 && echo no || echo yes)"

# The report instant is a parameter, not the wall clock — so a different
# instant gives a different, predictable answer.
"${python_bin}" "${lab_dir}/examples/05_report.py" "${db}" '2026-09-01T09:00:00Z' > "${work}/later.txt" 2>&1
check "with the instant moved forward, two more loans become overdue" \
  "$(grep -q '7 days  Dana Whitfield' "${work}/later.txt" && echo yes || echo no)"
check "and the two already-overdue loans grow from 10 and 5 days to 26 and 21" \
  "$(grep -q '26 days  Bruno Salgado' "${work}/later.txt" && grep -q '21 days  Chandra Iyer' "${work}/later.txt" && echo yes || echo no)"
check "the report reads no clock: it never imports datetime" \
  "$(grep -qE '^\s*(import|from)\s+datetime' "${lab_dir}/examples/05_report.py" && echo no || echo yes)"

echo
# ---------------------------------------------------------------------------
echo "6. The starter reports honest progress"
# ---------------------------------------------------------------------------
before="$(bash "${lab_dir}/starter/03_check.sh" 2>&1)"
before_status=$?
check "the untouched starter reports 0 of 16 exercises complete" \
  "$(printf '%s' "${before}" | grep -q '^0 of 16 exercises complete\.$' && echo yes || echo no)"
check_eq "and exits non-zero, so it cannot be mistaken for finished" "incomplete" \
  "$([ "${before_status}" -ne 0 ] && echo incomplete || echo "exit ${before_status}")"
check "it names the many-to-many table among the work still to do" \
  "$(printf '%s' "${before}" | grep -q 'book_authors' && echo yes || echo no)"

# Now solve it with the reference files, in a copy, and confirm 16 of 16.
solved="${work}/solved"
mkdir -p "${solved}"
cp -R "${lab_dir}/examples" "${lab_dir}/starter" "${solved}/"
cp "${solved}/examples/01_schema.sql"  "${solved}/starter/01_schema.sql"
cp "${solved}/examples/06_answers.sql" "${solved}/starter/02_questions.sql"
after="$(bash "${solved}/starter/03_check.sh" 2>&1)"
after_status=$?
check "with the reference schema and answers in place it reports 16 of 16" \
  "$(printf '%s' "${after}" | grep -q '^16 of 16 exercises complete\.$' && echo yes || echo no)"
check_eq "and exits 0" "0" "${after_status}"

# One deliberate wrong answer must be caught, or the checker proves nothing.
sed 's/WHERE m.left_at IS NULL$/WHERE 1 = 1/' "${solved}/examples/06_answers.sql" > "${solved}/starter/02_questions.sql"
broken="$(bash "${solved}/starter/03_check.sh" 2>&1)"
check "a query that forgets the soft-delete filter is caught, not waved through" \
  "$(printf '%s' "${broken}" | grep -q '^16 of 16 exercises complete\.$' && echo no || echo yes)"

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
check "every invented email address uses the reserved .invalid domain" \
  "$(grep -oE '[A-Za-z0-9._-]+@[A-Za-z0-9._-]+' "${lab_dir}/examples/02_seed.sql" | grep -v '\.invalid$' >/dev/null 2>&1 && echo no || echo yes)"
check "this suite created no database inside the lab directory" \
  "$([ ! -f "${lab_dir}/library.db" ] && [ ! -f "${lab_dir}/starter/library.db" ] && echo yes || echo no)"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
