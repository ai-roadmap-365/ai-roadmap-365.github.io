#!/usr/bin/env bash
# Day 030 lab — completed reference implementation.
#
# Demonstrates Git's core model end to end in a THROWAWAY repository:
#   working directory -> (git add) -> staging area -> (git commit) -> repository
#
# It creates a temporary repo under this lab directory, gives it a LOCAL
# identity (never touching your global git config), walks the full
# init -> status -> add -> commit -> edit -> diff -> add -> commit ->
# .gitignore -> log flow, then deletes the temporary repo on exit.
#
# No network, no sudo, no changes outside the temp directory it creates.
set -euo pipefail

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d "${lab_dir}/.gitdemo.XXXXXX")"

# Always clean up the throwaway repo, however the script exits.
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

# Run every git command with a LOCAL identity for this repo only. We pass the
# identity via -c on each call so nothing is written to your ~/.gitconfig.
git_local() {
  git -C "${work}" \
    -c user.name="Day 30 Learner" \
    -c user.email="learner@example.invalid" \
    -c init.defaultBranch=main \
    -c commit.gpgsign=false \
    "$@"
}

rule() { printf '\n----- %s -----\n' "$1"; }

rule "1. git init — create an empty repository"
git_local init -q
echo "Created a repository. The .git directory now exists:"
ls -d "${work}/.git" | sed "s#${work}/#./#"

rule "2. git status — a brand-new file is UNTRACKED"
printf 'notes for day 30\n' > "${work}/notes.txt"
git_local status --short
echo "(?? means Git sees the file but is not tracking it yet)"

rule "3. git add — move notes.txt into the STAGING AREA"
git_local add notes.txt
git_local status --short
echo "(A in the left column means the file is staged, ready to commit)"

rule "4. git commit — record the staged snapshot in the repository"
git_local commit -q -m "Add notes.txt with initial notes"
first_hash="$(git_local rev-parse --short HEAD)"
echo "First commit created: ${first_hash}"

rule "5. Edit the file, then git diff — see the UNSTAGED change"
printf 'a second line, added later\n' >> "${work}/notes.txt"
git_local status --short
echo "(the M means notes.txt is modified in the working directory but not staged)"
echo "Working directory vs last commit:"
git_local --no-pager diff

rule "6. git add + git commit — record the second snapshot"
git_local add notes.txt
git_local commit -q -m "Append a second line to notes.txt"
second_hash="$(git_local rev-parse --short HEAD)"
echo "Second commit created: ${second_hash}"

rule "7. .gitignore — keep an ignored file UNTRACKED"
printf 'secret.key\n' > "${work}/.gitignore"
printf 'PRETEND-API-KEY-do-not-commit\n' > "${work}/secret.key"
git_local add .gitignore
git_local commit -q -m "Add .gitignore to exclude secret.key"
echo "status --short (secret.key must NOT appear; .gitignore is now committed):"
git_local status --short
echo "(empty status above = clean tree; secret.key is ignored, not staged)"
echo "Proof Git is deliberately ignoring it:"
git_local check-ignore -v secret.key | sed "s#${work}/#./#"

rule "8. git log --oneline — read the history (newest first)"
git_local log --oneline

rule "Summary"
echo "First commit  (short hash): ${first_hash}"
echo "Second commit (short hash): ${second_hash}"
echo "HEAD points at: $(git_local rev-parse --short HEAD) (the latest commit on branch main)"
echo "Commits in history: $(git_local rev-list --count HEAD)"
echo "Ignored and never committed: secret.key"
echo
echo "Done. The throwaway repository at ${work} will now be deleted."
