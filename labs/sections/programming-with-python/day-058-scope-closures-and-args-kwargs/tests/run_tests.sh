#!/usr/bin/env bash
# Tests for the Day 058 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Exercises the reference module (examples/flexible.py) by importing its
# functions and asserting their behaviour: variadic total, keyword-only
# average, the make_counter closure (private, independent state), the
# make_multiplier factory, and the build_request **kwargs config merge. It
# also runs the module demo and checks its output, confirms DEFAULTS is not
# mutated, and finally checks the learner's starter — structurally while the
# exercises are unfinished, and to the same strict standard once complete.
# No network, non-interactive. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: do not let imported modules write __pycache__.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref_dir="${lab_dir}/examples"
starter_dir="${lab_dir}/starter"
ref="${ref_dir}/flexible.py"
starter="${starter_dir}/flexible.py"
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

# check_py <label> <module_dir> <python-body>
# Imports 'flexible' from module_dir and runs the assertion body; passes when
# python3 exits 0.
check_py() {
  local label="$1" mod_dir="$2" body="$3"
  if python3 -c "import sys; sys.path.insert(0, '${mod_dir}'); import flexible
${body}" 2>/dev/null; then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
}

run_fn_checks() {
  local mod_dir="$1"
  echo "Testing functions imported from ${mod_dir}/flexible.py ..."
  check_py "total() is 0 and total(2,4,6) is 12" "${mod_dir}" \
    "assert flexible.total() == 0; assert flexible.total(2, 4, 6) == 12"
  check_py "average(10,20,30) is 20.0 and empty is 0.0" "${mod_dir}" \
    "assert flexible.average(10, 20, 30) == 20.0; assert flexible.average() == 0.0"
  check_py "average ndigits is keyword-only" "${mod_dir}" \
    "assert flexible.average(1, 2, 3, ndigits=4) == 2.0; assert flexible.average(1, 2, 3, 4) == 2.5"
  check_py "make_counter yields 0,1,2 (private state)" "${mod_dir}" \
    "c = flexible.make_counter(); assert [c(), c(), c()] == [0, 1, 2]"
  check_py "two counters are independent" "${mod_dir}" \
    "c = flexible.make_counter(); d = flexible.make_counter(100); assert c() == 0; assert d() == 100; assert c() == 1"
  check_py "make_counter respects start and step" "${mod_dir}" \
    "e = flexible.make_counter(10, 5); assert [e(), e(), e()] == [10, 15, 20]"
  check_py "make_multiplier captures its own factor" "${mod_dir}" \
    "t = flexible.make_multiplier(3); x = flexible.make_multiplier(10); assert t(5) == 15; assert x(5) == 50"
  check_py "build_request fills all defaults" "${mod_dir}" \
    "r = flexible.build_request('hello'); assert r == {'prompt': 'hello', 'temperature': 0.7, 'max_tokens': 256, 'model': 'demo'}"
  check_py "build_request lets caller override, model kept" "${mod_dir}" \
    "r = flexible.build_request('hi', temperature=0.2, max_tokens=500); assert r['temperature'] == 0.2 and r['max_tokens'] == 500 and r['model'] == 'demo'"
  check_py "build_request does not mutate DEFAULTS" "${mod_dir}" \
    "flexible.build_request('hi', temperature=0.2); assert flexible.DEFAULTS == {'temperature': 0.7, 'max_tokens': 256, 'model': 'demo'}"
}

# check_demo <label> <script> <needle>
check_demo() {
  local label="$1" script="$2" needle="$3"
  local out
  out="$(python3 "${script}" 2>&1)"
  if printf '%s' "${out}" | grep -qF "${needle}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (output: ${out})"
  fi
}

run_demo_checks() {
  local script="$1"
  echo "Testing the demo of ${script} ..."
  check_demo "demo prints total(2, 4, 6) -> 12"      "${script}" "total(2, 4, 6) -> 12"
  check_demo "demo prints counter: 0 1 2 3"          "${script}" "counter: 0 1 2 3"
  check_demo "demo prints triple(5) -> 15"           "${script}" "triple(5) -> 15"
  check_demo "demo prints the default request dict"  "${script}" "'model': 'demo'"
}

# --- Reference module: always tested strictly ---
run_fn_checks "${ref_dir}"
run_demo_checks "${ref}"

# --- Learner starter ---
echo "Testing starter/flexible.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/flexible.py still has unfinished exercises — testing structure only."
  grep -q 'def total' "${starter}"        && check "starter defines total" "yes"        || check "starter defines total" "no"
  grep -q 'def make_counter' "${starter}" && check "starter defines make_counter" "yes" || check "starter defines make_counter" "no"
  grep -q 'def build_request' "${starter}" && check "starter defines build_request" "yes" || check "starter defines build_request" "no"
else
  run_fn_checks "${starter_dir}"
  run_demo_checks "${starter}"
  grep -q 'nonlocal' "${starter}" && check "starter uses nonlocal in the closure" "yes" || check "starter uses nonlocal in the closure" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
