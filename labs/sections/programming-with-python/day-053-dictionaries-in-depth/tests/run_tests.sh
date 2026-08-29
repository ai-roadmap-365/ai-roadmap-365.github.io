#!/usr/bin/env bash
# Tests for the Day 053 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Exercises the complete reference program (examples/wordstats.py) on known
# inputs, checking both the printed output and the process exit code, then
# imports functions from the module and checks their return values. Finally it
# checks the learner's starter: structurally while exercises are unfinished,
# and to the same strict standard once they are complete.
# No network, non-interactive. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: do not let imported modules write __pycache__.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref="${lab_dir}/examples/wordstats.py"
starter="${lab_dir}/starter/wordstats.py"
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
  # Counting: correct counts, insertion order, most-common line, exit 0.
  check_run "a a b -> a: 2"          "${script}" 0 "a: 2"                "a a b"
  check_run "a a b -> most common a" "${script}" 0 "most common: a (2)"  "a a b"
  check_run "counts in insertion order" "${script}" 0 "the: 3"           "the cat sat on the mat the cat"
  # Records: grouping with setdefault + dict comprehension, exit 0.
  check_run "records: engineers group" "${script}" 0 "engineers: ['Ada', 'Alan']" --records
  check_run "records: admirals group"  "${script}" 0 "admirals: ['Grace']"        --records
  check_run "records: A-M comprehension" "${script}" 0 "names A-M: ['Ada', 'Alan', 'Grace']" --records
  # Bad input: no argument -> clear error, non-zero exit.
  check_run "no argument rejected"   "${script}" 1 "expected text to count"
}

# --- Reference program: always tested strictly ---
run_program_checks "${ref}"

# --- Import functions and check return values (main-guard payoff) ---
echo "Testing importability of examples/wordstats.py ..."
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from wordstats import count_words; \
assert count_words('a b a') == {'a': 2, 'b': 1}"; then
  check "import count_words('a b a') == {'a': 2, 'b': 1}" "yes"
else
  check "import count_words('a b a') == {'a': 2, 'b': 1}" "no"
fi
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from wordstats import most_common; \
assert most_common({'x': 2, 'y': 2}) == ('x', 2)"; then
  check "import most_common ties to first seen" "yes"
else
  check "import most_common ties to first seen" "no"
fi

# --- Learner starter ---
echo "Testing starter/wordstats.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/wordstats.py still has unfinished exercises — testing structure only."
  grep -q 'def count_words' "${starter}" && check "starter defines count_words" "yes" || check "starter defines count_words" "no"
  grep -q 'def group_by_role' "${starter}" && check "starter defines group_by_role" "yes" || check "starter defines group_by_role" "no"
else
  # Learner finished: hold the starter to the same strict standard.
  run_program_checks "${starter}"
  grep -q '__name__ == "__main__"' "${starter}" && check "starter has the main guard" "yes" || check "starter has the main guard" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
