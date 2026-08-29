#!/usr/bin/env bash
# Day 029 lab — YOUR working file.
#
# The repository-building part is done for you: this script creates a
# THROWAWAY git repo in a temporary directory, sets a LOCAL identity, makes
# three commits to notes.txt, and cleans up on exit. Your job is the four
# numbered exercises below — each names the EXACT git command to run so you
# can inspect the history you built. Replace each 'echo "FILL-IN ..."' line with
# the command named in the comment above it, then run:
#
#   bash starter/history_demo.sh
#
# The completed reference version is examples/history_demo.sh — try it
# yourself first, then come back and fill these in.
#
# Local only: no network is used at any point.
set -euo pipefail

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/day029-vcs-demo.XXXXXX")"
cleanup() {
  echo
  echo "Cleaning up the temporary repository..."
  rm -rf "${tmp_dir}"
  echo "Done. Nothing left behind."
}
trap cleanup EXIT

echo "=== Version control history demo (starter) ==="
echo "Creating a throwaway repository in a temporary directory..."
echo "(temporary directory: ${tmp_dir})"

cd "${tmp_dir}"

git init --quiet --initial-branch=main
git config user.name "Course Learner"
git config user.email "learner@example.com"

printf 'Point one: version control keeps history.\n' > notes.txt
git add notes.txt
git commit --quiet -m "Start notes with a first point"
c1="$(git rev-parse HEAD)"
echo "Made commit 1: Start notes with a first point"

printf 'Point two: every commit records who, when, and why.\n' >> notes.txt
git add notes.txt
git commit --quiet -m "Expand the notes with a second point"
c2="$(git rev-parse HEAD)"
echo "Made commit 2: Expand the notes with a second point"

printf 'Closing line: nothing committed is ever truly lost.\n' >> notes.txt
git add notes.txt
git commit --quiet -m "Add a closing line to the notes"
echo "Made commit 3: Add a closing line to the notes"

# =====================  YOUR EXERCISES  =====================================

# --- Exercise 1: show the one-line history -------------------------------
# Replace the FILL-IN line with the command:   git log --oneline
echo
echo "--- Exercise 1: git log --oneline (newest first) ---"
echo "FILL-IN Exercise 1: run 'git log --oneline'"

# --- Exercise 2: diff commit 1 against commit 2 --------------------------
# The commit ids are already saved in ${c1} and ${c2}. Replace the FILL-IN with:
#   git diff "${c1}" "${c2}" -- notes.txt
echo
echo "--- Exercise 2: git diff between commit 1 and commit 2 (notes.txt) ---"
echo "FILL-IN Exercise 2: run 'git diff \"\${c1}\" \"\${c2}\" -- notes.txt'"

# --- Exercise 3: show the full detail of commit 2 ------------------------
# Replace the FILL-IN with:   git show "${c2}"
echo
echo "--- Exercise 3: git show of commit 2 ---"
echo "FILL-IN Exercise 3: run 'git show \"\${c2}\"'"

# --- Exercise 4: time machine — restore notes.txt to commit 1 ------------
# Replace the FILL-IN with (git 2.23+):   git restore --source="${c1}" -- notes.txt
# On older git, use instead:           git checkout "${c1}" -- notes.txt
echo
echo "--- Exercise 4: restore notes.txt to commit 1 ---"
echo "FILL-IN Exercise 4: run 'git restore --source=\"\${c1}\" -- notes.txt'"
echo "notes.txt now reads:"
cat notes.txt

# cleanup runs automatically via the EXIT trap.
