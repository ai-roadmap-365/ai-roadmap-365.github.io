#!/usr/bin/env bash
# Tests for the Day 074 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This suite asserts on pytest's REAL behaviour, including four cases where the
# correct outcome is a failure:
#
#   * an un-specced Mock lets a typo'd method through, so the naive test PASSES
#     while the same call against the real object raises AttributeError;
#   * an autospec'd double refuses the typo, so the honest test FAILS;
#   * a patch aimed at where a function was DEFINED reaches nobody, so that
#     test FAILS, while the same test aimed at where the name is LOOKED UP
#     passes;
#   * a deliberately broken core makes the passing suite fail, which is what
#     proves the suite tests something.
#
# It also proves the refactored core is pure twice over: once by reading its
# imports, once by running it from a directory containing no files at all.
#
# No network at any point, non-interactive, deterministic. Exits 0 only if
# every check passes.
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

run_pytest() {
  # Never write a cache directory into the learner's tree.
  "${pytest_bin}" -p no:cacheprovider -q "$@" >/dev/null 2>&1
}

expect_pass() {
  local label="$1"; shift
  if run_pytest "$@"; then check "${label}" "yes"; else check "${label}" "no"; fi
}

expect_fail() {
  local label="$1"; shift
  if run_pytest "$@"; then check "${label}" "no"; else check "${label}" "yes"; fi
}

# run_pure <label> <python-body>
# Runs a body with the report core importable, from an EMPTY working directory.
# If the body needs a file, a clock, a network or a patch, it fails — which is
# exactly the property being proved.
run_pure() {
  local label="$1" body="$2" empty_dir
  empty_dir="$(mktemp -d "${TMPDIR:-/tmp}/day074-pure.XXXXXX")"
  if (cd "${empty_dir}" && PYTHONPATH="${examples_dir}" python3 -c "
import datetime
from report_v2 import (DailyReport, ReadingsUnavailable, ReportError,
                       ReportUnavailable, build_report, summarise)
from fakes import (DummyClient, FakeSensorClient, RecordingSleep, ScriptedModel,
                   SpyClock, StubSensorClient, frozen_clock)
DAY = datetime.date(2026, 4, 12)
READINGS = [12.0, 14.0, 20.0, 22.0] * 6
${body}
" >/dev/null 2>&1); then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
  rm -rf "${empty_dir}"
}

check_purity() {
  local core_file="$1" label="$2"
  if python3 - "${core_file}" <<'PY' 2>/dev/null
import ast
import sys

BANNED_MODULES = {
    "json", "os", "sys", "io", "pathlib", "shutil", "subprocess", "socket",
    "urllib", "http", "requests", "time", "random", "secrets", "sqlite3",
    "tempfile", "logging", "csv", "pickle",
}
BANNED_CALLS = {"open", "print", "input", "exec", "eval", "compile"}

source = open(sys.argv[1], encoding="utf-8").read()
tree = ast.parse(source)
problems = []
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in BANNED_MODULES:
                problems.append(f"import {alias.name}")
    elif isinstance(node, ast.ImportFrom):
        root = (node.module or "").split(".")[0]
        if root in BANNED_MODULES:
            problems.append(f"from {node.module} import ...")
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id in BANNED_CALLS:
            problems.append(f"{node.func.id}(...)")
sys.exit(1 if problems else 0)
PY
  then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
}

echo "Day 074 — Test the Logic, Stub the World"
echo

# --- 0. the tool ------------------------------------------------------------
echo "Tool"
if "${pytest_bin}" --version >/dev/null 2>&1; then
  check "pytest is available ($("${pytest_bin}" --version 2>&1 | head -1))" "yes"
else
  check "pytest is available" "no"
fi

# --- 1. the suites that must pass -------------------------------------------
echo
echo "Suites that must pass"
expect_pass "examples/test_patch_right_target.py passes (patch aimed where the name is looked up)" \
  "${examples_dir}/test_patch_right_target.py"
expect_pass "examples/test_report_v2_fakes.py passes (10 tests, no patching at all)" \
  "${examples_dir}/test_report_v2_fakes.py"
expect_pass "examples/test_model_boundary.py passes (14 tests, no model called)" \
  "${examples_dir}/test_model_boundary.py"

# --- 2. the autospec demonstration ------------------------------------------
echo
echo "The autospec demonstration — an un-specced Mock is dangerous"
expect_pass "examples/test_autospec_naive.py PASSES despite the misspelled method" \
  "${examples_dir}/test_autospec_naive.py"
expect_fail "examples/test_autospec_specced.py FAILS — create_autospec refuses the typo" \
  "${examples_dir}/test_autospec_specced.py"

if (cd "${examples_dir}" && python3 -c "
from sensor_client import SensorClient
from typo_under_test import latest_average
try:
    latest_average(SensorClient(), 'ALPHA', '2026-04-12')
except AttributeError:
    raise SystemExit(0)
raise SystemExit(1)
" >/dev/null 2>&1); then
  check "the same call against the REAL SensorClient raises AttributeError (production breaks)" "yes"
else
  check "the same call against the REAL SensorClient raises AttributeError (production breaks)" "no"
fi

if (cd "${examples_dir}" && python3 -c "
from unittest.mock import Mock, create_autospec
from sensor_client import SensorClient
Mock().fetch_radings                       # a bare Mock invents it
try:
    Mock(spec=SensorClient).fetch_radings  # spec= refuses it
except AttributeError:
    pass
else:
    raise SystemExit(1)
try:
    create_autospec(SensorClient, instance=True).fetch_readings('ALPHA', '2026-04-12', retries=3)
except TypeError:
    raise SystemExit(0)                    # autospec also checks the signature
raise SystemExit(1)
" >/dev/null 2>&1); then
  check "bare Mock invents attributes; spec= refuses them; autospec also checks signatures" "yes"
else
  check "bare Mock invents attributes; spec= refuses them; autospec also checks signatures" "no"
fi

# --- 3. the patch-target demonstration --------------------------------------
echo
echo "The patch-target demonstration — patch where the name is LOOKED UP"
expect_fail "examples/test_patch_wrong_target.py FAILS — patching sensor_service reaches nobody" \
  "${examples_dir}/test_patch_wrong_target.py"

if (cd "${examples_dir}" && python3 -c "
from unittest.mock import patch
import report_v1, sensor_service
original = report_v1.fetch_readings
with patch('sensor_service.fetch_readings') as replaced:
    assert sensor_service.fetch_readings is replaced      # the patch worked
    assert report_v1.fetch_readings is original           # and reached nobody
with patch('report_v1.fetch_readings') as replaced:
    assert report_v1.fetch_readings is replaced           # this is the target
assert report_v1.fetch_readings is original               # and it was undone
" >/dev/null 2>&1); then
  check "patch swaps only the name it names, and puts it back on exit" "yes"
else
  check "patch swaps only the name it names, and puts it back on exit" "no"
fi

# --- 4. the tests actually test something -----------------------------------
echo
echo "The tests test something — a broken core must make them fail"
broken_dir="$(mktemp -d "${TMPDIR:-/tmp}/day074-broken.XXXXXX")"
cp "${examples_dir}"/*.py "${broken_dir}/"
# Break exactly one line: the mean is now always zero.
sed -i.bak 's|mean=round(sum(readings) / len(readings), 1),|mean=0.0,|' "${broken_dir}/report_v2.py"
rm -f "${broken_dir}/report_v2.py.bak"
if grep -q 'mean=0.0,' "${broken_dir}/report_v2.py"; then
  check "the broken copy really was broken (one line changed)" "yes"
else
  check "the broken copy really was broken (one line changed)" "no"
fi
expect_fail "the fakes suite FAILS against the broken core" "${broken_dir}/test_report_v2_fakes.py"
rm -rf "${broken_dir}"

# --- 5. the purity proof ----------------------------------------------------
echo
echo "The purity proof — the refactored core needs no patching at all"
check_purity "${examples_dir}/report_v2.py" "examples/report_v2.py imports nothing that does I/O"
check_purity "${examples_dir}/model_boundary.py" "examples/model_boundary.py imports nothing that does I/O"

if python3 - "${examples_dir}/report_v1.py" <<'PY' 2>/dev/null
import ast, sys
tree = ast.parse(open(sys.argv[1], encoding="utf-8").read())
names = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        names.update(a.name.split(".")[0] for a in node.names)
    elif isinstance(node, ast.ImportFrom) and node.module:
        names.add(node.module.split(".")[0])
sys.exit(0 if "pathlib" in names else 1)
PY
then
  check "examples/report_v1.py does reach the world (pathlib) — the contrast is real" "yes"
else
  check "examples/report_v1.py does reach the world (pathlib) — the contrast is real" "no"
fi

run_pure "a report is built from an empty directory, with no patching" \
  "r = build_report('ALPHA', clock=frozen_clock(DAY), client=StubSensorClient(READINGS))
assert r == DailyReport('ALPHA', DAY, 24, 12.0, 22.0, 17.0), r"
run_pure "the rendered report is exact, from an empty directory" \
  "r = summarise('ALPHA', DAY, READINGS)
assert r.render().splitlines()[0] == 'station ALPHA — 2026-04-12'
assert r.render().splitlines()[-1] == '  mean     17.0'
assert r.filename() == 'ALPHA-2026-04-12.txt'"
run_pure "an empty day is refused, from an empty directory" \
  "try:
    summarise('ALPHA', DAY, [])
except ReportError as exc:
    assert 'empty day' in str(exc)
else:
    raise SystemExit(1)"
run_pure "the clock is read exactly once per report" \
  "c = SpyClock(DAY)
build_report('ALPHA', clock=c, client=StubSensorClient(READINGS))
assert c.calls == 1, c.calls"
run_pure "two transient failures are retried, and the backoff is 0.5 then 1.0" \
  "w = RecordingSleep()
client = FakeSensorClient([ReadingsUnavailable('t'), ReadingsUnavailable('t'), READINGS])
r = build_report('ALPHA', clock=frozen_clock(DAY), client=client, attempts=3, sleep=w)
assert r.mean == 17.0 and len(client.calls) == 3
assert w.waits == [0.5, 1.0], w.waits"
run_pure "exhausting every attempt raises ReportUnavailable" \
  "client = FakeSensorClient([ReadingsUnavailable('timeout')] * 3)
try:
    build_report('ALPHA', clock=frozen_clock(DAY), client=client, attempts=3)
except ReportUnavailable as exc:
    assert 'after 3 attempts' in str(exc)
else:
    raise SystemExit(1)"
run_pure "a dummy client proves the attempts guard fires before any call" \
  "try:
    build_report('ALPHA', clock=frozen_clock(DAY), client=DummyClient(), attempts=0)
except ReportError as exc:
    assert 'attempts must be at least 1' in str(exc)
else:
    raise SystemExit(1)"

# --- 6. the model boundary --------------------------------------------------
echo
echo "The model boundary — deterministic tests of a non-deterministic thing"
run_pure "a prompt is built and a scripted verdict parsed, from an empty directory" \
  "from model_boundary import build_prompt, classify_day
r = summarise('ALPHA', DAY, READINGS)
assert 'mean: 17.0' in build_prompt(r)
m = ScriptedModel(['label: mild\nconfidence: 0.82\nnote: calm'])
v = classify_day(r, model=m)
assert (v.label, v.confidence) == ('mild', 0.82), v
assert len(m.prompts) == 1"
run_pure "a malformed reply is retried with the same prompt, and never waits" \
  "from model_boundary import classify_day
import time
r = summarise('ALPHA', DAY, READINGS)
w = RecordingSleep()
m = ScriptedModel(['no thanks', 'label: warm\nconfidence: 0.5\nnote: x'])
started = time.perf_counter()
v = classify_day(r, model=m, attempts=2, sleep=w)
assert v.label == 'warm' and len(set(m.prompts)) == 1
assert w.waits == [1.0] and time.perf_counter() - started < 0.1"
run_pure "an unusable answer after every attempt raises, naming the last failure" \
  "from model_boundary import ModelError, classify_day
r = summarise('ALPHA', DAY, READINGS)
try:
    classify_day(r, model=ScriptedModel(['nope', 'still nope']), attempts=2)
except ModelError as exc:
    assert 'MalformedResponse' in str(exc)
else:
    raise SystemExit(1)"

# --- 7. the demonstrations run ----------------------------------------------
echo
echo "The demonstrations run"
for script in demo.py doubles_demo.py autospec_demo.py; do
  if (cd "${examples_dir}" && python3 "${script}" >/dev/null 2>&1); then
    check "examples/${script} runs end to end and exits 0" "yes"
  else
    check "examples/${script} runs end to end and exits 0" "no"
  fi
done

# --- 8. nothing here touches the network ------------------------------------
echo
echo "Boundaries"
# Match real import statements only — the word "socket" appears in prose here.
if grep -REl '^[[:space:]]*(import|from)[[:space:]]+(socket|urllib|http|ftplib|smtplib|requests|httpx)\b' \
    "${examples_dir}" "${starter_dir}" >/dev/null 2>&1; then
  check "no example or starter file imports a real network module" "no"
else
  check "no example or starter file imports a real network module" "yes"
fi

# --- 9. the learner's starter -----------------------------------------------
echo
echo "Your starter"
for f in "${starter_dir}"/*.py; do
  if python3 -c "compile(open('${f}').read(), '${f}', 'exec')" 2>/dev/null; then
    check "$(basename "${f}") is valid Python" "yes"
  else
    check "$(basename "${f}") is valid Python" "no"
  fi
done

check_purity "${starter_dir}/report_v2.py" "starter/report_v2.py imports nothing that does I/O"

if grep -rq 'NotImplementedError' "${starter_dir}"; then
  echo "Note: starter/ still has unfinished exercises — testing structure only."
  for name in DailyReport ReportError ReadingsUnavailable ReportUnavailable; do
    if grep -q "^class ${name}" "${starter_dir}/report_v2.py"; then
      check "starter/report_v2.py defines ${name}" "yes"
    else
      check "starter/report_v2.py defines ${name}" "no"
    fi
  done
  for name in summarise build_report; do
    if grep -q "^def ${name}" "${starter_dir}/report_v2.py"; then
      check "starter/report_v2.py defines ${name}" "yes"
    else
      check "starter/report_v2.py defines ${name}" "no"
    fi
  done
  for name in DummyClient StubSensorClient SpyClock RecordingSleep FakeSensorClient; do
    if grep -q "^class ${name}" "${starter_dir}/fakes.py"; then
      check "starter/fakes.py defines ${name}" "yes"
    else
      check "starter/fakes.py defines ${name}" "no"
    fi
  done
  if grep -q "^def frozen_clock" "${starter_dir}/fakes.py"; then
    check "starter/fakes.py defines frozen_clock" "yes"
  else
    check "starter/fakes.py defines frozen_clock" "no"
  fi
  if grep -q 'def test_' "${starter_dir}/test_report_v1.py" && grep -q 'def test_' "${starter_dir}/test_report_v2.py"; then
    check "both starter test files declare tests to write" "yes"
  else
    check "both starter test files declare tests to write" "no"
  fi
else
  expect_pass "starter/test_report_v1.py passes (your patch tests)" \
    "${starter_dir}/test_report_v1.py"
  expect_pass "starter/test_report_v2.py passes (your fake-based tests)" \
    "${starter_dir}/test_report_v2.py"
  run_pure_starter() {
    local label="$1" body="$2" empty_dir
    empty_dir="$(mktemp -d "${TMPDIR:-/tmp}/day074-starter.XXXXXX")"
    if (cd "${empty_dir}" && PYTHONPATH="${starter_dir}" python3 -c "
import datetime
from report_v2 import DailyReport, ReportError, build_report, summarise
from fakes import StubSensorClient, frozen_clock
DAY = datetime.date(2026, 4, 12)
READINGS = [12.0, 14.0, 20.0, 22.0] * 6
${body}
" >/dev/null 2>&1); then
      check "${label}" "yes"
    else
      check "${label}" "no"
    fi
    rm -rf "${empty_dir}"
  }
  run_pure_starter "your core builds a report from an empty directory, no patching" \
    "r = build_report('ALPHA', clock=frozen_clock(DAY), client=StubSensorClient(READINGS))
assert r == DailyReport('ALPHA', DAY, 24, 12.0, 22.0, 17.0), r
assert r.filename() == 'ALPHA-2026-04-12.txt'
assert r.render().splitlines()[-1] == '  mean     17.0'"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
