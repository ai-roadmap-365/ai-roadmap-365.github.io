#!/usr/bin/env bash
# Day 030 lab — YOUR working file.
#
# Goal: drive Git's core model by hand in a THROWAWAY repository and watch a
# file move through the three areas:
#   working directory -> (git add) -> staging area -> (git commit) -> repository
#
# The scaffolding below sets up a temporary repo with a LOCAL identity (so
# nothing touches your global git config) and cleans it up on exit. Your job
# is the five numbered exercises: replace each `FILL_ME` line with the exact
# git command named in the comment above it. The finished reference is in
# examples/git_basics.sh — try it yourself first.
#
# Run it with:  bash starter/git_basics.sh
set -euo pipefail

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d "${lab_dir}/.gitdemo.XXXXXX")"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

# Every git command runs with a LOCAL identity for THIS repo only.
git_local() {
  git -C "${work}" \
    -c user.name="Day 30 Learner" \
    -c user.email="learner@example.invalid" \
    -c init.defaultBranch=main \
    -c commit.gpgsign=false \
    "$@"
}

# --- Exercise 1: initialise an empty repository ---------------------------
# Replace FILL_ME with:  git_local init -q
echo "Exercise 1: git init"
FILL_ME
[ -d "${work}/.git" ] && echo "  .git created" || { echo "  ERROR: no .git dir"; exit 1; }

# Create a file in the working directory (given).
printf 'notes for day 30\n' > "${work}/notes.txt"

# --- Exercise 2: stage notes.txt (move it to the staging area) ------------
# Replace FILL_ME with:  git_local add notes.txt
echo "Exercise 2: git add notes.txt"
FILL_ME
echo "  status after add:"; git_local status --short | sed 's/^/    /'

# --- Exercise 3: commit the staged snapshot -------------------------------
# Replace FILL_ME with:  git_local commit -q -m "Add notes.txt with initial notes"
echo "Exercise 3: git commit"
FILL_ME
echo "  first commit: $(git_local rev-parse --short HEAD)"

# Edit the file so there is an unstaged change to see (given).
printf 'a second line, added later\n' >> "${work}/notes.txt"

# --- Exercise 4: show the unstaged change with a diff ---------------------
# Replace FILL_ME with:  git_local --no-pager diff
echo "Exercise 4: git diff (working directory vs last commit)"
FILL_ME

# Stage and commit the second snapshot (given, so you finish with 2 commits).
git_local add notes.txt
git_local commit -q -m "Append a second line to notes.txt"
echo "  second commit: $(git_local rev-parse --short HEAD)"

# Add a .gitignore and an ignored file (given).
printf 'secret.key\n' > "${work}/.gitignore"
printf 'PRETEND-API-KEY-do-not-commit\n' > "${work}/secret.key"
git_local add .gitignore
git_local commit -q -m "Add .gitignore to exclude secret.key"

# --- Exercise 5: print the one-line history -------------------------------
# Replace FILL_ME with:  git_local log --oneline
echo "Exercise 5: git log --oneline"
FILL_ME

echo
echo "If you see 3 commits above and secret.key never appeared in a status, you did it."
