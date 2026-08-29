#!/usr/bin/env bash
# Tests for the Day 052 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Exercises the complete reference program (examples/toolkit.py) on known
# inputs, imports each toolkit function and checks its return value, and — the
# heart of this lab — proves the difference between in-place mutation and
# returning a new list (sorted vs .sort(), aliasing vs copy). Finally it checks
# the learner's starter: structurally while exercises are unfinished, and to the
# same strict standard once they are complete.
# No network, non-interactive. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: do not let imported modules write __pycache__.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref="${lab_dir}/examples/toolkit.py"
starter="${lab_dir}/starter/toolkit.py"
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
  check_run "pipeline runs, exit 0"     "${script}" 0 "built:    [88, 72, 95, 72, 60, 95, 81]"
  check_run "top 3 via sort+slice"      "${script}" 0 "top 3:    [95, 95, 88]"
  check_run "stride slice [::2]"        "${script}" 0 "stride:   [88, 95, 60, 81]"
  check_run "negative-index slice [-2:]" "${script}" 0 "last 2:   [95, 81]"
  check_run "stable sort by length"     "${script}" 0 "by len:   ['fig', 'fig', 'pear', 'kiwi', 'plum', 'apple']"
  check_run "order-preserving dedupe"   "${script}" 0 "unique:   ['pear', 'fig', 'apple', 'kiwi', 'plum']"
  check_run "flatten a matrix"          "${script}" 0 "flat:     [1, 2, 3, 4, 5, 6]"
  check_run "copy stayed safe"          "${script}" 0 "original: [10, 20, 30]"
}

# --- Reference program: always tested strictly ---
run_program_checks "${ref}"

# --- Import each function and check its return value ---
echo "Testing importability and return values of examples/toolkit.py ..."
if python3 -c "
import sys; sys.path.insert(0, '${lab_dir}/examples'); import toolkit
assert toolkit.dedupe([1, 1, 2, 1, 3]) == [1, 2, 3]
assert toolkit.flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]
assert toolkit.sort_by_length(['bbb', 'a', 'cc']) == ['a', 'cc', 'bbb']
assert toolkit.top_n([3, 9, 1, 7, 4], 2) == [9, 7]
assert toolkit.with_appended([1, 2], 3) == [1, 2, 3]
"; then
  check "each function returns the expected list" "yes"
else
  check "each function returns the expected list" "no"
fi

# --- The core lesson: in-place mutation vs returning a new list ---
echo "Testing in-place vs new-list behaviour ..."
if python3 -c "
import sys; sys.path.insert(0, '${lab_dir}/examples'); import toolkit
# sorted() returns a NEW list; the original is unchanged.
xs = [3, 1, 2]; ys = sorted(xs)
assert ys == [1, 2, 3] and xs == [3, 1, 2]
# .sort() mutates IN PLACE and returns None.
zs = [3, 1, 2]; ret = zs.sort()
assert ret is None and zs == [1, 2, 3]
# Aliasing: assignment shares one list, so a change shows through both names.
p = [1]; q = p; q.append(2)
assert p == [1, 2]
# A slice copy breaks the alias: the original is protected.
m = [1]; n = m[:]; n.append(2)
assert m == [1] and n == [1, 2]
# with_appended must NOT mutate its input (copy-before-mutate).
a = [1, 2]; b = toolkit.with_appended(a, 3)
assert b == [1, 2, 3] and a == [1, 2]
# dedupe/flatten/sort_by_length/top_n leave their inputs unchanged.
src = [1, 1, 2]; toolkit.dedupe(src); assert src == [1, 1, 2]
nested = [[1], [2]]; toolkit.flatten(nested); assert nested == [[1], [2]]
print('all in-place/new-list assertions passed')
"; then
  check "sorted vs .sort(), aliasing vs copy, no input mutation" "yes"
else
  check "sorted vs .sort(), aliasing vs copy, no input mutation" "no"
fi

# --- Learner starter ---
echo "Testing starter/toolkit.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/toolkit.py still has unfinished exercises — testing structure only."
  grep -q 'def dedupe' "${starter}" && check "starter defines dedupe" "yes" || check "starter defines dedupe" "no"
  grep -q 'def with_appended' "${starter}" && check "starter defines with_appended" "yes" || check "starter defines with_appended" "no"
else
  run_program_checks "${starter}"
  if python3 -c "
import sys; sys.path.insert(0, '${lab_dir}/starter'); import toolkit
a = [1, 2]; b = toolkit.with_appended(a, 3)
assert b == [1, 2, 3] and a == [1, 2]
assert toolkit.dedupe([1, 1, 2]) == [1, 2]
"; then
    check "starter copies before mutating (input unchanged)" "yes"
  else
    check "starter copies before mutating (input unchanged)" "no"
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
