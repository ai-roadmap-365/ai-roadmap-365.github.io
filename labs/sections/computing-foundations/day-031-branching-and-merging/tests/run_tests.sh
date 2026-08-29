#!/usr/bin/env bash
# Tests for the Day 031 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# These tests build their OWN throwaway repository in a temp directory and
# drive the same branch -> conflict -> resolve -> merge story the lab teaches,
# then assert on the resulting git state:
#   * a feature branch was created
#   * merging it produced a real conflict
#   * the conflict was resolved and the repo ends CLEAN
#   * the final history contains a real merge commit (two parents)
#   * git log --graph renders the merge (the |\ diamond)
#
# Everything is local and offline. The temp repo is deleted on exit.
set -u

# Resolve the lab directory BEFORE we change into the temp workspace, because
# BASH_SOURCE becomes a relative path once we cd elsewhere.
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

# Refuse to run without git rather than failing mysteriously later.
if ! command -v git >/dev/null 2>&1; then
  echo "FAIL: git is not installed or not on PATH." >&2
  exit 1
fi

workdir="$(mktemp -d "${TMPDIR:-/tmp}/day031-tests.XXXXXX")"
cleanup() { rm -rf "${workdir}"; }
trap cleanup EXIT
cd "${workdir}" || { echo "FAIL: could not enter temp dir" >&2; exit 1; }

echo "Testing branch/conflict/merge behavior in ${workdir} ..."

# --- Build the scenario ------------------------------------------------------
git init -q -b main
git config --local user.name "Day 31 Test"
git config --local user.email "test@example.invalid"

printf '%s\n' "# Pancakes" "flour: 1 cup" "milk: 1 cup" "eggs: 1" > recipe.txt
git add recipe.txt
git commit -q -m "base"

# Feature branch edits line 3.
git switch -q -c feature-x
printf '%s\n' "# Pancakes" "flour: 1 cup" "milk: 2 cups" "eggs: 1" > recipe.txt
git commit -q -am "feature edit"

# 1) A branch was created.
if git branch --format='%(refname:short)' | grep -qx "feature-x"; then
  check "a feature branch was created" "yes"
else
  check "a feature branch was created" "no"
fi

# Competing edit on main, same line.
git switch -q main
printf '%s\n' "# Pancakes" "flour: 1 cup" "milk: 1 cup buttermilk" "eggs: 1" > recipe.txt
git commit -q -am "main edit"

# 2) Merging produces a conflict (non-zero exit + markers in the file).
if git merge --no-edit feature-x >/dev/null 2>&1; then
  check "merging the divergent branches produced a conflict" "no"
else
  check "merging the divergent branches produced a conflict" "yes"
fi

if grep -qE '^(<<<<<<<|=======|>>>>>>>)' recipe.txt; then
  check "git wrote conflict markers into the file" "yes"
else
  check "git wrote conflict markers into the file" "no"
fi

# git records the file as unmerged (status code UU) mid-conflict.
if [ -n "$(git ls-files --unmerged)" ]; then
  check "git records the file as unmerged during the conflict" "yes"
else
  check "git records the file as unmerged during the conflict" "no"
fi

# --- Resolve ----------------------------------------------------------------
printf '%s\n' "# Pancakes" "flour: 1 cup" "milk: 2 cups buttermilk" "eggs: 1" > recipe.txt

# 3) No conflict markers remain after resolution.
if grep -qE '^(<<<<<<<|=======|>>>>>>>)' recipe.txt; then
  check "conflict markers removed after resolution" "no"
else
  check "conflict markers removed after resolution" "yes"
fi

git add recipe.txt
git commit --no-edit -q

# 4) Working tree is clean after committing the merge.
if [ -z "$(git status --porcelain)" ]; then
  check "repository is clean after resolving the merge" "yes"
else
  check "repository is clean after resolving the merge" "no"
fi

# 5) The tip commit is a real merge commit (exactly two parents).
parents="$(git cat-file -p HEAD | grep -c '^parent ')"
if [ "${parents}" -eq 2 ]; then
  check "the final commit is a merge commit (two parents)" "yes"
else
  check "the final commit is a merge commit (two parents)" "no"
fi

# git rev-list agrees there is a merge in history.
if [ "$(git rev-list --merges --count HEAD)" -ge 1 ]; then
  check "history contains at least one merge commit" "yes"
else
  check "history contains at least one merge commit" "no"
fi

# 6) The graph renders the merge diamond (a line containing |\).
if git log --graph --oneline | grep -q '|\\'; then
  check "git log --graph shows the merge diamond" "yes"
else
  check "git log --graph shows the merge diamond" "no"
fi

# 7) The reference example script also runs clean end to end.
if bash "${lab_dir}/examples/branch_merge.sh" >/dev/null 2>&1; then
  check "examples/branch_merge.sh runs end to end and exits 0" "yes"
else
  check "examples/branch_merge.sh runs end to end and exits 0" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
