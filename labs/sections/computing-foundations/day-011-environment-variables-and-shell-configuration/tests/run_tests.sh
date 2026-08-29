#!/usr/bin/env bash
# Tests for the Day 011 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the completed reference script prints every required field,
# that an exported variable reaches a child process, and — the key safety
# check — that the subshell variable does NOT leak into the environment.
# Also checks the starter's structure (or holds it to the strict standard
# once the learner has replaced every REPLACE_ME placeholder).
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

run_strict_checks() {
  local script="$1" output
  echo "Testing ${script} ..."
  if ! output="$(bash "${script}" 2>&1)"; then
    check "script exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "script exits successfully" "yes"

  echo "${output}" | grep -q '^=== Environment Inspection ===$' && check "prints header" "yes" || check "prints header" "no"
  echo "${output}" | grep -q '^=== End of inspection ===$' && check "prints footer" "yes" || check "prints footer" "no"

  for field in "HOME:" "USER:" "SHELL:" "LANG:"; do
    echo "${output}" | grep -q "^${field}" && check "prints '${field}'" "yes" || check "prints '${field}'" "no"
  done

  echo "${output}" | grep -q 'PATH directories (one per line):' && check "prints PATH heading" "yes" || check "prints PATH heading" "no"

  # Export flowed DOWN: the child process must see the exported value.
  echo "${output}" | grep -q 'child process sees demo_var = hello from a subshell' \
    && check "exported variable reached the child process" "yes" \
    || check "exported variable reached the child process" "no"

  # Safety check: the variable must NOT have leaked past the subshell.
  after_line="$(echo "${output}" | grep 'after subshell, demo_var =')"
  if echo "${after_line}" | grep -q 'hello from a subshell'; then
    check "subshell variable did NOT leak into the environment" "no"
  else
    check "subshell variable did NOT leak into the environment" "yes"
  fi

  echo "${output}" | grep -q 'alias greet ran' && check "alias was defined and ran" "yes" || check "alias was defined and ran" "no"

  # command -v resolved ls to a real, absolute path.
  ls_path="$(echo "${output}" | sed -n 's/^  command -v ls  -> //p')"
  case "${ls_path}" in
    /*) check "command -v resolved ls to an absolute path" "yes" ;;
    *)  check "command -v resolved ls to an absolute path" "no" ;;
  esac
}

# The reference example is always held to the strict standard.
run_strict_checks "${lab_dir}/examples/inspect_env.sh"

# The starter ships with REPLACE_ME placeholders. Only run it once the learner
# has replaced them all; before that, just confirm the exercises are present.
starter="${lab_dir}/starter/inspect_env.sh"
if grep -q 'REPLACE_ME_[1-4]' "${starter}"; then
  echo "Testing ${starter} (structure only — exercises not yet completed) ..."
  markers="$(grep -c 'REPLACE_ME_[1-4]' "${starter}")"
  [ "${markers}" -eq 4 ] && check "starter defines all 4 exercises" "yes" || check "starter defines all 4 exercises" "no"
else
  run_strict_checks "${starter}"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
