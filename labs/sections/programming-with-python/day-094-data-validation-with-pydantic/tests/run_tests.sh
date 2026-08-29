#!/usr/bin/env bash
# Tests for the Day 094 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This harness proves the claims the lesson makes, and proves them by running
# the code rather than by reading it:
#
#   * the schema refuses each of the eight planted problems, and the refusal
#     carries a machine-readable `type` and `loc`;
#   * lax mode really performs the conversions the lesson tabulates, and
#     strict mode really refuses them;
#   * the gate completes a two-thirds-bad batch with a non-zero reject count
#     instead of raising — the single most important behaviour in the lab;
#   * the miniature from-scratch validator collects every error rather than
#     the first, and lets through exactly the records it has no rules for;
#   * the starter suite is not vacuous: it goes fully green against the
#     reference implementation, and it goes RED when one rule is removed.
#
# Deterministic, non-interactive, offline. Exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. The README
# documents `pytest starter -q`, and running it writes .pyc files that would
# then fail the cleanliness check at the end of this script -- failing the
# reader for following the instructions. Clearing them here makes that final
# check measure what it claims to: what THIS run left behind. `.venv` is
# untouched, because the packages' own bytecode is theirs, not ours.
find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

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

# Resolve the tools: an explicit override, then this lab's own virtual
# environment, then whatever is on PATH. Fails loudly with instructions rather
# than skipping silently — a suite that quietly does nothing is worse than one
# that stops.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

install_hint() {
  echo "  Install this lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing environment:" >&2
  echo "    PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  install_hint
  exit 1
}

# The Python that owns that pytest is the one with pydantic installed, unless
# an explicit PYTHON says otherwise.
if [ -n "${PYTHON:-}" ] && [ -x "${PYTHON}" ]; then
  python_bin="${PYTHON}"
else
  python_bin="$(dirname "${pytest_bin}")/python3"
  [ -x "${python_bin}" ] || python_bin="$(command -v python3 || true)"
fi
if [ -z "${python_bin}" ] || [ ! -x "${python_bin}" ]; then
  echo "FAIL: python3 not found." >&2
  install_hint
  exit 1
fi

if ! "${python_bin}" -c "import pydantic" >/dev/null 2>&1; then
  echo "FAIL: pydantic is not importable from ${python_bin}." >&2
  install_hint
  exit 1
fi

echo "Day 094 — Guard the Boundary"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

echo "     python  $("${python_bin}" -c 'import sys; print(sys.version.split()[0])')"
versions="$("${python_bin}" - <<'PY'
from importlib.metadata import version
for name in ("pydantic", "pydantic_core", "pytest"):
    try:
        print(f"{name}=={version(name)}")
    except Exception:
        print(f"{name}==<not installed>")
PY
)"
printf '%s\n' "${versions}" | sed 's/^/     /'

for pin in "pydantic==2.13.4" "pytest==9.1.1"; do
  case "${versions}" in
    *"${pin}"*) check "installed ${pin} matches requirements/requirements.txt" "yes" ;;
    *) check "installed ${pin} matches requirements/requirements.txt" "no" ;;
  esac
done

# pydantic-settings is a separate distribution and this lab does not install
# it. The lesson describes it and reproduces no output from it; this check
# keeps that claim honest by confirming it really is absent here.
if "${python_bin}" -c "import pydantic_settings" >/dev/null 2>&1; then
  check "pydantic-settings is absent, as the lesson states" "no"
else
  check "pydantic-settings is absent, as the lesson states" "yes"
fi

# The v2 API surface the lesson teaches is the one that actually exists.
api_out="$("${python_bin}" - <<'PY' 2>&1
import pydantic

v2 = [
    "BaseModel", "Field", "ConfigDict", "TypeAdapter",
    "field_validator", "model_validator", "computed_field",
    "StringConstraints", "ValidationError",
]
missing = [name for name in v2 if not hasattr(pydantic, name)]
print("missing:" + ",".join(missing) if missing else "all-present")
print("model_validate:" + str(hasattr(pydantic.BaseModel, "model_validate")))
print("model_dump:" + str(hasattr(pydantic.BaseModel, "model_dump")))
PY
)"
case "${api_out}" in
  *all-present*) check "every pydantic v2 name the lesson uses exists" "yes" ;;
  *) check "every pydantic v2 name the lesson uses exists (${api_out})" "no" ;;
esac
case "${api_out}" in
  *"model_validate:True"*"model_dump:True"*)
    check "BaseModel exposes model_validate and model_dump (v2, not v1)" "yes" ;;
  *) check "BaseModel exposes model_validate and model_dump (v2, not v1)" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "2. The reference suite passes"
# --------------------------------------------------------------------------

tests_out="$(cd "${lab_dir}" && "${pytest_bin}" tests -q 2>&1)"
tests_exit=$?
if [ "${tests_exit}" -eq 0 ]; then
  check "pytest tests exits 0" "yes"
else
  check "pytest tests exits 0 (got ${tests_exit})" "no"
  printf '%s\n' "${tests_out}" | tail -40
fi
case "${tests_out}" in
  *"47 passed"*) check "pytest tests reports 47 passed" "yes" ;;
  *) check "pytest tests reports 47 passed (got: $(printf '%s' "${tests_out}" | tail -1))" "no" ;;
esac

collected="$(cd "${lab_dir}" && "${pytest_bin}" tests --collect-only -q 2>&1)"
for test_id in \
  "test_required_optional_and_nullable_are_three_different_things" \
  "test_one_call_reports_every_problem_at_once" \
  "test_every_error_entry_carries_loc_type_msg_and_input" \
  "test_strict_mode_refuses_the_same_strings" \
  "test_the_round_trip_is_not_symmetric_and_here_is_exactly_why" \
  "test_the_miniature_validator_collects_every_error_rather_than_the_first" \
  "test_the_gate_completes_the_batch_with_a_non_zero_reject_count" \
  "test_every_problem_the_brief_planted_is_actually_caught"
do
  case "${collected}" in
    *"${test_id}"*) check "collection finds ${test_id}" "yes" ;;
    *) check "collection finds ${test_id}" "no" ;;
  esac
done

# No test in this lab may assert on an error's prose. `type` and `loc` are the
# stable interface; `msg` is not. This is a grep, and it is deliberate.
if grep -nE "\[.msg.\]|errors\(\)\[0\]\[.msg.\]" \
     "${lab_dir}/tests/test_validation.py" "${lab_dir}/starter/test_starter.py" \
     | grep -vE "^\S+:[0-9]+: *#" | grep -q "assert"; then
  check "no test asserts on an error message string" "no"
else
  check "no test asserts on an error message string" "yes"
fi

# --------------------------------------------------------------------------
echo
echo "3. The gate runs the whole batch and reports what it refused"
# --------------------------------------------------------------------------

gate_dir="$(mktemp -d "${TMPDIR:-/tmp}/day094-gate.XXXXXX")"
gate_out="$(cd "${lab_dir}/examples" && "${python_bin}" gate.py \
  --input "${lab_dir}/data/raw-readings.json" --out-dir "${gate_dir}" 2>&1)"
gate_exit=$?
printf '%s\n' "${gate_out}" | sed 's/^/     /'
if [ "${gate_exit}" -eq 0 ]; then
  check "examples/gate.py exits 0 on a batch that is two-thirds bad" "yes"
else
  check "examples/gate.py exits 0 on a batch that is two-thirds bad (got ${gate_exit})" "no"
fi

for fragment in \
  'read      12 records' \
  'accepted  4' \
  'rejected  8' \
  'record 2 (RD-0003): operator [missing]' \
  'record 3 (RD-0004): pm2_5 [float_parsing]' \
  'record 4 (RD-0005): humidity_pct [less_than_equal]' \
  'humidty_pct [extra_forbidden]' \
  'record 6 (RD-0007): station.code [string_pattern_mismatch]' \
  'record 7 (RD-0001): reading_id [duplicate_id]' \
  'record 8 (RD-0009): recorded_at [datetime_from_date_parsing]' \
  'record 9 (RD-0010): <record> [value_error]'
do
  case "${gate_out}" in
    *"${fragment}"*) check "gate output contains: ${fragment}" "yes" ;;
    *) check "gate output contains: ${fragment}" "no" ;;
  esac
done

accepted_lines="$(wc -l < "${gate_dir}/accepted.jsonl" | tr -d ' ')"
if [ "${accepted_lines}" = "4" ]; then
  check "accepted.jsonl holds 4 records" "yes"
else
  check "accepted.jsonl holds 4 records (counted ${accepted_lines})" "no"
fi

report_check="$("${python_bin}" - "${gate_dir}/rejects.json" <<'PY' 2>&1
import json, sys
report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["records_seen"] == 12, report["records_seen"]
assert report["records_accepted"] == 4
assert report["records_rejected"] == 8
assert len(report["rejections"]) == 8
for rejection in report["rejections"]:
    for error in rejection["errors"]:
        assert set(error) >= {"loc", "type", "msg", "input"}, sorted(error)
print("report-ok")
PY
)"
case "${report_check}" in
  *report-ok*) check "rejects.json names all 8 refusals with loc/type/msg/input" "yes" ;;
  *) check "rejects.json names all 8 refusals with loc/type/msg/input (${report_check})" "no" ;;
esac

# The threshold flag really fails the build.
(cd "${lab_dir}/examples" && "${python_bin}" gate.py \
  --input "${lab_dir}/data/raw-readings.json" --out-dir "${gate_dir}" \
  --fail-over 0.1 >/dev/null 2>&1)
if [ $? -ne 0 ]; then
  check "--fail-over 0.1 exits non-zero on a 67% reject rate" "yes"
else
  check "--fail-over 0.1 exits non-zero on a 67% reject rate" "no"
fi
rm -rf "${gate_dir}"

# --------------------------------------------------------------------------
echo
echo "4. The demo scripts run and print what the lesson quotes"
# --------------------------------------------------------------------------

coercion_out="$(cd "${lab_dir}/examples" && "${python_bin}" coercion.py 2>&1)"
coercion_exit=$?
if [ "${coercion_exit}" -eq 0 ]; then
  check "examples/coercion.py exits 0" "yes"
else
  check "examples/coercion.py exits 0 (got ${coercion_exit})" "no"
fi
# Each of these is a claim the lesson makes about default coercion, checked
# against the line the program actually printed.
for fragment in \
  "'42'                     int          42                                 refused: int_type" \
  "'forty-two'              int          refused: int_parsing" \
  "42.7                     int          refused: int_from_float" \
  "True                     int          1  " \
  "42                       str          refused: string_type" \
  "3                        float        3.0                                3.0"
do
  case "${coercion_out}" in
    *"${fragment}"*) check "coercion table shows: $(echo "${fragment}" | tr -s ' ')" "yes" ;;
    *) check "coercion table shows: $(echo "${fragment}" | tr -s ' ')" "no" ;;
  esac
done

scratch_out="$(cd "${lab_dir}/examples" && "${python_bin}" scratch_demo.py 2>&1)"
scratch_exit=$?
if [ "${scratch_exit}" -eq 0 ]; then
  check "examples/scratch_demo.py exits 0" "yes"
else
  check "examples/scratch_demo.py exits 0 (got ${scratch_exit})" "no"
fi
for fragment in \
  'from scratch : accepted 9, rejected 3' \
  'pydantic     : accepted 5, rejected 7' \
  'record 4: pydantic says less_than_equal; the toy has no rule for it' \
  'record 8: pydantic says datetime_from_date_parsing; the toy has no rule for it'
do
  case "${scratch_out}" in
    *"${fragment}"*) check "scratch_demo shows: ${fragment}" "yes" ;;
    *) check "scratch_demo shows: ${fragment}" "no" ;;
  esac
done

serialize_out="$(cd "${lab_dir}/examples" && "${python_bin}" serialize.py 2>&1)"
serialize_exit=$?
if [ "${serialize_exit}" -eq 0 ]; then
  check "examples/serialize.py exits 0" "yes"
else
  check "examples/serialize.py exits 0 (got ${serialize_exit})" "no"
fi
for fragment in \
  'model_validate(model_dump())                  -> refused: band [extra_forbidden]' \
  'model_validate(model_dump(by_alias, -band))   -> accepted' \
  "required fields : ['humidity_pct', 'operator', 'pm2_5', 'reading_id', 'recorded_at', 'station', 'temperature_c']" \
  'loc[0]=(1, '"'"'station'"'"')'
do
  case "${serialize_out}" in
    *"${fragment}"*) check "serialize shows: ${fragment}" "yes" ;;
    *) check "serialize shows: ${fragment}" "no" ;;
  esac
done

# `notes` is optional, so it is absent from `required`; `operator` is required
# and nullable, so it is present. The line above asserts both at once.
case "${serialize_out}" in
  *"required fields : ['humidity_pct', 'operator',"*"'notes'"*)
    check "notes is absent from the required list" "no" ;;
  *) check "notes is absent from the required list" "yes" ;;
esac

# --------------------------------------------------------------------------
echo
echo "5. The starter is runnable before you start, and honest about it"
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

byhand_out="$(cd "${lab_dir}" && "${python_bin}" starter/byhand.py 2>&1)"
case "${byhand_out}" in
  *"by hand: accepted 10, rejected 2 of 12"*)
    check "starter/byhand.py runs and shows the hand-written validator's blind spots" "yes" ;;
  *) check "starter/byhand.py runs and shows the hand-written validator's blind spots" "no" ;;
esac

models_out="$(cd "${lab_dir}" && "${python_bin}" starter/models.py 2>&1)"
case "${models_out}" in
  *"No schema yet: Station, Reading not defined"*)
    check "starter/models.py reports its unfinished state honestly" "yes" ;;
  *) check "starter/models.py reports its unfinished state honestly" "no" ;;
esac

gate_starter_out="$(cd "${lab_dir}" && "${python_bin}" starter/gate.py 2>&1)"
case "${gate_starter_out}" in
  *"gate not built yet"*)
    check "starter/gate.py reports its unfinished state honestly" "yes" ;;
  *) check "starter/gate.py reports its unfinished state honestly" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "6. The starter suite is not vacuous — green when solved, red when broken"
# --------------------------------------------------------------------------

# Drop the reference implementation in as the student's answer, un-skip
# everything, and demand a fully green run. A suite that cannot tell a finished
# schema from an unfinished one is worth nothing.
work="$(mktemp -d "${TMPDIR:-/tmp}/day094-solved.XXXXXX")"
mkdir -p "${work}/lab"
cp -R "${lab_dir}/data" "${work}/data"
cp "${lab_dir}/starter/pytest.ini" "${lab_dir}/starter/byhand.py" "${work}/lab/"
cp "${lab_dir}/examples/models.py" "${lab_dir}/examples/gate.py" "${work}/lab/"
grep -v '^@pytest\.mark\.skip' "${lab_dir}/starter/test_starter.py" > "${work}/lab/test_starter.py"

solved_out="$(cd "${work}/lab" && "${pytest_bin}" . -q 2>&1)"
solved_exit=$?
if [ "${solved_exit}" -eq 0 ]; then
  check "the starter suite goes fully green against the finished schema" "yes"
else
  check "the starter suite goes fully green against the finished schema (exit ${solved_exit})" "no"
  printf '%s\n' "${solved_out}" | tail -20
fi
case "${solved_out}" in
  *"10 passed"*) check "all 10 starter tests pass once the exercises are done" "yes" ;;
  *) check "all 10 starter tests pass once the exercises are done" "no" ;;
esac

# Now break exactly one rule — widen the percentage constraint from 0-100 to
# 0-1000 — and demand the suite FAILS. This is the check that proves the range
# assertion is doing work rather than passing by accident.
"${python_bin}" - "${work}/lab/models.py" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
broken = text.replace("Annotated[int, Field(ge=0, le=100)]", "Annotated[int, Field(ge=0, le=1000)]")
assert broken != text, "the Percent constraint was not found — this check would be vacuous"
path.write_text(broken, encoding="utf-8")
PY
broken_out="$(cd "${work}/lab" && "${pytest_bin}" . -q 2>&1)"
broken_exit=$?
if [ "${broken_exit}" -ne 0 ]; then
  check "widening the percentage range makes the suite FAIL (exit ${broken_exit}, not 0)" "yes"
else
  check "widening the percentage range makes the suite FAIL — it did not, so the range check is vacuous" "no"
fi
case "${broken_out}" in
  *"test_an_out_of_range_percentage_is_refused_with_a_range_error_type"*)
    check "the failing run names the range check by test id" "yes" ;;
  *) check "the failing run names the range check by test id" "no" ;;
esac
rm -rf "${work}"

# --------------------------------------------------------------------------
echo
echo "7. The lab left nothing behind"
# --------------------------------------------------------------------------

# `.venv` is deliberately NOT in this list. The README tells the reader to
# create it, and the tool resolution at the top of this file looks inside
# it — so treating it as litter would fail the lab for following its own
# setup instructions.
for stray in "out"; do
  if [ -e "${lab_dir}/${stray}" ]; then
    check "no ${stray}/ left inside the lab after a full run" "no"
  else
    check "no ${stray}/ left inside the lab after a full run" "yes"
  fi
done

# `.venv` is pruned from the searches below. A virtual environment ships the
# installed packages' own precompiled bytecode -- hundreds of __pycache__
# directories that came with NumPy or pytest and have nothing to do with
# whether THIS lab tidied up after itself. Without the prune, following the
# README's own setup instructions makes this check fail, which reports a
# problem the reader cannot fix and did not cause.
if find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -print -quit 2>/dev/null | grep -q .; then
  check "no __pycache__ left inside the lab after a full run" "no"
else
  check "no __pycache__ left inside the lab after a full run" "yes"
fi

# Nothing here reaches the network at run time. The only network step is the
# one-off pip install described in the README.
# Restricted to .py files on purpose: this script quotes the pattern it is
# searching for, so scanning itself would always match.
if find "${lab_dir}/examples" "${lab_dir}/starter" "${lab_dir}/tests" -name '*.py' -print0 2>/dev/null \
     | xargs -0 grep -qE 'requests\.|urlopen|httpx\.|socket\.(create_connection|socket)\(' 2>/dev/null; then
  check "no lab source opens a network connection at run time" "no"
else
  check "no lab source opens a network connection at run time" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
