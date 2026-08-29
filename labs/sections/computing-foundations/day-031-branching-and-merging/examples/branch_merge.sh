#!/usr/bin/env bash
# Day 031 lab — completed reference implementation.
#
# "Branch, Conflict, Merge": builds a throwaway git repository in a temporary
# directory, then walks through the whole branching story end to end:
#
#   1. a base commit on the default branch
#   2. a feature branch that edits some lines
#   3. a competing edit to the SAME lines back on the default branch
#   4. a three-way merge that COLLIDES -> a real conflict
#   5. a programmatic conflict resolution (git add + git commit)
#   6. git log --graph to see the diamond shape the merge created
#   7. a separate branch that merges cleanly as a FAST-FORWARD
#
# Everything is local: no network, no GitHub, no credentials. The temporary
# repository is deleted on exit, so running this leaves your machine untouched.
set -euo pipefail

# --- Make a private, disposable workspace ------------------------------------
# mktemp -d creates a fresh directory with a random name. We remove it on exit
# (success OR failure) via a trap, so nothing lingers.
workdir="$(mktemp -d "${TMPDIR:-/tmp}/day031-branch-merge.XXXXXX")"
cleanup() { rm -rf "${workdir}"; }
trap cleanup EXIT

echo "=== Branch, Conflict, Merge ==="
echo "Workspace: ${workdir}"
echo

cd "${workdir}"

# --- Step 0: a repository with a LOCAL identity ------------------------------
# git init makes the current directory a repository. We set user.name and
# user.email with --local so this identity applies ONLY to this throwaway repo
# and never touches your real global git config. -b main names the first
# branch "main" so the output is predictable across git versions.
git init -q -b main
git config --local user.name "Day 31 Learner"
git config --local user.email "learner@example.invalid"

echo "--- Step 1: base commit on main ---"
# A tiny recipe file is our shared document. Everyone starts from this version.
printf '%s\n' \
  "# Pancakes" \
  "flour: 1 cup" \
  "milk: 1 cup" \
  "eggs: 1" > recipe.txt
git add recipe.txt
git commit -q -m "Add base pancake recipe"
git log --oneline
echo

# --- Step 2: a feature branch that changes a line ----------------------------
echo "--- Step 2: create feature branch 'feature-blueberries' and edit line 3 ---"
git switch -q -c feature-blueberries
# On the feature branch we double the milk. This rewrites line 3.
printf '%s\n' \
  "# Pancakes" \
  "flour: 1 cup" \
  "milk: 2 cups" \
  "eggs: 1" > recipe.txt
git commit -q -am "feature: use 2 cups of milk"
echo "feature-blueberries now says:"
sed -n '3p' recipe.txt
echo

# --- Step 3: a COMPETING edit to the same line, back on main -----------------
echo "--- Step 3: back on main, edit the SAME line 3 differently ---"
git switch -q main
# On main someone else changes line 3 to buttermilk instead. Two branches,
# two different values for the same line: this is what makes a conflict.
printf '%s\n' \
  "# Pancakes" \
  "flour: 1 cup" \
  "milk: 1 cup buttermilk" \
  "eggs: 1" > recipe.txt
git commit -q -am "main: switch to buttermilk"
echo "main now says:"
sed -n '3p' recipe.txt
echo

# --- Step 4: merge the feature branch -> a real three-way merge conflict -----
echo "--- Step 4: merge feature-blueberries into main (expect a conflict) ---"
# We want the merge to FAIL with a conflict, but 'set -e' would abort the
# script on git merge's non-zero exit. Guard it so we can react instead.
if git merge --no-edit feature-blueberries; then
  echo "Unexpected: the merge succeeded without a conflict." >&2
  exit 1
fi

echo
echo "Conflict detected. git status shows the unmerged file:"
git status --short
echo
echo "Git rewrote recipe.txt with conflict markers:"
cat recipe.txt
echo

# --- Step 5: resolve the conflict programmatically ---------------------------
echo "--- Step 5: resolve the conflict, then add + commit ---"
# A human would open the file and edit out the markers by hand. To keep this
# script deterministic we write the resolved file directly: we KEEP BOTH
# ideas — buttermilk AND more of it — which is a real editorial decision, not
# a blind "take theirs". The three marker lines (<<<<<<<, =======, >>>>>>>)
# are gone; that is what "resolved" means.
printf '%s\n' \
  "# Pancakes" \
  "flour: 1 cup" \
  "milk: 2 cups buttermilk" \
  "eggs: 1" > recipe.txt

# Prove no conflict markers remain before we stage the file.
if grep -qE '^(<<<<<<<|=======|>>>>>>>)' recipe.txt; then
  echo "Conflict markers still present — resolution incomplete." >&2
  exit 1
fi

git add recipe.txt          # staging the file tells git "this conflict is handled"
git commit --no-edit -q     # completes the merge; creates the MERGE COMMIT
echo "Resolved. Final recipe:"
cat recipe.txt
echo

# --- Step 6: view the history as a graph -------------------------------------
echo "--- Step 6: history graph (the merge commit ties both lines together) ---"
git log --graph --oneline
echo

# --- Step 7: a clean FAST-FORWARD merge on a separate branch -----------------
echo "--- Step 7: a clean fast-forward merge (no divergence, no conflict) ---"
# Branch off, add a brand-new file (touches nothing main changed), come back.
# Because main has not moved since we branched, git can merge by simply sliding
# main's pointer forward to the feature commit: a fast-forward, no merge commit.
git switch -q -c feature-notes
printf '%s\n' "Serve warm with syrup." > serving.txt
git add serving.txt
git commit -q -m "feature: add serving suggestion"
git switch -q main
git merge --ff-only feature-notes
echo
echo "History after the fast-forward (feature-notes just extends the line):"
git log --graph --oneline
echo

echo "=== Done. Temporary repository will be deleted on exit. ==="
