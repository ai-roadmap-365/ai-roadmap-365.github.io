#!/usr/bin/env bash
# Tests for the Day 008 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the completed reference tour prints every required section with
# real (non-"unknown") values, and — if the learner has finished the starter —
# checks their version the same way.
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

run_tour_checks() {
  local script="$1" strict="$2" output
  echo "Testing ${script} ..."
  if ! output="$(bash "${script}" 2>&1)"; then
    check "script exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "script exits successfully" "yes"
  echo "${output}" | grep -q '^=== Shell Tour ===$' && check "prints tour header" "yes" || check "prints tour header" "no"
  echo "${output}" | grep -q '^=== End of tour ===$' && check "prints tour footer" "yes" || check "prints tour footer" "no"
  # Required labelled sections (the tour must show each of these).
  for marker in \
    "Current shell (echo \$0):" \
    "Default shell (echo \$SHELL):" \
    "Shell process (ps -p \$\$):" \
    "Prompt string (echo \"\$PS1\"):" \
    "Working directory (pwd):" \
    "Echo demo (echo hello):" \
    "Date (date):" \
    "User (whoami):" \
    "Recent command history (history | tail)" \
    "type echo:"; do
    if echo "${output}" | grep -qF "${marker}"; then
      check "prints section '${marker}'" "yes"
    else
      check "prints section '${marker}'" "no"
    fi
  done
  # The echo demo must actually print the word it echoed.
  echo "${output}" | grep -qF "Echo demo (echo hello): hello" && check "echo hello prints 'hello'" "yes" || check "echo hello prints 'hello'" "no"
  # 'type echo' should identify echo as a shell builtin.
  echo "${output}" | grep -qi "echo is a shell builtin" && check "type echo reports a shell builtin" "yes" || check "type echo reports a shell builtin" "no"

  if [ "${strict}" = "strict" ]; then
    # In a finished tour, the five exercise fields must not read 'unknown'.
    for field in \
      "Current shell (echo \$0): unknown" \
      "Default shell (echo \$SHELL): unknown" \
      "Working directory (pwd): unknown" \
      "Date (date): unknown" \
      "User (whoami): unknown"; do
      if echo "${output}" | grep -qF "${field}"; then
        check "field is filled in, not 'unknown' (${field%%:*})" "no"
      else
        check "field is filled in, not 'unknown' (${field%%:*})" "yes"
      fi
    done
  fi
}

run_tour_checks "${lab_dir}/examples/shell_tour.sh" strict

# The starter ships with 'unknown' values on purpose; once the learner has
# replaced them all, hold their script to the same strict standard.
if grep -q '="unknown"' "${lab_dir}/starter/shell_tour.sh"; then
  echo "Note: starter/shell_tour.sh still has unfilled exercises — testing structure only."
  run_tour_checks "${lab_dir}/starter/shell_tour.sh" lenient
else
  run_tour_checks "${lab_dir}/starter/shell_tour.sh" strict
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
