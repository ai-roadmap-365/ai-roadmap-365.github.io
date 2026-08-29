#!/usr/bin/env bash
# Tests for the Day 054 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Exercises the complete reference program (examples/collections_tool.py) on
# known good and bad inputs, checking both the printed output and the process
# exit code, then imports functions from the module and checks their return
# values (dedupe returns an immutable tuple; compare's set algebra is correct).
# Finally it checks the learner's starter: structurally while exercises are
# unfinished, and to the same strict standard once they are complete.
# No network, non-interactive. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: do not let imported modules write __pycache__.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref="${lab_dir}/examples/collections_tool.py"
starter="${lab_dir}/starter/collections_tool.py"
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
  # Good input: dedupe count, set algebra, exit 0.
  check_run "A dedupes 4->3"        "${script}" 0 "List A: 4 items read, 3 unique" "apple,banana,apple,cherry" "banana,cherry,date,date"
  check_run "common intersection"   "${script}" 0 "Common (A & B): banana, cherry" "apple,banana,apple,cherry" "banana,cherry,date,date"
  check_run "only in A difference"  "${script}" 0 "Only in A (A - B): apple"       "apple,banana,apple,cherry" "banana,cherry,date,date"
  check_run "only in B difference"  "${script}" 0 "Only in B (B - A): date"        "apple,banana,apple,cherry" "banana,cherry,date,date"
  check_run "symmetric difference"  "${script}" 0 "Symmetric difference (A ^ B): apple, date" "apple,banana,apple,cherry" "banana,cherry,date,date"
  check_run "empty group -> (none)" "${script}" 0 "Only in A (A - B): (none)"      "banana" "banana,cherry"
  # Bad inputs: clear error, non-zero exit.
  check_run "wrong arg count"       "${script}" 1 "expected 2 arguments" "apple,banana"
  check_run "empty list rejected"   "${script}" 1 "at least one item"    " , ," "banana"
}

# --- Reference program: always tested strictly ---
run_program_checks "${ref}"

# --- Import functions and check return values (main-guard payoff) ---
echo "Testing importability of examples/collections_tool.py ..."
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from collections_tool import dedupe; \
result = dedupe(('a', 'a', 'b', 'c', 'b')); \
assert result == ('a', 'b', 'c'), result; \
assert isinstance(result, tuple), 'dedupe must return an immutable tuple'"; then
  check "import dedupe returns sorted immutable tuple" "yes"
else
  check "import dedupe returns sorted immutable tuple" "no"
fi
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from collections_tool import compare; \
r = compare(('a', 'b', 'c'), ('b', 'c', 'd')); \
assert r.common == ('b', 'c'), r.common; \
assert r.only_in_a == ('a',), r.only_in_a; \
assert r.symmetric == ('a', 'd'), r.symmetric"; then
  check "import compare set algebra correct" "yes"
else
  check "import compare set algebra correct" "no"
fi

# --- Learner starter ---
echo "Testing starter/collections_tool.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/collections_tool.py still has unfinished exercises — testing structure only."
  # Structural checks while the learner works.
  grep -q 'def parse_items' "${starter}" && check "starter defines parse_items" "yes" || check "starter defines parse_items" "no"
  grep -q 'def compare' "${starter}" && check "starter defines compare" "yes" || check "starter defines compare" "no"
else
  # Learner finished: hold the starter to the same strict standard.
  run_program_checks "${starter}"
  grep -q '__name__ == "__main__"' "${starter}" && check "starter has the main guard" "yes" || check "starter has the main guard" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
