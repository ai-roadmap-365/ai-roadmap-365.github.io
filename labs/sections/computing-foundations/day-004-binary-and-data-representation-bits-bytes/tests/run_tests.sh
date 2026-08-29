#!/usr/bin/env bash
# Tests for the Day 004 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the reference toolkit converts known values correctly, and —
# once the learner has completed the starter's four exercises — holds their
# toolkit to the same standard. Exits 0 on success, non-zero on any failure.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

# expect <script> <expected> <cmd> <arg>
expect() {
  local script="$1" expected="$2" got
  shift 2
  got="$(bash "${script}" "$@" 2>&1)" || true
  if [ "${got}" = "${expected}" ]; then
    check "$* -> ${expected}" "yes"
  else
    check "$* -> ${expected} (got: ${got})" "no"
  fi
}

run_conversion_checks() {
  local script="$1"
  echo "Testing ${script} ..."
  expect "${script}" "101010"   d2b 42
  expect "${script}" "11111111" d2b 255
  expect "${script}" "42"       b2d 101010
  expect "${script}" "181"      b2d 10110101
  expect "${script}" "2A"       d2h 42
  expect "${script}" "255"      h2d FF
  expect "${script}" "255"      h2d 0xFF
  expect "${script}" "00101111" h2b 2F
  local byte_line
  byte_line="$(bash "${script}" byte A 2>&1)" || true
  case "${byte_line}" in
    *65*01000001*) check "byte A reports decimal 65 and bits 01000001" "yes" ;;
    *)             check "byte A reports decimal 65 and bits 01000001 (got: ${byte_line})" "no" ;;
  esac
  # round trip: any value should survive d2b then b2d
  local rt
  rt="$(bash "${script}" b2d "$(bash "${script}" d2b 200)" 2>&1)" || true
  [ "${rt}" = "200" ] && check "round trip 200 -> binary -> 200" "yes" \
                       || check "round trip 200 -> binary -> 200 (got: ${rt})" "no"
}

run_structure_checks() {
  local script="$1" output
  echo "Testing ${script} (structure only — exercises not finished) ..."
  if output="$(bash "${script}" demo 2>&1)"; then
    check "starter demo runs and exits 0" "yes"
  else
    check "starter demo runs and exits 0" "no"
    echo "${output}" | sed 's/^/    /'
  fi
  echo "${output}" | grep -q '^=== Binary toolkit demo ===$' \
    && check "starter prints demo header" "yes" || check "starter prints demo header" "no"
  # the two prebuilt converters must already work in the skeleton
  expect "${script}" "2A"  d2h 42
  expect "${script}" "255" h2d FF
}

# bc is the only dependency beyond the shell; fail early with a clear message.
if ! command -v bc >/dev/null 2>&1; then
  echo "FAIL: 'bc' is not installed — see requirements/README.md" >&2
  exit 1
fi

run_conversion_checks "${lab_dir}/examples/binary_toolkit.sh"

# The starter ships with 'unknown' placeholders on purpose; once the learner
# has replaced them all, hold their toolkit to the full conversion standard.
if grep -q '"unknown"' "${lab_dir}/starter/binary_toolkit.sh"; then
  run_structure_checks "${lab_dir}/starter/binary_toolkit.sh"
else
  run_conversion_checks "${lab_dir}/starter/binary_toolkit.sh"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
