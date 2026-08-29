#!/usr/bin/env bash
# Tests for the Day 071 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This suite is unusual: it is a test suite ABOUT a test suite. Its job is to
# prove that the pytest suite in examples/ is not decorative. Three of the
# checks below do that directly, and they are the ones worth reading:
#
#   * "a broken implementation makes the suite fail" copies the fixed module
#     to a temporary directory, breaks exactly one line with sed, and asserts
#     that pytest exits NON-ZERO. A suite that stays green when the code is
#     wrong is worse than no suite at all;
#   * "the reference suite catches both shipped bugs" runs the reference tests
#     against the buggy starter module and asserts it fails on precisely the
#     two functions that are wrong;
#   * "an empty directory exits 5" pins pytest's own exit-code contract, which
#     is the thing continuous integration actually reads.
#
# No network, non-interactive, deterministic. Exits 0 only if every check
# passes.
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

# Resolve pytest: an explicit override, then this lab's .venv, then whatever
# is on PATH. Fails loudly with instructions rather than silently skipping.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install it with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest: PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

python_bin="$(command -v python3 || true)"
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi

echo "Day 071 — Your First Real Test Suite"
echo

# --------------------------------------------------------------------------
echo "1. The tool itself"
# --------------------------------------------------------------------------

version_line="$("${pytest_bin}" --version 2>&1 | head -1)"
case "${version_line}" in
  pytest*) check "pytest --version reports a pytest ( ${version_line} )" "yes" ;;
  *) check "pytest --version reports a pytest ( ${version_line} )" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "2. The reference suite passes"
# --------------------------------------------------------------------------

examples_out="$(cd "${lab_dir}" && "${pytest_bin}" examples -q 2>&1)"
examples_exit=$?
if [ "${examples_exit}" -eq 0 ]; then
  check "pytest examples exits 0" "yes"
else
  check "pytest examples exits 0 (got ${examples_exit})" "no"
  echo "${examples_out}" | tail -20
fi

case "${examples_out}" in
  *"19 passed"*) check "pytest examples reports 19 passed" "yes" ;;
  *) check "pytest examples reports 19 passed" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "3. Collection: rootdir, test ids, and selection"
# --------------------------------------------------------------------------

collected="$(cd "${lab_dir}" && "${pytest_bin}" examples --collect-only -q 2>&1)"

for test_id in \
  "test_textstats.py::test_words_of_empty_text_is_empty" \
  "test_textstats.py::test_average_word_length_of_empty_text_is_zero" \
  "test_textstats.py::TestTopWords::test_returns_exactly_n_items" \
  "test_textstats.py::test_reading_time_rejects_a_non_positive_speed"
do
  case "${collected}" in
    *"${test_id}"*) check "collection finds ${test_id}" "yes" ;;
    *) check "collection finds ${test_id}" "no" ;;
  esac
done

case "${collected}" in
  *"19 tests collected"*) check "collection finds exactly 19 tests" "yes" ;;
  *) check "collection finds exactly 19 tests" "no" ;;
esac

# `Test*` classes are collected too, and their ids carry the class name.
class_ids="$(printf '%s\n' "${collected}" | grep -c '::TestTopWords::' || true)"
if [ "${class_ids}" -eq 5 ]; then
  check "the TestTopWords class contributes 5 collected tests" "yes"
else
  check "the TestTopWords class contributes 5 collected tests (got ${class_ids})" "no"
fi

selected="$(cd "${lab_dir}" && "${pytest_bin}" examples -q -k "top_words or TestTopWords" 2>&1)"
case "${selected}" in
  *"5 passed, 14 deselected"*) check "-k 'top_words or TestTopWords' selects 5 of 19" "yes" ;;
  *) check "-k 'top_words or TestTopWords' selects 5 of 19" "no" ;;
esac

reading_selected="$(cd "${lab_dir}" && "${pytest_bin}" examples -q -k "reading_time" 2>&1)"
case "${reading_selected}" in
  *"5 passed, 14 deselected"*) check "-k reading_time selects the 5 reading-time tests" "yes" ;;
  *) check "-k reading_time selects the 5 reading-time tests" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "4. Failure reporting and assertion rewriting"
# --------------------------------------------------------------------------

failure_out="$(cd "${lab_dir}" && "${pytest_bin}" examples/failure-demo 2>&1)"
failure_exit=$?
if [ "${failure_exit}" -eq 1 ]; then
  check "the deliberate-failure demo exits 1" "yes"
else
  check "the deliberate-failure demo exits 1 (got ${failure_exit})" "no"
fi

case "${failure_out}" in
  *"assert 4 == 3"*) check "assertion rewriting shows both sides: 'assert 4 == 3'" "yes" ;;
  *) check "assertion rewriting shows both sides: 'assert 4 == 3'" "no" ;;
esac

case "${failure_out}" in
  *"where 4 = add(1, 2)"*) check "the report explains where the 4 came from" "yes" ;;
  *) check "the report explains where the 4 came from" "no" ;;
esac

case "${failure_out}" in
  *"At index 4 diff:"*) check "a list mismatch names the index that differs" "yes" ;;
  *) check "a list mismatch names the index that differs" "no" ;;
esac

case "${failure_out}" in
  *"DID NOT RAISE ValueError"*) check "pytest.raises reports a missing exception" "yes" ;;
  *) check "pytest.raises reports a missing exception" "no" ;;
esac

case "${failure_out}" in
  *"short test summary info"*) check "the short test summary lists every failure" "yes" ;;
  *) check "the short test summary lists every failure" "no" ;;
esac

stop_first="$(cd "${lab_dir}" && "${pytest_bin}" examples/failure-demo -x -q --tb=short 2>&1)"
case "${stop_first}" in
  *"1 failed"*) check "-x stops after the first failure" "yes" ;;
  *) check "-x stops after the first failure" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "5. Exit codes — the contract continuous integration reads"
# --------------------------------------------------------------------------

empty_dir="$(mktemp -d "${TMPDIR:-/tmp}/pytest-empty.XXXXXX")"
(cd "${empty_dir}" && "${pytest_bin}" . -q >/dev/null 2>&1)
empty_exit=$?
rm -rf "${empty_dir}"
if [ "${empty_exit}" -eq 5 ]; then
  check "a run that collects no tests exits 5, not 0" "yes"
else
  check "a run that collects no tests exits 5, not 0 (got ${empty_exit})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "6. The suite actually tests something (the checks that matter)"
# --------------------------------------------------------------------------

# 6a. Control: the fixed module plus the reference suite is green.
work="$(mktemp -d "${TMPDIR:-/tmp}/pytest-break.XXXXXX")"
cp "${lab_dir}/examples/textstats.py" "${lab_dir}/examples/test_textstats.py" \
   "${lab_dir}/examples/conftest.py" "${lab_dir}/examples/pytest.ini" "${work}/"
(cd "${work}" && "${pytest_bin}" . -q >/dev/null 2>&1)
control_exit=$?
if [ "${control_exit}" -eq 0 ]; then
  check "control: the fixed module passes the reference suite (exit 0)" "yes"
else
  check "control: the fixed module passes the reference suite (got ${control_exit})" "no"
fi

# 6b. Break exactly one line and demand a non-zero exit.
sed -i.bak 's/return len(words(text))/return len(words(text)) + 1/' "${work}/textstats.py"
rm -f "${work}/textstats.py.bak"
if grep -q 'return len(words(text)) + 1' "${work}/textstats.py"; then
  check "the sed edit really changed word_count" "yes"
else
  check "the sed edit really changed word_count" "no"
fi
broken_out="$(cd "${work}" && "${pytest_bin}" . -q 2>&1)"
broken_exit=$?
if [ "${broken_exit}" -ne 0 ]; then
  check "a one-line break makes the suite FAIL (exit ${broken_exit}, not 0)" "yes"
else
  check "a one-line break makes the suite FAIL — it did not, so the suite is vacuous" "no"
fi
case "${broken_out}" in
  *"test_word_count_of_the_sample_is_twelve"*)
    check "the failing run names test_word_count_of_the_sample_is_twelve" "yes" ;;
  *) check "the failing run names test_word_count_of_the_sample_is_twelve" "no" ;;
esac
rm -rf "${work}"

# 6c. The reference suite catches both bugs shipped in starter/textstats.py.
buggy="$(mktemp -d "${TMPDIR:-/tmp}/pytest-buggy.XXXXXX")"
cp "${lab_dir}/starter/textstats.py" "${buggy}/"
cp "${lab_dir}/examples/test_textstats.py" "${lab_dir}/examples/conftest.py" \
   "${lab_dir}/examples/pytest.ini" "${buggy}/"
buggy_out="$(cd "${buggy}" && "${pytest_bin}" . -q 2>&1)"
buggy_exit=$?
if [ "${buggy_exit}" -ne 0 ]; then
  check "the reference suite rejects the buggy starter module" "yes"
else
  check "the reference suite rejects the buggy starter module" "no"
fi
case "${buggy_out}" in
  *"test_average_word_length_of_empty_text_is_zero"*)
    check "bug 1 caught: average_word_length divides by zero on empty text" "yes" ;;
  *) check "bug 1 caught: average_word_length divides by zero on empty text" "no" ;;
esac
case "${buggy_out}" in
  *"TestTopWords::test_returns_exactly_n_items"*)
    check "bug 2 caught: top_words is off by one" "yes" ;;
  *) check "bug 2 caught: top_words is off by one" "no" ;;
esac
case "${buggy_out}" in
  *"4 failed, 15 passed"*)
    check "exactly 4 of the 19 reference tests fail on the buggy module" "yes" ;;
  *) check "exactly 4 of the 19 reference tests fail on the buggy module" "no" ;;
esac
rm -rf "${buggy}"

# 6d. The two repairs are exactly where the lesson says they are, and the
#     starter really does still carry both bugs.
if grep -q 'return ranked\[: n - 1\]' "${lab_dir}/starter/textstats.py"; then
  check "starter/textstats.py still carries the off-by-one slice" "yes"
else
  check "starter/textstats.py still carries the off-by-one slice" "no"
fi
if grep -q 'return ranked\[:n\]' "${lab_dir}/examples/textstats.py"; then
  check "examples/textstats.py repairs the slice to ranked[:n]" "yes"
else
  check "examples/textstats.py repairs the slice to ranked[:n]" "no"
fi
if grep -q 'if not found:' "${lab_dir}/examples/textstats.py"; then
  check "examples/textstats.py guards the empty-text division" "yes"
else
  check "examples/textstats.py guards the empty-text division" "no"
fi
if grep -q 'if not found:' "${lab_dir}/starter/textstats.py"; then
  check "starter/textstats.py still lacks the empty-text guard" "no"
else
  check "starter/textstats.py still lacks the empty-text guard" "yes"
fi

# 6e. The vacuous-test demonstration behaves exactly as the lesson claims:
#     four green tests on a knowingly broken function, and one honest test
#     that catches it. prove_it.sh exits 0 only if both halves hold.
if (cd "${lab_dir}" && PYTEST="${pytest_bin}" bash examples/vacuous-demo/prove_it.sh >/dev/null 2>&1); then
  check "four vacuous tests stay green on broken code; the honest one fails" "yes"
else
  check "four vacuous tests stay green on broken code; the honest one fails" "no"
fi

vacuous_out="$(cd "${lab_dir}" && "${pytest_bin}" examples/vacuous-demo -q 2>&1)"
case "${vacuous_out}" in
  *"5 passed"*) check "all 5 vacuous-demo tests pass on the CORRECT module" "yes" ;;
  *) check "all 5 vacuous-demo tests pass on the CORRECT module" "no" ;;
esac

# `pytest examples` must not wander into either deliberately-wrong directory.
case "${examples_out}" in
  *vacuous*|*failure*) check "norecursedirs keeps the wrong-on-purpose dirs out of 'pytest examples'" "no" ;;
  *) check "norecursedirs keeps the wrong-on-purpose dirs out of 'pytest examples'" "yes" ;;
esac

# --------------------------------------------------------------------------
echo
echo "7. The starter is runnable before you start"
# --------------------------------------------------------------------------

starter_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q 2>&1)"
starter_exit=$?
if [ "${starter_exit}" -eq 0 ]; then
  check "pytest starter exits 0 with the exercises unfinished" "yes"
else
  check "pytest starter exits 0 with the exercises unfinished (got ${starter_exit})" "no"
fi
case "${starter_out}" in
  *"1 passed, 9 skipped"*) check "the starter has 1 worked test and 9 skipped exercises" "yes" ;;
  *) check "the starter has 1 worked test and 9 skipped exercises" "no" ;;
esac

starter_collected="$(cd "${lab_dir}" && "${pytest_bin}" starter --collect-only -q 2>&1)"
case "${starter_collected}" in
  *"10 tests collected"*) check "the starter collects 10 tests" "yes" ;;
  *) check "the starter collects 10 tests" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "8. Testing without pytest: assert, unittest, doctest"
# --------------------------------------------------------------------------

if (cd "${lab_dir}" && "${python_bin}" examples/plain_asserts.py >/dev/null 2>&1); then
  check "examples/plain_asserts.py exits 0 — bare asserts are already a suite" "yes"
else
  check "examples/plain_asserts.py exits 0 — bare asserts are already a suite" "no"
fi

# The same file, with the module broken, must exit non-zero.
plain="$(mktemp -d "${TMPDIR:-/tmp}/plain-assert.XXXXXX")"
cp "${lab_dir}/examples/textstats.py" "${lab_dir}/examples/plain_asserts.py" "${plain}/"
sed -i.bak 's/return len(words(text))/return len(words(text)) + 1/' "${plain}/textstats.py"
rm -f "${plain}/textstats.py.bak"
if (cd "${plain}" && "${python_bin}" plain_asserts.py >/dev/null 2>&1); then
  check "a broken module makes the bare-assert script exit non-zero" "no"
else
  check "a broken module makes the bare-assert script exit non-zero" "yes"
fi
rm -rf "${plain}"

if (cd "${lab_dir}" && "${python_bin}" examples/unittest_demo.py >/dev/null 2>&1); then
  check "examples/unittest_demo.py passes under the stdlib runner" "yes"
else
  check "examples/unittest_demo.py passes under the stdlib runner" "no"
fi

unittest_fail_out="$(cd "${lab_dir}" && "${python_bin}" examples/failure-demo/unittest_failure.py 2>&1)"
unittest_fail_exit=$?
if [ "${unittest_fail_exit}" -ne 0 ]; then
  check "the unittest failure demo exits non-zero" "yes"
else
  check "the unittest failure demo exits non-zero" "no"
fi
case "${unittest_fail_out}" in
  *"AssertionError: 4 != 3"*)
    check "unittest's assertEqual reports both sides" "yes" ;;
  *) check "unittest's assertEqual reports both sides" "no" ;;
esac
# The bare assert inside unittest gets NO values — nothing rewrote it.
if printf '%s\n' "${unittest_fail_out}" \
   | grep -A2 'test_a_bare_assert_inside_unittest' >/dev/null 2>&1; then
  bare_detail="$(printf '%s\n' "${unittest_fail_out}" | grep -c '^AssertionError$' || true)"
  if [ "${bare_detail}" -ge 1 ]; then
    check "a bare assert under unittest reports no values at all" "yes"
  else
    check "a bare assert under unittest reports no values at all" "no"
  fi
else
  check "a bare assert under unittest reports no values at all" "no"
fi

doctest_out="$(cd "${lab_dir}" && "${python_bin}" examples/doctest_demo.py 2>&1)"
doctest_exit=$?
if [ "${doctest_exit}" -eq 0 ]; then
  check "examples/doctest_demo.py exits 0" "yes"
else
  check "examples/doctest_demo.py exits 0" "no"
fi
case "${doctest_out}" in
  *"8 examples attempted, 0 failed"*) check "doctest runs all 8 documented examples" "yes" ;;
  *) check "doctest runs all 8 documented examples (got: ${doctest_out})" "no" ;;
esac

if (cd "${lab_dir}" && "${python_bin}" -m doctest examples/doctest_demo.py >/dev/null 2>&1); then
  check "python3 -m doctest agrees, and says nothing when all is well" "yes"
else
  check "python3 -m doctest agrees, and says nothing when all is well" "no"
fi

# --------------------------------------------------------------------------
echo
echo "9. Nothing here touches the network or the clock"
# --------------------------------------------------------------------------

if grep -rqE 'import (socket|urllib|requests|http)|datetime\.now|time\.time|random\.' \
     "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null; then
  check "no network, clock or randomness in examples/ or starter/" "no"
else
  check "no network, clock or randomness in examples/ or starter/" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
