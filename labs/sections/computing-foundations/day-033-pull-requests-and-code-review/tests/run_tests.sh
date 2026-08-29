#!/usr/bin/env bash
# Tests for the Day 033 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Runs the completed reference flow in an inspectable throwaway repo and
# verifies the real Git state a pull request produces:
#   - a `feature` branch exists with the focused change + an "addressed
#     feedback" follow-up commit (the diff/commits a PR would show),
#   - the merge-commit strategy (--no-ff) produced a two-parent merge commit,
#   - the squash strategy landed a second branch as a SINGLE commit on main
#     (its intermediate "wip" commits absent from main's history).
# No network is used. Exits 0 on success, non-zero on any failure.
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

# 1. The starter must be valid bash and still contain the five exercises.
echo "Checking starter/pr_flow.sh ..."
if bash -n "${lab_dir}/starter/pr_flow.sh" 2>/dev/null; then
  check "starter is syntactically valid bash" "yes"
else
  check "starter is syntactically valid bash" "no"
fi
exercise_count="$(grep -c 'FILL-IN exercise' "${lab_dir}/starter/pr_flow.sh")"
[ "${exercise_count}" -ge 5 ] && check "starter has at least 5 exercises" "yes" || check "starter has at least 5 exercises" "no"

# 2. Run the reference flow, keeping the repo so we can inspect the end state.
echo "Running examples/pr_flow.sh (kept for inspection) ..."
output=""
if output="$(PR_FLOW_KEEP=1 bash "${lab_dir}/examples/pr_flow.sh" 2>&1)"; then
  check "reference flow runs and exits 0" "yes"
else
  check "reference flow runs and exits 0" "no"
  echo "${output}" | sed 's/^/    /'
  echo; echo "${checks} checks, ${failures} failure(s)."
  exit 1
fi

repo="$(printf '%s\n' "${output}" | sed -n 's/^PR_FLOW_REPO=//p' | tail -n 1)"
if [ -n "${repo}" ] && [ -d "${repo}/.git" ]; then
  check "inspectable throwaway repo was created" "yes"
else
  check "inspectable throwaway repo was created" "no"
  echo; echo "${checks} checks, ${failures} failure(s)."
  exit 1
fi
# Always clean up the kept repo ourselves.
trap 'rm -rf "${repo}"' EXIT

g() { git -C "${repo}" "$@"; }

# 3. The feature branch exists (the PR's source branch).
g show-ref --verify --quiet refs/heads/feature && check "feature branch exists" "yes" || check "feature branch exists" "no"

# 4. The PR's commits are on feature: the focused change AND the review follow-up.
feat_log="$(g log feature --oneline 2>/dev/null)"
printf '%s\n' "${feat_log}" | grep -q "Add greeting line to notes" && check "feature has the focused change commit" "yes" || check "feature has the focused change commit" "no"
printf '%s\n' "${feat_log}" | grep -q "Address review" && check "feature has the addressed-feedback commit" "yes" || check "feature has the addressed-feedback commit" "no"

# 5. The diff a PR would show is non-empty between main's base and feature's tip
#    (feature's notes.md contains the proposed line).
g show "feature:notes.md" 2>/dev/null | grep -q "proposal to merge a branch" && check "git diff main..feature would show the proposed change" "yes" || check "git diff main..feature would show the proposed change" "no"

# 6. The no-ff merge produced a two-parent merge commit on main.
merge_count="$(g rev-list --merges --count main 2>/dev/null)"
[ "${merge_count:-0}" -ge 1 ] && check "merge-commit strategy created a merge commit (--no-ff)" "yes" || check "merge-commit strategy created a merge commit (--no-ff)" "no"

# 7. The squash strategy landed as a SINGLE commit on main; the wip commits are absent.
main_log="$(g log main --oneline 2>/dev/null)"
printf '%s\n' "${main_log}" | grep -q "squashed" && check "squash produced a single 'squashed' commit on main" "yes" || check "squash produced a single 'squashed' commit on main" "no"
wip_on_main="$(printf '%s\n' "${main_log}" | grep -c 'wip')"
[ "${wip_on_main}" -eq 0 ] && check "squash collapsed the branch (no wip commits on main)" "yes" || check "squash collapsed the branch (no wip commits on main)" "no"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
