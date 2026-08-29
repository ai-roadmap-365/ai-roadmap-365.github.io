#!/usr/bin/env bash
# How far through the twelve exercises are you?
#
#   bash starter/03_check.sh
#
# It imports starter/01_logging.py and starter/02_config.py, calls your
# functions, captures log output into a buffer, and compares real values. It
# never looks at HOW you wrote anything, so any correct implementation passes.
#
# Exit status: 0 when all twelve pass, 1 otherwise.
#
# To check the reference answers instead of your own work:
#   bash starter/03_check.sh examples/07_solution_logging.py examples/08_solution_config.py
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON:-$(command -v python3 || true)}"

if [ -z "${python_bin}" ] || [ ! -x "${python_bin}" ]; then
  echo "python3 was not found. Install Python 3.11+ or set PYTHON=/path/to/python3."
  exit 1
fi

logging_file="${1:-${lab_dir}/starter/01_logging.py}"
config_file="${2:-${lab_dir}/starter/02_config.py}"

export PYTHONDONTWRITEBYTECODE=1

echo "Day 097 — Say It Where Someone Will Read It"
echo "python3: $("${python_bin}" -c 'import sys; print(sys.version.split()[0])')"
echo
echo "Checking:"
echo "  $(basename "$(dirname "${logging_file}")")/$(basename "${logging_file}")"
echo "  $(basename "$(dirname "${config_file}")")/$(basename "${config_file}")"
echo

"${python_bin}" "${lab_dir}/tests/check_exercises.py" "${logging_file}" "${config_file}"
status=$?

if [ "${status}" -ne 0 ]; then
  echo
  echo "Keep going. Each 'not yet' line above says what it wanted and what it got."
  echo "The brief is starter/00_brief.md; the reference answers are in examples/,"
  echo "and are worth more after you have tried than before."
fi
exit "${status}"
