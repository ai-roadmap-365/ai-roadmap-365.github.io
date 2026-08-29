#!/usr/bin/env bash
# Day 043 lab — completed reference implementation.
# Creates a virtual environment in a temporary directory, proves that
# activation isolates python/pip, writes a requirements.txt, then
# deactivates and cleans everything up. Fully OFFLINE: no network needed.
#
# Run from the lab directory:
#   bash examples/venv_demo.sh
set -euo pipefail

# Work in a throwaway temp directory so nothing is left in your project.
# Resolve symlinks (on macOS /var is a link to /private/var) so later path
# comparisons against sys.prefix line up exactly.
work_dir="$(mktemp -d "${TMPDIR:-/tmp}/venv-demo.XXXXXX")"
work_dir="$(cd "${work_dir}" && pwd -P)"
# Always clean up, even if a command fails partway through.
cleanup() {
  # Leaving an active venv is harmless in a subshell, but deactivate if we can.
  type deactivate >/dev/null 2>&1 && deactivate || true
  rm -rf "${work_dir}"
}
trap cleanup EXIT

echo "=== Virtual Environment Demo ==="
echo "Working directory: ${work_dir}"
cd "${work_dir}"

echo
echo "--- Step 1: the interpreter ---"
python3 --version

echo
echo "--- Step 2: create the virtual environment (offline) ---"
python3 -m venv .venv
echo "Created .venv/ — contents of .venv/bin (or Scripts on Windows):"
ls .venv/bin >/dev/null 2>&1 && ls .venv/bin | sed 's/^/    /' || true

echo
echo "--- Step 3: which python BEFORE activation ---"
before="$(command -v python || echo '(no python on PATH)')"
echo "which python -> ${before}"

echo
echo "--- Step 4: activate and prove isolation ---"
# shellcheck disable=SC1091
source .venv/bin/activate
after="$(command -v python)"
echo "which python -> ${after}"
echo "which pip    -> $(command -v pip)"
prefix="$(python -c 'import sys; print(sys.prefix)')"
echo "sys.prefix   -> ${prefix}"

# Confirm sys.prefix really points inside our .venv folder.
case "${prefix}" in
  "${work_dir}"/.venv*) echo "OK: sys.prefix is inside the .venv — the environment is isolated." ;;
  *) echo "WARNING: sys.prefix is not inside .venv" ; exit 1 ;;
esac

echo
echo "--- Step 5: record dependencies in requirements.txt ---"
# A fresh venv installs no third-party packages; document that we rely on the
# standard library only, and pin the Python version used to build it.
{
  echo "# Built and verified with $(python --version)"
  echo "# This project uses only the Python standard library — no PyPI packages required."
} > requirements.txt
echo "requirements.txt:"
sed 's/^/    /' requirements.txt

echo
echo "--- Step 6: deactivate ---"
deactivate
echo "which python -> $(command -v python || echo '(no python on PATH)')  (back to global)"

echo
echo "=== Demo complete — temp directory will be removed on exit ==="
