#!/usr/bin/env bash
# Tests for the Day 057 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The library is a set of PURE functions, so the tests are simple: import a
# function, call it, and assert on the value it returns. Every check drives
# real behaviour — return values, a returned tuple, default and keyword
# arguments, purity (calling twice gives the same answer and does not mutate
# the input), the mutable-default-argument trap, and that every public
# function carries a docstring. It first tests the complete reference
# (examples/library.py), then the learner's starter — structurally while the
# exercises are unfinished, and to the same strict standard once they are
# complete. No network, non-interactive. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: no __pycache__ from the imports below.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref_dir="${lab_dir}/examples"
starter_dir="${lab_dir}/starter"
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

# assert <dir> <label> <python-assertion-body>
# Runs a python snippet with library.py importable from <dir>. A small
# _raises(func, arg) helper is provided for "must raise ValueError" checks.
# The snippet fails the check if it raises anything or exits non-zero.
assert() {
  local dir="$1" label="$2" body="$3"
  if python3 -c "import sys; sys.path.insert(0, '${dir}')
from library import *
def _raises(func, arg):
    try:
        func(arg)
        return False
    except ValueError:
        return True
${body}" 2>/dev/null; then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
}

run_library_checks() {
  local dir="$1"
  echo "Testing ${dir}/library.py ..."

  # --- Return values ---
  assert "${dir}" "word_count returns 4"            "assert word_count('the quick brown fox') == 4"
  assert "${dir}" "word_count of blanks returns 0"  "assert word_count('   ') == 0"
  assert "${dir}" "normalize_whitespace collapses"  "assert normalize_whitespace('  a   b  ') == 'a b'"
  assert "${dir}" "reverse_words reverses order"    "assert reverse_words('one two three') == 'three two one'"
  assert "${dir}" "celsius_to_fahrenheit(100)=212"  "assert celsius_to_fahrenheit(100) == 212.0"
  assert "${dir}" "celsius_to_fahrenheit(0)=32"     "assert celsius_to_fahrenheit(0) == 32.0"
  assert "${dir}" "mean([2,4,6]) == 4.0"            "assert mean([2, 4, 6]) == 4.0"

  # --- Default and keyword arguments ---
  assert "${dir}" "clamp uses default range [0,1]"  "assert clamp(1.5) == 1.0"
  assert "${dir}" "clamp with keyword range"        "assert clamp(-3, low=-10, high=10) == -3"
  assert "${dir}" "greet default greeting"          "assert greet('Ada') == 'Hello, Ada!'"
  assert "${dir}" "greet keyword arguments"         "assert greet('Grace', greeting='Welcome', punctuation='.') == 'Welcome, Grace.'"

  # --- Returning a tuple of several results ---
  assert "${dir}" "summarize returns a 5-tuple"     "assert summarize([2, 4, 6]) == (3, 12, 2, 6, 4.0)"
  assert "${dir}" "summarize tuple unpacks"         "c, t, lo, hi, avg = summarize([7, 3, 9]); assert (c, t, lo, hi) == (3, 19, 3, 9)"

  # --- The mutable-default-argument trap is avoided ---
  assert "${dir}" "tally counts frequencies"         "assert tally(['a', 'b', 'a']) == {'a': 2, 'b': 1}"
  assert "${dir}" "tally with a starting count"       "assert tally(['a'], {'a': 5}) == {'a': 6}"
  assert "${dir}" "tally does not leak across calls"  "tally(['x', 'x']); assert tally(['y']) == {'y': 1}"
  assert "${dir}" "tally does not mutate its input"   "start = {'a': 5}; tally(['a'], start); assert start == {'a': 5}"

  # --- Purity: same args -> same result, input unchanged ---
  assert "${dir}" "word_count is pure (repeatable)"  "assert word_count('a b c') == word_count('a b c') == 3"
  assert "${dir}" "summarize does not mutate list"   "data = [3, 1, 2]; summarize(data); assert data == [3, 1, 2]"

  # --- Errors are raised, not hidden ---
  assert "${dir}" "mean([]) raises ValueError"       "assert _raises(mean, [])"
  assert "${dir}" "summarize([]) raises ValueError"  "assert _raises(summarize, [])"

  # --- Every public function carries a docstring ---
  assert "${dir}" "all public functions documented" "import library, inspect
missing = [n for n, f in inspect.getmembers(library, inspect.isfunction) if not (f.__doc__ or '').strip()]
assert not missing, missing"
}

# --- Reference library: always tested strictly ---
run_library_checks "${ref_dir}"

# --- The demo runs and uses the return values ---
echo "Testing examples/demo.py runs ..."
if python3 "${ref_dir}/demo.py" >/dev/null 2>&1; then
  check "demo.py runs and prints results" "yes"
else
  check "demo.py runs and prints results" "no"
fi

# --- Learner starter ---
echo "Testing starter/library.py ..."
if python3 -c "compile(open('${starter_dir}/library.py').read(), 'library.py', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter_dir}/library.py"; then
  echo "Note: starter/library.py still has unfinished exercises — testing structure only."
  for fn in word_count reverse_words celsius_to_fahrenheit clamp summarize tally; do
    if grep -q "def ${fn}" "${starter_dir}/library.py"; then
      check "starter defines ${fn}" "yes"
    else
      check "starter defines ${fn}" "no"
    fi
  done
else
  run_library_checks "${starter_dir}"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
