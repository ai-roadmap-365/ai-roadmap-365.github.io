#!/usr/bin/env bash
# Tests for the Day 019 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Structural checks always run. The certificate checks require network:
# if the host is unreachable, those checks are SKIPPED (not failed) with a
# clear message. The script exits 0 when nothing genuinely failed, so it is
# safe to run offline and in CI.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
host="example.com"
failures=0
checks=0
skipped=0

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
  echo "  SKIP: $1"
  skipped=$((skipped + 1))
}

echo "Structural checks ..."
# Required tools present.
command -v openssl >/dev/null 2>&1 && check "openssl is installed" "yes" || check "openssl is installed" "no"
command -v curl >/dev/null 2>&1 && check "curl is installed" "yes" || check "curl is installed" "no"
# Required files present.
[ -f "${lab_dir}/examples/inspect_tls.sh" ] && check "examples/inspect_tls.sh exists" "yes" || check "examples/inspect_tls.sh exists" "no"
[ -f "${lab_dir}/starter/inspect_tls.sh" ] && check "starter/inspect_tls.sh exists" "yes" || check "starter/inspect_tls.sh exists" "no"
[ -f "${lab_dir}/starter/tls-worksheet.md" ] && check "starter/tls-worksheet.md exists" "yes" || check "starter/tls-worksheet.md exists" "no"
# The example script is valid bash (parses without executing).
if bash -n "${lab_dir}/examples/inspect_tls.sh" 2>/dev/null; then
  check "examples/inspect_tls.sh is valid bash" "yes"
else
  check "examples/inspect_tls.sh is valid bash" "no"
fi

echo
echo "Network-dependent checks ..."
if ! curl -sI --max-time 15 "https://${host}" >/dev/null 2>&1; then
  skip "no network / ${host} unreachable — certificate checks skipped"
  skip "run again with an internet connection to exercise the full lab"
else
  cert="$(openssl s_client -connect "${host}:443" -servername "${host}" </dev/null 2>/dev/null \
    | openssl x509 -noout -subject -issuer -dates 2>/dev/null)"
  echo "${cert}" | grep -qi "subject=" && check "openssl returns a certificate subject" "yes" || check "openssl returns a certificate subject" "no"
  echo "${cert}" | grep -qi "issuer=" && check "openssl returns a certificate issuer" "yes" || check "openssl returns a certificate issuer" "no"
  echo "${cert}" | grep -qi "notAfter=" && check "openssl returns an expiry (notAfter) date" "yes" || check "openssl returns an expiry (notAfter) date" "no"
  # The reference script runs end to end and prints its footer.
  if bash "${lab_dir}/examples/inspect_tls.sh" "${host}" 2>&1 | grep -q "=== End of inspection ==="; then
    check "reference script runs and prints its footer" "yes"
  else
    check "reference script runs and prints its footer" "no"
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skipped} skipped."
[ "${failures}" -eq 0 ]
