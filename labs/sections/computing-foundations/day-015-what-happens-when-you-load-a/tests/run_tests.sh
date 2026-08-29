#!/usr/bin/env bash
# Tests for the Day 015 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The lab needs a network, but the tests degrade gracefully offline:
# structural checks (report shape) always run; the network checks
# (real DNS/curl values) run only when the network is reachable, and are
# SKIPPED with a clear message otherwise. The script exits 0 either way,
# as long as the structural checks pass.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
example="${lab_dir}/examples/trace_page_load.sh"
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
  echo "  skip: $1"
}

echo "Running ${example} against example.com ..."
output="$(bash "${example}" example.com 2>&1)"
exit_code=$?

# --- Structural checks (always run, offline or online) ---
[ "${exit_code}" -eq 0 ] && check "script exits successfully" "yes" || check "script exits successfully" "no"
echo "${output}" | grep -q '^=== Request Journey Report ===$' && check "prints report header" "yes" || check "prints report header" "no"
echo "${output}" | grep -q '^=== End of report ===$' && check "prints report footer" "yes" || check "prints report footer" "no"
echo "${output}" | grep -q '^Host: example.com$' && check "names the host" "yes" || check "names the host" "no"
echo "${output}" | grep -q -- '--- Stop 1: DNS lookup' && check "has Stop 1 (DNS)" "yes" || check "has Stop 1 (DNS)" "no"
echo "${output}" | grep -q -- '--- Stop 2: Round-trip time' && check "has Stop 2 (ping)" "yes" || check "has Stop 2 (ping)" "no"
echo "${output}" | grep -q -- '--- Stop 3: Connection stages' && check "has Stop 3 (curl)" "yes" || check "has Stop 3 (curl)" "no"

# --- Network detection: probe independently of the report ---
# Try a real request; if it fails (or curl is missing), treat as offline and
# skip the live-value checks instead of failing the suite.
if command -v curl >/dev/null 2>&1 && curl -sS --max-time 15 -o /dev/null https://example.com >/dev/null 2>&1; then
  network="up"
else
  network="down"
fi

if [ "${network}" = "up" ]; then
  echo "Network is reachable — running online checks."
  echo "${output}" | grep -Eq 'Resolved IP address' && check "DNS returned an address" "yes" || check "DNS returned an address" "no"
  # The IP line is an indented dotted quad or a hex IPv6 address.
  echo "${output}" | grep -Eq '^  [0-9a-fA-F:.]+$' && check "prints a resolved IP value" "yes" || check "prints a resolved IP value" "no"
  echo "${output}" | grep -Eq 'connect=[0-9]' && check "curl reports a connect time" "yes" || check "curl reports a connect time" "no"
  echo "${output}" | grep -Eq 'tls=[0-9]' && check "curl reports a TLS time" "yes" || check "curl reports a TLS time" "no"
  echo "${output}" | grep -Eq 'total=[0-9]' && check "curl reports a total time" "yes" || check "curl reports a total time" "no"
else
  echo "Network appears unavailable (curl did not return timings)."
  skip "DNS returned an address (needs network)"
  skip "prints a resolved IP value (needs network)"
  skip "curl connect/TLS/total timings (needs network)"
  echo "  The report structure is correct; re-run with a connection to see live values."
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skipped."
[ "${failures}" -eq 0 ]
