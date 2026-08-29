#!/usr/bin/env bash
# Tests for the Day 087 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Every check below compares a REAL VALUE, not the existence of a file. The
# questions the suite asks are the ones the lesson claims answers to:
#
#   * does the wide table really produce the update and deletion anomalies?
#   * does SQLite really leave foreign-key enforcement OFF by default, and does
#     the identical insert really get rejected once the pragma is on?
#   * which rows does each join type actually keep?
#   * does count(*) really give the wrong per-group count after a LEFT JOIN?
#   * does moving a predicate from ON to WHERE really change the result set —
#     in BOTH directions?
#   * do a hand-written nested-loop join and a hand-written hash join really
#     agree with SQLite, row for row?
#
# Nothing here touches the network. Nothing needs sudo. Everything is built in
# a temporary directory that is removed in a trap, so a completed run leaves
# your lab directory exactly as it found it.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work=""
checks=0
failures=0

cleanup() {
  [ -n "${work}" ] && [ -d "${work}" ] && rm -rf "${work}"
}
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

# Resolve the two tools this lab needs, allowing an override for people who
# keep them somewhere unusual. Fails loudly rather than skipping checks.
python_bin="${PYTHON:-}"
if [ -z "${python_bin}" ]; then
  python_bin="$(command -v python3 || true)"
fi
sqlite_bin="${SQLITE3:-}"
if [ -z "${sqlite_bin}" ]; then
  sqlite_bin="$(command -v sqlite3 || true)"
fi

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

# q SQL — one scalar or one newline-separated column, no headers, no padding.
q() { "${sqlite_bin}" "${db}" ".mode list" ".headers off" "$1"; }

echo "Day 087 — Joins and Relationships"
echo "python3: $("${python_bin}" -c 'import sys; print(sys.version.split()[0])')"
echo "sqlite3: $("${sqlite_bin}" --version | cut -d' ' -f1)"
echo "work:    a temporary directory, removed when this script exits"
echo

# ---------------------------------------------------------------------------
echo "1. The wide table really does produce the anomalies"
# ---------------------------------------------------------------------------
wide_db="${work}/wide.db"
"${sqlite_bin}" "${wide_db}" < "${lab_dir}/examples/01_wide_table.sql" > "${work}/wide.txt" 2>&1
wide_status=$?
check_eq "01_wide_table.sql runs clean — every anomaly below is silent" "0" "${wide_status}"
check_eq "3 books needed 5 rows, because 2 authors are written down twice" \
  "5" "$(grep -c '^The ' "${work}/wide.txt" | tr -d ' ')"

# The update anomaly: one human being, two spellings, no error raised.
names_1942="$("${sqlite_bin}" "${wide_db}" ".mode list" ".headers off" \
  "SELECT count(DISTINCT author_name) FROM catalog_wide WHERE author_birth_year = 1942")"
check_eq "update anomaly: one author now has 2 different names in the table" \
  "2" "${names_1942}"

check "update anomaly: the database raised no error while contradicting itself" \
  "$(grep -qc 'Runtime error' "${work}/wide.txt" >/dev/null 2>&1 && echo no || echo yes)"

# The deletion anomaly: removing the book removed the only record of the author.
brooks="$("${sqlite_bin}" "${wide_db}" ".mode list" ".headers off" \
  "SELECT count(*) FROM catalog_wide WHERE author_name LIKE '%Brooks%'")"
check_eq "deletion anomaly: withdrawing the book erased the author entirely" \
  "0" "${brooks}"

# The insertion anomaly is structural: every book column is NOT NULL, so there
# is no row shape that records an author without inventing a book.
notnull="$("${sqlite_bin}" "${wide_db}" ".mode list" ".headers off" \
  "SELECT count(*) FROM pragma_table_info('catalog_wide') WHERE \"notnull\" = 1")"
check_eq "insertion anomaly: all 4 columns are NOT NULL, so an author needs a book" \
  "4" "${notnull}"

echo
# ---------------------------------------------------------------------------
echo "2. The split schema builds, and models the relationships properly"
# ---------------------------------------------------------------------------
"${sqlite_bin}" "${db}" < "${lab_dir}/examples/02_schema.sql" 2>"${work}/schema.err"
check "schema.sql runs without error" \
  "$([ ! -s "${work}/schema.err" ] && echo yes || echo no)"
"${sqlite_bin}" "${db}" < "${lab_dir}/examples/03_seed.sql" 2>"${work}/seed.err"
check "seed.sql runs without error" \
  "$([ ! -s "${work}/seed.err" ] && echo yes || echo no)"

check_eq "five tables exist" "5" \
  "$(q "SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ('authors','books','book_authors','members','loans')")"
check_eq "row counts are 7 authors, 4 books, 7 pairs, 5 members, 6 loans" \
  "7|4|7|5|6" \
  "$(q "SELECT (SELECT count(*) FROM authors) || '|' || (SELECT count(*) FROM books) || '|' || (SELECT count(*) FROM book_authors) || '|' || (SELECT count(*) FROM members) || '|' || (SELECT count(*) FROM loans)")"

# The junction table's primary key is the PAIR — that is what makes it a
# junction table rather than a table that happens to have two columns.
check_eq "book_authors is keyed on the PAIR (book_id, author_id)" \
  "book_id,author_id" \
  "$(q "SELECT group_concat(name) FROM (SELECT name FROM pragma_table_info('book_authors') WHERE pk > 0 ORDER BY pk)")"

# One-to-many is modelled by putting the key on the many side.
check_eq "loans (the many side) carries both foreign keys" "books|members" \
  "$(q "SELECT group_concat(t, '|') FROM (SELECT \"table\" AS t FROM pragma_foreign_key_list('loans') ORDER BY t)")"
check_eq "members references itself, which is what makes a self-join possible" \
  "members" "$(q "SELECT \"table\" FROM pragma_foreign_key_list('members')")"

echo
# ---------------------------------------------------------------------------
echo "3. PRAGMA foreign_keys is OFF by default — proved, not asserted"
# ---------------------------------------------------------------------------
fk_out="${work}/fk.txt"
"${sqlite_bin}" "${db}" < "${lab_dir}/examples/04_foreign_keys.sql" > "${fk_out}" 2>&1
fk_status=$?

check "a fresh connection reports PRAGMA foreign_keys = 0" \
  "$(grep -q 'PRAGMA foreign_keys  0' "${fk_out}" && echo yes || echo no)"
check "with it off, a loan pointing at member 999 INSERTS SUCCESSFULLY" \
  "$(grep -qE '^900 +101 +999' "${fk_out}" && echo yes || echo no)"
check "pragma_foreign_key_check finds the orphan the insert created" \
  "$(grep -qE '^loans +900 +members' "${fk_out}" && echo yes || echo no)"
check "after PRAGMA foreign_keys = ON the setting reads back as 1" \
  "$(grep -q 'PRAGMA foreign_keys  1' "${fk_out}" && echo yes || echo no)"
check "the IDENTICAL insert is then rejected: FOREIGN KEY constraint failed" \
  "$(grep -q 'FOREIGN KEY constraint failed' "${fk_out}" && echo yes || echo no)"
check_eq "sqlite3 exits non-zero when the constraint fires" "rejected" \
  "$([ "${fk_status}" -ne 0 ] && echo rejected || echo "exit ${fk_status}")"
check_eq "the orphan row is gone, so the rest of the suite sees clean data" \
  "6" "$(q "SELECT count(*) FROM loans")"

# The same fact from Python, including the transaction trap.
py_fk="${work}/fk_python.txt"
"${python_bin}" "${lab_dir}/examples/07_foreign_keys_python.py" > "${py_fk}" 2>&1
check "python: a new connection also reports foreign_keys 0" \
  "$(grep -q 'new connection: 0' "${py_fk}" && echo yes || echo no)"
check "python: the pragma is a no-op inside an open transaction (reads back 0)" \
  "$(grep -q 'reads back as: 0' "${py_fk}" && echo yes || echo no)"
check "python: after commit() the same pragma takes effect (reads back 1)" \
  "$(grep -q 'setting it again reads back as: 1' "${py_fk}" && echo yes || echo no)"
check "python: the orphan insert then raises IntegrityError" \
  "$(grep -q 'IntegrityError: FOREIGN KEY constraint failed' "${py_fk}" && echo yes || echo no)"

echo
# ---------------------------------------------------------------------------
echo "4. INNER JOIN, the comma form, and the cartesian product"
# ---------------------------------------------------------------------------
inner="SELECT b.title || ' / ' || a.name FROM books b
       JOIN book_authors ba ON ba.book_id = b.book_id
       JOIN authors a ON a.author_id = ba.author_id
       ORDER BY b.title, a.name"
check_eq "inner join across the junction returns 7 book-author pairs" "7" \
  "$(q "SELECT count(*) FROM (${inner})")"
check_eq "the co-authored C book yields both of its authors, not one row" \
  "The C Programming Language / Brian W. Kernighan
The C Programming Language / Dennis M. Ritchie" \
  "$(q "${inner}" | grep '^The C Programming Language')"

comma="SELECT b.title || ' / ' || a.name FROM books b, book_authors ba, authors a
       WHERE ba.book_id = b.book_id AND a.author_id = ba.author_id
       ORDER BY b.title, a.name"
check_eq "the old comma-join-with-WHERE form gives byte-identical output" \
  "$(q "${inner}")" "$(q "${comma}")"

check_eq "an unconstrained CROSS JOIN is 4 books x 7 authors = 28 rows" "28" \
  "$(q "SELECT count(*) FROM books CROSS JOIN authors")"
check_eq "forgetting ONE join condition turns 7 correct rows into 49" \
  "49" "$(q "SELECT count(*) FROM books b JOIN book_authors ba ON ba.book_id = b.book_id JOIN authors a ON 1=1")"

echo
# ---------------------------------------------------------------------------
echo "5. LEFT OUTER JOIN — exactly which rows survive, and what turns NULL"
# ---------------------------------------------------------------------------
check_eq "left join authors->books keeps all 7 authors, giving 8 rows" "8" \
  "$(q "SELECT count(*) FROM authors a LEFT JOIN book_authors ba ON ba.author_id = a.author_id LEFT JOIN books b ON b.book_id = ba.book_id")"
check_eq "the unmatched author survives with NULL in every right-hand column" \
  "Donald E. Knuth|1" \
  "$(q "SELECT a.name || '|' || (b.title IS NULL AND b.published_year IS NULL) FROM authors a LEFT JOIN book_authors ba ON ba.author_id = a.author_id LEFT JOIN books b ON b.book_id = ba.book_id WHERE b.book_id IS NULL")"
check_eq "the mirror INNER join drops that author, giving 7 rows" "7" \
  "$(q "SELECT count(*) FROM authors a JOIN book_authors ba ON ba.author_id = a.author_id JOIN books b ON b.book_id = ba.book_id")"

echo
# ---------------------------------------------------------------------------
echo "6. LEFT JOIN + IS NULL — the anti-join idiom"
# ---------------------------------------------------------------------------
check_eq "authors with no catalogued book" "Donald E. Knuth" \
  "$(q "SELECT a.name FROM authors a LEFT JOIN book_authors ba ON ba.author_id = a.author_id WHERE ba.author_id IS NULL ORDER BY a.name")"
check_eq "books never borrowed" "104|The Practice of Programming" \
  "$(q "SELECT b.book_id || '|' || b.title FROM books b LEFT JOIN loans l ON l.book_id = b.book_id WHERE l.loan_id IS NULL ORDER BY b.title")"
check_eq "members who have never borrowed anything" "Eli Nakamura" \
  "$(q "SELECT m.name FROM members m LEFT JOIN loans l ON l.member_id = m.member_id WHERE l.loan_id IS NULL ORDER BY m.name")"
check_eq "NOT IN answers the same question here, since no member_id is NULL" \
  "Eli Nakamura" \
  "$(q "SELECT name FROM members WHERE member_id NOT IN (SELECT member_id FROM loans) ORDER BY name")"

echo
# ---------------------------------------------------------------------------
echo "7. Joins with GROUP BY — the zero-count trap"
# ---------------------------------------------------------------------------
check_eq "LEFT JOIN with count(l.loan_id) gives a genuine zero for Eli" \
  "Ada Okafor|2
Bruno Salgado|2
Chandra Iyer|1
Dana Whitfield|1
Eli Nakamura|0" \
  "$(q "SELECT m.name || '|' || count(l.loan_id) FROM members m LEFT JOIN loans l ON l.member_id = m.member_id GROUP BY m.member_id, m.name ORDER BY count(l.loan_id) DESC, m.name")"

check_eq "count(*) instead reports 1 for the member who borrowed nothing" "1" \
  "$(q "SELECT count(*) FROM members m LEFT JOIN loans l ON l.member_id = m.member_id WHERE m.name = 'Eli Nakamura' GROUP BY m.member_id")"

check_eq "an INNER JOIN drops her from the report altogether: 4 rows, not 5" "4" \
  "$(q "SELECT count(*) FROM (SELECT m.member_id FROM members m JOIN loans l ON l.member_id = m.member_id GROUP BY m.member_id)")"

check_eq "times borrowed per book, with a real zero for the unread one" \
  "The C Programming Language|3
The Mythical Man-Month|2
Artificial Intelligence: A Modern Approach|1
The Practice of Programming|0" \
  "$(q "SELECT b.title || '|' || count(l.loan_id) FROM books b LEFT JOIN loans l ON l.book_id = b.book_id GROUP BY b.book_id, b.title ORDER BY count(l.loan_id) DESC, b.title")"

echo
# ---------------------------------------------------------------------------
echo "8. ON versus WHERE on an outer join — wrong in BOTH directions"
# ---------------------------------------------------------------------------
on_form="SELECT m.name || '|' || coalesce(l.loan_id, 'none')
         FROM members m LEFT JOIN loans l
           ON l.member_id = m.member_id AND l.returned_on IS NULL
         ORDER BY m.name, l.loan_id"
where_form="SELECT m.name || '|' || coalesce(l.loan_id, 'none')
            FROM members m LEFT JOIN loans l ON l.member_id = m.member_id
            WHERE l.returned_on IS NULL
            ORDER BY m.name, l.loan_id"

check_eq "predicate in ON: all 5 members survive, unmatched ones showing none" \
  "Ada Okafor|2
Bruno Salgado|6
Chandra Iyer|4
Dana Whitfield|none
Eli Nakamura|none" \
  "$(q "${on_form}")"

check_eq "predicate in WHERE: only 4 rows — the outer join has collapsed" "4" \
  "$(q "SELECT count(*) FROM (${where_form})")"

check_eq "WHERE drops Dana, who is a member and has genuinely returned everything" \
  "0" "$(q "SELECT count(*) FROM members m LEFT JOIN loans l ON l.member_id = m.member_id WHERE l.returned_on IS NULL AND m.name = 'Dana Whitfield'")"

check_eq "and WHERE KEEPS Eli, who never borrowed at all — a false positive" \
  "1" "$(q "SELECT count(*) FROM members m LEFT JOIN loans l ON l.member_id = m.member_id WHERE l.returned_on IS NULL AND m.name = 'Eli Nakamura'")"

echo
# ---------------------------------------------------------------------------
echo "9. Self-joins and three-or-more-table joins"
# ---------------------------------------------------------------------------
check_eq "self-join with LEFT keeps the two members nobody referred" \
  "Ada Okafor|
Bruno Salgado|Ada Okafor
Chandra Iyer|Ada Okafor
Dana Whitfield|Bruno Salgado
Eli Nakamura|" \
  "$(q "SELECT m.name || '|' || coalesce(r.name, '') FROM members m LEFT JOIN members r ON r.member_id = m.referred_by ORDER BY m.member_id")"

check_eq "self-join with INNER silently loses those two" "3" \
  "$(q "SELECT count(*) FROM members m JOIN members r ON r.member_id = m.referred_by")"

check_eq "four tables at once: what is out on loan, with authors" \
  "Ada Okafor|The Mythical Man-Month|Frederick P. Brooks Jr.
Bruno Salgado|The Mythical Man-Month|Frederick P. Brooks Jr.
Chandra Iyer|Artificial Intelligence: A Modern Approach|Peter Norvig
Chandra Iyer|Artificial Intelligence: A Modern Approach|Stuart J. Russell" \
  "$(q "SELECT m.name || '|' || b.title || '|' || a.name FROM loans l JOIN members m ON m.member_id = l.member_id JOIN books b ON b.book_id = l.book_id JOIN book_authors ba ON ba.book_id = b.book_id JOIN authors a ON a.author_id = ba.author_id WHERE l.returned_on IS NULL ORDER BY m.name, a.name")"

check_eq "3 loans are outstanding, but the author join makes 4 rows — not a bug" \
  "3|4" \
  "$(q "SELECT (SELECT count(*) FROM loans WHERE returned_on IS NULL) || '|' || (SELECT count(*) FROM loans l JOIN books b ON b.book_id = l.book_id JOIN book_authors ba ON ba.book_id = b.book_id WHERE l.returned_on IS NULL)")"

echo
# ---------------------------------------------------------------------------
echo "10. The join implemented from scratch in Python agrees with SQL"
# ---------------------------------------------------------------------------
scratch="${work}/scratch.txt"
"${python_bin}" "${lab_dir}/examples/06_join_from_scratch.py" "${db}" > "${scratch}" 2>&1
scratch_status=$?
check_eq "06_join_from_scratch.py exits 0" "0" "${scratch_status}"
check "nested-loop join equals the SQL result" \
  "$(grep -q 'nested-loop == SQL: True' "${scratch}" && echo yes || echo no)"
check "hash join equals the SQL result" \
  "$(grep -q 'hash        == SQL: True' "${scratch}" && echo yes || echo no)"
check "the two algorithms agree with each other" \
  "$(grep -q 'nested-loop == hash: True' "${scratch}" && echo yes || echo no)"
check "nested loop costs 30 comparisons (6 x 5)" \
  "$(grep -q '30 key comparisons' "${scratch}" && echo yes || echo no)"
check "the hash join costs 11 operations (6 + 5) for the same answer" \
  "$(grep -q '11 operations' "${scratch}" && echo yes || echo no)"
check "the hand-written outer join keeps Eli Nakamura, as SQL does" \
  "$(grep -q "outer join agrees with SQL: True" "${scratch}" && echo yes || echo no)"

echo
# ---------------------------------------------------------------------------
echo "11. N+1 queries against one join — measured on this machine"
# ---------------------------------------------------------------------------
n1="${work}/n1.txt"
"${python_bin}" "${lab_dir}/examples/08_n_plus_one.py" > "${n1}" 2>&1
n1_status=$?
check_eq "08_n_plus_one.py exits 0" "0" "${n1_status}"
check "the loop really issues 501 queries" \
  "$(grep -qE 'N\+1 loop: +501 queries' "${n1}" && echo yes || echo no)"
check "the join really issues 1" \
  "$(grep -qE 'one join: +1 queries' "${n1}" && echo yes || echo no)"
check "both produce the same answer, so the comparison is fair" \
  "$(grep -q 'same answer: True' "${n1}" && echo yes || echo no)"

echo
# ---------------------------------------------------------------------------
echo "12. The planner really is choosing a join algorithm"
# ---------------------------------------------------------------------------
plans="${work}/plans.txt"
"${sqlite_bin}" "${db}" < "${lab_dir}/examples/09_query_plans.sql" > "${plans}" 2>&1
check "an indexed inner join plans as SCAN one side, SEARCH the other" \
  "$(grep -q 'SCAN l USING COVERING INDEX' "${plans}" && grep -q 'SEARCH m USING INTEGER PRIMARY KEY' "${plans}" && echo yes || echo no)"
check "the outer join is planned with a LEFT-JOIN marker on the inner search" \
  "$(grep -q 'LEFT-JOIN' "${plans}" && echo yes || echo no)"
check "a cartesian product plans as two bare SCANs and nothing else" \
  "$(grep -q 'SCAN books' "${plans}" && grep -q 'SCAN authors' "${plans}" && echo yes || echo no)"

echo
# ---------------------------------------------------------------------------
echo "13. The starter is runnable, and honest about being unfinished"
# ---------------------------------------------------------------------------
starter_db="${work}/starter.db"
"${sqlite_bin}" "${starter_db}" < "${lab_dir}/examples/02_schema.sql" 2>/dev/null
"${sqlite_bin}" "${starter_db}" < "${lab_dir}/examples/03_seed.sql" 2>/dev/null
"${sqlite_bin}" "${starter_db}" < "${lab_dir}/starter/02_exercises.sql" > "${work}/starter_sql.txt" 2>&1
starter_sql_status=$?
check_eq "the SQL starter runs end to end before you have changed anything" \
  "0" "${starter_sql_status}"
check "the SQL starter carries all six numbered exercises" \
  "$([ "$(grep -c '^-- EXERCISE [1-6] ' "${lab_dir}/starter/02_exercises.sql")" -eq 6 ] && echo yes || echo no)"
check "each SQL exercise names the check that verifies it" \
  "$([ "$(grep -c '^-- Checked by:' "${lab_dir}/starter/02_exercises.sql")" -eq 6 ] && echo yes || echo no)"

"${python_bin}" "${lab_dir}/starter/03_join_from_scratch.py" "${starter_db}" > "${work}/starter_py.txt" 2>&1
starter_py_status=$?
check_eq "the Python starter runs, and reports 0 of 3 exercises complete" "0 of 3 exercises complete." \
  "$(grep -o '. of 3 exercises complete.' "${work}/starter_py.txt")"
check_eq "the Python starter exits non-zero while it is unfinished" "unfinished" \
  "$([ "${starter_py_status}" -ne 0 ] && echo unfinished || echo "exit ${starter_py_status}")"

# The most important check in this section: fill the three gaps in a COPY of
# the starter and confirm it then passes. A starter whose exercises cannot be
# completed, or a checker that would pass anyway, is worth nothing.
solved="${work}/solved.py"
"${python_bin}" - "${lab_dir}/starter/03_join_from_scratch.py" "${solved}" <<'PY'
import sys
source, target = sys.argv[1], sys.argv[2]
text = open(source, encoding="utf-8").read()
replacements = [
    (
        "            pairs.append((left_row, right_row))  # <- exercise 7 goes here",
        "            if left_row[left_key] == right_row[right_key]:\n"
        "                pairs.append((left_row, right_row))",
    ),
    (
        "    for left_row in left:  # probe phase - exercise 8 goes here\n"
        "        operations += 1\n",
        "    for left_row in left:\n"
        "        operations += 1\n"
        "        for right_row in index.get(left_row[left_key], ()):\n"
        "            pairs.append((left_row, right_row))\n",
    ),
    (
        "        # exercise 9: the missing `else` goes here",
        "        else:\n            pairs.append((left_row, None))",
    ),
]
for old, new in replacements:
    assert old in text, f"starter text drifted: {old!r}"
    text = text.replace(old, new)
open(target, "w", encoding="utf-8").write(text)
PY
check "the three starter gaps are still exactly where the answer key expects" \
  "$([ -f "${solved}" ] && echo yes || echo no)"

"${python_bin}" "${solved}" "${starter_db}" > "${work}/solved.txt" 2>&1
solved_status=$?
check_eq "completing the three exercises makes the starter pass" "3 of 3 exercises complete." \
  "$(grep -o '. of 3 exercises complete.' "${work}/solved.txt")"
check_eq "and exit 0" "0" "${solved_status}"

echo
# ---------------------------------------------------------------------------
echo "14. Hygiene: offline, no privilege, no mess left behind"
# ---------------------------------------------------------------------------
# Every URL anywhere in the lab's scripts, and every line that would actually
# RUN sudo (as opposed to a comment saying this lab does not need it).
"${python_bin}" - "${lab_dir}" > "${work}/hygiene.txt" 2>&1 <<'PY'
import re
import sys
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
check_eq "the only URL anywhere in the lab's scripts is the cited SQLite page" \
  "URLS https://www.sqlite.org/np1queryprob.html" \
  "$(grep '^URLS ' "${work}/hygiene.txt")"
check_eq "no line in this lab would actually invoke sudo" "SUDO" \
  "$(grep '^SUDO ' "${work}/hygiene.txt" | sed 's/ *$//')"
check "nothing in this lab imports a networking module" \
  "$(grep -rlE '^\s*(import|from)\s+(socket|urllib|http|requests)' "${lab_dir}/examples" "${lab_dir}/starter" >/dev/null 2>&1 && echo no || echo yes)"
check "no captured output leaks an absolute home path" \
  "$(grep -rl '/Users/\|/home/' "${lab_dir}/expected-output" >/dev/null 2>&1 && echo no || echo yes)"
check "this suite created no database inside the lab directory" \
  "$([ ! -f "${lab_dir}/library.db" ] && echo yes || echo no)"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
