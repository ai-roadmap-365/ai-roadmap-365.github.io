#!/usr/bin/env bash
# Rebuild library.db from examples/seed.sql.
#
# Run from the lab directory:
#   bash examples/build_db.sh
#
# The build is destructive on purpose: it deletes the existing library.db and
# recreates it, so every exercise in this lab starts from the same rows no
# matter what you did to the database in between. That is the whole reason the
# seed is a file and not something you typed once.
set -eu

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
db="${1:-${lab_dir}/examples/library.db}"

rm -f "${db}"
sqlite3 "${db}" < "${lab_dir}/examples/seed.sql"
echo "built: ${db}"
