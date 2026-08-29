#!/usr/bin/env bash
# Tests for the Day 032 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies the full local-remote cycle with NO network: a push to a bare
# repository succeeds, a second clone receives the history, and a change
# pushed from one clone propagates to the other via pull. Also runs the
# shipped reference script and checks its output for the same evidence.
# Exits 0 on success, non-zero on any failure (CI-friendly).
set -uo pipefail

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0

check() {
  local label="$1" ok="$2"
  checks=$((checks + 1))
  if [ "${ok}" = "yes" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    failures=$((failures + 1))
  fi
}

id=(-c user.name="Day 32 Test" -c user.email="test@example.invalid")

# --------------------------------------------------------------------------
# Part 1: an independent local-remote cycle, asserted directly.
# --------------------------------------------------------------------------
echo "Part 1: independent push / clone / pull cycle (no network) ..."
ws="$(mktemp -d "${TMPDIR:-/tmp}/day32-test.XXXXXX")"
trap 'rm -rf "${ws}"' EXIT

origin="${ws}/origin.git"
repo_a="${ws}/repo-a"
repo_b="${ws}/repo-b"

git init --bare -b main "${origin}" >/dev/null 2>&1
git init -b main "${repo_a}" >/dev/null 2>&1
(
  cd "${repo_a}"
  echo "# Shared Notes" > README.md
  git "${id[@]}" add README.md
  git "${id[@]}" commit -q -m "Initial commit"
  git remote add origin "${origin}"
  git "${id[@]}" push -u origin main
) >/dev/null 2>&1
push_rc=$?
check "push to the bare remote succeeds (exit 0)" "$([ ${push_rc} -eq 0 ] && echo yes || echo no)"

# The remote (a bare repo) now has a main branch pointing at a commit.
if git --git-dir="${origin}" rev-parse --verify -q main >/dev/null; then
  check "remote now has a 'main' branch" "yes"
else
  check "remote now has a 'main' branch" "no"
fi

# A second clone must receive the pushed history.
git clone "${origin}" "${repo_b}" >/dev/null 2>&1
if [ -f "${repo_b}/README.md" ]; then
  check "second clone receives the pushed file (README.md)" "yes"
else
  check "second clone receives the pushed file (README.md)" "no"
fi

# Commit a change in the clone and push it.
(
  cd "${repo_b}"
  echo "line from repo-b" > shared.txt
  git "${id[@]}" add shared.txt
  git "${id[@]}" commit -q -m "Add shared.txt"
  git "${id[@]}" push origin main
) >/dev/null 2>&1

# Before pull, repo-a must NOT have the file; after pull, it must.
before="absent"; [ -f "${repo_a}/shared.txt" ] && before="present"
( cd "${repo_a}" && git "${id[@]}" pull origin main ) >/dev/null 2>&1
after="absent"; [ -f "${repo_a}/shared.txt" ] && after="present"
if [ "${before}" = "absent" ] && [ "${after}" = "present" ]; then
  check "a change propagates via pull (absent before, present after)" "yes"
else
  check "a change propagates via pull (absent before, present after)" "no"
fi

# The upstream tracking must be set on repo-a's main.
if ( cd "${repo_a}" && git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null | grep -q '^origin/main$' ); then
  check "repo-a's main tracks origin/main (upstream set)" "yes"
else
  check "repo-a's main tracks origin/main (upstream set)" "no"
fi

# No remote was a network URL — all paths are local folders.
url="$(cd "${repo_a}" && git remote get-url origin)"
case "${url}" in
  http://*|https://*|git@*) check "remote is a LOCAL path, not a network URL" "no" ;;
  *) check "remote is a LOCAL path, not a network URL" "yes" ;;
esac

# --------------------------------------------------------------------------
# Part 2: the shipped reference script runs and shows the same evidence.
# --------------------------------------------------------------------------
echo "Part 2: examples/remote_demo.sh produces the expected evidence ..."
if out="$(bash "${lab_dir}/examples/remote_demo.sh" 2>&1)"; then
  check "reference script exits successfully" "yes"
else
  check "reference script exits successfully" "no"
fi
echo "${out}" | grep -q '\[new branch\] *main -> main' && check "reference shows the push creating 'main' on the remote" "yes" || check "reference shows the push creating 'main' on the remote" "no"
echo "${out}" | grep -q 'set up to track' && check "reference shows the upstream being set" "yes" || check "reference shows the upstream being set" "no"
echo "${out}" | grep -q 'Fast-forward' && check "reference shows a fast-forward pull" "yes" || check "reference shows a fast-forward pull" "no"
echo "${out}" | grep -q 'shared.txt present in repo-a: yes' && check "reference confirms the change reached repo-a" "yes" || check "reference confirms the change reached repo-a" "no"

# --------------------------------------------------------------------------
# Part 3: the starter runs without error (structure only).
# --------------------------------------------------------------------------
echo "Part 3: starter/remote_demo.sh runs as a skeleton ..."
if bash "${lab_dir}/starter/remote_demo.sh" >/dev/null 2>&1; then
  check "starter script runs without a fatal error" "yes"
else
  check "starter script runs without a fatal error" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
