#!/usr/bin/env bash
# hook_demo.sh — a complete, offline walkthrough of a real pre-commit hook.
#
# It creates a throwaway git repository in a temporary directory, installs the
# reference pre-commit hook, then:
#   2. attempts to commit a file with trailing whitespace  -> the hook BLOCKS it
#   3. fixes the file and commits cleanly                   -> the hook ALLOWS it
#   4. runs the fail-fast pipeline both green and forced to fail
# The temporary repository is deleted on exit. No network, no sudo, no changes
# outside the temp directory.
set -uo pipefail

# Locate this script's directory so we can find pre-commit and pipeline.sh
# even after we cd into the temporary repository.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create an isolated, self-cleaning workspace.
work="$(mktemp -d 2>/dev/null || mktemp -d -t hookdemo)"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

cd "${work}"
git init -q
# A local identity so commits work without touching your global git config.
git config user.email "learner@example.local"
git config user.name "Automation Learner"

echo "=== 1. Installing the pre-commit hook ==="
mkdir -p .git/hooks
cp "${here}/pre-commit" .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
echo "Hook installed at .git/hooks/pre-commit (executable)."
echo

echo "=== 2. Attempting a BAD commit (trailing whitespace) ==="
# The three trailing spaces after "hello" are the defect the hook catches.
printf 'echo "hello"   \n' > bad.sh
git add bad.sh
if git commit -q -m "add bad.sh" 2>&1; then
  echo "UNEXPECTED: the bad commit was allowed."
else
  echo "Result: the hook BLOCKED the bad commit (exit non-zero), as intended."
fi
echo

echo "=== 3. Fixing the file and committing CLEAN ==="
printf 'echo "hello"\n' > bad.sh   # same file, trailing whitespace removed
git add bad.sh
if git commit -q -m "add clean script" 2>&1; then
  echo "Result: the hook ALLOWED the clean commit."
else
  echo "UNEXPECTED: the clean commit was blocked."
fi
echo

echo "=== 4. Running the pipeline ==="
echo "--- pipeline: all stages ---"
bash "${here}/pipeline.sh" || true
echo "--- pipeline: forced failure at 'test' ---"
bash "${here}/pipeline.sh" test || true
echo

echo "Demo complete. Temporary repository at ${work} will now be removed."
