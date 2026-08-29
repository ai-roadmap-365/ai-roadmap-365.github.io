#!/usr/bin/env bash
# Tests for the Day 034 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Builds its own throwaway repository in a temp directory and independently
# verifies the three claims of the lesson:
#   (1) git commit --amend changes the last commit,
#   (2) git revert creates a new inverse commit,
#   (3) after git reset --hard the dropped commits are RECOVERED via reflog.
# Exits 0 on success, non-zero on any failure. No network, no sudo.
set -u

# Resolve the lab directory before we change into the scratch repo.
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

# --- isolated scratch repo ----------------------------------------------
work="$(mktemp -d "${TMPDIR:-/tmp}/undo-test.XXXXXX")"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT
cd "${work}" || { echo "cannot enter temp dir"; exit 1; }

git init -q
git config user.email "test@example.com"
git config user.name "Undo Test"
git symbolic-ref HEAD refs/heads/main 2>/dev/null || true

echo "Testing undo and recovery in a throwaway repo ..."

# Build a three-commit history.
echo "a" > f.txt; git add f.txt; git commit -q -m "Frist commit"
echo "b" >> f.txt; git commit -q -am "Second commit"
echo "c" >> f.txt; git commit -q -am "Third commit"

# (1) amend changes the last commit (subject and hash both change).
before_hash="$(git rev-parse HEAD)"
before_subj="$(git log -1 --pretty=%s)"
git commit -q --amend -m "Third commit (fixed)"
after_hash="$(git rev-parse HEAD)"
after_subj="$(git log -1 --pretty=%s)"
[ "${before_hash}" != "${after_hash}" ] && check "amend changes the commit hash" "yes" || check "amend changes the commit hash" "no"
[ "${before_subj}" = "Third commit" ] && [ "${after_subj}" = "Third commit (fixed)" ] \
  && check "amend changes the commit message" "yes" || check "amend changes the commit message" "no"

# (2) revert creates a new inverse commit on top.
count_before_revert="$(git rev-list --count HEAD)"
git revert --no-edit HEAD >/dev/null
count_after_revert="$(git rev-list --count HEAD)"
revert_subj="$(git log -1 --pretty=%s)"
[ "${count_after_revert}" -eq "$((count_before_revert + 1))" ] \
  && check "revert adds one new commit" "yes" || check "revert adds one new commit" "no"
case "${revert_subj}" in
  Revert*) check "the new commit is an inverse (Revert) commit" "yes" ;;
  *)       check "the new commit is an inverse (Revert) commit" "no" ;;
esac

# (3) hard reset drops commits; reflog recovers them.
full_count="$(git rev-list --count HEAD)"
git reset --hard HEAD~2 >/dev/null
dropped_count="$(git rev-list --count HEAD)"
[ "${dropped_count}" -eq "$((full_count - 2))" ] \
  && check "hard reset drops two commits" "yes" || check "hard reset drops two commits" "no"

# The pre-disaster commit is reflog entry HEAD@{1}.
lost="$(git rev-parse 'HEAD@{1}')"
[ -n "${lost}" ] && check "reflog still references the lost commit" "yes" || check "reflog still references the lost commit" "no"
git reset --hard "${lost}" >/dev/null
recovered_count="$(git rev-list --count HEAD)"
[ "${recovered_count}" -eq "${full_count}" ] \
  && check "commits RECOVERED via reflog (count restored)" "yes" || check "commits RECOVERED via reflog (count restored)" "no"

# The reference implementation runs end to end and exits 0.
if bash "${lab_dir}/examples/undo_recover.sh" >/dev/null 2>&1; then
  check "examples/undo_recover.sh runs end to end" "yes"
else
  check "examples/undo_recover.sh runs end to end" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
