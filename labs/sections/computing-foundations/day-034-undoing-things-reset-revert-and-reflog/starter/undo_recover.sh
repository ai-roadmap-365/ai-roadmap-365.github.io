#!/usr/bin/env bash
# Day 034 lab — YOUR working file: undo and recover in Git.
#
# This starter builds a THROWAWAY git repository in a temporary directory
# and sets up a small history for you. Your job is to complete the five
# numbered exercises below: replace each line marked  # <-- replace  with the
# single git command named just above it in the  # TASK:  comment. The
# completed reference is in examples/undo_recover.sh — try it yourself first.
#
# As shipped, the script runs to the end and prints "NOT YET" because the
# recovery is not done. When you have finished all five tasks it prints
# "SUCCESS". Nothing outside the temp directory is touched; it is deleted on
# exit. Run it from the lab directory:  bash starter/undo_recover.sh
#
# Note: this starter uses `set -uo pipefail` (no `-e`) on purpose, so an
# unfinished exercise does not abort the whole script.
set -uo pipefail

work="$(mktemp -d "${TMPDIR:-/tmp}/undo-starter.XXXXXX")"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT
cd "${work}" || exit 1

section() { printf '\n=== %s ===\n' "$1"; }

git init -q
git config user.email "learner@example.com"
git config user.name "Undo Learner"
git symbolic-ref HEAD refs/heads/main 2>/dev/null || true

section "Setup: a three-commit history"
echo "line 1" > notes.txt
git add notes.txt
git commit -q -m "Frist commit"          # note the deliberate typo
echo "line 2" >> notes.txt
git commit -q -am "Second commit"
echo "line 3" >> notes.txt
git commit -q -am "Third commit"
git log --oneline

section "Exercise 1: fix the last commit message with amend"
echo "before:"; git log -1 --pretty=%s
# TASK 1: amend the last commit's message here, using:
#         git commit --amend -m "Third commit (fixed)"
echo 'TASK 1 not done — replace this line with the amend command'   # <-- replace
echo "after:"; git log -1 --pretty=%s

section "Exercise 2: un-stage a file with restore --staged"
echo "scratch" > scratch.txt
git add scratch.txt
echo "staged now:"; git status --short
# TASK 2: un-stage scratch.txt using:  git restore --staged scratch.txt
echo 'TASK 2 not done — replace this line with the restore --staged command'   # <-- replace
echo "after un-staging (should be ?? not A):"; git status --short
rm -f scratch.txt

section "Exercise 3: discard a working change with restore"
echo "unwanted line" >> notes.txt
echo "last line before restore:"; tail -n 1 notes.txt
# TASK 3: discard the edit to notes.txt using:  git restore notes.txt
echo 'TASK 3 not done — replace this line with the restore command'   # <-- replace
echo "last line after restore (should be 'line 3'):"; tail -n 1 notes.txt
git checkout -q -- notes.txt 2>/dev/null || true   # keep the repo tidy for later steps

section "Exercise 4: un-commit with reset --soft, then re-commit"
echo "line 3 again" >> notes.txt
# TASK 4: rewind one commit but keep the change staged, using:
#         git reset --soft HEAD~1
echo 'TASK 4 not done — replace this line with the reset --soft command'   # <-- replace
echo "staged after soft reset (should list notes.txt as M):"; git status --short
git commit -q -am "Third commit (re-committed)" 2>/dev/null || true

section "Exercise 5: DISASTER and RECOVERY"
before_count="$(git rev-list --count HEAD)"
echo "commit count before disaster: ${before_count}"
git reset --hard HEAD~2 >/dev/null
echo "count after --hard HEAD~2: $(git rev-list --count HEAD)"
git reflog -n 5
# TASK 5: recover the dropped commits. The pre-disaster commit is HEAD@{1}
#         in the reflog. Restore it using:  git reset --hard 'HEAD@{1}'
echo 'TASK 5 not done — replace this line with the recovery reset command'   # <-- replace
recovered_count="$(git rev-list --count HEAD)"
echo "commit count after recovery attempt: ${recovered_count}"
git log --oneline

section "Result"
if [ "${recovered_count}" = "${before_count}" ]; then
  echo "SUCCESS: recovered ${recovered_count} commits — nothing was lost."
else
  echo "NOT YET: expected ${before_count}, got ${recovered_count}. Finish the five TASKs above."
fi
