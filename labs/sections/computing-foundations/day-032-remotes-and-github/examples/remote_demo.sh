#!/usr/bin/env bash
# Day 032 lab — Remotes Without a Network (completed reference implementation).
#
# Demonstrates the full clone / push / fetch / pull cycle using a LOCAL bare
# repository as the remote. No GitHub account, no network, no authentication:
# the "remote" is just a folder on your own disk. Every git command here is
# the SAME one you would run against a real hosting platform — only the
# address is a path instead of a web URL.
#
# Run from the lab directory:
#   bash examples/remote_demo.sh
set -euo pipefail

# --- A private scratch workspace, cleaned up automatically on exit ----------
workspace="$(mktemp -d "${TMPDIR:-/tmp}/day32-remote.XXXXXX")"
cleanup() { rm -rf "${workspace}"; }
trap cleanup EXIT

# A local identity JUST for this demo, so commits work without touching your
# global git config. -c passes config to a single command only.
id=(-c user.name="Day 32 Learner" -c user.email="learner@example.invalid")

origin="${workspace}/origin.git"     # the "remote": a bare repository
repo_a="${workspace}/repo-a"         # first working copy
repo_b="${workspace}/repo-b"         # second working copy (a clone)

section() { printf '\n=== %s ===\n' "$1"; }

section "1. Create a bare repository to act as the remote (origin)"
git init --bare -b main "${origin}" >/dev/null
echo "Created bare remote at: ${origin}"
echo "A bare repo stores history but has NO working files — exactly like a server."

section "2. Create a working repository and register the remote"
git init -b main "${repo_a}" >/dev/null
cd "${repo_a}"
echo "# Shared Notes" > README.md
git "${id[@]}" add README.md
git "${id[@]}" commit -q -m "Initial commit"
git remote add origin "${origin}"
echo "git remote -v:"
git remote -v

section "3. Push the first commit and set the upstream"
git "${id[@]}" push -u origin main
echo "git branch -vv (note 'origin/main' upstream):"
git branch -vv

section "4. Clone the remote into a SECOND working copy"
git clone "${origin}" "${repo_b}" 2>&1 | sed 's/^/  /'
echo "Files in the clone:"
ls -1 "${repo_b}"

section "5. Make a commit in the clone and push it up"
cd "${repo_b}"
echo "line added from repo-b" > shared.txt
git "${id[@]}" add shared.txt
git "${id[@]}" commit -q -m "Add shared.txt from the second copy"
git "${id[@]}" push origin main
echo "repo-b pushed a new commit to origin."

section "6. Back in the first copy: fetch shows what changed, pull integrates it"
cd "${repo_a}"
git fetch origin >/dev/null 2>&1
echo "git branch -vv after fetch (repo-a is now 'behind'):"
git branch -vv
echo
echo "git pull (fetch + merge):"
git "${id[@]}" pull origin main 2>&1 | sed 's/^/  /'
echo "Files in repo-a now include the file pushed from repo-b:"
ls -1

section "7. Confirm both working copies and the remote agree"
echo "repo-a log:"
git log --oneline
echo "shared.txt present in repo-a: $([ -f shared.txt ] && echo yes || echo no)"

echo
echo "=== Done: a change travelled repo-b -> origin -> repo-a, with no network. ==="
