#!/usr/bin/env bash
# Day 033 lab — completed reference implementation.
#
# Simulates the pull-request-and-review workflow entirely LOCALLY, with no
# GitHub account and no network. A pull request is just review and merge
# gates wrapped around Git branches and merges, so we can rehearse the whole
# logic with plain Git:
#
#   1. Create a throwaway repo with a LOCAL identity (never touches your global config).
#   2. Make a focused change on a `feature` branch and commit it.
#   3. Produce the "pull request": `git diff main..feature` and `git log main..feature`.
#   4. Simulate a round of review by adding an "addressed feedback" commit.
#   5. Merge with --no-ff to create a merge commit, like a PR merge, and show the graph.
#   6. Contrast a squash-merge on a second branch.
#
# Everything happens in a temporary directory that is removed on exit.
set -euo pipefail

# --- Set up an isolated throwaway repository ---------------------------------
# By default the throwaway repo is deleted on exit. The test harness sets
# PR_FLOW_KEEP=1 to inspect the final repo state; it then removes the dir itself.
work="$(mktemp -d "${TMPDIR:-/tmp}/pr-flow.XXXXXX")"
cleanup() { rm -rf "${work}"; }
if [ -z "${PR_FLOW_KEEP:-}" ]; then
  trap cleanup EXIT
fi

echo "Working in throwaway repo: ${work}"
git init -q -b main "${work}" 2>/dev/null || { git init -q "${work}"; git -C "${work}" symbolic-ref HEAD refs/heads/main; }
cd "${work}"

# A LOCAL identity, scoped to this repo only — your global Git config is untouched.
git config user.email "learner@example.com"
git config user.name "Course Learner"

# --- Seed main with an initial commit ----------------------------------------
cat > notes.md <<'EOF'
# Course Notes

## Day 33: Pull Requests
EOF
git add notes.md
git commit -q -m "Initial notes"
echo
echo "== main starts here =="
git log --oneline

# --- Step 1: branch off main, like starting a pull request -------------------
echo
echo "== Step 1: create a feature branch =="
git switch -c feature 2>/dev/null || git checkout -q -b feature

# --- Step 2: make ONE focused change and commit it ---------------------------
cat >> notes.md <<'EOF'

A pull request is a proposal to merge a branch, reviewed before it lands.
EOF
git add notes.md
git commit -q -m "Add greeting line to notes"
echo "Committed the focused change on 'feature'."

# --- Step 3: produce the "pull request" --------------------------------------
echo
echo "== Step 3: the PR — what you are proposing to merge into main =="
echo "--- git diff main..feature (the change) ---"
git --no-pager diff main..feature
echo
echo "--- git log main..feature (commits the PR would show) ---"
git --no-pager log main..feature --oneline

# --- Step 4: simulate review by addressing feedback --------------------------
echo
echo "== Step 4: reviewer asked to clarify wording — push a follow-up commit =="
# Reviewer comment: "spell out that review happens before the merge, plainly."
sed -i.bak 's/reviewed before it lands\./reviewed by teammates before it lands in main./' notes.md
rm -f notes.md.bak
git add notes.md
git commit -q -m "Address review: clarify wording"
echo "The PR now contains two commits (original + addressed feedback):"
git --no-pager log main..feature --oneline

# --- Step 5: merge with --no-ff, like a PR merge, and show the graph ---------
echo
echo "== Step 5: merge the PR with a merge commit (--no-ff) =="
git switch main 2>/dev/null || git checkout -q main
git merge --no-ff -q -m "Merge branch 'feature'" feature
echo "History after the merge (note the two-parent merge commit):"
git --no-pager log --graph --oneline

# --- Step 6: contrast a squash-merge on a second branch ----------------------
echo
echo "== Step 6: contrast the SQUASH strategy on a second branch =="
git switch -c feature2 2>/dev/null || git checkout -q -b feature2
cat >> notes.md <<'EOF'

Squash merge collapses a branch's commits into a single commit on main.
EOF
git add notes.md
git commit -q -m "wip: draft squash note"
# A messy second commit, the kind squash is meant to tidy away.
printf '\nStill drafting the squash example.\n' >> notes.md
git add notes.md
git commit -q -m "wip: fix typo"

git switch main 2>/dev/null || git checkout -q main
git merge --squash feature2
git commit -q -m "Add feature2 note (squashed)"
echo "feature2 had two 'wip' commits; squash landed them as ONE commit on main:"
git --no-pager log --graph --oneline

echo
echo "== Done. The merge commit and the squashed commit show the two strategies side by side. =="
if [ -n "${PR_FLOW_KEEP:-}" ]; then
  echo "PR_FLOW_REPO=${work}"
else
  echo "Throwaway repo ${work} will be removed on exit."
fi
