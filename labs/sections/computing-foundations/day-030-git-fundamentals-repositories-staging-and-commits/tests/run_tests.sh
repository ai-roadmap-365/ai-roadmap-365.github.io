#!/usr/bin/env bash
# Tests for the Day 030 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Builds a throwaway repository the same way the lab does (temp dir under the
# lab directory, LOCAL identity only, no network) and verifies the real
# behaviour of Git's core model: init works, staging works, commits accumulate,
# .gitignore actually excludes a file, and cleanup leaves nothing behind.
set -u

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

# --- 0. The reference script runs cleanly and cleans up after itself -------
before_count="$(ls -1d "${lab_dir}"/.gitdemo.* 2>/dev/null | wc -l | tr -d ' ')"
if bash "${lab_dir}/examples/git_basics.sh" >/dev/null 2>&1; then
  check "examples/git_basics.sh exits successfully" "yes"
else
  check "examples/git_basics.sh exits successfully" "no"
fi
after_count="$(ls -1d "${lab_dir}"/.gitdemo.* 2>/dev/null | wc -l | tr -d ' ')"
if [ "${before_count}" = "${after_count}" ]; then
  check "reference script leaves no .gitdemo.* directory behind" "yes"
else
  check "reference script leaves no .gitdemo.* directory behind" "no"
fi

# --- Build our own throwaway repo to assert on Git's behaviour directly ----
work="$(mktemp -d "${lab_dir}/.gittest.XXXXXX")"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

git_local() {
  git -C "${work}" \
    -c user.name="Test Runner" \
    -c user.email="test@example.invalid" \
    -c init.defaultBranch=main \
    -c commit.gpgsign=false \
    "$@"
}

# 1. init creates a repository
git_local init -q >/dev/null 2>&1
[ -d "${work}/.git" ] && check "git init creates a .git repository" "yes" \
  || check "git init creates a .git repository" "no"

# 2. a new file is untracked
printf 'hello\n' > "${work}/file.txt"
if git_local status --short | grep -q '^?? file.txt$'; then
  check "a new file shows as untracked (??)" "yes"
else
  check "a new file shows as untracked (??)" "no"
fi

# 3. staging moves it to the index
git_local add file.txt
if git_local status --short | grep -q '^A  file.txt$'; then
  check "git add stages the file (A in status)" "yes"
else
  check "git add stages the file (A in status)" "no"
fi

# 4. first commit lands
git_local commit -q -m "first commit" >/dev/null 2>&1
c1="$(git_local rev-list --count HEAD 2>/dev/null || echo 0)"
[ "${c1}" = "1" ] && check "first commit is recorded (1 commit)" "yes" \
  || check "first commit is recorded (1 commit)" "no"

# 5. edit + second commit -> 2 commits
printf 'world\n' >> "${work}/file.txt"
# the edit must be visible as an unstaged modification before we stage it
if git_local status --short | grep -q '^ M file.txt$'; then
  check "an edit shows as modified-but-unstaged ( M)" "yes"
else
  check "an edit shows as modified-but-unstaged ( M)" "no"
fi
git_local add file.txt
git_local commit -q -m "second commit" >/dev/null 2>&1
c2="$(git_local rev-list --count HEAD 2>/dev/null || echo 0)"
if [ "${c2}" -ge 2 ]; then
  check "history reaches 2+ commits" "yes"
else
  check "history reaches 2+ commits" "no"
fi

# 6. .gitignore actually excludes a file
printf 'ignored.log\n' > "${work}/.gitignore"
printf 'noise\n' > "${work}/ignored.log"
if git_local status --short | grep -q 'ignored.log'; then
  check ".gitignore keeps the ignored file out of status" "no"
else
  check ".gitignore keeps the ignored file out of status" "yes"
fi
if git_local check-ignore -q ignored.log; then
  check "git confirms the file is ignored (check-ignore)" "yes"
else
  check "git confirms the file is ignored (check-ignore)" "no"
fi

# 7. HEAD resolves to a real commit hash
if git_local rev-parse --short HEAD >/dev/null 2>&1; then
  check "HEAD points at a real commit" "yes"
else
  check "HEAD points at a real commit" "no"
fi

# 8. no network was used — assert the repo has no configured remote
if [ -z "$(git_local remote 2>/dev/null)" ]; then
  check "repository has no remote (fully local, no network)" "yes"
else
  check "repository has no remote (fully local, no network)" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
