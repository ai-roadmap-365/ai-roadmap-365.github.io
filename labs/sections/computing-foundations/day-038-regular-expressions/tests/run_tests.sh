#!/usr/bin/env bash
# Tests for the Day 038 regex lab. Run from anywhere:
#   bash tests/run_tests.sh
#
# Verifies that the reference drills extract the KNOWN correct counts from the
# committed synthetic sample, and that the example script runs clean. No
# network, no writes outside stdout. Exits 0 on success, non-zero on any
# failure, so it is safe for CI.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sample="${lab_dir}/examples/samples/data.txt"
example="${lab_dir}/examples/regex_drills.sh"
failures=0
checks=0

check() {
  local label="$1" expected="$2" actual="$3"
  checks=$((checks + 1))
  if [ "${expected}" = "${actual}" ]; then
    echo "  ok: ${label} (${actual})"
  else
    echo "  FAIL: ${label} — expected '${expected}', got '${actual}'"
    failures=$((failures + 1))
  fi
}

echo "Checking the committed sample exists ..."
if [ ! -f "${sample}" ]; then
  echo "  FAIL: sample file not found at ${sample}"
  echo
  echo "1 checks, 1 failure(s)."
  exit 1
fi
echo "  ok: ${sample}"

echo "Checking known counts from the sample ..."

# Drill 1: email addresses (expected 6)
emails="$(grep -E -o '[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}' "${sample}" | grep -c .)"
check "email addresses extracted" "6" "${emails}"

# Drill 2: lines containing a YYYY-MM-DD date (expected 9)
dated="$(grep -E -c '[0-9]{4}-[0-9]{2}-[0-9]{2}' "${sample}")"
check "lines with a YYYY-MM-DD date" "9" "${dated}"

# Drill 3: IP-ish addresses (expected 5)
ips="$(grep -E -o '([0-9]{1,3}\.){3}[0-9]{1,3}' "${sample}" | grep -c .)"
check "IP-ish addresses extracted" "5" "${ips}"

# Status codes from log lines (expected 5): select log lines, then pull the code
codes="$(grep -E '" [0-9]{3}$' "${sample}" | grep -E -o '[0-9]{3}$' | grep -c .)"
check "status codes from log lines" "5" "${codes}"

# Non-comment lines (expected 16)
noncomment="$(grep -E -c -v '^#' "${sample}")"
check "non-comment lines" "16" "${noncomment}"

# Drill 4: sed reformat of a slash date to a hyphen date
reformatted="$(echo '2026/07/12' | sed -E 's#([0-9]{4})/([0-9]{2})/([0-9]{2})#\1-\2-\3#')"
check "sed backreference reformat" "2026-07-12" "${reformatted}"

echo "Checking the example drills script runs clean ..."
if out="$(bash "${example}" 2>&1)"; then
  check "examples/regex_drills.sh exits 0" "yes" "yes"
else
  check "examples/regex_drills.sh exits 0" "yes" "no"
  echo "${out}" | sed 's/^/    /'
fi
# The example output must contain the reformatted date it demonstrates.
if echo "${out}" | grep -q '2026-07-12'; then
  check "example output shows reformatted date" "yes" "yes"
else
  check "example output shows reformatted date" "yes" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
