#!/usr/bin/env bash
# Day 033 lab — YOUR working file: simulate a pull request locally.
#
# The scaffolding below creates a throwaway repo with a LOCAL identity and an
# initial commit on main. Your job is to complete the FIVE numbered exercises,
# each of which names the exact command to run. Replace every line that reads
#   : "FILL-IN ..."
# with the real command shown in the comment above it, then run:
#   bash starter/pr_flow.sh
#
# The completed reference is in examples/pr_flow.sh — try this yourself first.
set -euo pipefail

# --- Scaffolding (already done for you) --------------------------------------
work="$(mktemp -d "${TMPDIR:-/tmp}/pr-flow-starter.XXXXXX")"
trap 'rm -rf "${work}"' EXIT
echo "Working in throwaway repo: ${work}"
git init -q -b main "${work}" 2>/dev/null || { git init -q "${work}"; git -C "${work}" symbolic-ref HEAD refs/heads/main; }
cd "${work}"
git config user.email "learner@example.com"
git config user.name "Course Learner"
printf '# Course Notes\n\n## Day 33: Pull Requests\n' > notes.md
git add notes.md
git commit -q -m "Initial notes"
echo "main starts at:"; git --no-pager log --oneline

# --- Exercise 1: create a feature branch (like starting a pull request) -------
# Command:  git switch -c feature      (older Git:  git checkout -b feature)
: "FILL-IN exercise 1: replace this line with the branch-creating command"

# --- Make a focused change (already written for you) -------------------------
printf '\nA pull request is a proposal to merge a branch, reviewed before it lands.\n' >> notes.md

# --- Exercise 2: stage and commit the focused change -------------------------
# Commands:  git add notes.md   then   git commit -m "Add greeting line to notes"
: "FILL-IN exercise 2a: replace with 'git add notes.md'"
: "FILL-IN exercise 2b: replace with the commit command and message above"

# --- Exercise 3: produce the PR — the diff and the commit log ----------------
# Commands:  git --no-pager diff main..feature   then   git --no-pager log main..feature --oneline
echo; echo "== The pull request: what you propose to merge into main =="
: "FILL-IN exercise 3a: replace with the diff command above"
: "FILL-IN exercise 3b: replace with the log command above"

# --- Simulate review, then Exercise 4: commit the addressed feedback ---------
sed -i.bak 's/reviewed before it lands\./reviewed by teammates before it lands in main./' notes.md
rm -f notes.md.bak
# Commands:  git add notes.md   then   git commit -m "Address review: clarify wording"
: "FILL-IN exercise 4a: replace with 'git add notes.md'"
: "FILL-IN exercise 4b: replace with the commit command and message above"

# --- Exercise 5: merge the PR with a MERGE COMMIT (--no-ff) -------------------
# Commands:  git switch main    (older: git checkout main)
#            git merge --no-ff -m "Merge branch 'feature'" feature
#            git --no-pager log --graph --oneline
echo; echo "== Merge the pull request (merge-commit strategy) =="
: "FILL-IN exercise 5a: replace with the command to switch back to main"
: "FILL-IN exercise 5b: replace with the --no-ff merge command above"
: "FILL-IN exercise 5c: replace with the graph log command above"

echo; echo "== Done — you have simulated a pull request from branch to merge. =="
