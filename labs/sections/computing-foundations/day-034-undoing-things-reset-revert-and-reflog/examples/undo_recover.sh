#!/usr/bin/env bash
# Day 034 lab — completed reference: undo and recover in Git.
#
# Builds a THROWAWAY git repository in a temporary directory, then walks
# through every undo move from the lesson and ends with a deliberate
# "disaster" (git reset --hard HEAD~2) that we recover from with the reflog.
# Nothing outside the temp directory is touched, and it is deleted on exit.
#
# Run it from the lab directory:  bash examples/undo_recover.sh
set -euo pipefail

# --- create an isolated scratch repo ------------------------------------
work="$(mktemp -d "${TMPDIR:-/tmp}/undo-recover.XXXXXX")"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT
cd "${work}"

section() { printf '\n=== %s ===\n' "$1"; }

git init -q
# Local identity only — your global git config is left untouched.
git config user.email "learner@example.com"
git config user.name "Undo Learner"
# Keep the branch name predictable across git versions.
git symbolic-ref HEAD refs/heads/main 2>/dev/null || true

section "1. Build a small history"
echo "line 1" > notes.txt
git add notes.txt
git commit -q -m "Frist commit"          # deliberate typo, fixed next
echo "step two" >> notes.txt
git commit -q -am "Second commit"
echo "step three" >> notes.txt
git commit -q -am "Third commit"
git log --oneline

section "2. git commit --amend fixes the last message"
echo "before amend, HEAD subject:"
git log -1 --pretty=%s
git commit -q --amend -m "Third commit (message fixed)"
echo "after amend, HEAD subject:"
git log -1 --pretty=%s

section "3. git restore --staged un-stages a file"
echo "a scratch change" > scratch.txt
git add scratch.txt
echo "status shows scratch.txt as staged:"
git status --short
git restore --staged scratch.txt
echo "after restore --staged, scratch.txt is no longer staged:"
git status --short
rm -f scratch.txt

section "4. git restore discards a working-tree change"
echo "OOPS unwanted edit" >> notes.txt
echo "notes.txt now has an unwanted last line:"
tail -n 1 notes.txt
git restore notes.txt
echo "after restore, the unwanted line is gone; last line is:"
tail -n 1 notes.txt

section "5. git reset --soft keeps changes staged, then re-commit"
git reset --soft HEAD~1
echo "after --soft reset, the change is still staged:"
git status --short
git commit -q -m "Third commit (re-committed after soft reset)"
git log --oneline

section "6. git revert adds an inverse commit (safe for shared history)"
target="$(git rev-parse --short HEAD)"
git revert --no-edit "${target}"
echo "log now shows the original commit AND its revert:"
git log --oneline -n 2

section "7. DISASTER: git reset --hard HEAD~2 drops two commits"
before_count="$(git rev-list --count HEAD)"
echo "commit count before disaster: ${before_count}"
git reset --hard HEAD~2
after_count="$(git rev-list --count HEAD)"
echo "commit count after --hard reset: ${after_count}"
echo "log is now shorter:"
git log --oneline

section "8. RECOVER with git reflog"
echo "the reflog still remembers where HEAD used to be:"
git reflog -n 5
# The commit we were on BEFORE the disastrous reset is reflog entry HEAD@{1}.
lost="$(git rev-parse --short 'HEAD@{1}')"
echo "recovering to the pre-disaster commit: ${lost}"
git reset --hard "${lost}"
recovered_count="$(git rev-list --count HEAD)"
echo "commit count after recovery: ${recovered_count}"
git log --oneline

section "Result"
if [ "${recovered_count}" = "${before_count}" ]; then
  echo "SUCCESS: recovered ${recovered_count} commits — nothing was truly lost."
else
  echo "MISMATCH: expected ${before_count}, got ${recovered_count}" >&2
  exit 1
fi
