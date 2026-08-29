#!/usr/bin/env bash
# Mark the ten exercises in starter/01_timezones.py.
#
#   bash starter/02_check.sh                    # marks your starter file
#   bash starter/02_check.sh some/other/file.py # marks a file of your choosing
#
# Prints "N of 10 exercises complete." and exits 0 only when N is 10.
# Set PYTHON=/path/to/python3 if python3 is somewhere unusual.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${1:-${lab_dir}/starter/01_timezones.py}"

python_bin="${PYTHON:-$(command -v python3 || true)}"
if [ -z "${python_bin}" ] || [ ! -x "${python_bin}" ]; then
  echo "python3 was not found. Install Python 3.11+ or set PYTHON=/path/to/python3."
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
"${python_bin}" "${lab_dir}/starter/check_exercises.py" "${target}"
