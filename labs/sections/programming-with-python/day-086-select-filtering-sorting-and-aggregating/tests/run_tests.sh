#!/usr/bin/env bash
# Tests for the Day 086 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Every check here compares an ACTUAL RESULT VALUE against a number or string
# that was worked out from the seed data by hand. A test that only proves a
# query parsed would pass on every one of the twelve broken queries in
# starter/exercises.sql, which is exactly the failure mode this day is about.
#
# The suite builds its own throwaway database under a mktemp -d directory and
# removes it in a trap, so it never touches examples/library.db and never
# depends on what you did to it. Nothing here reaches the network, nothing
# needs sudo, and nothing survives the run.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checks=0
failures=0
work_root=""

cleanup() {
  [ -n "${work_root}" ] && [ -d "${work_root}" ] && rm -rf "${work_root}"
}
trap cleanup EXIT INT TERM

pass() { checks=$((checks + 1)); echo "  ok: $1"; }
fail() { checks=$((checks + 1)); failures=$((failures + 1)); echo "  FAIL: $1"; }

# check <label> <expected> <actual>
check() {
  if [ "$2" = "$3" ]; then
    pass "$1 = $3"
  else
    fail "$1: expected [$2] but got [$3]"
  fi
}

# check_ne <label> <must-not-equal> <actual>
check_ne() {
  if [ "$2" != "$3" ]; then
    pass "$1 (is not $2)"
  else
    fail "$1: value must NOT be [$2] but it is"
  fi
}

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "FAIL: the sqlite3 shell is not on PATH." >&2
  echo "  macOS ships it; on Debian or Ubuntu: sudo apt install sqlite3" >&2
  exit 1
fi
python_bin="${PYTHON:-python3}"
if ! command -v "${python_bin}" >/dev/null 2>&1; then
  echo "FAIL: python3 is not on PATH (needed for the from-scratch comparison)." >&2
  exit 1
fi

work_root="$(mktemp -d)"
db="${work_root}/library.db"

# q <sql> -> the single value the query returns, with no header and no padding
q() { sqlite3 "${db}" "$1"; }

echo "Day 086 — Ask the Database Questions"
echo "sqlite3 $(sqlite3 --version | cut -d' ' -f1), $(${python_bin} --version)"
echo "throwaway database: ${db}"
echo

echo "1. The seed builds, and builds the same thing every time"
bash "${lab_dir}/examples/build_db.sh" "${db}" >/dev/null 2>&1
if [ -f "${db}" ]; then pass "examples/build_db.sh created the database"
else fail "examples/build_db.sh did not create a database"; fi
check "books"   "24" "$(q 'SELECT COUNT(*) FROM books;')"
check "members" "12" "$(q 'SELECT COUNT(*) FROM members;')"
check "loans"   "45" "$(q 'SELECT COUNT(*) FROM loans;')"
check "the deliberate holes: unrated books"      "4"  "$(q 'SELECT COUNT(*)-COUNT(rating) FROM books;')"
check "the deliberate holes: unclassified books" "3"  "$(q 'SELECT COUNT(*)-COUNT(genre) FROM books;')"
check "the deliberate holes: members with no city" "2" "$(q 'SELECT COUNT(*)-COUNT(city) FROM members;')"
check "the deliberate holes: loans still out"    "15" "$(q 'SELECT COUNT(*)-COUNT(returned_on) FROM loans;')"
# Rebuilding must be idempotent — the same rows, not a doubled table.
bash "${lab_dir}/examples/build_db.sh" "${db}" >/dev/null 2>&1
check "rebuilding gives the same 24 books, not 48" "24" "$(q 'SELECT COUNT(*) FROM books;')"
echo

echo "2. WHERE: comparisons, boolean operators, IN, BETWEEN"
check "science books from 2000 onwards" "7" \
  "$(q "SELECT COUNT(*) FROM books WHERE genre='science' AND published_year>=2000;")"
check "BETWEEN 2015 AND 2018 includes both endpoints" "4" \
  "$(q 'SELECT COUNT(*) FROM books WHERE published_year BETWEEN 2015 AND 2018;')"
check "the same range spelled out with >= and <=" "4" \
  "$(q 'SELECT COUNT(*) FROM books WHERE published_year>=2015 AND published_year<=2018;')"
check "IN over two genres" "7" \
  "$(q "SELECT COUNT(*) FROM books WHERE genre IN ('poetry','mystery');")"
check "brackets change the meaning: (A OR B) AND C" "5" \
  "$(q "SELECT COUNT(*) FROM books WHERE (genre='science' OR genre='history') AND published_year>=2015;")"
check "AND binds tighter than OR: A OR (B AND C)" "8" \
  "$(q "SELECT COUNT(*) FROM books WHERE genre='science' OR genre='history' AND published_year>=2015;")"
# NOT IN drops the NULL-genre rows: 24 - 7 matching - 3 unclassified = 14.
check "NOT IN silently excludes the NULL genres too" "14" \
  "$(q "SELECT COUNT(*) FROM books WHERE genre NOT IN ('poetry','mystery');")"
echo

echo "3. LIKE and GLOB really do differ on case"
check "LIKE %archive% folds case"        "2" "$(q "SELECT COUNT(*) FROM books WHERE title LIKE '%archive%';")"
check "GLOB *archive* does not"          "0" "$(q "SELECT COUNT(*) FROM books WHERE title GLOB '*archive*';")"
check "GLOB *Archive* spelled as stored" "2" "$(q "SELECT COUNT(*) FROM books WHERE title GLOB '*Archive*';")"
check "LIKE underscore matches exactly one character" "The Quiet Algorithm" \
  "$(q "SELECT title FROM books WHERE title LIKE 'The _____ Algorithm';")"
check "one underscore too few matches nothing, and does not error" "0" \
  "$(q "SELECT COUNT(*) FROM books WHERE title LIKE 'The ____ Algorithm';")"
check "GLOB character classes have no LIKE equivalent" "4" \
  "$(q "SELECT COUNT(*) FROM books WHERE title GLOB '[AN]*';")"
echo

echo "4. NULL and three-valued logic"
# An empty result string is how the sqlite3 shell renders a NULL scalar.
check "NULL = NULL is NULL, not 1"  "" "$(q 'SELECT NULL = NULL;')"
check "NULL <> NULL is NULL too"    "" "$(q 'SELECT NULL <> NULL;')"
check "NULL IS NULL is 1"           "1" "$(q 'SELECT NULL IS NULL;')"
check "NULL AND false is FALSE"     "0" "$(q 'SELECT NULL AND 0;')"
check "NULL AND true is UNKNOWN"    "" "$(q 'SELECT NULL AND 1;')"
check "NULL OR true is TRUE"        "1" "$(q 'SELECT NULL OR 1;')"
check "NULL OR false is UNKNOWN"    "" "$(q 'SELECT NULL OR 0;')"
check "NOT NULL is UNKNOWN"         "" "$(q 'SELECT NOT NULL;')"
check "the trap: returned_on = NULL finds nothing" "0" \
  "$(q 'SELECT COUNT(*) FROM loans WHERE returned_on = NULL;')"
check "the other trap: returned_on <> empty string finds the RETURNED ones" "30" \
  "$(q "SELECT COUNT(*) FROM loans WHERE returned_on <> '';")"
check "IS NULL is the only correct test" "15" \
  "$(q 'SELECT COUNT(*) FROM loans WHERE returned_on IS NULL;')"
check "naive not-from-Pune loses the members with no city" "8" \
  "$(q "SELECT COUNT(*) FROM members WHERE city <> 'Pune';")"
check "the honest version keeps them" "10" \
  "$(q "SELECT COUNT(*) FROM members WHERE city IS NULL OR city <> 'Pune';")"
check "and 8 + 2 Pune members would be 10, not 12 — so the naive query lost 2" "2" \
  "$(q "SELECT COUNT(*) FROM members WHERE city = 'Pune';")"
echo

echo "5. The NULL traps must NOT be 'fixed' by inventing data"
# These are the checks that go red if somebody makes the numbers agree by
# writing zeros and empty strings into the holes instead of understanding them.
check_ne "AVG(rating) must not equal the COALESCE-to-zero average" \
  "$(q 'SELECT ROUND(AVG(COALESCE(rating,0.0)),2) FROM books;')" \
  "$(q 'SELECT ROUND(AVG(rating),2) FROM books;')"
check "AVG(rating) ignores the 4 NULLs" "4.16" "$(q 'SELECT ROUND(AVG(rating),2) FROM books;')"
check "COALESCE to zero gives a different, wrong answer" "3.47" \
  "$(q 'SELECT ROUND(AVG(COALESCE(rating,0.0)),2) FROM books;')"
check "SUM over zero matching rows is NULL, not 0" "" \
  "$(q "SELECT SUM(rating) FROM books WHERE genre='no-such-genre';")"
check "TOTAL over the same zero rows is 0.0" "0.0" \
  "$(q "SELECT TOTAL(rating) FROM books WHERE genre='no-such-genre';")"
check "an aggregate over zero rows still returns exactly one row" "1" \
  "$(q 'SELECT COUNT(*) FROM (SELECT AVG(rating) FROM books WHERE published_year=1066);')"
# If a well-meaning fix replaced NULL ratings with 0.0 in the table itself, this
# MIN would become 0.0 and this check would fail.
check "MIN(rating) is a real rating, not an invented zero" "3.2" "$(q 'SELECT MIN(rating) FROM books;')"
echo

echo "6. ORDER BY, DISTINCT, LIMIT and OFFSET"
check "ascending puts NULLs first in SQLite" "" \
  "$(q 'SELECT rating FROM books ORDER BY rating ASC LIMIT 1;')"
check "descending puts them last" "4.9" \
  "$(q 'SELECT rating FROM books ORDER BY rating DESC LIMIT 1;')"
check "NULLS LAST overrides the ascending default" "3.2" \
  "$(q 'SELECT rating FROM books ORDER BY rating ASC NULLS LAST LIMIT 1;')"
check "so does ORDER BY rating IS NULL, rating" "3.2" \
  "$(q 'SELECT rating FROM books ORDER BY rating IS NULL, rating ASC LIMIT 1;')"
# genre ASC first, so the winner is the best book of the ALPHABETICALLY FIRST
# genre — fiction — not the best book overall. Key order is the whole meaning.
check "two sort keys: first key wins, so this is the top FICTION book" "The Long Instrument" \
  "$(q "SELECT title FROM books WHERE genre IS NOT NULL AND rating IS NOT NULL ORDER BY genre ASC, rating DESC LIMIT 1;")"
check "swap the keys and you get the best book overall instead" "Grammar of Machines" \
  "$(q "SELECT title FROM books WHERE genre IS NOT NULL AND rating IS NOT NULL ORDER BY rating DESC, genre ASC LIMIT 1;")"
check "the top MYSTERY needs the genre in the WHERE, not the ORDER BY" "The Second Archive" \
  "$(q "SELECT title FROM books WHERE genre='mystery' ORDER BY rating DESC NULLS LAST LIMIT 1;")"
check "ORDER BY may use a SELECT alias — standard SQL, works everywhere" "The Lost Cartographers" \
  "$(q 'SELECT title, pages*2 AS reading_minutes FROM books ORDER BY reading_minutes DESC LIMIT 1;' | cut -d'|' -f1)"
# SQLite ACCEPTS a SELECT alias in WHERE as an extension; standard SQL does not,
# and PostgreSQL rejects it. Pinning the behaviour here so the lesson's claim
# stays honest about which engine does what.
check "SQLite accepts a SELECT alias in WHERE, as an extension" "6" \
  "$(q 'SELECT COUNT(*) FROM (SELECT title, pages*2 AS reading_minutes FROM books WHERE reading_minutes > 800);')"
check "the portable spelling gives the same six rows" "6" \
  "$(q 'SELECT COUNT(*) FROM (SELECT title, pages*2 AS reading_minutes FROM books WHERE pages*2 > 800);')"
check "DISTINCT over one column: distinct authors" "7" \
  "$(q 'SELECT COUNT(*) FROM (SELECT DISTINCT author FROM books);')"
check "DISTINCT over two columns keeps one row per PAIR" "15" \
  "$(q 'SELECT COUNT(*) FROM (SELECT DISTINCT author, genre FROM books);')"
check "top-N with a deterministic tie-break" "Small Gods of Arithmetic" \
  "$(q 'SELECT title FROM books ORDER BY rating DESC NULLS LAST, title ASC LIMIT 1;')"
check "OFFSET 5 starts page two of the same list" "The Silent Archive" \
  "$(q 'SELECT title FROM books ORDER BY rating DESC NULLS LAST, title ASC LIMIT 1 OFFSET 5;')"
echo

echo "7. Aggregates, and what NULL does to each"
check "COUNT(*) counts rows"              "24" "$(q 'SELECT COUNT(*) FROM books;')"
check "COUNT(rating) counts values"       "20" "$(q 'SELECT COUNT(rating) FROM books;')"
check "COUNT(genre) counts values"        "21" "$(q 'SELECT COUNT(genre) FROM books;')"
check "COUNT(DISTINCT genre) skips NULL"  "5"  "$(q 'SELECT COUNT(DISTINCT genre) FROM books;')"
check "COUNT(DISTINCT author)"            "7"  "$(q 'SELECT COUNT(DISTINCT author) FROM books;')"
check "AVG is SUM over the NON-NULL count" "1" \
  "$(q 'SELECT ROUND(AVG(rating),6) = ROUND(SUM(rating)/COUNT(rating),6) FROM books;')"
check "MIN(published_year)" "1988" "$(q 'SELECT MIN(published_year) FROM books;')"
check "MAX(published_year)" "2025" "$(q 'SELECT MAX(published_year) FROM books;')"
echo

echo "8. GROUP BY"
check "one bucket per distinct genre, NULLs together in one more" "6" \
  "$(q 'SELECT COUNT(*) FROM (SELECT genre FROM books GROUP BY genre);')"
check "the science bucket has 7 books" "7" \
  "$(q "SELECT COUNT(*) FROM books GROUP BY genre HAVING genre='science';")"
check "the unclassified bucket has 3" "3" \
  "$(q 'SELECT COUNT(*) FROM books GROUP BY genre HAVING genre IS NULL;')"
check "grouping by an expression: books published in the 2010s" "9" \
  "$(q 'SELECT n FROM (SELECT (published_year/10)*10 AS decade, COUNT(*) AS n FROM books WHERE published_year IS NOT NULL GROUP BY decade) WHERE decade=2010;')"
check "grouping by two keys gives one row per combination that occurs" "15" \
  "$(q 'SELECT COUNT(*) FROM (SELECT author, genre FROM books GROUP BY author, genre);')"
check "the busiest borrower took 6 loans" "6" \
  "$(q 'SELECT COUNT(*) AS n FROM loans GROUP BY member_id ORDER BY n DESC LIMIT 1;')"
check "SUM over a CASE counts a subset inside each bucket" "15" \
  "$(q 'SELECT SUM(still) FROM (SELECT SUM(CASE WHEN returned_on IS NULL THEN 1 ELSE 0 END) AS still FROM loans GROUP BY member_id);')"
check "WHERE runs before GROUP BY: Q1 loans for member 1" "5" \
  "$(q "SELECT COUNT(*) FROM loans WHERE member_id=1 AND borrowed_on BETWEEN '2026-01-01' AND '2026-03-31';")"
echo

echo "9. HAVING — the filter WHERE cannot express"
check "authors with more than three titles" "3" \
  "$(q 'SELECT COUNT(*) FROM (SELECT author FROM books GROUP BY author HAVING COUNT(*) > 3);')"
check "the most prolific of them" "Ada Fenwick" \
  "$(q 'SELECT author FROM books GROUP BY author ORDER BY COUNT(*) DESC, author ASC LIMIT 1;')"
# The proof that WHERE cannot do this: the engine refuses the query outright.
where_err="$(sqlite3 "${db}" 'SELECT author FROM books WHERE COUNT(*) > 3 GROUP BY author;' 2>&1)"
if printf '%s' "${where_err}" | grep -qi 'misuse of aggregate'; then
  pass "WHERE COUNT(*) > 3 is rejected: ${where_err}"
else
  fail "WHERE COUNT(*) > 3 should be rejected as a misuse of an aggregate, but SQLite said: ${where_err}"
fi
check "WHERE and HAVING together: post-2000 genres with 2+ books" "6" \
  "$(q 'SELECT COUNT(*) FROM (SELECT genre FROM books WHERE published_year>=2000 GROUP BY genre HAVING COUNT(*)>=2);')"
check "HAVING on an aggregate absent from the SELECT list" "2" \
  "$(q 'SELECT COUNT(*) FROM (SELECT genre FROM books GROUP BY genre HAVING AVG(pages) > 350);')"
check "books borrowed more than twice" "7" \
  "$(q 'SELECT COUNT(*) FROM (SELECT book_id FROM loans GROUP BY book_id HAVING COUNT(*) > 2);')"
check "the most borrowed book was taken out 7 times" "7" \
  "$(q 'SELECT COUNT(*) AS n FROM loans GROUP BY book_id ORDER BY n DESC LIMIT 1;')"
check "HAVING over two aggregates: members with 2+ books still out" "5" \
  "$(q 'SELECT COUNT(*) FROM (SELECT member_id FROM loans GROUP BY member_id HAVING COUNT(*)-COUNT(returned_on) >= 2);')"
echo

echo "10. Scalar functions and CASE"
check "|| concatenates" "The Silent Archive (Priya Raman)" \
  "$(q "SELECT title || ' (' || author || ')' FROM books WHERE book_id=1;")"
check "a scalar function on NULL returns NULL" "" "$(q 'SELECT LOWER(genre) FROM books WHERE book_id=15;')"
check "TYPEOF names the storage class of the value in the row" "null" \
  "$(q 'SELECT TYPEOF(rating) FROM books WHERE book_id=4;')"
check "JULIANDAY subtraction gives real elapsed days" "28.0" \
  "$(q 'SELECT JULIANDAY(returned_on)-JULIANDAY(borrowed_on) FROM loans WHERE loan_id=2;')"
check "subtracting the raw TEXT dates confidently returns nonsense" "0" \
  "$(q 'SELECT returned_on - borrowed_on FROM loans WHERE loan_id=2;')"
check "STRFTIME buckets a stored date by month" "2026-01" \
  "$(q "SELECT STRFTIME('%Y-%m', borrowed_on) FROM loans WHERE loan_id=1;")"
check "GROUP BY over a CASE: the 'good' band" "8" \
  "$(q "SELECT n FROM (SELECT CASE WHEN rating IS NULL THEN 'unrated' WHEN rating>=4.5 THEN 'excellent' WHEN rating>=4.0 THEN 'good' WHEN rating>=3.5 THEN 'fair' ELSE 'poor' END AS band, COUNT(*) AS n FROM books GROUP BY band) WHERE band='good';")"
check "with the NULL branch first, 4 books are 'unrated'" "4" \
  "$(q "SELECT COUNT(*) FROM (SELECT CASE WHEN rating IS NULL THEN 'unrated' WHEN rating>=4.0 THEN 'good' ELSE 'poor' END AS band FROM books) WHERE band='unrated';")"
check "with the NULL branch, 'poor' holds the 6 genuinely low-rated books" "6" \
  "$(q "SELECT COUNT(*) FROM (SELECT CASE WHEN rating IS NULL THEN 'unrated' WHEN rating>=4.0 THEN 'good' ELSE 'poor' END AS band FROM books) WHERE band='poor';")"
# Drop the NULL branch and 'poor' swells from 6 to 10: the 4 unrated books fall
# through the ELSE and are quietly reported as the worst books in the library.
check "without it, 'poor' swells to 10 as the 4 unrated books fall through" "10" \
  "$(q "SELECT COUNT(*) FROM (SELECT CASE WHEN rating>=4.0 THEN 'good' ELSE 'poor' END AS band FROM books) WHERE band='poor';")"
echo

echo "11. Every example query file runs against a fresh database"
for f in "${lab_dir}"/examples/queries/*.sql; do
  name="$(basename "${f}")"
  if err="$(sqlite3 "${db}" < "${f}" 2>&1 >/dev/null)" && [ -z "${err}" ]; then
    pass "examples/queries/${name} runs clean"
  else
    fail "examples/queries/${name} produced errors: ${err}"
  fi
done
echo

echo "12. The from-scratch GROUP BY agrees with the one-line SQL"
gb_out="$("${python_bin}" "${lab_dir}/examples/groupby_from_scratch.py" "${db}" 2>&1)"
gb_status=$?
if [ "${gb_status}" -eq 0 ]; then pass "groupby_from_scratch.py exits 0"
else fail "groupby_from_scratch.py exited ${gb_status}"; fi
if printf '%s' "${gb_out}" | grep -q 'IDENTICAL: 3 rows match exactly.'; then
  pass "the Python accumulators and the SQL agree on all 3 rows"
else
  fail "the Python and SQL results did not match: $(printf '%s' "${gb_out}" | tail -3)"
fi
check "the pipeline it prints: FROM 24 rows" "  FROM      -> 24 rows" \
  "$(printf '%s\n' "${gb_out}" | grep 'FROM ')"
check "WHERE keeps 20" "  WHERE     -> 20 rows survive" \
  "$(printf '%s\n' "${gb_out}" | grep 'WHERE ')"
check "GROUP BY makes 6 buckets" "  GROUP BY  -> 6 buckets" \
  "$(printf '%s\n' "${gb_out}" | grep 'GROUP BY ')"
check "HAVING leaves 3" "  HAVING    -> 3 buckets survive" \
  "$(printf '%s\n' "${gb_out}" | grep 'HAVING ')"
echo

echo "13. The exercises: the answer key is right and the starter is wrong"
answers="$(sqlite3 "${db}" < "${lab_dir}/examples/exercise-answers.sql" 2>&1)"
starter="$(sqlite3 "${db}" < "${lab_dir}/starter/exercises.sql" 2>&1)"
check "the answer key emits 12 labelled lines" "12" "$(printf '%s\n' "${answers}" | grep -c '^ex[0-9][0-9]|')"
check "the starter emits the same 12 labels"   "12" "$(printf '%s\n' "${starter}" | grep -c '^ex[0-9][0-9]|')"

expect_answer() {
  check "answer $1" "$2" "$(printf '%s\n' "${answers}" | grep "^$1|" | cut -d'|' -f2-)"
}
expect_answer ex01 "15"
expect_answer ex02 "10"
expect_answer ex03 "2"
expect_answer ex04 "4"
expect_answer ex05 "4.16"
expect_answer ex06 "4"
expect_answer ex07 "Ledger of Tides"
expect_answer ex08 "6"
expect_answer ex09 "Ada Fenwick"
expect_answer ex10 "3"
expect_answer ex11 "28.0"
expect_answer ex12 "4"

# Every starter answer must DIFFER from the model answer. If a starter query
# ever accidentally became right, the exercise would teach nothing.
disagreements=0
for label in ex01 ex02 ex03 ex04 ex05 ex06 ex07 ex08 ex09 ex10 ex11 ex12; do
  a="$(printf '%s\n' "${answers}" | grep "^${label}|" | cut -d'|' -f2-)"
  s="$(printf '%s\n' "${starter}" | grep "^${label}|" | cut -d'|' -f2-)"
  [ "${a}" != "${s}" ] && disagreements=$((disagreements + 1))
done
check "all 12 starter queries return a WRONG answer before you fix them" "12" "${disagreements}"
echo

echo "14. The lab stays offline, stays out of your way, and cleans up"
if grep -rInE 'https?://[a-zA-Z0-9]' "${lab_dir}/examples" "${lab_dir}/starter" "${lab_dir}/tests" >/dev/null 2>&1; then
  fail "something under examples/, starter/ or tests/ names a URL"
else
  pass "no URL anywhere in examples/, starter/ or tests/"
fi
if grep -rIn 'sudo' "${lab_dir}/examples" "${lab_dir}/starter" >/dev/null 2>&1; then
  fail "an example or starter file calls sudo"
else
  pass "nothing under examples/ or starter/ calls sudo"
fi
if [ -e "${lab_dir}/library.db" ]; then
  fail "a database was left in the lab root; it belongs under examples/"
else
  pass "no stray database in the lab root"
fi
if grep -q 'library.db' "${lab_dir}/.gitignore" 2>/dev/null; then
  pass "the built database is git-ignored, so it is never committed"
else
  fail ".gitignore does not exclude the built database"
fi
echo

echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ] || exit 1
exit 0
