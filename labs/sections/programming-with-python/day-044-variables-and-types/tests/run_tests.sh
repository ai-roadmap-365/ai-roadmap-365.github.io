#!/usr/bin/env bash
# Tests for the Day 044 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the example program prints the expected type names and the
# correct mutability results, and independently asserts Python's data-model
# behaviour with `python3 -c`. No network access is used.
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

# Require a working Python 3 interpreter.
if ! command -v python3 >/dev/null 2>&1; then
  echo "FAIL: python3 not found on PATH — install Python 3 (see Day 43)."
  exit 1
fi

echo "Testing examples/types_demo.py ..."
if ! output="$(python3 "${lab_dir}/examples/types_demo.py" 2>&1)"; then
  check "example program exits successfully" "no"
  echo "${output}" | sed 's/^/    /'
  echo
  echo "${checks} checks, ${failures} failure(s)."
  exit 1
fi
check "example program exits successfully" "yes"

# Each core type name must appear in the output.
for type_name in "type = int" "type = float" "type = bool" "type = str" "type = NoneType"; do
  echo "${output}" | grep -q "${type_name}" \
    && check "prints '${type_name}'" "yes" \
    || check "prints '${type_name}'" "no"
done

# Dynamic typing: the same name shows two different types.
echo "${output}" | grep -q "same name, different type" \
  && check "shows dynamic re-binding" "yes" \
  || check "shows dynamic re-binding" "no"

# Mutability results: list id unchanged after append; str id changed after '+'.
echo "${output}" | grep -q "id unchanged after append: True" \
  && check "list mutates in place (id unchanged)" "yes" \
  || check "list mutates in place (id unchanged)" "no"
echo "${output}" | grep -q "id changed after '+': True" \
  && check "string is immutable (new object on '+')" "yes" \
  || check "string is immutable (new object on '+')" "no"

# Safe conversion: good input converts, bad input is handled, not fatal.
echo "${output}" | grep -q "'30'  -> 30 (int)" \
  && check "safe conversion succeeds on '30'" "yes" \
  || check "safe conversion succeeds on '30'" "no"
echo "${output}" | grep -q "could not convert (ValueError handled)" \
  && check "safe conversion handles bad input" "yes" \
  || check "safe conversion handles bad input" "no"

# Independent assertion of the data model, straight from the interpreter.
echo "Asserting the data model with python3 -c ..."
if python3 -c '
a = [1, 2, 3]
b = a
b.append(4)
assert a == [1, 2, 3, 4], "aliasing: a should see b'"'"'s append"
assert isinstance(True, int), "bool is a subtype of int"
s = "cat"; before = id(s); s = s + "s"
assert id(s) != before, "str must be a new object after +"
n = [1]; before = id(n); n.append(2)
assert id(n) == before, "list must mutate in place"
try:
    int("3.5"); raise SystemExit("int(\"3.5\") should have raised ValueError")
except ValueError:
    pass
assert bool("False") is True, "non-empty string is truthy"
'; then
  check "python3 -c data-model assertions pass" "yes"
else
  check "python3 -c data-model assertions pass" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
