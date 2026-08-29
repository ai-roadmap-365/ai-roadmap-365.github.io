#!/usr/bin/env bash
# Tests for the Day 035 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Runs the workflow scripts (each in its own throwaway, network-free repo) and
# verifies the resulting history: a feature branch was merged into main, an
# annotated v1.0.0 tag exists, and the commits follow the feat:/fix:
# Conventional Commits convention. Exits 0 on success, non-zero on any failure.
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

# A workflow script proves its behavior through the history it prints. We run
# it, capture output, and assert on the merge, the tag, and the commit types.
run_workflow_checks() {
  local script="$1" output
  echo "Testing ${script} ..."
  if ! output="$(bash "${script}" 2>&1)"; then
    check "script exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "script exits successfully" "yes"

  echo "${output}" | grep -q "Merge branch 'feat/notes-search'" \
    && check "feature branch merged into main (merge commit present)" "yes" \
    || check "feature branch merged into main (merge commit present)" "no"

  echo "${output}" | grep -q "tag: v1.0.0" \
    && check "annotated v1.0.0 tag pinned in history" "yes" \
    || check "annotated v1.0.0 tag pinned in history" "no"

  echo "${output}" | awk '/^=== Tags ===/{f=1;next} /^===/{f=0} f' | grep -qx "v1.0.0" \
    && check "git tag lists v1.0.0" "yes" \
    || check "git tag lists v1.0.0" "no"

  echo "${output}" | grep -q "feat: add case-insensitive note search" \
    && check "has a Conventional Commit feat: message" "yes" \
    || check "has a Conventional Commit feat: message" "no"

  echo "${output}" | grep -q "fix: handle empty query without crashing" \
    && check "has a Conventional Commit fix: message" "yes" \
    || check "has a Conventional Commit fix: message" "no"
}

# 1) The reference implementation must satisfy every behavioral check.
run_workflow_checks "${lab_dir}/examples/workflow_demo.sh"

# 2) The starter: only run it once the learner has completed the exercises;
#    while placeholders remain it cannot build a valid repo, so we check
#    structure instead.
echo "Testing starter/workflow_demo.sh ..."
if grep -q '__FILL_ME_IN__' "${lab_dir}/starter/workflow_demo.sh"; then
  echo "  Note: starter still has unfilled exercises — checking structure only."
  count="$(grep -c 'Exercise [0-9]' "${lab_dir}/starter/workflow_demo.sh")"
  [ "${count}" -ge 5 ] \
    && check "starter names all five exercises" "yes" \
    || check "starter names all five exercises" "no"
else
  run_workflow_checks "${lab_dir}/starter/workflow_demo.sh"
fi

# 3) Hard rule: lab scripts stay fully local — no network URLs anywhere.
if grep -rEn 'https?://' "${lab_dir}/examples" "${lab_dir}/starter" "${lab_dir}/tests" >/dev/null 2>&1; then
  check "lab scripts contain no network URLs" "no"
else
  check "lab scripts contain no network URLs" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
