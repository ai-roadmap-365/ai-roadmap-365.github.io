#!/usr/bin/env bash
# Tests for the Day 049 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Exercises the complete reference program (examples/converter.py) on known
# good and bad inputs, checking both the printed output and the process exit
# code, then imports a function from the module and checks its return value.
# Finally it checks the learner's starter: structurally while exercises are
# unfinished, and to the same strict standard once they are complete.
# No network, non-interactive. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: do not let imported modules write __pycache__.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref="${lab_dir}/examples/converter.py"
starter="${lab_dir}/starter/converter.py"
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

# check_run <label> <script> <expect_exit> <needle> <arg...>
# Runs the program, checks its exit code equals expect_exit and that its
# combined output contains needle.
check_run() {
  local label="$1" script="$2" expect_exit="$3" needle="$4"
  shift 4
  local out code
  out="$(python3 "${script}" "$@" 2>&1)"
  code=$?
  if [ "${code}" -eq "${expect_exit}" ] && printf '%s' "${out}" | grep -qF "${needle}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (exit ${code}, expected ${expect_exit}; output: ${out})"
  fi
}

run_program_checks() {
  local script="$1"
  echo "Testing ${script} ..."
  # Good inputs: correct conversion, exit 0.
  check_run "100 C -> 212.0 F"      "${script}" 0 "100.0 C = 212.0 F" 100 C
  check_run "32 F -> 0.0 C"         "${script}" 0 "32.0 F = 0.0 C"    32 F
  check_run "98.6 F -> 37.0 C"      "${script}" 0 "98.6 F = 37.0 C"   98.6 F
  # Bad inputs: clear error, non-zero exit.
  check_run "non-number rejected"   "${script}" 1 "is not a number"   hot C
  check_run "bad unit rejected"     "${script}" 1 "unit must be C or F" 100 K
  check_run "wrong arg count"       "${script}" 1 "expected 2 arguments" 100
  check_run "below absolute zero"   "${script}" 1 "below absolute zero" -300 C
}

# --- Reference program: always tested strictly ---
run_program_checks "${ref}"

# --- Import a function and check its return value (main-guard payoff) ---
echo "Testing importability of examples/converter.py ..."
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from converter import celsius_to_fahrenheit; \
assert celsius_to_fahrenheit(100) == 212.0"; then
  check "import celsius_to_fahrenheit(100) == 212.0" "yes"
else
  check "import celsius_to_fahrenheit(100) == 212.0" "no"
fi
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from converter import fahrenheit_to_celsius; \
assert fahrenheit_to_celsius(32) == 0.0"; then
  check "import fahrenheit_to_celsius(32) == 0.0" "yes"
else
  check "import fahrenheit_to_celsius(32) == 0.0" "no"
fi

# --- Learner starter ---
echo "Testing starter/converter.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/converter.py still has unfinished exercises — testing structure only."
  # Structural checks while the learner works.
  grep -q 'def celsius_to_fahrenheit' "${starter}" && check "starter defines celsius_to_fahrenheit" "yes" || check "starter defines celsius_to_fahrenheit" "no"
  grep -q 'def main' "${starter}" && check "starter defines main" "yes" || check "starter defines main" "no"
else
  # Learner finished: hold the starter to the same strict standard.
  run_program_checks "${starter}"
  grep -q '__name__ == "__main__"' "${starter}" && check "starter has the main guard" "yes" || check "starter has the main guard" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
