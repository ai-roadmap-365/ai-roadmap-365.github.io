#!/usr/bin/env bash
# Tests for the Day 072 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This is the outer harness. It does not test the practice store — the pytest
# suites inside examples/ and starter/ do that. This harness tests the SUITES:
#
#   * the refactored suite still passes;
#   * parametrization really expanded — the collected COUNT is exact, which is
#     the one check that distinguishes N independent tests from one loop;
#   * `-k` and `-m` select exactly the subsets the lesson claims;
#   * fixture scope is an observable number of executions, not a comment;
#   * `yield` teardown runs even when the test it served has failed;
#   * conftest discovery is directory-scoped — a fixture defined in a
#     subdirectory is invisible above it;
#   * --strict-markers turns a mistyped marker into an error;
#   * and, most important of all, breaking one line of the implementation
#     makes the suite FAIL. A suite that passes against broken code is not a
#     suite, it is decoration.
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

check_equals() {
  local label="$1" expected="$2" actual="$3"
  if [ "${expected}" = "${actual}" ]; then
    check "${label} (${actual})" "yes"
  else
    check "${label} — expected ${expected}, got ${actual}" "no"
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

# collected <dir> [extra pytest args...] -> the number of items collected.
# Reads the summary line pytest prints in quiet collect mode, which is either
# "36 tests collected in 0.01s" or "11/36 tests collected (25 deselected)...".
collected() {
  local dir="$1"
  shift
  (cd "${dir}" && "${pytest_bin}" --collect-only -q "$@" 2>/dev/null) \
    | grep -E '[0-9]+ tests? collected' \
    | head -1 \
    | sed -E 's|^([0-9]+)(/[0-9]+)? tests? collected.*|\1|'
}

echo "Day 072 lab checks"
echo
echo "pytest: $("${pytest_bin}" --version 2>&1 | head -1)"
echo

# --------------------------------------------------------------------------
echo "1. The refactored suite"
# --------------------------------------------------------------------------

if (cd "${lab_dir}/examples" && "${pytest_bin}" -q >/dev/null 2>&1); then
  check "examples/ suite passes and exits 0" "yes"
else
  check "examples/ suite passes and exits 0" "no"
fi

summary="$(cd "${lab_dir}/examples" && "${pytest_bin}" -q 2>&1 | tail -1)"
case "${summary}" in
  *"39 passed, 2 xfailed"*) check "examples/ run summary is '39 passed, 2 xfailed'" "yes" ;;
  *) check "examples/ run summary is '39 passed, 2 xfailed' — got: ${summary}" "no" ;;
esac

if (cd "${lab_dir}/starter" && "${pytest_bin}" -q >/dev/null 2>&1); then
  check "starter/ suite passes as shipped (the refactor must not break it)" "yes"
else
  check "starter/ suite passes as shipped (the refactor must not break it)" "no"
fi

# --------------------------------------------------------------------------
echo
echo "2. Parametrization expanded — exact collected counts"
# --------------------------------------------------------------------------

check_equals "examples/ collects the full expanded suite" "41" "$(collected "${lab_dir}/examples")"
check_equals "starter/ collects its hand-written tests" "13" "$(collected "${lab_dir}/starter")"

# One function, six cases -> six independent items.
check_equals "test_refuses_a_bad_value expands to six items" "6" \
  "$(collected "${lab_dir}/examples" test_sessions.py -k test_refuses_a_bad_value)"

# Two stacked decorators, three values each -> the nine-item cross product.
check_equals "two stacked parametrize decorators give the 3x3 cross product" "9" \
  "$(collected "${lab_dir}/examples" test_sessions.py -k test_every_topic_accepts_every_legal_duration)"

ids="$(cd "${lab_dir}/examples" && "${pytest_bin}" --collect-only -q test_sessions.py 2>/dev/null \
  | grep 'test_refuses_a_bad_value' || true)"
case "${ids}" in
  *"[minutes-over-the-cap]"*) check "ids= produced readable test ids, not [ref0]" "yes" ;;
  *) check "ids= produced readable test ids, not [ref0]" "no" ;;
esac
case "${ids}" in
  *"[ref0]"*|*"[minutes0]"*) check "no generated placeholder ids remain" "no" ;;
  *) check "no generated placeholder ids remain" "yes" ;;
esac

# --------------------------------------------------------------------------
echo
echo "3. Selection: -k expressions and registered markers"
# --------------------------------------------------------------------------

check_equals "-k refuses selects exactly the eleven refusal items" "11" \
  "$(collected "${lab_dir}/examples" -k refuses)"
check_equals "-m validation selects exactly the value-rule module" "21" \
  "$(collected "${lab_dir}/examples" -m validation)"
check_equals "-m 'not slow' deselects exactly the one file-reading test" "40" \
  "$(collected "${lab_dir}/examples" -m "not slow")"

# --------------------------------------------------------------------------
echo
echo "4. Fixture scope is an observable number of executions"
# --------------------------------------------------------------------------

scope_log="$(cd "${lab_dir}/examples" && "${pytest_bin}" scopes -s -q 2>&1)"
check_equals "session-scoped fixture body ran once for the whole run" "1" \
  "$(printf '%s\n' "${scope_log}" | grep -c '\[session\] body ran')"
check_equals "module-scoped fixture body ran once per module (two modules)" "2" \
  "$(printf '%s\n' "${scope_log}" | grep -c '\[module \] body ran')"
check_equals "function-scoped fixture body ran once per test (four tests)" "4" \
  "$(printf '%s\n' "${scope_log}" | grep -c '\[funct  \] body ran')"
check_equals "every function-scoped setup was matched by a teardown" "4" \
  "$(printf '%s\n' "${scope_log}" | grep -c '\[funct  \] teardown ran')"

# The fourth function-scoped test is the one that fails on purpose. Four
# setups and four teardowns therefore proves teardown ran after a failure.
case "${scope_log}" in
  *"4 passed, 1 xfailed"*) check "the deliberately failing test is reported as xfailed" "yes" ;;
  *) check "the deliberately failing test is reported as xfailed" "no" ;;
esac

audit_log="$(cd "${lab_dir}/examples" && "${pytest_bin}" -s -q test_store.py 2>&1)"
case "${audit_log}" in
  *"[audit] sessions before: 3, after: 4"*) check "yield-fixture teardown observed the test's changes" "yes" ;;
  *) check "yield-fixture teardown observed the test's changes" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "5. The built-in fixtures behave as documented"
# --------------------------------------------------------------------------

check_equals "the built-in fixture demonstrations all pass" "5" \
  "$(collected "${lab_dir}/examples" test_builtin_fixtures.py)"

# monkeypatch must undo itself: the test that asserts the environment is back
# to its original value runs AFTER the one that changed it, and passes.
if (cd "${lab_dir}/examples" && "${pytest_bin}" -q test_builtin_fixtures.py >/dev/null 2>&1); then
  check "monkeypatch's change did not survive the test that made it" "yes"
else
  check "monkeypatch's change did not survive the test that made it" "no"
fi

for builtin in tmp_path capsys monkeypatch; do
  if grep -q "def test_[a-z_]*(.*${builtin}" "${lab_dir}/examples/test_builtin_fixtures.py"; then
    check "a test demonstrates the built-in ${builtin} fixture" "yes"
  else
    check "a test demonstrates the built-in ${builtin} fixture" "no"
  fi
done

# --------------------------------------------------------------------------
echo
echo "6. conftest.py discovery is directory-scoped"
# --------------------------------------------------------------------------

leak_dir="$(mktemp -d "${TMPDIR:-/tmp}/day072-leak.XXXXXX")"
cp -R "${lab_dir}/examples/." "${leak_dir}/"
cat > "${leak_dir}/test_scope_leak.py" <<'PY'
def test_a_subdirectory_fixture_is_not_visible_here(session_scoped):
    assert session_scoped == "session-value"
PY
leak_out="$(cd "${leak_dir}" && "${pytest_bin}" -q test_scope_leak.py 2>&1)"
leak_rc=$?
if [ "${leak_rc}" -ne 0 ]; then
  check "a fixture from scopes/conftest.py is unusable outside scopes/" "yes"
else
  check "a fixture from scopes/conftest.py is unusable outside scopes/" "no"
fi
case "${leak_out}" in
  *"fixture 'session_scoped' not found"*) check "pytest names the missing fixture in its error" "yes" ;;
  *) check "pytest names the missing fixture in its error" "no" ;;
esac
rm -rf "${leak_dir}"

# --------------------------------------------------------------------------
echo
echo "7. --strict-markers turns a typo into an error"
# --------------------------------------------------------------------------

marker_dir="$(mktemp -d "${TMPDIR:-/tmp}/day072-marker.XXXXXX")"
cp -R "${lab_dir}/examples/." "${marker_dir}/"
cat > "${marker_dir}/test_typo_marker.py" <<'PY'
import pytest


@pytest.mark.slwo
def test_with_a_mistyped_marker():
    assert True
PY
if (cd "${marker_dir}" && "${pytest_bin}" -q test_typo_marker.py >/dev/null 2>&1); then
  check "an unregistered marker is rejected under --strict-markers" "no"
else
  check "an unregistered marker is rejected under --strict-markers" "yes"
fi
rm -rf "${marker_dir}"

# --------------------------------------------------------------------------
echo
echo "8. The suite fails when the implementation is broken"
# --------------------------------------------------------------------------

break_dir="$(mktemp -d "${TMPDIR:-/tmp}/day072-break.XXXXXX")"
cp -R "${lab_dir}/examples/." "${break_dir}/"
# One character of damage: a session of zero minutes is now accepted.
sed -e 's|if self.minutes <= 0:|if self.minutes < 0:|' \
  "${lab_dir}/examples/practice_store.py" > "${break_dir}/practice_store.py"

if grep -q 'if self.minutes < 0:' "${break_dir}/practice_store.py"; then
  check "the deliberate break was applied to the copy" "yes"
else
  check "the deliberate break was applied to the copy" "no"
fi

break_out="$(cd "${break_dir}" && "${pytest_bin}" -q 2>&1)"
if (cd "${break_dir}" && "${pytest_bin}" -q >/dev/null 2>&1); then
  check "broken implementation makes the suite fail" "no"
else
  check "broken implementation makes the suite fail" "yes"
fi
case "${break_out}" in
  *"minutes-zero"*) check "the failure names the exact parametrized case: [minutes-zero]" "yes" ;;
  *) check "the failure names the exact parametrized case: [minutes-zero]" "no" ;;
esac
# The other five cases of the same function must still pass — that is what
# independent test items buy you over a loop inside one test.
case "${break_out}" in
  *"1 failed"*) check "exactly one of the six parametrized cases failed" "yes" ;;
  *) check "exactly one of the six parametrized cases failed" "no" ;;
esac
rm -rf "${break_dir}"

# --------------------------------------------------------------------------
echo
echo "9. The lab's own premise holds"
# --------------------------------------------------------------------------

starter_dupes="$(grep -c 'store = PracticeStore(path)' "${lab_dir}/starter/test_practice_store.py")"
check_equals "starter/ really does copy-paste its setup" "8" "${starter_dupes}"

if grep -q 'PracticeStore(' "${lab_dir}/examples/test_store.py"; then
  check "examples/test_store.py constructs no store of its own" "no"
else
  check "examples/test_store.py constructs no store of its own" "yes"
fi

for name in store_path empty_store loaded_store audited_store sample_sessions; do
  if grep -q "^def ${name}(" "${lab_dir}/examples/conftest.py"; then
    check "conftest.py defines the ${name} fixture" "yes"
  else
    check "conftest.py defines the ${name} fixture" "no"
  fi
done

if grep -q 'tmp_path' "${lab_dir}/examples/conftest.py"; then
  check "the store fixture is built on the built-in tmp_path fixture" "yes"
else
  check "the store fixture is built on the built-in tmp_path fixture" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
if [ "${failures}" -ne 0 ]; then
  exit 1
fi
exit 0
