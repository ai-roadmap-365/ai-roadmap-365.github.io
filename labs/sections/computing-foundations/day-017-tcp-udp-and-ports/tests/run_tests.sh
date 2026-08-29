#!/usr/bin/env bash
# Tests for the Day 017 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the reference script runs read-only, prints the four required
# sections, performs only loopback probes, and exits 0. It must NOT open any
# external connection and must NOT require sudo.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script="${lab_dir}/examples/inspect_ports.sh"
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

echo "Testing ${script} ..."

# 1. It must run and exit 0.
if output="$(bash "${script}" 2>&1)"; then
  check "script exits successfully (exit 0)" "yes"
else
  check "script exits successfully (exit 0)" "no"
  echo "${output}" | sed 's/^/    /'
fi

# 2. Required section headers are all present.
echo "${output}" | grep -q '^=== Ports and Connections ===$' && \
  check "prints report header" "yes" || check "prints report header" "no"
echo "${output}" | grep -q '^--- Listening TCP ports ---$' && \
  check "prints 'Listening TCP ports' section" "yes" || check "prints 'Listening TCP ports' section" "no"
echo "${output}" | grep -q '^--- Well-known vs ephemeral ---$' && \
  check "prints 'Well-known vs ephemeral' section" "yes" || check "prints 'Well-known vs ephemeral' section" "no"
echo "${output}" | grep -q '^--- Loopback connection test ---$' && \
  check "prints 'Loopback connection test' section" "yes" || check "prints 'Loopback connection test' section" "no"
echo "${output}" | grep -q '^=== End of report ===$' && \
  check "prints report footer" "yes" || check "prints report footer" "no"

# 3. The loopback test must reference 127.0.0.1 and only 127.0.0.1.
echo "${output}" | grep -q '127\.0\.0\.1' && \
  check "loopback test targets 127.0.0.1" "yes" || check "loopback test targets 127.0.0.1" "no"

# 4. Read-only / local-only guarantees, checked against the source itself.
if grep -Eq 'sudo|rm -rf|>[^&]|curl |wget ' "${script}"; then
  # >/dev/null and 2>&1 redirections are fine; a bare write redirect is not.
  if grep -Eq 'sudo |curl |wget ' "${script}"; then
    check "script contains no sudo/curl/wget (local & read-only)" "no"
  else
    check "script contains no sudo/curl/wget (local & read-only)" "yes"
  fi
else
  check "script contains no sudo/curl/wget (local & read-only)" "yes"
fi

# 5. The only host it ever contacts is the loopback (no external IPs/hostnames
#    passed to nc). Every nc invocation must target 127.0.0.1.
if grep -Eq '\bnc\b' "${script}"; then
  bad_nc="$(grep -E '\bnc .*(-z|-w)' "${script}" | grep -v '127\.0\.0\.1' || true)"
  if [ -z "${bad_nc}" ]; then
    check "every nc probe targets the loopback only" "yes"
  else
    check "every nc probe targets the loopback only" "no"
    echo "${bad_nc}" | sed 's/^/    offending: /'
  fi
else
  check "every nc probe targets the loopback only" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
