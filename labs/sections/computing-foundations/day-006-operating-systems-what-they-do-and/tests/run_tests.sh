#!/usr/bin/env bash
# Tests for the Day 006 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the completed reference script exits cleanly and prints every
# required section of the OS profile with real (non-"unknown") values, and —
# once the learner has finished the starter script — checks their version the
# same way. Exits 0 on success, 1 on any failure.
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
  echo "${output}" | grep -q '^=== Meet Your Operating System ===$' && check "prints profile header" "yes" || check "prints profile header" "no"
  echo "${output}" | grep -q '^=== End of OS profile ===$' && check "prints profile footer" "yes" || check "prints profile footer" "no"
  for section in "--- Kernel ---" "--- Uptime ---" "--- Identity ---" "--- Mounted filesystems ---" "--- Top 5 processes by memory ---" "--- Where the kernel lives ---"; do
    echo "${output}" | grep -q "^${section}$" && check "prints section '${section}'" "yes" || check "prints section '${section}'" "no"
  done
  for field in "Kernel line (uname -a):" "Logged-in user:" "Login shell:" "Root filesystem (mounted on /):"; do
    echo "${output}" | grep -q "^${field}" && check "prints '${field}'" "yes" || check "prints '${field}'" "no"
  done
  if [ "${strict}" = "strict" ]; then
    if echo "${output}" | grep -q "unknown"; then
      check "no field is left 'unknown'" "no"
    else
      check "no field is left 'unknown'" "yes"
    fi
    # The kernel line must actually name a kernel this course supports.
    if echo "${output}" | grep -E '^Kernel line \(uname -a\): (Darwin|Linux)' >/dev/null; then
      check "kernel line names Darwin or Linux" "yes"
    else
      check "kernel line names Darwin or Linux" "no"
    fi
    # The top-processes section must contain at least one PID-looking row.
    procs_section="$(echo "${output}" | sed -n '/^--- Top 5 processes by memory ---$/,/^--- Where the kernel lives ---$/p')"
    if echo "${procs_section}" | grep -E '[0-9]+ ' >/dev/null; then
      check "top-processes section lists real processes" "yes"
    else
      check "top-processes section lists real processes" "no"
    fi
  fi
}

run_profile_checks "${lab_dir}/examples/explore_os.sh" strict

# The starter ships with 'unknown' values on purpose; once the learner has
# replaced them all, hold their script to the same strict standard.
if grep -q '"unknown"' "${lab_dir}/starter/explore_os.sh"; then
  echo "Note: starter/explore_os.sh still has unfilled exercises — testing structure only."
  run_profile_checks "${lab_dir}/starter/explore_os.sh" lenient
else
  run_profile_checks "${lab_dir}/starter/explore_os.sh" strict
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
