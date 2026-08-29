#!/usr/bin/env bash
# Day 039 lab — "Store Data Four Ways" (completed reference implementation).
#
# Stores the SAME small dataset four ways and shows what each is good for:
#   1) FILE            — structured data as a CSV file you read back
#   2) DATABASE        — a SQLite database you QUERY (beats grepping a file)
#   3) OBJECT STORAGE  — a blob filed by a content-key (hash) in a bucket dir
#   4) CACHE           — a key->value file cache showing a HIT vs a recompute
#
# Offline, no network, no sudo. Requires: bash and sqlite3 (preinstalled on
# macOS and most Linux). Everything is created under a temporary work dir and
# cleaned up on exit.
set -euo pipefail

# --- Setup: a private scratch directory, removed automatically on exit -------
# The test harness may set STORAGE_DEMO_WORKDIR to a directory it wants to
# inspect afterward; in that case we use it and do NOT delete it. Normal runs
# get a fresh temp dir that is cleaned up on exit.
if [ -n "${STORAGE_DEMO_WORKDIR:-}" ]; then
  work="${STORAGE_DEMO_WORKDIR}"
  mkdir -p "${work}"
  trap - EXIT
else
  work="$(mktemp -d "${TMPDIR:-/tmp}/storage_demo.XXXXXX")"
  cleanup() { rm -rf "${work}"; }
  trap cleanup EXIT
fi

# Pick a SHA-256 tool that exists on both macOS and Linux.
if command -v shasum >/dev/null 2>&1; then
  sha256() { shasum -a 256 "$1" | awk '{print $1}'; }
elif command -v sha256sum >/dev/null 2>&1; then
  sha256() { sha256sum "$1" | awk '{print $1}'; }
else
  echo "Need shasum or sha256sum (both are standard on macOS/Linux)." >&2
  exit 1
fi

echo "=== Store Data Four Ways ==="
echo "Work dir: ${work}"
echo

# --- 1) FILE: structured data as CSV -----------------------------------------
# A file is the simplest store: named bytes on disk. Perfect for a small,
# single-writer dataset like this. We write it, then read it back.
echo "[1/4] FILE (structured CSV)"
orders_csv="${work}/orders.csv"
cat > "${orders_csv}" <<'CSV'
id,customer,state,amount
1,ada,OH,120.0
2,grace,OH,90.0
3,linus,CA,200.0
4,ada,OH,60.0
CSV
echo "  Wrote ${orders_csv}:"
sed 's/^/    /' "${orders_csv}"
echo "  -> A file holds the raw rows, but can only be read whole or grepped."
echo

# --- 2) DATABASE: SQLite you can QUERY ---------------------------------------
# The same data in a real relational database. We create a table, insert the
# rows, then run a SELECT with a WHERE and an aggregate (SUM ... GROUP BY) —
# a precise question a file could never answer without scanning everything.
echo "[2/4] DATABASE (SQLite)"
db="${work}/storage_demo.db"
sqlite3 "${db}" <<'SQL'
CREATE TABLE orders (
  id       INTEGER PRIMARY KEY,
  customer TEXT NOT NULL,
  state    TEXT NOT NULL,
  amount   REAL NOT NULL
);
INSERT INTO orders (customer, state, amount) VALUES
  ('ada',   'OH', 120.0),
  ('grace', 'OH',  90.0),
  ('linus', 'CA', 200.0),
  ('ada',   'OH',  60.0);
CREATE INDEX idx_orders_state ON orders(state);
SQL
echo "  Created table 'orders' and inserted 4 rows (with an index on state)."
echo "  Query: total revenue per customer in state 'OH'"
sqlite3 "${db}" \
  "SELECT customer, SUM(amount) AS total
     FROM orders
    WHERE state = 'OH'
    GROUP BY customer
    ORDER BY customer;" | sed 's/^/  /'
echo "  -> A SQL query answered a precise question that a file could only grep."
echo

# --- 3) OBJECT STORAGE: a blob filed by content-key --------------------------
# Object storage keeps whole blobs in a flat "bucket", each under a key. Here
# the key is the blob's own SHA-256 hash (content-addressed): identical bytes
# always get the same key, and you fetch the blob back by that key.
echo "[3/4] OBJECT STORAGE (bucket + content key)"
bucket="${work}/bucket"
mkdir -p "${bucket}"
blob_src="${work}/report.txt"
printf 'quarterly report: revenue up, storage bill down\n' > "${blob_src}"
key="$(sha256 "${blob_src}")"
cp "${blob_src}" "${bucket}/${key}"
echo "  PUT object under key: ${key}"
echo "  GET object back by key:"
cat "${bucket}/${key}" | sed 's/^/    /'
echo "  -> The bucket is flat; the key names the blob; we fetch it whole."
echo

# --- 4) CACHE: key -> value with a HIT vs recompute --------------------------
# A cache is a fast, disposable copy in front of slow work. compute() pretends
# to be expensive. The cache stores results by key; a second call for the same
# key is served from the cache (a HIT) instead of recomputing.
echo "[4/4] CACHE (key -> value with timestamp)"
cache_dir="${work}/cache"
mkdir -p "${cache_dir}"

expensive_total_for_state() {
  # Pretend this is slow (e.g. a big scan). It queries the DB for a state total.
  sqlite3 "${db}" "SELECT COALESCE(SUM(amount),0) FROM orders WHERE state='$1';"
}

cached_total_for_state() {
  local state="$1"
  local cache_file="${cache_dir}/total_${state}"
  if [ -f "${cache_file}" ]; then
    echo "HIT  -> served from cache (no recompute): $(cat "${cache_file}")"
  else
    local value; value="$(expensive_total_for_state "${state}")"
    printf '%s' "${value}" > "${cache_file}"
    echo "MISS -> computed and stored: ${value} (at $(date '+%H:%M:%S'))"
  fi
}

echo "  First call:  $(cached_total_for_state OH)"
echo "  Second call: $(cached_total_for_state OH)"
echo "  -> The second call skipped the work. Delete the cache and nothing is"
echo "     lost — the real data still lives in the file, database, and bucket."
echo

echo "=== Done. Each store fit a different job. Scratch dir will be cleaned up. ==="
