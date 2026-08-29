#!/usr/bin/env bash
# Tests for the Day 042 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the toolkit check runs, reports the core tools that this
# machine has (git, curl, python3), and that its end-to-end skill checks
# touch git, a SQLite query, and a shell pipeline. No network is used.
# If the learner has completed the starter (no FILL_ME_IN left), their
# version is held to the same standard.
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

has() { echo "$1" | grep -q "$2" && echo yes || echo no; }

run_check_script() {
  local script="$1" strict="$2" output
  echo "Testing ${script} ..."
  if ! output="$(bash "${script}" 2>&1)"; then
    check "script exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "script exits successfully" "yes"

  # Structure: header, sections, footer.
  check "prints report header"        "$(has "${output}" '^=== Computing Foundations Toolkit Check ===$')"
  check "prints tool inventory block" "$(has "${output}" '^-- Tool inventory --$')"
  check "prints skill checks block"   "$(has "${output}" '^-- Skill checks --$')"
  check "prints readiness block"      "$(has "${output}" '^-- Readiness --$')"
  check "prints report footer"        "$(has "${output}" '^=== End of check ===$')"

  # Every tool line maps to a Course 1 day.
  check "tool lines map to a day" "$(has "${output}" 'maps to Day')"

  if [ "${strict}" = "strict" ]; then
    # Core tools known to be present on this machine must report [ok].
    for t in git curl python3; do
      check "reports ${t} present ([ok])" "$(echo "${output}" | grep -E "^\[ok\]   ${t}" >/dev/null && echo yes || echo no)"
    done
    # The end-to-end must exercise git + a query + a pipeline, all passing.
    check "git init + commit skill passes" "$(echo "${output}" | grep -E '^\[ok\]   git init \+ commit works' >/dev/null && echo yes || echo no)"
    check "sqlite query skill passes"      "$(echo "${output}" | grep -E '^\[ok\]   sqlite query works' >/dev/null && echo yes || echo no)"
    check "shell pipeline skill passes"    "$(echo "${output}" | grep -E '^\[ok\]   shell pipeline works' >/dev/null && echo yes || echo no)"
    # Readiness verdict for a fully-equipped machine.
    check "reports ready for Course 2" "$(has "${output}" 'You are ready for Course 2')"
  fi
}

# The completed reference must pass strictly on this machine.
run_check_script "${lab_dir}/examples/toolkit_check.sh" strict

# The starter ships with FILL_ME_IN placeholders in executable positions;
# once the learner replaces them all, hold their script to the same strict
# standard. (Match only the code forms, not the comment prose that names
# the placeholder, so a completed starter is graded strictly.)
if grep -qE '\$\(FILL_ME_IN\)|FILL_ME_IN &&|if FILL_ME_IN' "${lab_dir}/starter/toolkit_check.sh"; then
  echo "Note: starter/toolkit_check.sh still has unfilled exercises — testing structure only."
  run_check_script "${lab_dir}/starter/toolkit_check.sh" lenient
else
  run_check_script "${lab_dir}/starter/toolkit_check.sh" strict
fi

# Confirm the lab makes no network calls (offline by contract).
if grep -RIE 'curl [^|]*http|wget |ping ' "${lab_dir}/examples" "${lab_dir}/starter" >/dev/null 2>&1; then
  check "lab scripts make no network calls" "no"
else
  check "lab scripts make no network calls" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
