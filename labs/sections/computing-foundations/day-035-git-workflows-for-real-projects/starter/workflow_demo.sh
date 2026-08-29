#!/usr/bin/env bash
# Day 035 lab — YOUR working file: run a real git workflow yourself.
#
# This starter builds the same isolated, network-free setup as the reference
# (a throwaway working repo plus a local bare "origin" in a temp directory,
# with a LOCAL git identity so your global config is never touched). Your job
# is to complete the five numbered exercises below, replacing each
#   : "__FILL_ME_IN__ exercise N ..."   # a harmless no-op placeholder line
# with the real git command named in its comment. Try it before peeking at
# examples/workflow_demo.sh.
#
# Run it with:   bash starter/workflow_demo.sh
# Check it with: bash tests/run_tests.sh
set -euo pipefail

# --- Isolated workspace, cleaned up on exit (already done for you) ----------
work_root="$(mktemp -d "${TMPDIR:-/tmp}/day035-starter.XXXXXX")"
cleanup() { rm -rf "${work_root}"; }
trap cleanup EXIT

origin="${work_root}/origin.git"
repo="${work_root}/notes"

git init --quiet --bare -b main "${origin}"
git clone --quiet "${origin}" "${repo}" 2>/dev/null
cd "${repo}"
git config user.name  "Workflow Learner"
git config user.email "learner@example.invalid"

echo "=== 1. Initial commit with a .gitignore ==="
printf '%s\n' 'node_modules/' '*.log' '.env' > .gitignore
printf '%s\n' '# Course Notes' '' 'Notes for the 365 Days of AI course.' > README.md
git add .gitignore README.md
# Exercise 1: make the initial commit with a chore: Conventional Commit message.
#   Use: git commit -m "chore: initialize notes repository with .gitignore"
: "__FILL_ME_IN__ exercise 1 — replace this line with the git commit command above"

echo
echo "=== 2. Create a short-lived feature branch (GitHub Flow) ==="
# Exercise 2: create AND switch to a feature branch named feat/notes-search.
#   Use: git switch -c feat/notes-search
: "__FILL_ME_IN__ exercise 2 — replace this line with the git switch command above"
echo "  on branch: $(git branch --show-current)"

echo
echo "=== 3. Two atomic commits with Conventional Commit messages ==="
printf '%s\n' 'def search(notes, query):' '    return [n for n in notes if query.lower() in n.lower()]' > search.py
git add search.py
# Exercise 3a: commit this as a feature.
#   Use: git commit -m "feat: add case-insensitive note search"
: "__FILL_ME_IN__ exercise 3a — replace this line with the feat: commit command above"
printf '%s\n' 'def search(notes, query):' '    if not query:' '        return []' '    return [n for n in notes if query.lower() in n.lower()]' > search.py
git add search.py
# Exercise 3b: commit the bug fix separately (this is what makes it atomic).
#   Use: git commit -m "fix: handle empty query without crashing"
: "__FILL_ME_IN__ exercise 3b — replace this line with the fix: commit command above"

echo
echo "=== 4. Merge back to main with --no-ff (like merging a pull request) ==="
git switch --quiet main
# Exercise 4: merge the feature branch WITHOUT fast-forward so a merge commit
# is recorded (the shape of a merged pull request).
#   Use: git merge --no-ff -m "Merge branch 'feat/notes-search'" feat/notes-search
: "__FILL_ME_IN__ exercise 4 — replace this line with the git merge --no-ff command above"

echo
echo "=== 5. Tag an annotated release ==="
# Exercise 5: create an ANNOTATED tag for the first release. Choose the semver
# deliberately and record your reasoning in starter/workflow-worksheet.md.
#   Use: git tag -a v1.0.0 -m "First release: note search"
: "__FILL_ME_IN__ exercise 5 — replace this line with the git tag -a command above"

echo
echo "=== Tags ==="
git tag
echo "=== History (main) ==="
git log --oneline --decorate --graph
echo "=== Workflow demo complete ==="
