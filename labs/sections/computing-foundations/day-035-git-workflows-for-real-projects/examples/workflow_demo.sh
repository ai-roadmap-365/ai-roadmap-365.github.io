#!/usr/bin/env bash
# Day 035 lab — completed reference implementation: a real git workflow.
#
# Simulates GitHub Flow entirely on your own machine, with no network and no
# account. It creates a throwaway working repository and a local bare "origin"
# in a temporary directory, sets a LOCAL git identity (never touching your
# global config), then:
#   1. commits an initial .gitignore  (chore:)
#   2. branches off main               (feat/notes-search)
#   3. makes two atomic commits        (feat: , fix:)
#   4. merges back with --no-ff        (like merging a pull request)
#   5. tags an annotated release       (git tag -a v1.0.0)
# It also demonstrates that an ignored file stays out of git, and contrasts an
# atomic commit sequence with a sloppy one. The temp directory is removed on
# exit, so the demo leaves nothing behind.
set -euo pipefail

# --- Create an isolated workspace and clean it up on exit -------------------
work_root="$(mktemp -d "${TMPDIR:-/tmp}/day035-demo.XXXXXX")"
cleanup() { rm -rf "${work_root}"; }
trap cleanup EXIT

origin="${work_root}/origin.git"   # local bare repo standing in for a remote
repo="${work_root}/notes"          # our working clone

# --- A local bare repo acts as "origin" (no network involved) ---------------
git init --quiet --bare -b main "${origin}"
git clone --quiet "${origin}" "${repo}" 2>/dev/null
cd "${repo}"

# LOCAL identity only: these writes stay inside ${repo}/.git/config and never
# alter your machine's global git identity.
git config user.name  "Workflow Demo"
git config user.email "demo@example.invalid"

echo "=== 1. Initial commit with a .gitignore ==="
printf '%s\n' 'node_modules/' '*.log' '.env' > .gitignore
printf '%s\n' '# Course Notes' '' 'Notes for the 365 Days of AI course.' > README.md
git add .gitignore README.md
git commit --quiet -m "chore: initialize notes repository with .gitignore"

# Prove .gitignore works: a matching file must NOT appear in git status.
echo 'SECRET_KEY=do-not-commit-me' > .env
if git status --porcelain | grep -q '\.env'; then
  echo "  UNEXPECTED: .env showed up in git status" >&2
else
  echo "  .env is present on disk but correctly ignored by git (not tracked)"
fi

echo
echo "=== 2. Create a short-lived feature branch (GitHub Flow) ==="
git switch --quiet -c feat/notes-search
echo "  on branch: $(git branch --show-current)"

echo
echo "=== 3. Two atomic commits with Conventional Commit messages ==="
printf '%s\n' 'def search(notes, query):' '    return [n for n in notes if query.lower() in n.lower()]' > search.py
git add search.py
git commit --quiet -m "feat: add case-insensitive note search"

printf '%s\n' 'def search(notes, query):' '    if not query:' '        return []' '    return [n for n in notes if query.lower() in n.lower()]' > search.py
git add search.py
git commit --quiet -m "fix: handle empty query without crashing"

echo
echo "=== 4. Merge back to main with --no-ff (like merging a pull request) ==="
git switch --quiet main
git merge --no-ff --quiet -m "Merge branch 'feat/notes-search'" feat/notes-search
echo "  merged; main now has a merge commit recording the reviewed branch"

echo
echo "=== 5. Tag an annotated release and push everything to origin ==="
git tag -a v1.0.0 -m "First release: note search"
git push --quiet origin main
git push --quiet origin v1.0.0

echo
echo "=== Atomic vs sloppy commit (illustration on a scratch branch) ==="
git switch --quiet -c demo/atomic-vs-sloppy
# Atomic: two separate logical changes -> two commits you can revert or bisect.
echo 'MAX_RESULTS = 50' > config.py
git add config.py
git commit --quiet -m "feat: add MAX_RESULTS setting"
printf '%s\n' 'def tidy(s):' '    return s.strip()' > utils.py
git add utils.py
git commit --quiet -m "refactor: add tidy() helper"
echo "  Atomic history on this branch:"
git log --oneline -2 | sed 's/^/    /'
git switch --quiet main
git branch -D demo/atomic-vs-sloppy >/dev/null 2>&1
echo "  (A sloppy alternative would cram both changes into one 'stuff' commit,"
echo "   which you could not revert or bisect independently.)"

echo
echo "=== Tags ==="
git tag
echo "=== History (main) ==="
git log --oneline --decorate --graph
echo "=== Workflow demo complete ==="
