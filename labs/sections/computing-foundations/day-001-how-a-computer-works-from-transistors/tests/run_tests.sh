#!/usr/bin/env bash
# Tests for the Day 001 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the completed reference script produces a well-formed
# machine profile with real (non-"unknown") values, and — if the learner
# has finished the starter script — checks their version the same way.
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

run_profile_checks() {
  local script="$1" strict="$2" output
  echo "Testing ${script} ..."
  if ! output="$(bash "${script}" 2>&1)"; then
    check "script exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "script exits successfully" "yes"
  echo "${output}" | grep -q '^=== My Machine Profile ===$' && check "prints profile header" "yes" || check "prints profile header" "no"
  echo "${output}" | grep -q '^=== End of profile ===$' && check "prints profile footer" "yes" || check "prints profile footer" "no"
  for field in "CPU model:" "CPU cores:" "RAM:" "Free disk on /:" "OS version:"; do
    echo "${output}" | grep -q "^${field}" && check "prints '${field}'" "yes" || check "prints '${field}'" "no"
  done
  if [ "${strict}" = "strict" ]; then
    if echo "${output}" | grep -q "unknown"; then
      check "no field is left 'unknown'" "no"
    else
      check "no field is left 'unknown'" "yes"
    fi
    cores="$(echo "${output}" | sed -n 's/^CPU cores: //p')"
    case "${cores}" in
      '' | *[!0-9]*) check "CPU cores is a positive integer" "no" ;;
      *) check "CPU cores is a positive integer" "yes" ;;
    esac
  fi
}

run_profile_checks "${lab_dir}/examples/inspect_my_computer_completed.sh" strict

# The starter ships with 'unknown' values on purpose; once the learner has
# replaced them all, hold their script to the same strict standard.
if grep -q '"unknown"' "${lab_dir}/starter/inspect_my_computer.sh"; then
  echo "Note: starter/inspect_my_computer.sh still has unfilled exercises — testing structure only."
  run_profile_checks "${lab_dir}/starter/inspect_my_computer.sh" lenient
else
  run_profile_checks "${lab_dir}/starter/inspect_my_computer.sh" strict
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
