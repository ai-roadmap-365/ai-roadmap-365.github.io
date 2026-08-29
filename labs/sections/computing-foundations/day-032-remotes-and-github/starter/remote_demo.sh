#!/usr/bin/env bash
# Day 032 lab — Remotes Without a Network (STARTER).
#
# This starter sets up the workspace for you. Your job is to complete the five
# numbered exercises below by replacing each `REPLACE_ME` call with the exact
# git command named in the comment above it. The completed reference version
# is in examples/remote_demo.sh — try this yourself first, then compare.
#
# Run from the lab directory:
#   bash starter/remote_demo.sh
#
# Note: we deliberately do NOT use `set -e` here, so that an unfinished
# exercise reports itself instead of stopping the whole script.
set -uo pipefail

# Absolute path to this script, captured before we change directories, so the
# completion check at the end can scan the file wherever it is run from.
self="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# --- A private scratch workspace, cleaned up automatically on exit ----------
workspace="$(mktemp -d "${TMPDIR:-/tmp}/day32-remote.XXXXXX")"
cleanup() { rm -rf "${workspace}"; }
trap cleanup EXIT

# A local identity JUST for this demo, so commits work without touching your
# global git config.
id=(-c user.name="Day 32 Learner" -c user.email="learner@example.invalid")

origin="${workspace}/origin.git"     # the "remote": a bare repository
repo_a="${workspace}/repo-a"         # first working copy
repo_b="${workspace}/repo-b"         # second working copy (a clone)

# When an exercise is still unfinished, this stand-in prints a reminder
# instead of running a command. Replace each REPLACE_ME line with real git.
REPLACE_ME() { echo "  [ ] Exercise not completed yet — replace this line (see the comment above)."; }

section() { printf '\n=== %s ===\n' "$1"; }

# --- Given for you: a bare remote and a first working repo with one commit ---
git init --bare -b main "${origin}" >/dev/null
git init -b main "${repo_a}" >/dev/null
cd "${repo_a}"
echo "# Shared Notes" > README.md
git "${id[@]}" add README.md
git "${id[@]}" commit -q -m "Initial commit"

section "Exercise 1 — register the bare repo as a remote named 'origin'"
# Replace the next line with:
#   git remote add origin "${origin}"
REPLACE_ME
echo "Check it with:"; git remote -v

section "Exercise 2 — push the first commit and set the upstream"
# Replace the next line with:
#   git "${id[@]}" push -u origin main
REPLACE_ME
echo "Check the upstream with:"; git branch -vv

section "Exercise 3 — clone the remote into a second working copy"
# Replace the next line with:
#   git clone "${origin}" "${repo_b}"
REPLACE_ME
echo "If it worked, the clone contains:"; ls -1 "${repo_b}" 2>/dev/null || echo "  (no clone yet)"

section "Exercise 4 — in the clone, make a commit and push it up"
if [ -d "${repo_b}" ]; then
  cd "${repo_b}"
  echo "line added from repo-b" > shared.txt
  git "${id[@]}" add shared.txt
  git "${id[@]}" commit -q -m "Add shared.txt from the second copy"
  # Replace the next line with:
  #   git "${id[@]}" push origin main
  REPLACE_ME
else
  echo "  (skipped — finish Exercise 3 first so the clone exists)"
fi

section "Exercise 5 — back in the first copy, pull the new commit"
cd "${repo_a}"
# Replace the next line with:
#   git "${id[@]}" pull origin main
REPLACE_ME
echo "Files in repo-a now:"; ls -1

# --- Completion check --------------------------------------------------------
echo
if grep -q "REPLACE_ME$" "${self}" 2>/dev/null; then
  echo "Some exercises are still unfinished — search this file for REPLACE_ME."
else
  echo "All five exercises look complete. Compare with examples/remote_demo.sh."
fi
