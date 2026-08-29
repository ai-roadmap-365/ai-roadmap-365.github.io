#!/usr/bin/env bash
# Tests for the Day 007 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the completed reference script spawns its OWN background
# worker, finds it, terminates it with SIGTERM, and verifies its death —
# and, if the learner has finished the starter script, checks their version
# the same way. The test suite never signals any process the scripts did
# not start themselves.
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

run_playground_checks() {
  local script="$1" strict="$2" output
  echo "Testing ${script} ..."
  if ! output="$(bash "${script}" 2>&1)"; then
    check "script exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "script exits successfully" "yes"
  echo "${output}" | grep -q '^=== Process Playground ===$' && check "prints playground header" "yes" || check "prints playground header" "no"
  echo "${output}" | grep -q '^=== End of playground ===$' && check "prints playground footer" "yes" || check "prints playground footer" "no"
  echo "${output}" | grep -q '^Processes running right now:' && check "prints a process count line" "yes" || check "prints a process count line" "no"
  echo "${output}" | grep -q '^This script'"'"'s PID:' && check "prints its own PID" "yes" || check "prints its own PID" "no"

  if [ "${strict}" = "strict" ]; then
    # The process count must be a real positive integer, not 'unknown'.
    count="$(echo "${output}" | sed -n 's/^Processes running right now: //p' | head -n 1)"
    case "${count}" in
      '' | *[!0-9]*) check "process count is a positive integer" "no" ;;
      *) check "process count is a positive integer" "yes" ;;
    esac
    if echo "${output}" | grep -q "unknown"; then
      check "no value is left 'unknown'" "no"
    else
      check "no value is left 'unknown'" "yes"
    fi

    # The script must have spawned its own worker and captured a numeric PID.
    worker_pid="$(echo "${output}" | sed -n 's/^Started background worker: sleep 300 (PID \([0-9][0-9]*\)).*/\1/p' | head -n 1)"
    if [ -n "${worker_pid}" ]; then
      check "spawned its own background worker and captured its PID" "yes"
    else
      check "spawned its own background worker and captured its PID" "no"
    fi
    echo "${output}" | grep -q 'sleep 300' && check "found the worker with ps/jobs (sleep 300 visible)" "yes" || check "found the worker with ps/jobs (sleep 300 visible)" "no"

    # Polite termination: exit status 143 = 128 + 15 (SIGTERM).
    echo "${output}" | grep -q 'wait reported exit status 143' && check "worker died to SIGTERM (exit status 143)" "yes" || check "worker died to SIGTERM (exit status 143)" "no"
    echo "${output}" | grep -Eq '^Verified: PID [0-9]+ is gone$' && check "script verified its worker is gone" "yes" || check "script verified its worker is gone" "no"

    # Independent verification: the worker PID must no longer exist. (We only
    # *read* the process table here — the test signals nothing itself.)
    if [ -n "${worker_pid}" ]; then
      if ps -p "${worker_pid}" > /dev/null 2>&1; then
        check "worker PID ${worker_pid} really is gone (no orphaned sleep)" "no"
      else
        check "worker PID ${worker_pid} really is gone (no orphaned sleep)" "yes"
      fi
    fi
  fi
}

run_playground_checks "${lab_dir}/examples/process_playground.sh" strict

# The starter ships with 'unknown' values on purpose; once the learner has
# replaced them all, hold their script to the same strict standard.
if grep -q '"unknown"' "${lab_dir}/starter/process_playground.sh"; then
  echo "Note: starter/process_playground.sh still has unfilled exercises — testing structure only."
  run_playground_checks "${lab_dir}/starter/process_playground.sh" lenient
else
  run_playground_checks "${lab_dir}/starter/process_playground.sh" strict
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
