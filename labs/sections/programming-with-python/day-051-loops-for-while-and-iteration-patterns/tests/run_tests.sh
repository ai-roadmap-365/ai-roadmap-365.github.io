#!/usr/bin/env bash
# Tests for the Day 051 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Exercises the complete reference program (examples/patterns.py) on the five
# iteration patterns, feeding numbers on standard input and checking both the
# printed output and the process exit code. It then imports two pattern
# functions and checks their return values, and finally checks the learner's
# starter: structurally while exercises are unfinished, and to the same strict
# standard once they are complete. No network, non-interactive. Exits 0 only
# if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref="${lab_dir}/examples/patterns.py"
starter="${lab_dir}/starter/patterns.py"
data="3 1 4 1 5 9 2 6"
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

# check_stdin <label> <script> <input> <expect_exit> <needle> <cmd> [args...]
# Pipes <input> to the program's stdin, checks its exit code and that its
# combined output contains <needle>.
check_stdin() {
  local label="$1" script="$2" input="$3" expect_exit="$4" needle="$5"
  shift 5
  local out code
  out="$(printf '%s' "${input}" | python3 "${script}" "$@" 2>&1)"
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
  # demo needs no stdin; the rest read numbers from stdin.
  check_stdin "demo shows all patterns" "${script}" ""      0 "count=8 sum=31"          demo
  check_stdin "total (accumulate)"      "${script}" "${data}" 0 "count=8 sum=31"         total
  check_stdin "filter > 4"              "${script}" "${data}" 0 "[5, 9, 6]"              filter 4
  check_stdin "transform (squares)"     "${script}" "${data}" 0 "[9, 1, 16, 1, 25, 81, 4, 36]" transform
  check_stdin "search 5 found early"    "${script}" "${data}" 0 "found 5 at index 4 after 5 comparisons" search 5
  check_stdin "search 7 not found"      "${script}" "${data}" 1 "7 not found after 8 comparisons" search 7
  check_stdin "histogram bars"          "${script}" "1 2 2 3 3 3" 0 "3 | ###"           histogram
  # Bad input is validated at the boundary.
  check_stdin "non-number rejected"     "${script}" "1 x 3"   1 "is not a whole number"  total
  check_stdin "unknown command rejected" "${script}" "1 2 3"  1 "unknown command"        frobnicate
  check_stdin "filter missing arg"      "${script}" "1 2 3"   1 "filter needs one threshold" filter
}

# --- Reference program: always tested strictly ---
run_program_checks "${ref}"

# --- Import functions and check return values (module is importable) ---
echo "Testing importability of examples/patterns.py ..."
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from patterns import accumulate_total; \
assert accumulate_total([3, 1, 4, 1, 5, 9, 2, 6]) == (8, 31)"; then
  check "import accumulate_total -> (8, 31)" "yes"
else
  check "import accumulate_total -> (8, 31)" "no"
fi
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from patterns import linear_search; \
assert linear_search([3, 1, 4, 1, 5], 5) == (4, 5); \
assert linear_search([1, 2, 3], 9) == (-1, 3)"; then
  check "import linear_search early-exit + not-found" "yes"
else
  check "import linear_search early-exit + not-found" "no"
fi

# --- Learner starter ---
echo "Testing starter/patterns.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/patterns.py still has unfinished exercises — testing structure only."
  grep -q 'def accumulate_total' "${starter}" && check "starter defines accumulate_total" "yes" || check "starter defines accumulate_total" "no"
  grep -q 'def build_histogram' "${starter}" && check "starter defines build_histogram" "yes" || check "starter defines build_histogram" "no"
else
  run_program_checks "${starter}"
  grep -q '__name__ == "__main__"' "${starter}" && check "starter has the main guard" "yes" || check "starter has the main guard" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
