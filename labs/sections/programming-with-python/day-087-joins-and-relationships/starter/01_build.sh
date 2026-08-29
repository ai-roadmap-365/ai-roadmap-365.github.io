#!/usr/bin/env bash
# Day 087 starter — build a fresh library.db for your own work.
#
# This script is complete and working. Run it first, and run it again whenever
# you want to start over; it drops and recreates everything.
#
#   bash starter/01_build.sh
#
# It writes starter/library.db, which is yours to break. Nothing else in the
# lab reads it.
set -eu

starter_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(cd "${starter_dir}/.." && pwd)"
database="${starter_dir}/library.db"

rm -f "${database}"
sqlite3 "${database}" < "${lab_dir}/examples/02_schema.sql"
sqlite3 "${database}" < "${lab_dir}/examples/03_seed.sql"

echo "built ${database#"${lab_dir}/"}"
sqlite3 "${database}" <<'SQL'
.mode list
.headers off
SELECT 'authors      ' || count(*) FROM authors;
SELECT 'books        ' || count(*) FROM books;
SELECT 'book_authors ' || count(*) FROM book_authors;
SELECT 'members      ' || count(*) FROM members;
SELECT 'loans        ' || count(*) FROM loans;
SQL
