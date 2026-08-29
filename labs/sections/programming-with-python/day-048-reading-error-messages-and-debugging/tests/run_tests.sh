#!/usr/bin/env bash
# Tests for the Day 048 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies two things, with no network access:
#   1. Each BUGGY program fails with the EXPECTED exception type
#      (non-zero exit AND the exception name printed to stderr).
#   2. Each FIXED program runs cleanly (exit 0).
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0

PY="python3"
command -v "${PY}" >/dev/null 2>&1 || PY="python"

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

# Expected exception type for each buggy program.
expect_buggy() {
  local name="$1" want="$2"
  local src="${lab_dir}/examples/buggy/${name}.py"
  local err rc
  err="$("${PY}" "${src}" 2>&1 >/dev/null)"
  rc=$?
  if [ "${rc}" -eq 0 ]; then
    check "buggy/${name}.py fails (non-zero exit)" "no"
  else
    check "buggy/${name}.py fails (non-zero exit)" "yes"
  fi
  if printf '%s\n' "${err}" | grep -q "${want}"; then
    check "buggy/${name}.py raises ${want}" "yes"
  else
    check "buggy/${name}.py raises ${want}" "no"
    printf '%s\n' "${err}" | sed 's/^/    /'
  fi
}

# Fixed programs must run cleanly.
expect_fixed_ok() {
  local name="$1"
  local src="${lab_dir}/examples/fixed/${name}.py"
  if "${PY}" "${src}" >/dev/null 2>&1; then
    check "fixed/${name}.py runs cleanly (exit 0)" "yes"
  else
    check "fixed/${name}.py runs cleanly (exit 0)" "no"
  fi
}

echo "Checking buggy programs raise the expected exceptions ..."
expect_buggy average_scores IndexError
expect_buggy lookup_capital KeyError
expect_buggy total_price   TypeError

echo "Checking fixed programs run cleanly ..."
expect_fixed_ok average_scores
expect_fixed_ok lookup_capital
expect_fixed_ok total_price

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
