#!/usr/bin/env bash
# Tests for the Day 069 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Everything here runs with python3 and bash only: no installs, no network,
# no type checker required. Each check is a real assertion about behaviour —
# generated __repr__ and __eq__, the mutable-default ValueError,
# __post_init__ validation, frozen hashing and FrozenInstanceError, a JSON
# round trip, runtime introspection of __annotations__ and
# dataclasses.fields(), and the from-scratch mini_dataclass decorator.
#
# The reference in examples/ is always tested strictly. The learner's
# starter/ is tested structurally while exercises are unfinished, and to the
# same strict standard once they are complete.
# Exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

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

# assert_py <label> <module_dir> <python-body>
# Runs an assertion body with <module_dir> on the import path. A clean exit
# (every assert held) is a pass; any exception is a failure.
assert_py() {
  local label="$1" module_dir="$2" body="$3"
  local out
  if out="$(PYTHONPATH="${module_dir}" python3 -c "${body}" 2>&1)"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    ${out##*$'\n'}"
  fi
}

run_record_checks() {
  local dir="$1"
  echo "Testing records.py in ${dir} ..."

  assert_py "generated __repr__ names every field" "${dir}" \
"from records import EvalRecord
text = repr(EvalRecord('2+2?', '4'))
assert text.startswith('EvalRecord('), text
for name in ('prompt', 'expected', 'score', 'tags'):
    assert name + '=' in text, text
assert 'prompt_length' not in text, 'prompt_length is repr=False'"

  assert_py "generated __eq__ compares by value, not identity" "${dir}" \
"from records import EvalRecord
a, b = EvalRecord('2+2?', '4'), EvalRecord('2+2?', '4')
assert a is not b
assert a == b
assert a != EvalRecord('2+2?', '5')
assert a != EvalRecord('2+3?', '4')"

  assert_py "hand-written and dataclass versions agree on equality" "${dir}" \
"from records import EvalRecord, HandWrittenRecord
assert HandWrittenRecord('q', 'a') == HandWrittenRecord('q', 'a')
assert EvalRecord('q', 'a') == EvalRecord('q', 'a')"

  assert_py "a bare [] default raises ValueError at class creation" "${dir}" \
"from dataclasses import dataclass
try:
    @dataclass
    class Broken:
        name: str
        tags: list = []
except ValueError as err:
    assert 'default_factory' in str(err), err
else:
    raise AssertionError('a mutable default was accepted')"

  assert_py "default_factory gives every instance its own list" "${dir}" \
"from records import EvalRecord
first, second = EvalRecord('a?', 'a'), EvalRecord('b?', 'b')
assert first.tags == [] and second.tags == []
assert first.tags is not second.tags
first.tags.append('math')
assert first.tags == ['math']
assert second.tags == []"

  assert_py "__post_init__ rejects a blank prompt" "${dir}" \
"from records import EvalRecord
try:
    EvalRecord('   ', '4')
except ValueError as err:
    assert 'prompt' in str(err), err
else:
    raise AssertionError('blank prompt was accepted')"

  assert_py "__post_init__ rejects an out-of-range score" "${dir}" \
"from records import EvalRecord
try:
    EvalRecord('2+2?', '4', 3.0)
except ValueError as err:
    assert '3.0' in str(err), err
else:
    raise AssertionError('score 3.0 was accepted')
EvalRecord('2+2?', '4', 0.0)
EvalRecord('2+2?', '4', 1.0)"

  assert_py "__post_init__ computes the derived prompt_length" "${dir}" \
"from records import EvalRecord
assert EvalRecord('Capital of France?', 'Paris').prompt_length == 18"

  assert_py "frozen RunKey is hashable and works as a dict key" "${dir}" \
"from records import RunKey
key = RunKey('arithmetic', 7)
assert hash(key) == hash(RunKey('arithmetic', 7))
counts = {key: 12}
assert counts[RunKey('arithmetic', 7)] == 12
assert len({RunKey('a', 1), RunKey('a', 1)}) == 1"

  assert_py "frozen RunKey refuses assignment and sorts by field order" "${dir}" \
"from dataclasses import FrozenInstanceError
from records import RunKey
key = RunKey('arithmetic', 7)
try:
    key.seed = 8
except FrozenInstanceError:
    pass
else:
    raise AssertionError('assignment to a frozen dataclass succeeded')
assert sorted([RunKey('geo', 2), RunKey('arith', 9), RunKey('arith', 1)]) == [
    RunKey('arith', 1), RunKey('arith', 9), RunKey('geo', 2)]"

  assert_py "records survive a JSON round trip unchanged" "${dir}" \
"import json
from records import EvalRecord, records_from_json, records_to_json
originals = [EvalRecord('2+2?', '4', 0.5, ['math']),
             EvalRecord('Capital of France?', 'Paris', 1.0, ['geo', 'easy'])]
text = records_to_json(originals)
rows = json.loads(text)
assert isinstance(rows, list) and len(rows) == 2
assert rows[0]['prompt'] == '2+2?' and rows[0]['tags'] == ['math']
rebuilt = records_from_json(text)
assert rebuilt == originals
assert rebuilt[0] is not originals[0]
assert rebuilt[1].prompt_length == originals[1].prompt_length"

  assert_py "replace() copies a record and revalidates it" "${dir}" \
"from records import EvalRecord, rescore
original = EvalRecord('2+2?', '4', 0.5, ['math'])
copy = rescore(original, 0.9)
assert copy.score == 0.9 and original.score == 0.5
assert copy.prompt == original.prompt
try:
    rescore(original, 4.0)
except ValueError:
    pass
else:
    raise AssertionError('replace() skipped __post_init__ validation')"

  assert_py "annotation_names reads __annotations__ in declaration order" "${dir}" \
"from records import EvalRecord, annotation_names
assert annotation_names(EvalRecord) == [
    'prompt', 'expected', 'score', 'tags', 'prompt_length']"

  assert_py "describe_fields reports types, defaults and factories" "${dir}" \
"from records import EvalRecord, describe_fields
lines = describe_fields(EvalRecord)
assert lines[0] == 'prompt: str = (required)', lines[0]
assert lines[2] == 'score: float = 0.0', lines[2]
assert lines[3] == 'tags: list[str] = factory list()', lines[3]"

  assert_py "annotations are stored but never enforced at runtime" "${dir}" \
"from records import EvalRecord
record = EvalRecord('2+2?', '4', 0.5)
record.score = 'not a number'
record.tags = 17
assert record.score == 'not a number'
assert record.tags == 17"
}

run_mini_checks() {
  local dir="$1"
  echo "Testing mini_dataclass.py in ${dir} ..."

  assert_py "mini __repr__ matches the real one field for field" "${dir}" \
"from mini_dataclass import MiniRecord, RealRecord
mini = repr(MiniRecord('2+2?', '4'))
real = repr(RealRecord('2+2?', '4'))
assert mini.startswith('MiniRecord('), mini
assert mini.split('(', 1)[1] == real.split('(', 1)[1], (mini, real)"

  assert_py "mini __init__ handles positional, keyword and default values" "${dir}" \
"from mini_dataclass import MiniRecord
assert repr(MiniRecord('q', 'a')) == repr(MiniRecord(prompt='q', expected='a'))
assert MiniRecord('q', 'a').score == 0.0
assert MiniRecord('q', 'a', 0.5).score == 0.5
assert MiniRecord('q', expected='a', score=0.5).score == 0.5"

  assert_py "mini __init__ rejects bad calls the way the real one does" "${dir}" \
"from mini_dataclass import MiniRecord, RealRecord
for cls in (MiniRecord, RealRecord):
    try:
        cls('only-one')
    except TypeError:
        pass
    else:
        raise AssertionError(cls.__name__ + ' accepted a missing argument')
    try:
        cls('q', 'a', 0.5, 'extra')
    except TypeError:
        pass
    else:
        raise AssertionError(cls.__name__ + ' accepted too many arguments')
    try:
        cls('q', 'a', nope=1)
    except TypeError:
        pass
    else:
        raise AssertionError(cls.__name__ + ' accepted an unknown keyword')"

  assert_py "mini __eq__ behaves like the real generated __eq__" "${dir}" \
"from mini_dataclass import MiniRecord, RealRecord
assert MiniRecord('q', 'a') == MiniRecord('q', 'a')
assert RealRecord('q', 'a') == RealRecord('q', 'a')
assert not (MiniRecord('q', 'a') == MiniRecord('q', 'b'))
assert not (RealRecord('q', 'a') == RealRecord('q', 'b'))
assert MiniRecord('q', 'a') != 'a string'
assert RealRecord('q', 'a') != 'a string'"
}

run_script_checks() {
  echo "Testing the runnable scripts ..."
  local out code

  out="$(cd "${lab_dir}" && python3 examples/demo.py 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ] \
    && printf '%s' "${out}" | grep -qF "use default_factory" \
    && printf '%s' "${out}" | grep -qF "rebuilt == original: True" \
    && printf '%s' "${out}" | grep -qF "same repr shape (fields and formatting): True"; then
    check "examples/demo.py runs and reports the expected results" "yes"
  else
    check "examples/demo.py runs and reports the expected results" "no"
    echo "    (exit ${code})"
  fi

  out="$(cd "${lab_dir}" && python3 examples/inspect_runtime.py 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ] \
    && printf '%s' "${out}" | grep -qF "tags: list[str] = factory list()" \
    && printf '%s' "${out}" | grep -qF "double('ab') -> 'abab'"; then
    check "examples/inspect_runtime.py shows stored-but-unenforced annotations" "yes"
  else
    check "examples/inspect_runtime.py shows stored-but-unenforced annotations" "no"
    echo "    (exit ${code})"
  fi

  out="$(cd "${lab_dir}" && bash examples/check_types.sh 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ] && printf '%s' "${out}" | grep -qE "Type checker found|No static type checker is installed"; then
    check "examples/check_types.sh runs or skips cleanly (optional step)" "yes"
  else
    check "examples/check_types.sh runs or skips cleanly (optional step)" "no"
    echo "    (exit ${code})"
  fi

  out="$(cd "${lab_dir}" && python3 starter/demo.py 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ]; then
    check "starter/demo.py runs without crashing" "yes"
  else
    check "starter/demo.py runs without crashing" "no"
    echo "    (exit ${code})"
  fi
}

# --- Reference: always tested strictly ---
run_record_checks "${lab_dir}/examples"
run_mini_checks "${lab_dir}/examples"
run_script_checks

# --- Learner starter ---
echo "Testing the starter files ..."
starter_records="${lab_dir}/starter/records.py"
starter_mini="${lab_dir}/starter/mini_dataclass.py"

for path in "${starter_records}" "${starter_mini}"; do
  if python3 -c "import sys; compile(open(sys.argv[1]).read(), sys.argv[1], 'exec')" "${path}" 2>/dev/null; then
    check "$(basename "${path}") is valid Python" "yes"
  else
    check "$(basename "${path}") is valid Python" "no"
  fi
done

if grep -q 'NotImplementedError' "${starter_records}" || grep -q 'NotImplementedError' "${starter_mini}"; then
  echo "Note: the starter still has unfinished exercises — testing structure only."
  for name in EvalRecord RunKey records_to_json records_from_json rescore describe_fields annotation_names; do
    if grep -qE "^(class|def) ${name}\b" "${starter_records}"; then
      check "starter defines ${name}" "yes"
    else
      check "starter defines ${name}" "no"
    fi
  done
  if grep -qE '^def mini_dataclass\b' "${starter_mini}"; then
    check "starter defines mini_dataclass" "yes"
  else
    check "starter defines mini_dataclass" "no"
  fi
else
  run_record_checks "${lab_dir}/starter"
  run_mini_checks "${lab_dir}/starter"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
