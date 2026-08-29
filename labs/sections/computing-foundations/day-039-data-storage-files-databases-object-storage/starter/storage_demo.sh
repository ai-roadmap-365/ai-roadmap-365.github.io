#!/usr/bin/env bash
# Day 039 lab — "Store Data Four Ways" (YOUR working file).
#
# Complete the FOUR numbered exercises below. Each one names the exact command
# to use. The finished reference is in examples/storage_demo.sh — try to do it
# yourself first, then compare. Run this file with:  bash starter/storage_demo.sh
#
# Offline, no network, no sudo. Requires: bash and sqlite3.
set -euo pipefail

work="$(mktemp -d "${TMPDIR:-/tmp}/storage_demo.XXXXXX")"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

if command -v shasum >/dev/null 2>&1; then
  sha256() { shasum -a 256 "$1" | awk '{print $1}'; }
elif command -v sha256sum >/dev/null 2>&1; then
  sha256() { sha256sum "$1" | awk '{print $1}'; }
else
  echo "Need shasum or sha256sum." >&2; exit 1
fi

echo "=== Store Data Four Ways (starter) ==="
echo "Work dir: ${work}"
echo

# --- 1) FILE (given, already works) ------------------------------------------
echo "[1/4] FILE (structured CSV)"
orders_csv="${work}/orders.csv"
cat > "${orders_csv}" <<'CSV'
id,customer,state,amount
1,ada,OH,120.0
2,grace,OH,90.0
3,linus,CA,200.0
4,ada,OH,60.0
CSV
echo "  Wrote ${orders_csv}"
echo

# --- 2) DATABASE -------------------------------------------------------------
echo "[2/4] DATABASE (SQLite)"
db="${work}/storage_demo.db"

# Exercise 1: CREATE the 'orders' table and INSERT the four rows.
# Use sqlite3 with a heredoc. Columns: id INTEGER PRIMARY KEY, customer TEXT,
# state TEXT, amount REAL. Insert the same four rows as the CSV above.
# Replace the line below with your sqlite3 command.
#   sqlite3 "${db}" <<'SQL'  ... SQL
echo "  (exercise 1: create table + insert rows)"

# Exercise 2: run a SELECT with a WHERE and an aggregate. Print total revenue
# per customer in state 'OH', grouped by customer, ordered by customer:
#   sqlite3 "${db}" "SELECT customer, SUM(amount) AS total FROM orders
#                    WHERE state='OH' GROUP BY customer ORDER BY customer;"
echo "  Query result (exercise 2):"
echo "  (exercise 2: run the SELECT here)"
echo

# --- 3) OBJECT STORAGE -------------------------------------------------------
echo "[3/4] OBJECT STORAGE (bucket + content key)"
bucket="${work}/bucket"; mkdir -p "${bucket}"
blob_src="${work}/report.txt"
printf 'quarterly report: revenue up, storage bill down\n' > "${blob_src}"

# Exercise 3: store the blob under a content key (its SHA-256 hash), then fetch
# it back by key. Compute the key with:  key="$(sha256 "${blob_src}")"
# Then copy the blob into the bucket:     cp "${blob_src}" "${bucket}/${key}"
# Then read it back:                      cat "${bucket}/${key}"
echo "  (exercise 3: put blob by key, then get it back)"
echo

# --- 4) CACHE ----------------------------------------------------------------
echo "[4/4] CACHE (key -> value)"
cache_dir="${work}/cache"; mkdir -p "${cache_dir}"

expensive_total_for_state() {
  sqlite3 "${db}" "SELECT COALESCE(SUM(amount),0) FROM orders WHERE state='$1';"
}

cached_total_for_state() {
  local state="$1"
  local cache_file="${cache_dir}/total_${state}"
  # Exercise 4: implement the cache. If "${cache_file}" exists, print
  #   "HIT  -> $(cat "${cache_file}")"
  # otherwise compute value="$(expensive_total_for_state "${state}")", save it
  # to "${cache_file}", and print "MISS -> ${value}".
  echo "MISS -> (exercise 4: implement HIT/MISS)"
}

echo "  First call:  $(cached_total_for_state OH)"
echo "  Second call: $(cached_total_for_state OH)"
echo

echo "=== Done. Compare with examples/storage_demo.sh. ==="
