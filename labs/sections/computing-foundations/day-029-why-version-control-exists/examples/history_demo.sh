#!/usr/bin/env bash
# Day 029 lab — completed reference implementation.
#
# Builds a THROWAWAY git repository in a temporary directory, makes three
# commits to a single file, then shows the history four ways:
#   1. git log --oneline   (the shelf of snapshots)
#   2. git diff            (what changed between two commits)
#   3. git show            (the full detail of one commit)
#   4. restore an earlier version (the "time machine")
# It sets a LOCAL git identity inside the temp repo only, so it works even
# if you have never configured git globally, and it deletes the temporary
# directory on exit (including on Ctrl-C) so nothing is left behind.
#
# Local only: no network is used at any point.
set -euo pipefail

# --- create a throwaway working area, and guarantee cleanup on exit ---------
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/day029-vcs-demo.XXXXXX")"
cleanup() {
  echo
  echo "Cleaning up the temporary repository..."
  rm -rf "${tmp_dir}"
  echo "Done. Nothing left behind."
}
trap cleanup EXIT

echo "=== Version control history demo ==="
echo "Creating a throwaway repository in a temporary directory..."
echo "(temporary directory: ${tmp_dir})"

cd "${tmp_dir}"

# --- initialize the repository and set a LOCAL identity ---------------------
# --initial-branch keeps output stable across git versions; the identity is
# scoped to THIS repo only (no --global), so your machine's config is untouched.
git init --quiet --initial-branch=main
git config user.name "Course Learner"
git config user.email "learner@example.com"

# --- commit 1 ---------------------------------------------------------------
printf 'Point one: version control keeps history.\n' > notes.txt
git add notes.txt
git commit --quiet -m "Start notes with a first point"
c1="$(git rev-parse HEAD)"
echo "Made commit 1: Start notes with a first point"

# --- commit 2 ---------------------------------------------------------------
printf 'Point two: every commit records who, when, and why.\n' >> notes.txt
git add notes.txt
git commit --quiet -m "Expand the notes with a second point"
c2="$(git rev-parse HEAD)"
echo "Made commit 2: Expand the notes with a second point"

# --- commit 3 ---------------------------------------------------------------
printf 'Closing line: nothing committed is ever truly lost.\n' >> notes.txt
git add notes.txt
git commit --quiet -m "Add a closing line to the notes"
echo "Made commit 3: Add a closing line to the notes"

# --- view 1: the one-line log ----------------------------------------------
echo
echo "--- git log --oneline (newest first) ---"
git log --oneline

# --- view 2: a diff between commit 1 and commit 2 ---------------------------
echo
echo "--- git diff between commit 1 and commit 2 (notes.txt) ---"
# Show only the added/removed content lines to keep the demo readable.
git diff "${c1}" "${c2}" -- notes.txt | grep -E '^[+-][^+-]' || true

# --- view 3: the full detail of commit 2 -----------------------------------
echo
echo "--- git show of commit 2 ---"
git show --no-patch --format='Author: %an <%ae>%n    %s' "${c2}"

# --- view 4: the time machine — restore notes.txt to commit 1 ---------------
echo
echo "--- Time machine: restoring notes.txt to commit 1 ---"
# 'git restore' (git >= 2.23) is preferred; fall back to 'git checkout' if the
# installed git is older, so the demo works everywhere.
if git restore --source="${c1}" -- notes.txt 2>/dev/null; then
  :
else
  git checkout "${c1}" -- notes.txt
fi
echo "Restored. notes.txt now reads:"
cat notes.txt

# cleanup runs automatically via the EXIT trap.
