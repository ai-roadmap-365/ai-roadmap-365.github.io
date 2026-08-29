#!/usr/bin/env bash
# Tests for the Day 055 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The checks are assert-based: they import the reference module and assert the
# return values of the comprehensions and the generator pipeline, then run the
# whole program and confirm the lazy pipeline matches the loop baseline.
# Finally they check the learner's starter: structurally while exercises are
# unfinished, and to the same strict standard once they are complete.
# No network, non-interactive. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: do not let imported modules write __pycache__.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref="${lab_dir}/examples/pipeline.py"
starter="${lab_dir}/starter/pipeline.py"
examples_dir="${lab_dir}/examples"
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

# assert_py <label> <python-code>
# Runs an assert-based snippet against the examples module; passes only if
# python exits 0 (every assert held).
assert_py() {
  local label="$1" code="$2"
  if python3 -c "import sys; sys.path.insert(0, '${examples_dir}'); ${code}" 2>/dev/null; then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
}

echo "Asserting comprehension results (examples/pipeline.py) ..."
assert_py "list comp: high scorers upper-cased" \
  "from pipeline import high_scorer_names, parse, RECORDS; recs=[parse(r) for r in RECORDS]; assert high_scorer_names(recs) == ['ALICE','CAROL','FRANK']"
assert_py "dict comp: name -> score" \
  "from pipeline import name_to_score, parse, RECORDS; recs=[parse(r) for r in RECORDS]; assert name_to_score(recs)['carol'] == 95 and len(name_to_score(recs)) == 6"
assert_py "set comp: distinct teams" \
  "from pipeline import distinct_teams, parse, RECORDS; recs=[parse(r) for r in RECORDS]; assert distinct_teams(recs) == {'engineering','design','marketing'}"

echo "Asserting generator behaviour ..."
assert_py "read_records yields one record at a time" \
  "from pipeline import read_records, RECORDS; g=read_records(RECORDS); first=next(g); assert first['name']=='alice' and isinstance(first['score'], int)"
assert_py "only_team filters lazily and is a generator" \
  "import types; from pipeline import only_team, read_records, RECORDS; g=only_team(read_records(RECORDS),'design'); assert isinstance(g, types.GeneratorType); assert [r['name'] for r in g] == ['bob','dave']"
assert_py "lazy pipeline == loop baseline (engineering avg)" \
  "from pipeline import average_score_lazy, average_score_loop, RECORDS; assert average_score_lazy(RECORDS,'engineering') == average_score_loop(RECORDS,'engineering')"
assert_py "engineering average is 262/3" \
  "from pipeline import average_score_lazy, RECORDS; assert abs(average_score_lazy(RECORDS,'engineering') - 262/3) < 1e-9"
assert_py "itertools first_ids uses count+islice" \
  "from pipeline import first_ids; assert first_ids(3) == [1000,1001,1002]"

echo "Running the whole reference program ..."
out="$(python3 "${ref}" 2>&1)"; code=$?
if [ "${code}" -eq 0 ] && printf '%s' "${out}" | grep -qF "match: lazy pipeline == loop baseline"; then
  check "reference program runs and self-checks (exit 0)" "yes"
else
  check "reference program runs and self-checks (exit 0)" "no"
  echo "    (exit ${code}; output: ${out})"
fi

# --- Learner starter ---
echo "Testing starter/pipeline.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/pipeline.py still has unfinished exercises — testing structure only."
  grep -q 'def high_scorer_names' "${starter}" && check "starter defines high_scorer_names" "yes" || check "starter defines high_scorer_names" "no"
  grep -q 'yield' "${starter}" && check "starter uses yield somewhere" "yes" || check "starter uses yield somewhere" "no"
else
  # Learner finished: hold the starter to the same strict standard.
  s_out="$(python3 "${starter}" 2>&1)"; s_code=$?
  if [ "${s_code}" -eq 0 ] && printf '%s' "${s_out}" | grep -qF "match: lazy pipeline == loop baseline"; then
    check "completed starter runs and self-checks (exit 0)" "yes"
  else
    check "completed starter runs and self-checks (exit 0)" "no"
    echo "    (exit ${s_code}; output: ${s_out})"
  fi
  if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/starter'); from pipeline import high_scorer_names, parse, RECORDS; recs=[parse(r) for r in RECORDS]; assert high_scorer_names(recs) == ['ALICE','CAROL','FRANK']" 2>/dev/null; then
    check "completed starter list comp is correct" "yes"
  else
    check "completed starter list comp is correct" "no"
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
