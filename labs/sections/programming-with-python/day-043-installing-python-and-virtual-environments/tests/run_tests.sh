#!/usr/bin/env bash
# Tests for the Day 043 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies, entirely OFFLINE, that a virtual environment can be created, that
# activation isolates the interpreter (sys.prefix points inside the venv), and
# that cleanup leaves nothing behind. Also checks that the completed example
# script runs and that the starter still ships its four exercises.
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

echo "Testing venv creation and isolation (offline) ..."

# Python 3 must be available.
if command -v python3 >/dev/null 2>&1; then
  check "python3 is available" "yes"
else
  check "python3 is available" "no"
  echo
  echo "${checks} checks, ${failures} failure(s)."
  exit 1
fi

# 1. A venv can be created in a throwaway temp directory.
# Resolve symlinks so the path lines up with what sys.prefix reports.
work_dir="$(mktemp -d "${TMPDIR:-/tmp}/venv-test.XXXXXX")"
work_dir="$(cd "${work_dir}" && pwd -P)"
created="no"
if python3 -m venv "${work_dir}/.venv" >/dev/null 2>&1; then created="yes"; fi
check "python3 -m venv creates an environment" "${created}"

# 2. The environment has an activate script and a python interpreter.
[ -f "${work_dir}/.venv/bin/activate" ] && check "environment has bin/activate" "yes" || check "environment has bin/activate" "no"
[ -x "${work_dir}/.venv/bin/python" ] && check "environment has its own python" "yes" || check "environment has its own python" "no"

# 3. After activation, sys.prefix points INSIDE the venv.
prefix=""
# shellcheck disable=SC1090
if source "${work_dir}/.venv/bin/activate" 2>/dev/null; then
  prefix="$(python -c 'import sys; print(sys.prefix)' 2>/dev/null)"
  which_python="$(command -v python)"
  type deactivate >/dev/null 2>&1 && deactivate || true
fi
case "${prefix}" in
  "${work_dir}"/.venv*) check "sys.prefix points inside the venv" "yes" ;;
  *) check "sys.prefix points inside the venv" "no" ;;
esac
case "${which_python:-}" in
  "${work_dir}"/.venv/bin/python) check "activation redirects 'which python' into the venv" "yes" ;;
  *) check "activation redirects 'which python' into the venv" "no" ;;
esac

# 4. Cleanup leaves nothing behind.
rm -rf "${work_dir}"
[ ! -e "${work_dir}" ] && check "cleanup leaves nothing behind" "yes" || check "cleanup leaves nothing behind" "no"

# 5. The completed example script runs end to end and confirms isolation.
if out="$(bash "${lab_dir}/examples/venv_demo.sh" 2>&1)"; then
  check "examples/venv_demo.sh exits successfully" "yes"
  echo "${out}" | grep -q "the environment is isolated" && check "example confirms isolation" "yes" || check "example confirms isolation" "no"
else
  check "examples/venv_demo.sh exits successfully" "no"
  echo "${out}" | sed 's/^/    /'
fi

# 6. The example leaves no temp directory behind (it cleans up its own).
leftover="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'venv-demo.*' 2>/dev/null | wc -l | tr -d ' ')"
[ "${leftover}" = "0" ] && check "example cleans up its temp directory" "yes" || check "example cleans up its temp directory" "no"

# 7. The starter still ships its four exercises for the learner.
starter="${lab_dir}/starter/venv_demo.sh"
missing=0
for n in 1 2 3 4; do
  grep -q "EXERCISE_${n}_NOT_DONE" "${starter}" || missing=1
done
[ "${missing}" = "0" ] && check "starter ships all four exercises" "yes" || check "starter ships all four exercises" "no"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
