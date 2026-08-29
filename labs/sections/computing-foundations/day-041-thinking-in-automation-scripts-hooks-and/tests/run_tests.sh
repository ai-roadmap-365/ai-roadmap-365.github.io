#!/usr/bin/env bash
# Tests for the Day 041 lab. Run from anywhere:
#   bash tests/run_tests.sh
#
# Verifies real behavior, not just file existence:
#   - the pre-commit hook BLOCKS a commit with trailing whitespace (non-zero)
#   - the pre-commit hook ALLOWS a clean commit (zero)
#   - the pre-commit hook BLOCKS a commit with a shell syntax error
#   - the pipeline FAILS FAST on a failing stage (non-zero, later stages skipped)
#   - the pipeline SUCCEEDS when every stage passes (zero)
# Offline; needs only git and bash. Exits 0 on success, non-zero on any failure.
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

# --- Set up a throwaway repo with the reference hook installed. ---
work="$(mktemp -d 2>/dev/null || mktemp -d -t hooktest)"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

cd "${work}"
git init -q
git config user.email "test@example.local"
git config user.name "Test Runner"
mkdir -p .git/hooks
cp "${lab_dir}/examples/pre-commit" .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "Testing the pre-commit hook ..."

# 1. Bad commit: trailing whitespace must be rejected.
printf 'echo "hi"   \n' > bad.sh
git add bad.sh
if git commit -q -m "bad" >/dev/null 2>&1; then
  check "hook blocks a commit with trailing whitespace" "no"
else
  check "hook blocks a commit with trailing whitespace" "yes"
fi

# 2. Clean commit: no defects must be allowed.
printf 'echo "hi"\n' > bad.sh
git add bad.sh
if git commit -q -m "clean" >/dev/null 2>&1; then
  check "hook allows a clean commit" "yes"
else
  check "hook allows a clean commit" "no"
fi

# 3. Syntax-error commit: broken shell must be rejected.
printf 'if [ 1 -eq 1 ]; then\n  echo oops\n' > broken.sh   # missing 'fi'
git add broken.sh
if git commit -q -m "broken" >/dev/null 2>&1; then
  check "hook blocks a commit with a shell syntax error" "no"
else
  check "hook blocks a commit with a shell syntax error" "yes"
fi

echo "Testing the pipeline ..."

# 4. Pipeline succeeds when every stage passes.
if bash "${lab_dir}/examples/pipeline.sh" >/dev/null 2>&1; then
  check "pipeline succeeds when all stages pass" "yes"
else
  check "pipeline succeeds when all stages pass" "no"
fi

# 5. Pipeline fails fast on a failing stage.
if bash "${lab_dir}/examples/pipeline.sh" test >/dev/null 2>&1; then
  check "pipeline fails fast on a failing stage" "no"
else
  check "pipeline fails fast on a failing stage" "yes"
fi

# 6. Fail fast really skips later stages: build/deploy must NOT appear.
ff_out="$(bash "${lab_dir}/examples/pipeline.sh" test 2>&1)"
if echo "${ff_out}" | grep -q "stage: build"; then
  check "later stages are skipped after a failure" "no"
else
  check "later stages are skipped after a failure" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
