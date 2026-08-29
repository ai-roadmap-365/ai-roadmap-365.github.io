#!/usr/bin/env bash
# Day 091 — how far through the sixteen exercises are you?
#
#   bash starter/03_check.sh
#
# Builds YOUR schema (starter/01_schema.sql) in a temporary directory, loads
# the shared seed into it, runs YOUR queries (starter/02_questions.sql) and the
# reference queries (examples/06_answers.sql) against the same data, and
# compares the ten answer blocks.
#
# It reports "N of 16 exercises complete." and exits 0 only when N is 16.
# Nothing is written inside the lab directory, and the temporary directory is
# removed on the way out, whether the run succeeded or not.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work=""
done_count=0
total=16

cleanup() { [ -n "${work}" ] && [ -d "${work}" ] && rm -rf "${work}"; }
trap cleanup EXIT INT TERM

sqlite_bin="${SQLITE3:-$(command -v sqlite3 || true)}"
if [ -z "${sqlite_bin}" ] || [ ! -x "${sqlite_bin}" ]; then
  echo "sqlite3 was not found. Install it, or set SQLITE3=/path/to/sqlite3."
  exit 1
fi

work="$(mktemp -d)"
db="${work}/yours.db"
ref="${work}/reference.db"

pass() { echo "  done      ${1}"; done_count=$((done_count + 1)); }
todo() { echo "  still to do: ${1}"; }

# q SQL — one scalar from the learner's database, empty string on any error.
q() { "${sqlite_bin}" "${db}" ".mode list" ".headers off" "$1" 2>/dev/null; }

echo "Day 091 — from requirements to report"
echo

# ---------------------------------------------------------------------------
# Exercises 1-6: the schema.
# ---------------------------------------------------------------------------
echo "Schema (exercises 1-6)"
"${sqlite_bin}" "${db}" < "${lab_dir}/starter/01_schema.sql" 2>"${work}/schema.err"
if [ -s "${work}/schema.err" ]; then
  echo "  your schema did not build cleanly. sqlite3 said:"
  sed 's/^/      /' "${work}/schema.err"
  echo
fi

# 1. books, with the decisions the brief forces.
books_ok=no
if [ "$(q "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='books'")" = "1" ]; then
  cols="$(q "SELECT group_concat(name) FROM (SELECT name FROM pragma_table_info('books') ORDER BY cid)")"
  isbn_nullable="$(q "SELECT \"notnull\" FROM pragma_table_info('books') WHERE name='isbn13'")"
  fk_cat="$(q "SELECT count(*) FROM pragma_foreign_key_list('books') WHERE \"table\"='categories'")"
  if [ "${cols}" = "book_id,isbn13,title,published_year,category_id,acquisition_cost_pence,withdrawn_at" ] \
     && [ "${isbn_nullable}" = "0" ] && [ "${fk_cat}" = "1" ]; then
    books_ok=yes
  fi
fi
if [ "${books_ok}" = "yes" ]; then
  pass "1. books — seven columns, a nullable isbn13, a foreign key to categories"
else
  todo "1. books — see the column list in starter/01_schema.sql. isbn13 must be"
  echo "               nullable, because the 1818 book in the seed has no ISBN."
fi

# 2. book_authors — the many-to-many. This is the check that fails if the
#    relationship is modelled wrongly.
ba_ok=no
ba_note="not created yet"
if [ "$(q "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='book_authors'")" = "1" ]; then
  ba_pk="$(q "SELECT group_concat(name) FROM (SELECT name FROM pragma_table_info('book_authors') WHERE pk > 0 ORDER BY pk)")"
  ba_pos="$(q "SELECT count(*) FROM pragma_table_info('book_authors') WHERE name='author_position'")"
  ba_fks="$(q "SELECT group_concat(t) FROM (SELECT \"table\" AS t FROM pragma_foreign_key_list('book_authors') ORDER BY t)")"
  if [ "${ba_pk}" != "book_id,author_id" ]; then
    ba_note="the primary key must be the PAIR (book_id, author_id) — yours is '${ba_pk}'"
  elif [ "${ba_pos}" != "1" ]; then
    ba_note="add author_position: the credit order is an attribute of the relationship"
  elif [ "${ba_fks}" != "authors,books" ]; then
    ba_note="it needs a foreign key to books AND one to authors"
  else
    ba_ok=yes
  fi
fi
if [ "${ba_ok}" = "yes" ]; then
  pass "2. book_authors — keyed on the pair, with author_position"
else
  todo "2. book_authors — ${ba_note}"
fi

# 3. loans, including the two ordering CHECKs the ISO 8601 format makes possible.
loans_ok=no
if [ "$(q "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='loans'")" = "1" ]; then
  cols="$(q "SELECT group_concat(name) FROM (SELECT name FROM pragma_table_info('loans') ORDER BY cid)")"
  ret_nullable="$(q "SELECT \"notnull\" FROM pragma_table_info('loans') WHERE name='returned_at'")"
  ddl="$(q "SELECT sql FROM sqlite_master WHERE name='loans'")"
  if [ "${cols}" = "loan_id,book_id,member_id,borrowed_at,due_at,returned_at,fine_pence" ] \
     && [ "${ret_nullable}" = "0" ] \
     && printf '%s' "${ddl}" | grep -q "due_at > borrowed_at"; then
    loans_ok=yes
  fi
fi
if [ "${loans_ok}" = "yes" ]; then
  pass "3. loans — returned_at nullable, and CHECK (due_at > borrowed_at)"
else
  todo "3. loans — seven columns, returned_at nullable meaning 'still out', and a"
  echo "               table CHECK that due_at is later than borrowed_at."
fi

# 4. reservations — and specifically the ABSENCE of a stored queue position.
res_ok=no
res_note="not created yet"
if [ "$(q "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='reservations'")" = "1" ]; then
  cols="$(q "SELECT group_concat(name) FROM (SELECT name FROM pragma_table_info('reservations') ORDER BY cid)")"
  ddl="$(q "SELECT sql FROM sqlite_master WHERE name='reservations'")"
  if printf '%s' "${cols}" | grep -q "position"; then
    res_note="remove the stored queue position — run examples/04_rejected_design.sql"
  elif [ "${cols}" != "reservation_id,book_id,member_id,reserved_at,status" ]; then
    res_note="columns must be reservation_id, book_id, member_id, reserved_at, status"
  elif ! printf '%s' "${ddl}" | grep -q "waiting"; then
    res_note="status needs a CHECK constraining it to the four documented values"
  else
    res_ok=yes
  fi
fi
if [ "${res_ok}" = "yes" ]; then
  pass "4. reservations — status checked, and no stored queue position"
else
  todo "4. reservations — ${res_note}"
fi

# 5. indexes: one per foreign key, plus the two partial ones.
idx_count="$(q "SELECT count(*) FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")"
partial_plain="$(q "SELECT count(*) FROM sqlite_master WHERE type='index' AND sql LIKE '%returned_at IS NULL%'")"
partial_unique="$(q "SELECT count(*) FROM sqlite_master WHERE type='index' AND sql LIKE '%UNIQUE%' AND sql LIKE '%waiting%'")"
if [ "${idx_count:-0}" -ge 9 ] && [ "${partial_plain}" = "1" ] && [ "${partial_unique}" = "1" ]; then
  pass "5. indexes — every foreign key covered, plus both partial indexes"
else
  todo "5. indexes — ${idx_count:-0} of the 9 expected explicit indexes exist"
  echo "               (a foreign key creates none of its own), and you still need"
  echo "               the partial index on outstanding loans and the partial"
  echo "               UNIQUE index on waiting reservations."
fi

# 6. the two views.
views="$(q "SELECT group_concat(name) FROM (SELECT name FROM sqlite_master WHERE type='view' ORDER BY name)")"
if [ "${views}" = "current_collection,current_members" ]; then
  pass "6. views — current_collection and current_members"
else
  todo "6. views — create current_collection and current_members"
fi

# ---------------------------------------------------------------------------
# Exercises 7-16: the ten questions.
# ---------------------------------------------------------------------------
echo
echo "Questions (exercises 7-16)"

"${sqlite_bin}" "${db}" < "${lab_dir}/examples/02_seed.sql" 2>"${work}/seed.err"
if [ -s "${work}/seed.err" ]; then
  echo "  the shared seed will not load into your schema yet, so the ten answers"
  echo "  cannot be checked. sqlite3 said:"
  sed 's/^/      /' "${work}/seed.err"
else
  # The reference database is built from the reference schema, so a mistake in
  # your schema can never quietly change what the right answer is.
  "${sqlite_bin}" "${ref}" < "${lab_dir}/examples/01_schema.sql" 2>/dev/null
  "${sqlite_bin}" "${ref}" < "${lab_dir}/examples/02_seed.sql"   2>/dev/null

  "${sqlite_bin}" "${db}"  < "${lab_dir}/starter/02_questions.sql" > "${work}/yours.txt"  2>&1
  "${sqlite_bin}" "${ref}" < "${lab_dir}/examples/06_answers.sql"  > "${work}/theirs.txt" 2>&1

  # block N FILE — everything between the '### N' marker and the next marker.
  block() {
    awk -v want="### $1" '
      $0 == want          { grab = 1; next }
      /^### /             { grab = 0 }
      grab                { print }
    ' "$2"
  }

  for n in 1 2 3 4 5 6 7 8 9 10; do
    exercise=$((n + 6))
    if [ "$(block "${n}" "${work}/yours.txt")" = "$(block "${n}" "${work}/theirs.txt")" ]; then
      pass "${exercise}. question ${n}"
    else
      todo "${exercise}. question ${n} — your answer does not match the reference yet"
    fi
  done
fi

echo
echo "${done_count} of ${total} exercises complete."
[ "${done_count}" -eq "${total}" ]
