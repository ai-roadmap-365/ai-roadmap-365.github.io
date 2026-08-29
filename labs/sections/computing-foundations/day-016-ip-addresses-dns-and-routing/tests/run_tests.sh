#!/usr/bin/env bash
# Tests for the Day 016 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Structural checks always run (the reference script must produce a
# well-formed report and exit cleanly). Network checks (dig returns a real
# IP) run only when the machine is online; offline they are SKIPPED with a
# message and the suite still passes. Exit status is 0 when all run checks
# pass, non-zero on any structural failure — so it is CI-safe either way.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0
skips=0

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

skip() {
  skips=$((skips + 1))
  echo "  SKIP: $1"
}

# --- Are we online with a working DNS tool? ---------------------------------
network_ok="no"
if command -v dig >/dev/null 2>&1; then
  if dig +time=3 +tries=1 +short A example.com 2>/dev/null | grep -qE '^[0-9]+\.'; then
    network_ok="yes"
  fi
fi
if [ "${network_ok}" = "yes" ]; then
  echo "Network: online (dig resolved example.com) — running full checks."
else
  echo "Network: offline or 'dig' unavailable — network checks will be SKIPPED."
fi
echo

# --- Structural checks against the reference script -------------------------
ref="${lab_dir}/examples/explore_dns.sh"
echo "Testing ${ref} ..."
if output="$(bash "${ref}" 2>&1)"; then
  check "reference script exits successfully" "yes"
else
  check "reference script exits successfully" "no"
  echo "${output}" | sed 's/^/    /'
fi

echo "${output}" | grep -q '^=== DNS and Routing Report ===$' && check "prints report header" "yes" || check "prints report header" "no"
echo "${output}" | grep -q '^=== End of report ===$' && check "prints report footer" "yes" || check "prints report footer" "no"
echo "${output}" | grep -q 'A record (IPv4' && check "has A-record section" "yes" || check "has A-record section" "no"
echo "${output}" | grep -q 'AAAA record (IPv6' && check "has AAAA-record section" "yes" || check "has AAAA-record section" "no"
echo "${output}" | grep -q 'MX record' && check "has MX-record section" "yes" || check "has MX-record section" "no"
echo "${output}" | grep -q 'Route to' && check "has route section" "yes" || check "has route section" "no"
echo "${output}" | grep -q 'dig +trace' && check "mentions dig +trace for the hierarchy" "yes" || check "mentions dig +trace for the hierarchy" "no"

# --- Network-dependent checks -----------------------------------------------
if [ "${network_ok}" = "yes" ]; then
  if echo "${output}" | grep -qE 'A record IP \(first\): [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'; then
    check "reference script resolved a real IPv4 address" "yes"
  else
    check "reference script resolved a real IPv4 address" "no"
  fi
  if dig +time=3 +tries=1 +short A example.com 2>/dev/null | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
    check "dig independently returns an IPv4 for example.com" "yes"
  else
    check "dig independently returns an IPv4 for example.com" "no"
  fi
else
  skip "network check: reference script resolves an IPv4 (offline)"
  skip "network check: dig returns an IPv4 for example.com (offline)"
fi

# --- Structural checks against the starter ----------------------------------
starter="${lab_dir}/starter/explore_dns.sh"
echo "Testing ${starter} ..."
if bash "${starter}" >/dev/null 2>&1; then
  check "starter script exits successfully" "yes"
else
  check "starter script exits successfully" "no"
fi
if grep -q '"REPLACE_ME"' "${starter}"; then
  echo "  Note: starter still has unfinished exercises (REPLACE_ME) — structure only."
  check "starter names the four required commands in comments" \
    "$(grep -qE 'dig \+short A' "${starter}" && grep -qE 'dig \+short AAAA' "${starter}" && grep -qE 'dig \+short MX' "${starter}" && grep -qE 'traceroute' "${starter}" && echo yes || echo no)"
else
  # Learner has completed it: hold it to the same output shape.
  sout="$(bash "${starter}" 2>&1 || true)"
  echo "${sout}" | grep -q '^=== DNS and Routing Report ===$' && check "completed starter prints header" "yes" || check "completed starter prints header" "no"
  if [ "${network_ok}" = "yes" ]; then
    echo "${sout}" | grep -qE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' && check "completed starter shows a resolved IPv4" "yes" || check "completed starter shows a resolved IPv4" "no"
  else
    skip "network check: completed starter shows a resolved IPv4 (offline)"
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skipped."
[ "${failures}" -eq 0 ]
