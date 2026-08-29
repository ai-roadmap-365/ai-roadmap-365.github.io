#!/usr/bin/env bash
# Tests for the Day 077 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# A lab about quality gates has exactly one obligation: prove the gate has
# TEETH. It is trivial to write a check.sh that prints five green lines and
# exits 0 no matter what the code does, and such a script is worse than
# nothing, because everyone downstream believes it.
#
# So this suite does not merely run the gate. It takes a temporary copy of the
# reference project, introduces ONE defect, and asserts the gate goes red —
# once for each of the five stages. If a stage were mis-wired, or the exit
# code were swallowed, exactly one of those five checks would go green when it
# should be red, and you would know which stage to look at.
#
# It also proves the lesson's most important claim mechanically: a test file
# containing zero assert statements still produces 100% coverage of a module
# that has a real bug in it.
#
# No network, non-interactive, deterministic. Exits 0 only if every check
# passes.

set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
examples_dir="${lab_dir}/examples"
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

# --- Tool resolution --------------------------------------------------------
# An explicit override, then this lab's .venv, then PATH. Fails loudly with
# instructions rather than silently skipping.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

need() {
  local tool="$1" override="$2" path
  if ! path="$(resolve_tool "${tool}" "${override}")"; then
    echo "FAIL: ${tool} not found." >&2
    echo "  Install it with:" >&2
    echo "    python3 -m venv .venv" >&2
    echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
    echo "  Or point this suite at existing tools, e.g." >&2
    echo "    RUFF=/path/to/ruff MYPY=/path/to/mypy COVERAGE=/path/to/coverage \\" >&2
    echo "      PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
    exit 1
  fi
  echo "${path}"
}

ruff_bin="$(need ruff "${RUFF:-}")" || exit 1
mypy_bin="$(need mypy "${MYPY:-}")" || exit 1
coverage_bin="$(need coverage "${COVERAGE:-}")" || exit 1
pytest_bin="$(need pytest "${PYTEST:-}")" || exit 1

export RUFF="${ruff_bin}" MYPY="${mypy_bin}" COVERAGE="${coverage_bin}"

# copy_project <destination>
# Make a throwaway copy of the reference project. Each defect check gets a
# fresh one, so the defects can never interact.
copy_project() {
  local dest="$1"
  cp -R "${examples_dir}/pricekit" "${dest}/pricekit"
  cp -R "${examples_dir}/tests" "${dest}/tests"
  cp "${examples_dir}/pyproject.toml" "${dest}/pyproject.toml"
  cp "${examples_dir}/check.sh" "${dest}/check.sh"
}

# gate_exit <project_dir> [flag]
# Run the gate in a project copy and echo its exit code.
gate_exit() {
  local dir="$1" flag="${2:-}" status
  (cd "${dir}" && bash check.sh ${flag} >"${dir}/gate.log" 2>&1)
  status=$?
  echo "${status}"
}

# expect_gate_fails <label> <stage> <defect-command>
# Copy the project, run the defect command inside the copy, then assert BOTH
# that the gate exited non-zero AND that the named stage is the one that
# complained. Asserting only the exit code would pass even if the wrong stage
# failed for the wrong reason.
expect_gate_fails() {
  local label="$1" stage="$2" defect="$3" work status log
  work="$(mktemp -d "${TMPDIR:-/tmp}/gate-defect.XXXXXX")"
  copy_project "${work}"
  (cd "${work}" && eval "${defect}")
  status="$(gate_exit "${work}")"
  log="$(cat "${work}/gate.log" 2>/dev/null || true)"
  if [ "${status}" -ne 0 ] && printf '%s' "${log}" | grep -q "FAIL: ${stage}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "      (exit ${status}; expected non-zero with a failing '${stage}' stage)"
  fi
  rm -rf "${work}"
}

echo "Testing the reference gate ..."

# --- 1. The gate is green on clean code ------------------------------------
clean="$(mktemp -d "${TMPDIR:-/tmp}/gate-clean.XXXXXX")"
copy_project "${clean}"
clean_status="$(gate_exit "${clean}")"
if [ "${clean_status}" -eq 0 ]; then
  check "check.sh exits 0 on the clean reference project" "yes"
else
  check "check.sh exits 0 on the clean reference project" "no"
  cat "${clean}/gate.log"
fi

for stage in format lint types tests coverage; do
  if grep -q "PASS: ${stage}" "${clean}/gate.log"; then
    check "the clean run reports PASS for the ${stage} stage" "yes"
  else
    check "the clean run reports PASS for the ${stage} stage" "no"
  fi
done

if grep -q "gate PASSED" "${clean}/gate.log"; then
  check "the clean run prints the gate PASSED verdict" "yes"
else
  check "the clean run prints the gate PASSED verdict" "no"
fi

if grep -q "TOTAL .* 100%" "${clean}/gate.log"; then
  check "the clean run reports 100% coverage of pricekit" "yes"
else
  check "the clean run reports 100% coverage of pricekit" "no"
fi
rm -rf "${clean}"

# --- 2. Five defects, five red gates ---------------------------------------
# This block is the point of the whole lab. Each defect is one line, breaks
# exactly one property, and must be caught by exactly one stage.
echo "Proving each stage can actually fail ..."

expect_gate_fails \
  "a formatting violation makes the gate fail at the format stage" \
  "format" \
  "python3 - <<'PY'
from pathlib import Path
p = Path('pricekit/receipt.py')
p.write_text(p.read_text().replace('return Money(0)', 'return Money( 0 )'))
PY"

expect_gate_fails \
  "an unused import makes the gate fail at the lint stage" \
  "lint" \
  "python3 - <<'PY'
from pathlib import Path
p = Path('pricekit/money.py')
p.write_text(p.read_text().replace(
    'from dataclasses import dataclass',
    'from dataclasses import dataclass\nimport os',
))
PY"

expect_gate_fails \
  "a wrong return annotation makes the gate fail at the types stage" \
  "types" \
  "python3 - <<'PY'
from pathlib import Path
p = Path('pricekit/money.py')
p.write_text(p.read_text().replace(
    'def __str__(self) -> str:',
    'def __str__(self) -> int:',
))
PY"

expect_gate_fails \
  "a broken implementation makes the gate fail at the tests stage" \
  "tests" \
  "python3 - <<'PY'
from pathlib import Path
p = Path('pricekit/money.py')
p.write_text(p.read_text().replace(
    'return Money(self.cents + other.cents, self.currency)',
    'return Money(self.cents + other.cents + 1, self.currency)',
))
PY"

expect_gate_fails \
  "untested new code makes the gate fail at the coverage stage" \
  "coverage" \
  "cat '${examples_dir}/../tests/fixtures/untested_addition.py' >> pricekit/receipt.py"

# --- 3. Fail-fast really stops early ---------------------------------------
# With --fail-fast the gate must stop at the first red stage. The proof is
# that the later stages are absent from the log, not merely that the exit code
# is non-zero.
ff="$(mktemp -d "${TMPDIR:-/tmp}/gate-ff.XXXXXX")"
copy_project "${ff}"
(cd "${ff}" && python3 - <<'PY'
from pathlib import Path
p = Path('pricekit/receipt.py')
p.write_text(p.read_text().replace('return Money(0)', 'return Money( 0 )'))
PY
)
ff_status="$(gate_exit "${ff}" "--fail-fast")"
if [ "${ff_status}" -ne 0 ] && ! grep -q "=== tests ===" "${ff}/gate.log"; then
  check "--fail-fast stops before the later stages run" "yes"
else
  check "--fail-fast stops before the later stages run" "no"
fi
if grep -q "=== tests ===" "${ff}/gate.log"; then
  check "the default (report-all) mode does reach the tests stage" "no"
else
  # Re-run the same defect WITHOUT --fail-fast and confirm the later stages
  # do run, so the two modes are genuinely different.
  gate_exit "${ff}" >/dev/null
  if grep -q "=== coverage ===" "${ff}/gate.log"; then
    check "the default (report-all) mode does reach the tests stage" "yes"
  else
    check "the default (report-all) mode does reach the tests stage" "no"
  fi
fi
rm -rf "${ff}"

# --- 4. Coverage measures execution, not verification ----------------------
# The claim: a test file with ZERO assert statements produces 100% coverage of
# a module that is wrong. Both halves are asserted mechanically.
echo "Proving what coverage cannot see ..."

demo="$(mktemp -d "${TMPDIR:-/tmp}/gate-cov.XXXXXX")"
cp "${examples_dir}/coverage-demo/promo.py" "${demo}/"
cp "${examples_dir}/coverage-demo/test_promo_no_assertions.py" "${demo}/"
cp "${examples_dir}/coverage-demo/test_promo_with_assertions.py" "${demo}/"

assert_count="$(grep -cE '^[[:space:]]*assert ' "${demo}/test_promo_no_assertions.py" || true)"
if [ "${assert_count}" -eq 0 ]; then
  check "the assertion-free test file contains zero assert statements" "yes"
else
  check "the assertion-free test file contains zero assert statements" "no"
fi

(cd "${demo}" && "${coverage_bin}" run --branch --source=promo -m pytest \
  test_promo_no_assertions.py -q >cov.log 2>&1 &&
  "${coverage_bin}" report --show-missing --fail-under=0 >>cov.log 2>&1)
if grep -qE 'promo\.py +4 +0 +2 +0 +100%' "${demo}/cov.log"; then
  check "a test file with no assertions still reports 100% coverage" "yes"
else
  check "a test file with no assertions still reports 100% coverage" "no"
  cat "${demo}/cov.log"
fi

# The same module, one assertion added: the tests now fail. Coverage did not
# change; only the verdict did.
if (cd "${demo}" && "${pytest_bin}" -p no:cacheprovider test_promo_with_assertions.py -q \
  >assert.log 2>&1); then
  check "adding one assertion catches the bug coverage could not see" "no"
else
  if grep -q 'assert 100 == 900' "${demo}/assert.log"; then
    check "adding one assertion catches the bug coverage could not see" "yes"
  else
    check "adding one assertion catches the bug coverage could not see" "no"
    cat "${demo}/assert.log"
  fi
fi
rm -rf "${demo}"

# --- 5. Reference files exist and are documentation, not decoration --------
echo "Checking the shipped reference files ..."

ci_yaml="${examples_dir}/ci-reference/quality-gate.yml"
if [ -f "${ci_yaml}" ]; then
  check "the continuous-integration workflow reference is present" "yes"
else
  check "the continuous-integration workflow reference is present" "no"
fi
if python3 -c "
import sys
text = open(sys.argv[1]).read()
required = ['actions/checkout', 'actions/setup-python', 'matrix:', 'bash check.sh', 'concurrency:']
sys.exit(0 if all(token in text for token in required) else 1)
" "${ci_yaml}" 2>/dev/null; then
  check "the workflow reference contains checkout, setup, matrix and the gate" "yes"
else
  check "the workflow reference contains checkout, setup, matrix and the gate" "no"
fi
if grep -qi 'REFERENCE' "${ci_yaml}" && grep -qi 'not executed by this lab' "${ci_yaml}"; then
  check "the workflow reference says plainly that it is not executed here" "yes"
else
  check "the workflow reference says plainly that it is not executed here" "no"
fi

pc_yaml="${examples_dir}/ci-reference/pre-commit-config.yaml"
if grep -q 'ruff-format' "${pc_yaml}" && ! grep -qE '^\s*-\s*id:\s*pytest' "${pc_yaml}"; then
  check "the pre-commit reference holds fast hooks and no test-suite hook" "yes"
else
  check "the pre-commit reference holds fast hooks and no test-suite hook" "no"
fi

# --- 6. One configuration file, not five -----------------------------------
if python3 -c "
import sys, tomllib
with open(sys.argv[1], 'rb') as handle:
    data = tomllib.load(handle)
tool = data.get('tool', {})
needed = ['pytest', 'mypy', 'ruff', 'coverage']
missing = [name for name in needed if name not in tool]
if missing:
    print('missing tool tables:', missing)
    sys.exit(1)
if tool['coverage']['report']['fail_under'] != 95:
    sys.exit(1)
if tool['coverage']['run']['branch'] is not True:
    sys.exit(1)
" "${examples_dir}/pyproject.toml"; then
  check "one pyproject.toml configures pytest, mypy, ruff and coverage" "yes"
else
  check "one pyproject.toml configures pytest, mypy, ruff and coverage" "no"
fi

for dotfile in .flake8 setup.cfg .isort.cfg mypy.ini pytest.ini .coveragerc; do
  if [ -e "${examples_dir}/${dotfile}" ]; then
    check "the reference project ships no ${dotfile}" "no"
  else
    check "the reference project ships no ${dotfile}" "yes"
  fi
done

# --- 7. The starter is a real skeleton -------------------------------------
echo "Checking the starter ..."

if bash -n "${starter_dir}/check.sh"; then
  check "starter/check.sh is valid bash" "yes"
else
  check "starter/check.sh is valid bash" "no"
fi

if python3 -c "
import sys, tomllib
with open(sys.argv[1], 'rb') as handle:
    tomllib.load(handle)
" "${starter_dir}/pyproject.toml"; then
  check "starter/pyproject.toml is valid TOML" "yes"
else
  check "starter/pyproject.toml is valid TOML" "no"
fi

for n in 1 2 3 4 5; do
  if grep -q "EXERCISE ${n} " "${starter_dir}/check.sh"; then
    check "starter/check.sh states exercise ${n}" "yes"
  else
    check "starter/check.sh states exercise ${n}" "no"
  fi
done

# The starter's gate must start with NO stages — that is the pedagogical
# point, and it is also what makes exercise 1 meaningful.
if grep -qE '^run_stage ' "${starter_dir}/check.sh"; then
  check "starter/check.sh ships with no stages wired in yet" "no"
else
  check "starter/check.sh ships with no stages wired in yet" "yes"
fi

# The starter deliberately ships tests for money.py and none for receipt.py,
# so the coverage floor genuinely bites when the learner reaches exercise 5.
if [ -f "${starter_dir}/tests/test_money.py" ] && [ ! -f "${starter_dir}/tests/test_receipt.py" ]; then
  check "the starter's suite is deliberately incomplete (no receipt tests)" "yes"
else
  check "the starter's suite is deliberately incomplete (no receipt tests)" "no"
fi

# And that incompleteness must be measurable: the starter's own coverage has
# to be UNDER the floor it will be asked to clear.
gap="$(mktemp -d "${TMPDIR:-/tmp}/gate-gap.XXXXXX")"
cp -R "${starter_dir}/pricekit" "${gap}/pricekit"
cp -R "${starter_dir}/tests" "${gap}/tests"
cp "${examples_dir}/pyproject.toml" "${gap}/pyproject.toml"
if (cd "${gap}" && "${coverage_bin}" run -m pytest >gap.log 2>&1 &&
  "${coverage_bin}" report >>gap.log 2>&1); then
  check "the starter's coverage starts below the 95% floor" "no"
else
  if grep -q 'Coverage failure' "${gap}/gap.log" || grep -q 'fail_under' "${gap}/gap.log"; then
    check "the starter's coverage starts below the 95% floor" "yes"
  else
    check "the starter's coverage starts below the 95% floor" "no"
    tail -6 "${gap}/gap.log"
  fi
fi
rm -rf "${gap}"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
