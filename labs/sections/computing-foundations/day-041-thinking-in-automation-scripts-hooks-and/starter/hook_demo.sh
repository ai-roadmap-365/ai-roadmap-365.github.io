#!/usr/bin/env bash
# hook_demo.sh (STARTER) — build your own pre-commit hook and pipeline.
#
# This skeleton already sets up a throwaway git repository and installs a hook
# with ONE check (trailing whitespace). Complete the four numbered exercises
# below. The finished reference version is examples/hook_demo.sh — try the
# exercises yourself first, then compare.
#
# Run it at any time to see your progress:
#   bash starter/hook_demo.sh
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
work="$(mktemp -d 2>/dev/null || mktemp -d -t hookstart)"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

cd "${work}"
git init -q
git config user.email "learner@example.local"
git config user.name "Automation Learner"
mkdir -p .git/hooks

# -------------------------------------------------------------------------
# EXERCISE 1: write a hook check.
# The hook below already rejects trailing whitespace. Add a SECOND check that
# rejects any staged *.sh file with a shell syntax error. Inside the `case`
# block, use `bash -n "${f}"` (it parses a script without running it) and set
# `fail=1` plus an explanatory message if it fails. Uncomment and complete the
# marked lines.
# -------------------------------------------------------------------------
cat > .git/hooks/pre-commit <<'HOOK'
#!/usr/bin/env bash
set -u
fail=0
staged="$(git diff --cached --name-only --diff-filter=ACM)"
for f in ${staged}; do
  [ -f "${f}" ] || continue

  # Check 1 (provided): trailing whitespace.
  if grep -nE '[ 	]+$' "${f}" >/dev/null 2>&1; then
    echo "pre-commit: trailing whitespace in ${f}" >&2
    fail=1
  fi

  # Check 2 (EXERCISE 1): shell syntax for *.sh files.
  case "${f}" in
    *.sh)
      # if ! bash -n "${f}" 2>/dev/null; then
      #   echo "pre-commit: shell syntax error in ${f}" >&2
      #   fail=1
      # fi
      : # remove this no-op line once you complete the check above
      ;;
  esac
done
if [ "${fail}" -ne 0 ]; then
  echo "pre-commit: commit rejected." >&2
  exit 1
fi
echo "pre-commit: quality gate passed."
exit 0
HOOK
chmod +x .git/hooks/pre-commit
echo "Hook installed."

# -------------------------------------------------------------------------
# EXERCISE 2: make it block a bad commit.
# Create a file with trailing whitespace, stage it, and try to commit. The hook
# should reject it. The commands are given; run the script to see the result.
# -------------------------------------------------------------------------
printf 'echo "hello"   \n' > bad.sh    # note the trailing spaces
git add bad.sh
if git commit -q -m "add bad.sh" 2>&1; then
  echo "The bad commit was allowed — check your hook."
else
  echo "Good: the hook BLOCKED the bad commit."
fi

# -------------------------------------------------------------------------
# EXERCISE 3: fix the file and commit clean.
# Overwrite bad.sh with a clean version (no trailing whitespace), stage it, and
# commit. The hook should allow it.
# -------------------------------------------------------------------------
printf 'echo "hello"\n' > bad.sh
git add bad.sh
if git commit -q -m "add clean script" 2>&1; then
  echo "Good: the hook ALLOWED the clean commit."
else
  echo "The clean commit was blocked — check your hook."
fi

# -------------------------------------------------------------------------
# EXERCISE 4: add a pipeline stage.
# The stage list below runs lint -> test -> build. Add a fourth stage, "deploy",
# so the list reads: lint test build deploy. Then run the script and watch the
# pipeline print your new stage.
# -------------------------------------------------------------------------
echo "--- pipeline ---"
for stage in lint test build; do   # EXERCISE 4: add 'deploy' to this list
  echo "==> stage: ${stage}"
done
echo "Pipeline finished."
