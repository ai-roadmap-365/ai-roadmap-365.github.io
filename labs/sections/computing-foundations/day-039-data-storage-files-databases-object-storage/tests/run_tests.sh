#!/usr/bin/env bash
# Tests for the Day 039 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Drives the completed reference demo into an inspectable work directory and
# checks real behavior of all four stores:
#   - the SQLite database file is created
#   - the SELECT ... WHERE ... GROUP BY returns the expected OH rows
#   - the object blob is retrievable from the bucket by its content key
#   - the cache returns a HIT on the second call for the same key
# No network. Exits 0 on success, non-zero on any failure.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
demo="${lab_dir}/examples/storage_demo.sh"
failures=0
checks=0

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

# Pre-flight: sqlite3 must exist (the lab's whole point).
if command -v sqlite3 >/dev/null 2>&1; then
  check "sqlite3 is installed" "yes"
else
  check "sqlite3 is installed" "no"
  echo
  echo "${checks} checks, ${failures} failure(s)."
  echo "Install sqlite3 first (macOS: preinstalled; Debian/Ubuntu: apt install sqlite3)."
  exit 1
fi

# Run the reference demo into a known, inspectable work dir (no network).
work="$(mktemp -d "${TMPDIR:-/tmp}/storage_demo_test.XXXXXX")"
trap 'rm -rf "${work}"' EXIT
output="$(STORAGE_DEMO_WORKDIR="${work}" bash "${demo}" 2>&1)"
rc=$?
check "demo script exits successfully" "$([ ${rc} -eq 0 ] && echo yes || echo no)"

# 1) DATABASE: file created and the query returns the expected aggregated rows.
check "SQLite database file was created" "$([ -f "${work}/storage_demo.db" ] && echo yes || echo no)"

query_out="$(sqlite3 "${work}/storage_demo.db" \
  "SELECT customer, SUM(amount) FROM orders WHERE state='OH' GROUP BY customer ORDER BY customer;" 2>/dev/null)"
expected_query="ada|180.0
grace|90.0"
check "query returns expected OH rows (ada|180.0, grace|90.0)" \
  "$([ "${query_out}" = "${expected_query}" ] && echo yes || echo no)"

# 2) OBJECT STORAGE: the blob is retrievable from the bucket by its key, and
#    re-hashing the retrieved bytes reproduces that same key (content-addressed).
if command -v shasum >/dev/null 2>&1; then
  hasher() { shasum -a 256 "$1" | awk '{print $1}'; }
else
  hasher() { sha256sum "$1" | awk '{print $1}'; }
fi
stored_key="$(ls "${work}/bucket" 2>/dev/null | head -1)"
if [ -n "${stored_key}" ] && [ -f "${work}/bucket/${stored_key}" ]; then
  rehash="$(hasher "${work}/bucket/${stored_key}")"
  check "blob is retrievable by key and key matches its content hash" \
    "$([ "${rehash}" = "${stored_key}" ] && echo yes || echo no)"
else
  check "blob is retrievable by key and key matches its content hash" "no"
fi

# 3) CACHE: the printed output shows a MISS then a HIT for the same key.
echo "${output}" | grep -q "First call:  MISS" && miss=yes || miss=no
echo "${output}" | grep -q "Second call: HIT"  && hit=yes  || hit=no
check "cache prints MISS on the first call" "${miss}"
check "cache prints HIT on the second call (no recompute)" "${hit}"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
