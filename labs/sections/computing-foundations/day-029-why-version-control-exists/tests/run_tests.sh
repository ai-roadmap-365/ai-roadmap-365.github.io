#!/usr/bin/env bash
# Tests for the Day 029 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the reference demo:
#   - builds a repository with exactly three commits,
#   - shows a diff (an added line) between two commits,
#   - restores an earlier version (the time machine), and
#   - cleans up its temporary directory, leaving nothing behind.
# Also checks the starter file names the four required git commands.
# No network is used.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
demo="${lab_dir}/examples/history_demo.sh"
starter="${lab_dir}/starter/history_demo.sh"
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

# --- git must be available --------------------------------------------------
if ! command -v git >/dev/null 2>&1; then
  echo "FAIL: git is not installed — see requirements/README.md"
  exit 1
fi

echo "Testing ${demo} ..."
if ! output="$(bash "${demo}" 2>&1)"; then
  check "demo script exits successfully" "no"
  echo "${output}" | sed 's/^/    /'
  echo
  echo "${checks} checks, ${failures} failure(s)."
  exit 1
fi
check "demo script exits successfully" "yes"

# Three commits were made.
made_count="$(printf '%s\n' "${output}" | grep -c '^Made commit [123]:')"
[ "${made_count}" -eq 3 ] && check "demo reports three commits made" "yes" || check "demo reports three commits made" "no"

# git log --oneline showed three commit lines (between its header and the next blank line).
log_count="$(printf '%s\n' "${output}" | awk '/^--- git log --oneline/{f=1;next} /^$/{f=0} f' | grep -c '.')"
[ "${log_count}" -eq 3 ] && check "git log --oneline lists three commits" "yes" || check "git log --oneline lists three commits" "no"

# A diff was shown: the added second-point line appears with a leading '+'.
printf '%s\n' "${output}" | grep -q '^+Point two:' && check "a diff shows an added line between two commits" "yes" || check "a diff shows an added line between two commits" "no"

# git show revealed an author line.
printf '%s\n' "${output}" | grep -q '^Author: Course Learner' && check "git show reveals the commit author" "yes" || check "git show reveals the commit author" "no"

# The time machine restored commit 1's content.
printf '%s\n' "${output}" | grep -q '^Point one: version control keeps history\.$' && check "restore brings back commit 1's version" "yes" || check "restore brings back commit 1's version" "no"

# Cleanup ran and the temporary directory it named no longer exists.
printf '%s\n' "${output}" | grep -q '^Done\. Nothing left behind\.$' && check "demo prints its cleanup confirmation" "yes" || check "demo prints its cleanup confirmation" "no"
tmp_path="$(printf '%s\n' "${output}" | sed -n 's/^(temporary directory: \(.*\))$/\1/p')"
if [ -n "${tmp_path}" ] && [ ! -e "${tmp_path}" ]; then
  check "temporary directory is gone after the run" "yes"
elif [ -z "${tmp_path}" ]; then
  check "temporary directory path was reported" "no"
else
  check "temporary directory is gone after the run" "no"
fi

# --- starter names the four required git commands ---------------------------
echo "Testing ${starter} ..."
for cmd in "git log --oneline" "git diff" "git show" "git restore"; do
  grep -q "${cmd}" "${starter}" && check "starter names '${cmd}'" "yes" || check "starter names '${cmd}'" "no"
done

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
