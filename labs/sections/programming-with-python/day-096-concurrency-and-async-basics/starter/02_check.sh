#!/usr/bin/env bash
# How far through the eight exercises are you?
#
#   bash starter/02_check.sh                          # checks your work
#   bash starter/02_check.sh examples/07_solutions.py  # checks the reference
#
# Exits 0 only when all eight are complete, so it cannot be mistaken for
# finished. Every check is a real value or a real speed ratio; none of them
# looks at how you wrote anything.
set -u

starter_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(cd "${starter_dir}/.." && pwd)"

python_bin="${PYTHON:-$(command -v python3 || true)}"
if [ -z "${python_bin}" ] || [ ! -x "${python_bin}" ]; then
  echo "python3 was not found. Install Python 3.11 or newer, or set PYTHON=/path/to/python3."
  exit 2
fi

# Keep the lab directory clean: no __pycache__ left behind by the import.
export PYTHONDONTWRITEBYTECODE=1

if [ "$#" -ge 1 ]; then
  target="$1"
  case "${target}" in
    /*) ;;
    *) target="${lab_dir}/${target}" ;;
  esac
else
  target="${starter_dir}/01_exercises.py"
fi

"${python_bin}" "${starter_dir}/_progress.py" "${target}"
