#!/usr/bin/env bash
# Day 043 lab — YOUR working file.
#
# The scaffolding (temp directory, cleanup, the interpreter check) is done for
# you. Your job is the four numbered exercises below: replace each placeholder
# line with the single command named in its comment. The completed reference is
# examples/venv_demo.sh — try to do it yourself first, then compare.
#
# Everything here is OFFLINE: no network is needed at any step.
#
# Run from the lab directory:
#   bash starter/venv_demo.sh
set -euo pipefail

# --- Scaffolding (already done for you) ---
work_dir="$(mktemp -d "${TMPDIR:-/tmp}/venv-demo.XXXXXX")"
cleanup() {
  type deactivate >/dev/null 2>&1 && deactivate || true
  rm -rf "${work_dir}"
}
trap cleanup EXIT

echo "=== Virtual Environment Demo (starter) ==="
echo "Working directory: ${work_dir}"
cd "${work_dir}"

echo
echo "--- The interpreter (already done) ---"
python3 --version

echo
echo "--- Exercise 1: create a virtual environment named .venv ---"
# Replace the next line with:  python3 -m venv .venv
echo "EXERCISE_1_NOT_DONE: create the .venv here"

echo
echo "--- Exercise 2: activate the environment ---"
# Replace the next line with:  source .venv/bin/activate
echo "EXERCISE_2_NOT_DONE: activate the .venv here"

echo
echo "--- Exercise 3: prove isolation ---"
# After activating, these two commands prove the environment is active.
# Replace the next line with BOTH commands (one per line):
#   command -v python
#   python -c 'import sys; print("sys.prefix:", sys.prefix)'
echo "EXERCISE_3_NOT_DONE: print 'which python' and sys.prefix here"

echo
echo "--- Exercise 4: deactivate the environment ---"
# Replace the next line with:  deactivate
echo "EXERCISE_4_NOT_DONE: deactivate the .venv here"

echo
echo "=== Done — temp directory will be removed on exit ==="
echo "When all four EXERCISE_*_NOT_DONE lines are replaced, run tests/run_tests.sh."
