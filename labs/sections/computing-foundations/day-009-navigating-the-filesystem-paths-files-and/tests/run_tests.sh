#!/usr/bin/env bash
# Tests for the Day 009 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the reference script builds the sample tree, makes a file
# executable (before/after permission strings), prints the required lines,
# exits 0, and leaves NOTHING behind (its temporary workspace is removed).
# The starter is checked the same way once its exercises are completed.
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

count_workspaces() {
  # How many leftover temp workspaces exist directly under the lab directory.
  find "${lab_dir}" -maxdepth 1 -type d -name 'tmp.explore.*' 2>/dev/null | wc -l | tr -d ' '
}

run_script_checks() {
  local script="$1" strict="$2" output before after
  echo "Testing ${script} ..."

  before="$(count_workspaces)"
  if ! output="$(bash "${script}" 2>&1)"; then
    check "script exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "script exits successfully" "yes"
  after="$(count_workspaces)"

  echo "${output}" | grep -q '^=== Build and Explore a File Tree ===$' \
    && check "prints the lab header" "yes" || check "prints the lab header" "no"
  echo "${output}" | grep -q '^=== Done ===$' \
    && check "prints the done footer" "yes" || check "prints the done footer" "no"

  # Leaves nothing behind: no new workspace directory remains.
  if [ "${after}" -le "${before}" ]; then
    check "removes its temporary workspace (leaves nothing behind)" "yes"
  else
    check "removes its temporary workspace (leaves nothing behind)" "no"
  fi

  if [ "${strict}" = "strict" ]; then
    # The sample tree was built: mkdir and a listing that includes data/.
    echo "${output}" | grep -q 'mkdir -p project/data' \
      && check "builds the nested directory tree" "yes" || check "builds the nested directory tree" "no"
    echo "${output}" | grep -Eq '(^| )data( |$)' \
      && check "sample tree lists the data directory" "yes" || check "sample tree lists the data directory" "no"

    # A file became executable: before shows no x for owner, after shows -rwx.
    echo "${output}" | grep -q '^Before chmod:$' \
      && check "shows the 'Before chmod:' listing" "yes" || check "shows the 'Before chmod:' listing" "no"
    echo "${output}" | grep -q '^After chmod:$' \
      && check "shows the 'After chmod:' listing" "yes" || check "shows the 'After chmod:' listing" "no"
    echo "${output}" | grep -q -- '-rw-r--r--.*run\.sh' \
      && check "before: run.sh is not executable (-rw-r--r--)" "yes" || check "before: run.sh is not executable (-rw-r--r--)" "no"
    echo "${output}" | grep -q -- '-rwxr-xr--.*run\.sh' \
      && check "after: run.sh is executable (-rwxr-xr--, octal 754)" "yes" || check "after: run.sh is executable (-rwxr-xr--, octal 754)" "no"

    # A file was moved into data/.
    echo "${output}" | grep -q 'Moved report.md into data/\|report.md into data' \
      && check "moves report.md into data/" "yes" || check "moves report.md into data/" "no"
  fi
}

run_script_checks "${lab_dir}/examples/explore_files.sh" strict

# The starter ships with REPLACE-ME placeholders on purpose; once the learner
# has replaced them all, hold their script to the same strict standard.
if grep -q 'REPLACE-ME' "${lab_dir}/starter/explore_files.sh"; then
  echo "Note: starter/explore_files.sh still has unfinished exercises — testing structure only."
  run_script_checks "${lab_dir}/starter/explore_files.sh" lenient
else
  run_script_checks "${lab_dir}/starter/explore_files.sh" strict
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
