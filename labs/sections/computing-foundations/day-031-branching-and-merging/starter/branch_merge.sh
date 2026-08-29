#!/usr/bin/env bash
# Day 031 lab — YOUR working file: "Branch, Conflict, Merge".
#
# This starter builds a throwaway git repository for you and makes the base
# commit. Your job is to complete the five numbered exercises below by filling
# in the exact git commands named in each comment, replacing every line that
# says:  echo "EXERCISE N -- replace this line ...".
#
# The finished reference version is in examples/branch_merge.sh — try the
# exercises yourself first, then compare.
#
# Everything is local and offline. The temporary repository is deleted on exit,
# so you can run this as many times as you like without touching your machine.
set -euo pipefail

# --- A private, disposable workspace (already done for you) -------------------
workdir="$(mktemp -d "${TMPDIR:-/tmp}/day031-starter.XXXXXX")"
cleanup() { rm -rf "${workdir}"; }
trap cleanup EXIT
cd "${workdir}"

echo "=== Branch, Conflict, Merge (starter) ==="
echo "Workspace: ${workdir}"
echo

# --- Repo with a LOCAL identity + base commit (already done for you) ----------
git init -q -b main
git config --local user.name "Day 31 Learner"
git config --local user.email "learner@example.invalid"
printf '%s\n' "# Pancakes" "flour: 1 cup" "milk: 1 cup" "eggs: 1" > recipe.txt
git add recipe.txt
git commit -q -m "Add base pancake recipe"
echo "Base commit made on main. recipe.txt line 3 is: $(sed -n '3p' recipe.txt)"
echo

# =============================================================================
# EXERCISE 1 — create and switch to a feature branch.
# Use ONE command that both creates the branch and moves onto it:
#     git switch -c feature-blueberries
# (older git: git checkout -b feature-blueberries)
# Replace the placeholder line below with that command.
# =============================================================================
echo "EXERCISE 1 (replace this line): create and switch to branch feature-blueberries with git switch -c"

# On the feature branch, change line 3 to "milk: 2 cups", then commit it.
printf '%s\n' "# Pancakes" "flour: 1 cup" "milk: 2 cups" "eggs: 1" > recipe.txt
git commit -q -am "feature: use 2 cups of milk"
echo "On feature branch, line 3 is now: $(sed -n '3p' recipe.txt)"
echo

# =============================================================================
# EXERCISE 2 — switch back to main.
# Use:  git switch main   (older git: git checkout main)
# Replace the placeholder line below with that command.
# =============================================================================
echo "EXERCISE 2 (replace this line): switch back to main with git switch main"

# Back on main, change the SAME line 3 differently, then commit it. Two branches
# now disagree about line 3 — the setup for a conflict.
printf '%s\n' "# Pancakes" "flour: 1 cup" "milk: 1 cup buttermilk" "eggs: 1" > recipe.txt
git commit -q -am "main: switch to buttermilk"
echo "On main, line 3 is now: $(sed -n '3p' recipe.txt)"
echo

# =============================================================================
# EXERCISE 3 — merge the feature branch into main.
# Use:  git merge --no-edit feature-blueberries
# This WILL report a conflict — that is expected and correct. Because the
# script uses 'set -e', wrap the command so a conflict does not abort us:
#     git merge --no-edit feature-blueberries || true
# Replace the placeholder line below with that guarded command.
# =============================================================================
echo "EXERCISE 3 (replace this line): merge feature-blueberries into main with git merge --no-edit (guard with || true)"

echo
echo "git status after the merge attempt:"
git status --short
echo
echo "recipe.txt now contains conflict markers:"
cat recipe.txt
echo

# =============================================================================
# EXERCISE 4 — resolve the conflict.
# A real resolution removes the three marker lines (<<<<<<<, =======, >>>>>>>)
# and leaves the wording you want. Here we keep BOTH ideas. Replace the
# placeholder line below with a command that writes the resolved line 3, e.g.:
#     printf '%s\n' "# Pancakes" "flour: 1 cup" "milk: 2 cups buttermilk" "eggs: 1" > recipe.txt
# =============================================================================
echo "EXERCISE 4 (replace this line): write the resolved recipe.txt (line 3 = milk: 2 cups buttermilk, no markers)"

echo "recipe.txt after your resolution:"
cat recipe.txt
echo

# =============================================================================
# EXERCISE 5 — stage the resolved file and complete the merge.
# Two commands: stage the file, then commit to create the merge commit:
#     git add recipe.txt
#     git commit --no-edit
# Replace the placeholder line below with those two commands.
# =============================================================================
echo "EXERCISE 5 (replace this line): run git add recipe.txt then git commit --no-edit to finish the merge"

echo
echo "Final history graph:"
git log --graph --oneline
echo
echo "=== Done. Temporary repository will be deleted on exit. ==="
