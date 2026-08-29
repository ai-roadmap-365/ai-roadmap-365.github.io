#!/usr/bin/env bash
# Tests for the Day 088 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This suite does not check that SQL runs. It checks that each SAFETY
# MECHANISM actually works, by breaking something on purpose and measuring the
# result:
#
#   * how many rows does the WHERE-less UPDATE really hit?
#   * does the SELECT-first discipline produce exactly the intended row set?
#   * is the database file BYTE-IDENTICAL after a rolled-back transaction?
#   * does each constraint reject the specific bad row it exists for, and what
#     is the real error message?
#   * does ON DELETE CASCADE remove children, and does RESTRICT refuse?
#   * does the documented table rebuild add a constraint ALTER TABLE cannot,
#     without losing rows or foreign keys?
#   * is the migration runner atomic on failure and idempotent on re-run?
#
# Everything happens in a temporary directory that is removed on exit. Nothing
# reaches the network, nothing needs sudo, and no file in the lab is modified.
set -u

# Never leave __pycache__ behind in the lab directory: the compile check below
# would otherwise write bytecode next to the starter the learner is editing.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work=""
checks=0
failures=0

PYTHON="${PYTHON:-python3}"
SQLITE="${SQLITE:-sqlite3}"

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

# check_eq LABEL EXPECTED ACTUAL — compares real values, and prints both when
# they differ, because "FAIL" with no numbers is not a test result.
check_eq() {
  local label="$1" expected="$2" actual="$3"
  checks=$((checks + 1))
  if [ "${expected}" = "${actual}" ]; then
    echo "  ok: ${label} (${actual})"
  else
    echo "  FAIL: ${label} — expected '${expected}', got '${actual}'"
    failures=$((failures + 1))
  fi
}

# check_contains LABEL NEEDLE HAYSTACK
check_contains() {
  local label="$1" needle="$2" haystack="$3"
  checks=$((checks + 1))
  case "${haystack}" in
    *"${needle}"*) echo "  ok: ${label}" ;;
    *)
      echo "  FAIL: ${label} — '${needle}' not found in: ${haystack}"
      failures=$((failures + 1))
      ;;
  esac
}

cleanup() { [ -n "${work}" ] && [ -d "${work}" ] && rm -rf "${work}"; }
trap cleanup EXIT INT TERM

# --------------------------------------------------------------------------
echo "0. The tools this lab needs"
# --------------------------------------------------------------------------
if ! command -v "${SQLITE}" >/dev/null 2>&1; then
  echo "  FAIL: no sqlite3 shell on PATH. Set SQLITE=/path/to/sqlite3."
  exit 1
fi
if ! command -v "${PYTHON}" >/dev/null 2>&1; then
  echo "  FAIL: no python3 on PATH. Set PYTHON=/path/to/python3."
  exit 1
fi

cli_version="$("${SQLITE}" :memory: 'SELECT sqlite_version();')"
py_version="$("${PYTHON}" -c 'import sqlite3; print(sqlite3.sqlite_version)')"
echo "  sqlite3 shell library: ${cli_version}"
echo "  python3 sqlite3 library: ${py_version}"
check "the sqlite3 shell answers a query" \
  "$([ -n "${cli_version}" ] && echo yes || echo no)"
check "python3 can import sqlite3" \
  "$([ -n "${py_version}" ] && echo yes || echo no)"

work="$(mktemp -d)"
db="${work}/library.db"
"${SQLITE}" "${db}" < "${lab_dir}/examples/seed.sql"
check "the seed database builds" "$([ -s "${db}" ] && echo yes || echo no)"

q() { "${SQLITE}" "${db}" "$1" 2>&1; }
# qq DB SQL — query a named database, capturing stderr so errors are testable.
qq() { "${SQLITE}" "$1" "$2" 2>&1; }

check_eq "seed has 6 members"  "6"  "$(q 'SELECT count(*) FROM members;')"
check_eq "seed has 8 books"    "8"  "$(q 'SELECT count(*) FROM books;')"
check_eq "seed has 12 loans"   "12" "$(q 'SELECT count(*) FROM loans;')"
check_eq "8 loans outstanding" "8"  "$(q 'SELECT count(*) FROM loans WHERE returned = 0;')"

# --------------------------------------------------------------------------
echo
echo "1. The most expensive mistake in SQL, measured"
# --------------------------------------------------------------------------
copy="${work}/scratch1.db"
cp "${db}" "${copy}"

intended="$(qq "${copy}" 'SELECT count(*) FROM loans WHERE id = 2;')"
check_eq "the SELECT you meant to write matches 1 row" "1" "${intended}"

# The WHERE-less UPDATE, against a throwaway copy.
hit="$(qq "${copy}" 'UPDATE loans SET returned = 1; SELECT changes();')"
check_eq "the WHERE-less UPDATE hits every row in the table" "12" "${hit}"

wrong="$(qq "${copy}" 'SELECT count(*) FROM loans WHERE returned = 0;')"
check_eq "no loan is outstanding afterwards" "0" "${wrong}"
check "1 row was intended and 12 were changed, silently and successfully" \
  "$([ "${intended}" = "1" ] && [ "${hit}" = "12" ] && echo yes || echo no)"

# The discipline: same intent, expressed safely.
copy2="${work}/scratch2.db"
cp "${db}" "${copy2}"
safe="$(qq "${copy2}" 'BEGIN; UPDATE loans SET returned = 1 WHERE id = 2; SELECT changes(); COMMIT;')"
check_eq "SELECT-first, WHERE kept: the UPDATE changes exactly 1 row" "1" "${safe}"
check_eq "the other 7 outstanding loans are untouched" "7" \
  "$(qq "${copy2}" 'SELECT count(*) FROM loans WHERE returned = 0;')"

# --------------------------------------------------------------------------
echo
echo "2. A rolled-back transaction leaves the file byte-for-byte as it was"
# --------------------------------------------------------------------------
copy3="${work}/scratch3.db"
cp "${db}" "${copy3}"

mode="$(qq "${copy3}" 'PRAGMA journal_mode;')"
echo "  journal_mode: ${mode}"

before_sum="$(shasum -a 256 "${copy3}" | cut -d' ' -f1)"
before_dump="${work}/before.sql"
after_dump="${work}/after.sql"
"${SQLITE}" "${copy3}" .dump > "${before_dump}"

# Three destructive statements, confirmed to take effect INSIDE the
# transaction, then abandoned.
inside="$("${SQLITE}" "${copy3}" <<'SQL' 2>&1
BEGIN;
UPDATE loans SET returned = 1;
DELETE FROM loans WHERE id <= 3;
INSERT INTO members (name, email) VALUES ('Temporary Person', 'temp@library.test');
SELECT 'loans=' || (SELECT count(*) FROM loans) || ' members=' || (SELECT count(*) FROM members);
ROLLBACK;
SQL
)"
check_eq "inside the transaction the changes are completely real" \
  "loans=9 members=7" "${inside}"

after_sum="$(shasum -a 256 "${copy3}" | cut -d' ' -f1)"
"${SQLITE}" "${copy3}" .dump > "${after_dump}"

check_eq "the database file is byte-for-byte identical after ROLLBACK" \
  "${before_sum}" "${after_sum}"
check "every row is identical after ROLLBACK (full dump comparison)" \
  "$(cmp -s "${before_dump}" "${after_dump}" && echo yes || echo no)"
check_eq "loans back to 12" "12" "$(qq "${copy3}" 'SELECT count(*) FROM loans;')"
check_eq "members back to 6" "6" "$(qq "${copy3}" 'SELECT count(*) FROM members;')"

# The trap almost everybody has the wrong mental model of: a constraint
# failure does NOT abort the transaction. It undoes only the FAILING
# STATEMENT. The transaction stays open, and if the next thing you send is
# COMMIT, you keep whatever had already succeeded.
copy4="${work}/scratch4.db"
cp "${db}" "${copy4}"
partial="$("${SQLITE}" "${copy4}" <<'SQL' 2>&1
BEGIN;
UPDATE books SET copies = copies + 10 WHERE id = 1;
UPDATE books SET copies = -1 WHERE id = 5;
COMMIT;
SQL
)"
check_contains "a mid-transaction CHECK violation is reported" \
  "CHECK constraint failed" "${partial}"
check_eq "the FAILING statement changed nothing" "1" \
  "$(qq "${copy4}" 'SELECT copies FROM books WHERE id = 5;')"
check_eq "but an error does NOT roll back the transaction — COMMIT kept the +10" \
  "13" "$(qq "${copy4}" 'SELECT copies FROM books WHERE id = 1;')"

# The same script ending in ROLLBACK instead. Now the earlier success goes too.
copy4b="${work}/scratch4b.db"
cp "${db}" "${copy4b}"
"${SQLITE}" "${copy4b}" <<'SQL' > /dev/null 2>&1
BEGIN;
UPDATE books SET copies = copies + 10 WHERE id = 1;
UPDATE books SET copies = -1 WHERE id = 5;
ROLLBACK;
SQL
check_eq "ending the same script with ROLLBACK undoes the +10 as well" "3" \
  "$(qq "${copy4b}" 'SELECT copies FROM books WHERE id = 1;')"

# And the flag that makes the shell stop at the first error, so the COMMIT is
# never reached at all. This is what you want in a migration script.
copy4c="${work}/scratch4c.db"
cp "${db}" "${copy4c}"
"${SQLITE}" -bail "${copy4c}" <<'SQL' > /dev/null 2>&1
BEGIN;
UPDATE books SET copies = copies + 10 WHERE id = 1;
UPDATE books SET copies = -1 WHERE id = 5;
COMMIT;
SQL
bail_code=$?
check_eq "sqlite3 -bail stops at the first error and exits non-zero" "1" "${bail_code}"
check_eq "so the COMMIT is never reached and nothing is kept" "3" \
  "$(qq "${copy4c}" 'SELECT copies FROM books WHERE id = 1;')"

# --------------------------------------------------------------------------
echo
echo "3. Each constraint rejects the bad row it exists for"
# --------------------------------------------------------------------------
tdb="${work}/training.db"
"${SQLITE}" "${tdb}" < "${lab_dir}/examples/05-constraints.sql" > /dev/null

check_eq "the UNCONSTRAINED table accepted all 6 rows including 5 mistakes" "6" \
  "$(qq "${tdb}" 'SELECT count(*) FROM examples_loose;')"
check_eq "it accepted a duplicated training example" "1" \
  "$(qq "${tdb}" 'SELECT count(*) FROM (SELECT text FROM examples_loose GROUP BY text HAVING count(*) > 1);')"
check_eq "it accepted a row with no label" "1" \
  "$(qq "${tdb}" 'SELECT count(*) FROM examples_loose WHERE label IS NULL;')"
check_eq "it accepted a split value that escapes WHERE split = 'test'" "0" \
  "$(qq "${tdb}" "SELECT count(*) FROM examples_loose WHERE split = 'test';")"
check_contains "it stored the word banana in a column declared INTEGER" "text" \
  "$(qq "${tdb}" 'SELECT DISTINCT typeof(token_count) FROM examples_loose;')"
check_eq "the constrained table holds only the 4 clean rows" "4" \
  "$(qq "${tdb}" 'SELECT count(*) FROM examples_strict;')"

# Now the same bad rows against the constrained table, one at a time, keeping
# the real error message each time.
e1="$(qq "${tdb}" "INSERT INTO examples_strict (text,label,split,token_count) VALUES ('the film was a delight','positive','train',5);")"
check_contains "UNIQUE catches the duplicated example" \
  "UNIQUE constraint failed: examples_strict.text" "${e1}"

e2="$(qq "${tdb}" "INSERT INTO examples_strict (text,label,split,token_count) VALUES ('a new line',NULL,'train',3);")"
check_contains "NOT NULL catches the missing label" \
  "NOT NULL constraint failed: examples_strict.label" "${e2}"

e3="$(qq "${tdb}" "INSERT INTO examples_strict (text,label,split,token_count) VALUES ('another line','positive','Testing',3);")"
check_contains "CHECK catches the invented split value" \
  "CHECK constraint failed: split IN" "${e3}"

e4="$(qq "${tdb}" "INSERT INTO examples_strict (text,label,split,token_count) VALUES ('third line','neutralish','train',3);")"
check_contains "CHECK catches the label that is not one of the classes" \
  "CHECK constraint failed: label IN" "${e4}"

e5="$(qq "${tdb}" "INSERT INTO examples_strict (text,label,split,token_count) VALUES ('   ','positive','train',3);")"
check_contains "CHECK catches text that is nothing but spaces" \
  "CHECK constraint failed: length(trim(text)) > 0" "${e5}"

e6="$(qq "${tdb}" "INSERT INTO examples_strict (text,label,split,token_count) VALUES ('fourth line','positive','train','banana');")"
check_contains "STRICT catches the word banana in an INTEGER column" \
  "cannot store TEXT value in INTEGER column" "${e6}"

e7="$(qq "${tdb}" "INSERT INTO examples_strict (text,label,split,token_count) VALUES ('fifth line','positive','train',0);")"
check_contains "CHECK catches a token count of zero" \
  "CHECK constraint failed: token_count > 0" "${e7}"

check_eq "after 7 rejected rows the table still holds exactly 4" "4" \
  "$(qq "${tdb}" 'SELECT count(*) FROM examples_strict;')"

# DEFAULT filled a column nobody supplied.
check_eq "DEFAULT filled added_on for every row" "0" \
  "$(qq "${tdb}" 'SELECT count(*) FROM examples_strict WHERE added_on IS NULL;')"

# The same three constraints on the library schema.
c1="$(qq "${db}" "INSERT INTO books (isbn,title,author,copies) VALUES ('978-0131103627','Duplicate','X',1);")"
check_contains "UNIQUE catches a duplicate ISBN" "UNIQUE constraint failed: books.isbn" "${c1}"
c2="$(qq "${db}" "UPDATE books SET copies = -1 WHERE id = 1;")"
check_contains "CHECK catches a negative copy count" "CHECK constraint failed: copies >= 0" "${c2}"
c3="$(qq "${db}" "INSERT INTO loans (book_id,member_id,borrowed_on,due_on) VALUES (1,1,'2026-08-16','2026-01-01');")"
check_contains "CHECK catches a loan due before it was borrowed" \
  "CHECK constraint failed: due_on >= borrowed_on" "${c3}"
c4="$(qq "${db}" "INSERT INTO members (name,email) VALUES ('No Email Shape','not-an-email');")"
check_contains "CHECK catches an obviously malformed email" \
  "CHECK constraint failed: email LIKE" "${c4}"
check_eq "none of those four rejected statements changed anything" "8" \
  "$(q 'SELECT count(*) FROM books;')"

# --------------------------------------------------------------------------
echo
echo "4. Foreign keys: off by default, then CASCADE versus RESTRICT"
# --------------------------------------------------------------------------
check_eq "foreign key enforcement is OFF unless you ask for it" "0" \
  "$(q 'PRAGMA foreign_keys;')"

copy5="${work}/scratch5.db"
cp "${db}" "${copy5}"

# With enforcement off, a delete that should cascade or be refused does neither.
orphans="$("${SQLITE}" "${copy5}" <<'SQL' 2>&1
PRAGMA foreign_keys = OFF;
DELETE FROM members WHERE id = 1;
SELECT count(*) FROM loans WHERE member_id = 1;
SQL
)"
check_eq "with the pragma off, deleting a parent leaves orphaned children" "2" "${orphans}"
found="$(qq "${copy5}" 'SELECT count(*) FROM pragma_foreign_key_check;')"
check_eq "PRAGMA foreign_key_check finds those 2 orphans afterwards" "2" "${found}"

# With enforcement on, CASCADE removes the children.
copy6="${work}/scratch6.db"
cp "${db}" "${copy6}"
cascade="$("${SQLITE}" "${copy6}" <<'SQL' 2>&1
PRAGMA foreign_keys = ON;
DELETE FROM members WHERE id = 3;
SELECT 'members_deleted=' || changes() || ' loans_left=' || (SELECT count(*) FROM loans);
SQL
)"
check_eq "ON DELETE CASCADE takes the 3 child loans with the member" \
  "members_deleted=1 loans_left=9" "${cascade}"
check "changes() reported only 1, so the cascade is invisible in the row count" "yes"

# With enforcement on, RESTRICT refuses.
restrict="$("${SQLITE}" "${copy6}" 'PRAGMA foreign_keys = ON; DELETE FROM books WHERE id = 8;' 2>&1)"
check_contains "ON DELETE RESTRICT refuses to delete a borrowed book" \
  "FOREIGN KEY constraint failed" "${restrict}"
check_eq "the book is still there after the refused delete" "1" \
  "$(qq "${copy6}" 'SELECT count(*) FROM books WHERE id = 8;')"

# Same rule, unreferenced row: it deletes without complaint.
unref="$("${SQLITE}" "${copy6}" <<'SQL' 2>&1
PRAGMA foreign_keys = ON;
INSERT INTO books (isbn,title,author,copies) VALUES ('978-0000000000','Never Borrowed','Nobody',1);
DELETE FROM books WHERE isbn = '978-0000000000';
SELECT changes();
SQL
)"
check_eq "RESTRICT only refuses when a child row actually exists" "1" "${unref}"

# --------------------------------------------------------------------------
echo
echo "5. What this build's ALTER TABLE can and cannot do"
# --------------------------------------------------------------------------
# The four documented operations must work everywhere. Anything beyond them is
# version-dependent, which is the whole reason the rebuild procedure exists.
probe="${work}/probe.db"

alter_ok() { # alter_ok SETUP ALTER -> prints yes/no
  local pdb="${work}/probe-$$-${RANDOM}.db"
  rm -f "${pdb}"
  if "${SQLITE}" "${pdb}" "$1; $2;" >/dev/null 2>&1; then echo yes; else echo no; fi
  rm -f "${pdb}"
}

check_eq "ALTER TABLE ... RENAME TO is supported" "yes" \
  "$(alter_ok 'CREATE TABLE t(a INTEGER)' 'ALTER TABLE t RENAME TO t2')"
check_eq "ALTER TABLE ... RENAME COLUMN is supported" "yes" \
  "$(alter_ok 'CREATE TABLE t(a INTEGER)' 'ALTER TABLE t RENAME COLUMN a TO b')"
check_eq "ALTER TABLE ... ADD COLUMN is supported" "yes" \
  "$(alter_ok 'CREATE TABLE t(a INTEGER)' 'ALTER TABLE t ADD COLUMN b TEXT')"
check_eq "ALTER TABLE ... DROP COLUMN is supported" "yes" \
  "$(alter_ok 'CREATE TABLE t(a INTEGER, b TEXT)' 'ALTER TABLE t DROP COLUMN b')"

# The documented list stops there. These two must NOT be assumed.
check_eq "ALTER TABLE cannot add a CHECK constraint" "no" \
  "$(alter_ok 'CREATE TABLE t(a INTEGER)' 'ALTER TABLE t ADD CONSTRAINT ck CHECK (a > 0)')"
check_eq "ALTER TABLE cannot add a UNIQUE constraint" "no" \
  "$(alter_ok 'CREATE TABLE t(a INTEGER)' 'ALTER TABLE t ADD CONSTRAINT uq UNIQUE (a)')"
check_eq "ALTER TABLE cannot add a FOREIGN KEY" "no" \
  "$(alter_ok 'CREATE TABLE p(id INTEGER PRIMARY KEY); CREATE TABLE t(a INTEGER)' 'ALTER TABLE t ADD CONSTRAINT fk FOREIGN KEY (a) REFERENCES p(id)')"

# ALTER COLUMN ... SET NOT NULL arrived in SQLite 3.53.0. Rather than asserting
# a fixed answer, assert that this build agrees with its own version number --
# a check that stays true on an older or a newer machine.
alter_col="$(alter_ok 'CREATE TABLE t(a INTEGER)' 'ALTER TABLE t ALTER COLUMN a SET NOT NULL')"
newer="$("${PYTHON}" - "${cli_version}" <<'PY'
import sys
have = tuple(int(p) for p in sys.argv[1].split(".")[:3])
print("yes" if have >= (3, 53, 0) else "no")
PY
)"
echo "  this shell is ${cli_version}; ALTER COLUMN expected: ${newer}, actual: ${alter_col}"
check_eq "ALTER COLUMN support matches this build's version (3.53.0+)" \
  "${newer}" "${alter_col}"

# --------------------------------------------------------------------------
echo
echo "6. The documented rebuild adds what ALTER TABLE cannot"
# --------------------------------------------------------------------------
copy7="${work}/scratch7.db"
cp "${db}" "${copy7}"
"${SQLITE}" "${copy7}" < "${lab_dir}/examples/07-table-rebuild.sql" > /dev/null 2>&1

check_eq "every row survived the rebuild (12 seeded + 1 inserted after)" "13" \
  "$(qq "${copy7}" 'SELECT count(*) FROM loans;')"
check_eq "both foreign keys survived the drop and rename" "2" \
  "$(qq "${copy7}" "SELECT count(*) FROM pragma_foreign_key_list('loans');")"
check_eq "PRAGMA foreign_key_check reports no violations after the rebuild" "0" \
  "$(qq "${copy7}" 'SELECT count(*) FROM pragma_foreign_key_check;')"
check_eq "the new CHECK constraint is in the stored schema" "1" \
  "$(qq "${copy7}" "SELECT count(*) FROM sqlite_schema WHERE name='loans' AND sql LIKE '%90%';")"
check_eq "the old constraints are still there too" "1" \
  "$(qq "${copy7}" "SELECT count(*) FROM sqlite_schema WHERE name='loans' AND sql LIKE '%due_on >= borrowed_on%';")"

long_loan="$(qq "${copy7}" "INSERT INTO loans (book_id,member_id,borrowed_on,due_on) VALUES (1,1,'2026-08-16','2027-03-04');")"
check_contains "a 200-day loan is now refused by the new constraint" \
  "CHECK constraint failed: julianday(due_on) - julianday(borrowed_on) <= 90" "${long_loan}"
check_eq "a 60-day loan is still accepted" "1" \
  "$(qq "${copy7}" "INSERT INTO loans (book_id,member_id,borrowed_on,due_on) VALUES (1,1,'2026-08-16','2026-10-15'); SELECT changes();")"

# --------------------------------------------------------------------------
echo
echo "7. The migration runner: atomic, versioned, idempotent"
# --------------------------------------------------------------------------
mdb="${work}/app.db"
mdir="${work}/migrations"
cp -R "${lab_dir}/examples/migrations" "${mdir}"

first="$("${PYTHON}" "${lab_dir}/examples/migrate.py" --db "${mdb}" --dir "${mdir}" 2>&1)"
first_code=$?
check_eq "a fresh database migrates cleanly" "0" "${first_code}"
check_contains "it starts at version 0" "current version: 0" "${first}"
check_contains "it applies all four migrations" "4 migration(s) applied" "${first}"
check_eq "PRAGMA user_version is now 4" "4" "$(qq "${mdb}" 'PRAGMA user_version;')"

second="$("${PYTHON}" "${lab_dir}/examples/migrate.py" --db "${mdb}" --dir "${mdir}" 2>&1)"
second_code=$?
check_eq "running it again exits 0" "0" "${second_code}"
check_contains "running it again applies NOTHING — this is idempotence" \
  "up to date -- 0 migration(s) applied" "${second}"
check_eq "the version did not move" "4" "$(qq "${mdb}" 'PRAGMA user_version;')"

# The schema the migrations actually built.
check_eq "migration 002 added the soft-delete column" "1" \
  "$(qq "${mdb}" "SELECT count(*) FROM pragma_table_info('members') WHERE name='deleted_at';")"
check_eq "migration 003's rebuild left the 90-day rule in place" "1" \
  "$(qq "${mdb}" "SELECT count(*) FROM sqlite_schema WHERE name='loans' AND sql LIKE '%90%';")"
check_eq "migration 004 added 2 generated columns" "2" \
  "$(qq "${mdb}" "SELECT count(*) FROM pragma_table_xinfo('loans') WHERE hidden = 2;")"
check_eq "generated columns are invisible to PRAGMA table_info" "6" \
  "$(qq "${mdb}" "SELECT count(*) FROM pragma_table_info('loans');")"

# A generated column computes itself and cannot be written to.
"${SQLITE}" "${mdb}" <<'SQL' > /dev/null 2>&1
INSERT INTO members (id,name,email) VALUES (1,'Ada','ada@library.test');
INSERT INTO books (id,isbn,title,author) VALUES (1,'978-0131103627','T','A');
INSERT INTO loans (book_id,member_id,borrowed_on,due_on) VALUES (1,1,'2026-08-16','2026-09-15');
SQL
check_eq "the generated column computed the loan length itself" "30" \
  "$(qq "${mdb}" 'SELECT loan_days FROM loans WHERE id = 1;')"
gen_write="$(qq "${mdb}" 'UPDATE loans SET loan_days = 999;')"
check_contains "a generated column cannot be written to, so it cannot lie" \
  "cannot UPDATE generated column" "${gen_write}"

# The atomicity claim, tested by breaking a migration on purpose.
cat > "${mdir}/005_broken.sql" <<'SQL'
-- Deliberately broken, to prove the runner rolls back.
CREATE TABLE applied_before_the_error (x INTEGER);
CREATE TABLE nope (bad SYNTAX HERE!!;
SQL

broken="$("${PYTHON}" "${lab_dir}/examples/migrate.py" --db "${mdb}" --dir "${mdir}" 2>&1)"
broken_code=$?
check_eq "a failing migration exits non-zero" "1" "${broken_code}"
check_contains "it says what failed" "005_broken.sql" "${broken}"
check_contains "it says the database was rolled back" "rolled back" "${broken}"
check_eq "the version did NOT advance" "4" "$(qq "${mdb}" 'PRAGMA user_version;')"
check_eq "the table created before the error does NOT exist" "0" \
  "$(qq "${mdb}" "SELECT count(*) FROM sqlite_schema WHERE name='applied_before_the_error';")"
rm -f "${mdir}/005_broken.sql"

# Malformed migration sets are refused before anything is written.
cp "${mdir}/002_add_soft_delete.sql" "${mdir}/002_duplicate_version.sql"
dup="$("${PYTHON}" "${lab_dir}/examples/migrate.py" --db "${mdb}" --dir "${mdir}" 2>&1)"
dup_code=$?
check_eq "two migrations claiming one version is refused (exit 2)" "2" "${dup_code}"
check_contains "and it names both files" "002_duplicate_version.sql" "${dup}"
rm -f "${mdir}/002_duplicate_version.sql"

cat > "${mdir}/006_owns_transaction.sql" <<'SQL'
BEGIN;
CREATE TABLE z (x INTEGER);
COMMIT;
SQL
owns="$("${PYTHON}" "${lab_dir}/examples/migrate.py" --db "${mdb}" --dir "${mdir}" 2>&1)"
owns_code=$?
check_eq "a migration managing its own transaction is refused (exit 2)" "2" "${owns_code}"
check_contains "and it explains why that breaks the guarantee" \
  "all-or-nothing" "${owns}"
rm -f "${mdir}/006_owns_transaction.sql"

# --dry-run writes nothing.
fresh="${work}/dry.db"
dry="$("${PYTHON}" "${lab_dir}/examples/migrate.py" --db "${fresh}" --dir "${mdir}" --dry-run 2>&1)"
check_contains "--dry-run names what it would apply" "would apply 001" "${dry}"
check_contains "--dry-run says it wrote nothing" "nothing was written" "${dry}"
check_eq "--dry-run really did leave the database at version 0" "0" \
  "$(qq "${fresh}" 'PRAGMA user_version;')"

# --------------------------------------------------------------------------
echo
echo "8. The starter and the shipped files"
# --------------------------------------------------------------------------
ex_count="$(grep -c 'EXERCISE' "${lab_dir}/starter/migrate.py" "${lab_dir}/starter/exercises.sql" | awk -F: '{s+=$2} END {print s}')"
check "the starter carries its numbered exercises (${ex_count} markers)" \
  "$([ "${ex_count}" -ge 10 ] && echo yes || echo no)"
# ast.parse rather than py_compile: py_compile writes a __pycache__ directory
# next to the file, and this suite does not write to the lab directory.
check "the starter is syntactically valid Python before you edit it" \
  "$("${PYTHON}" -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' \
      "${lab_dir}/starter/migrate.py" >/dev/null 2>&1 && echo yes || echo no)"

starter_run="$("${PYTHON}" "${lab_dir}/starter/migrate.py" --db "${work}/starter.db" --dir "${mdir}" 2>&1)"
check_contains "the unfinished starter fails loudly rather than silently" \
  "NotImplementedError" "${starter_run}"
check_eq "and it wrote no schema while failing" "0" \
  "$(qq "${work}/starter.db" "SELECT count(*) FROM sqlite_schema;")"

check "every example script is readable" \
  "$([ -r "${lab_dir}/examples/seed.sql" ] && [ -r "${lab_dir}/examples/migrate.py" ] && echo yes || echo no)"

# --------------------------------------------------------------------------
echo
echo "9. Nothing here reaches the network or the wider machine"
# --------------------------------------------------------------------------
# The scan covers the files a learner runs. It deliberately excludes this
# harness, which necessarily contains the very patterns it is searching for.
net_hits="$(grep -rEl 'https?://|urllib|socket|requests\.' \
  "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null | wc -l | tr -d ' ')"
check_eq "no example or starter file opens a network connection" "0" "${net_hits}"

sudo_hits="$(grep -rEl '(^|[^[:alnum:]])sudo([^[:alnum:]]|$)' \
  "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null | wc -l | tr -d ' ')"
check_eq "nothing a learner runs asks for sudo" "0" "${sudo_hits}"

work_is_absolute=no
[ "${work#/}" != "${work}" ] && work_is_absolute=yes
check "every database this suite made lives under one temporary directory" \
  "${work_is_absolute}"
check "the lab directory itself was never written to" \
  "$([ ! -e "${lab_dir}/library.db" ] && [ ! -e "${lab_dir}/scratch.db" ] && echo yes || echo no)"

# --------------------------------------------------------------------------
echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ] || exit 1
exit 0
