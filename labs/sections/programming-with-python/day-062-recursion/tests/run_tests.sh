#!/usr/bin/env bash
# Tests for the Day 062 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Exercises the complete reference module (examples/recursion.py) across all
# five recursive subcommands: factorial (incl. the base case and a rejected
# negative), recursive list sum (incl. the empty-list base case), flatten of
# a nested list, treesum over a nested dict/list tree, and fib (naive vs
# memoized). Every check verifies BOTH the printed output and the exit code.
# It then imports the pure functions to check return values, and — the key
# recursion assertion — imports fib_naive and the memoized fib and asserts
# the naive version makes FAR MORE calls than the memoized version computes
# (a call-count comparison, not a fragile wall-clock timing). Finally it
# checks the learner's starter — structurally while exercises are unfinished,
# and to the same strict standard once they are complete. No network,
# non-interactive. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: do not let imported modules write __pycache__.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref="${lab_dir}/examples/recursion.py"
starter="${lab_dir}/starter/recursion.py"
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
# Runs the module and checks the exit code and that combined output contains
# the needle.
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

run_cli_checks() {
  local script="$1"
  echo "Testing ${script} ..."
  # factorial: recursive case and the base case, plus a rejected negative.
  check_run "factorial 5 = 120"          "${script}" 0 "factorial(5) = 120"   factorial --n 5
  check_run "factorial 0 = 1 (base case)" "${script}" 0 "factorial(0) = 1"    factorial --n 0
  check_run "factorial negative rejected" "${script}" 1 "undefined for negative" factorial --n -3
  # recursive list sum, incl. the empty-list base case.
  check_run "sum 1..5 = 15"              "${script}" 0 "= 15"                 sum --values 1,2,3,4,5
  check_run "sum empty = 0 (base case)"  "${script}" 0 "sum([]) = 0"          sum --values ""
  check_run "sum bad values rejected"    "${script}" 1 "comma-separated integers" sum --values 1,x,3
  # flatten a nested list to any depth.
  check_run "flatten nested list"        "${script}" 0 "flatten -> [1, 2, 3, 4, 5]" flatten --data "[1, [2, [3, 4]], 5]"
  check_run "flatten rejects bad JSON"   "${script}" 1 "not valid JSON"       flatten --data "[1, 2"
  # treesum walks a nested dict/list tree.
  check_run "treesum nested tree = 10"   "${script}" 0 "treesum -> 10"        treesum --data '{"a": 1, "b": {"c": 2, "d": [3, 4]}}'
  # fib: value, naive call count, and that memoized computes fewer.
  check_run "fib 10 value = 55"          "${script}" 0 "fib(10) = 55"         fib --n 10
  check_run "fib 10 naive = 177 calls"   "${script}" 0 "naive recursion: 177 calls" fib --n 10
  check_run "fib 10 memoized 11 computations" "${script}" 0 "memoized (lru_cache): 11 computations" fib --n 10
}

# --- Reference module: always tested strictly ---
run_cli_checks "${ref}"

# --- Import pure functions and check return values (importability payoff) ---
echo "Testing importability of examples/recursion.py ..."
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from recursion import factorial; \
assert factorial(0) == 1; assert factorial(5) == 120"; then
  check "import factorial computes 1 and 120" "yes"
else
  check "import factorial computes 1 and 120" "no"
fi
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from recursion import list_sum; \
assert list_sum([]) == 0; assert list_sum([1, 2, 3, 4, 5]) == 15"; then
  check "import list_sum computes 0 and 15" "yes"
else
  check "import list_sum computes 0 and 15" "no"
fi
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from recursion import flatten; \
assert flatten([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5]"; then
  check "import flatten handles deep nesting" "yes"
else
  check "import flatten handles deep nesting" "no"
fi
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from recursion import tree_sum; \
assert tree_sum({'a': 1, 'b': {'c': 2, 'd': [3, 4]}}) == 10; \
assert tree_sum({'x': 'skip', 'y': True, 'z': 5}) == 5"; then
  check "import tree_sum walks a tree and ignores non-numbers" "yes"
else
  check "import tree_sum walks a tree and ignores non-numbers" "no"
fi

# --- The key recursion assertion: memoization slashes the call count ---
# Robust: compares CALL COUNTS (naive calls vs memoized computations), never
# wall-clock time, so it is deterministic on every machine.
echo "Testing that memoization slashes the call count (examples/recursion.py) ..."
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from recursion import fib_naive, make_memoized_fib; \
c = [0]; v1 = fib_naive(25, c); naive = c[0]; \
fib = make_memoized_fib(); v2 = fib(25); misses = fib.cache_info().misses; \
assert v1 == v2 == 75025, ('values', v1, v2); \
assert misses == 26, ('unique computations', misses); \
assert naive > 50 * misses, ('naive should dwarf memoized', naive, misses)"; then
  check "memoized fib(25) computes 26 vs naive's 242785 calls" "yes"
else
  check "memoized fib(25) computes 26 vs naive's 242785 calls" "no"
fi

# --- Learner starter ---
echo "Testing starter/recursion.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/recursion.py still has unfinished exercises — testing structure only."
  grep -q 'def factorial' "${starter}" && check "starter defines factorial" "yes" || check "starter defines factorial" "no"
  grep -q 'def fib_naive' "${starter}" && check "starter defines fib_naive" "yes" || check "starter defines fib_naive" "no"
else
  run_cli_checks "${starter}"
  grep -q '__name__ == "__main__"' "${starter}" && check "starter has the main guard" "yes" || check "starter has the main guard" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
