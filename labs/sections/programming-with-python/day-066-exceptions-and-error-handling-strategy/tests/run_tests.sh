#!/usr/bin/env bash
# Tests for the Day 066 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# These checks test BEHAVIOUR, not the presence of files: that the right
# exception type comes out of the right input, that __cause__ carries the
# original error (chaining), that a bad record is rejected while the rest of
# the file still processes, that a missing file exits non-zero, that the
# retry helper backs off and then gives up with the cause preserved, and
# that logging.exception really wrote a chained traceback to the log file.
#
# Everything is deterministic: no randomness, no network, no clock reading.
# Exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
samples="${lab_dir}/examples/samples"
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
# Runs assertions against `triage` imported from module_dir. Any AssertionError
# (or any other exception) fails the check.
check_py() {
  local label="$1" module_dir="$2" body="$3"
  if PYTHONPATH="${module_dir}" python3 -c "import triage
${body}" >/dev/null 2>&1; then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
}

# check_run <label> <script> <args...> :: expects exit code in EXPECT_EXIT and
# a substring in EXPECT_TEXT (searched in combined stdout+stderr).
check_run() {
  local label="$1" script="$2" expect_exit="$3" needle="$4"
  shift 4
  local out code logfile
  logfile="$(mktemp -t triage-test.XXXXXX)"
  out="$(python3 "${script}" "$@" "${logfile}" 2>&1)"
  code=$?
  rm -f "${logfile}"
  if [ "${code}" -eq "${expect_exit}" ] && printf '%s' "${out}" | grep -qF "${needle}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (exit ${code}, expected ${expect_exit}; output: ${out})"
  fi
}

run_unit_checks() {
  local module_dir="$1"
  echo "Testing the handlers in ${module_dir} (direct calls) ..."

  check_py "parse_record accepts a good line" "${module_dir}" \
    'import json
record = triage.parse_record(json.dumps({"id": "P-1", "name": "Ada", "severity": 3}), 1)
assert record == {"id": "P-1", "severity": 3}, record'

  check_py "missing field -> RecordError chained from KeyError" "${module_dir}" \
    'import json
line = json.dumps({"id": "P-1"})
try:
    triage.parse_record(line, 7)
except triage.RecordError as err:
    assert "line 7" in str(err), str(err)
    assert "severity" in str(err), str(err)
    assert isinstance(err.__cause__, KeyError), err.__cause__
else:
    raise SystemExit("no RecordError raised")'

  check_py "bad severity -> RecordError chained from ValueError" "${module_dir}" \
    'import json
line = json.dumps({"id": "P-1", "severity": "high"})
try:
    triage.parse_record(line, 2)
except triage.RecordError as err:
    assert isinstance(err.__cause__, ValueError), err.__cause__
    assert not isinstance(err.__cause__, json.JSONDecodeError), err.__cause__
else:
    raise SystemExit("no RecordError raised")'

  check_py "malformed JSON -> RecordError chained from JSONDecodeError" "${module_dir}" \
    'import json
try:
    triage.parse_record("this is not json", 4)
except triage.RecordError as err:
    assert "not valid JSON" in str(err), str(err)
    assert isinstance(err.__cause__, json.JSONDecodeError), err.__cause__
else:
    raise SystemExit("no RecordError raised")'

  check_py "out-of-range severity -> RecordError with NO cause" "${module_dir}" \
    'import json
line = json.dumps({"id": "P-1", "severity": 9})
try:
    triage.parse_record(line, 3)
except triage.RecordError as err:
    assert "outside 1-5" in str(err), str(err)
    assert err.__cause__ is None, err.__cause__
else:
    raise SystemExit("no RecordError raised")'

  check_py "band and summarize count the three bands" "${module_dir}" \
    'assert triage.band(1) == "immediate" and triage.band(3) == "urgent" and triage.band(5) == "routine"
counts = triage.summarize([{"severity": 1}, {"severity": 2}, {"severity": 4}, {"severity": 5}])
assert counts == {"immediate": 2, "urgent": 1, "routine": 1}, counts'

  check_py "retry succeeds after two failures, with backoff" "${module_dir}" \
    'calls = []
delays = []
@triage.retry(attempts=3, base_delay=0.05, sleep=delays.append)
def flaky():
    calls.append(1)
    if len(calls) < 3:
        raise ConnectionError("not yet")
    return "ok"
assert flaky() == "ok"
assert len(calls) == 3, calls
assert delays == [0.05, 0.1], delays'

  check_py "retry gives up as DispatchError chained from the last error" "${module_dir}" \
    '@triage.retry(attempts=3, base_delay=0.05, sleep=lambda seconds: None)
def always_down():
    raise ConnectionError("down")
try:
    always_down()
except triage.DispatchError as err:
    assert "3 attempts" in str(err), str(err)
    assert isinstance(err.__cause__, ConnectionError), err.__cause__
else:
    raise SystemExit("no DispatchError raised")'

  check_py "retry does not retry a non-transient error" "${module_dir}" \
    'calls = []
@triage.retry(attempts=3, base_delay=0.05, sleep=lambda seconds: None)
def broken():
    calls.append(1)
    raise ValueError("permanently wrong")
try:
    broken()
except ValueError:
    assert len(calls) == 1, calls
else:
    raise SystemExit("ValueError should have propagated on the first attempt")'
}

run_end_to_end_checks() {
  local script="$1"
  echo "Testing ${script} end to end ..."

  check_run "clean intake: 5 admitted, exit 0" "${script}" 0 "admitted 5 record(s), rejected 0" \
    "${samples}/intake.jsonl"
  check_run "clean intake: two immediate" "${script}" 0 "immediate  2" \
    "${samples}/intake.jsonl"
  check_run "bad severity: rejected by name, rest still processed" "${script}" 0 \
    "rejected: line 2: severity is not a whole number" "${samples}/bad-severity.jsonl"
  check_run "missing field: rejected by name, rest still processed" "${script}" 0 \
    "rejected: line 2: missing field 'severity'" "${samples}/missing-field.jsonl"
  check_run "missing field: 2 admitted, 1 rejected" "${script}" 0 \
    "admitted 2 record(s), rejected 1" "${samples}/missing-field.jsonl"
  check_run "retry backs off before succeeding" "${script}" 0 \
    "retrying in 0.10s" "${samples}/intake.jsonl"
  check_run "missing file: fails fast, exit 1" "${script}" 1 \
    "error: no such intake file" "${samples}/no-such-file.jsonl"

  # No argument at all: the shell prints usage and exits 2.
  local usage_out usage_code
  usage_out="$(python3 "${script}" 2>&1)"
  usage_code=$?
  if [ "${usage_code}" -eq 2 ] && printf '%s' "${usage_out}" | grep -qF "usage: python3 triage.py"; then
    check "no argument: usage message, exit 2" "yes"
  else
    check "no argument: usage message, exit 2" "no"
    echo "    (exit ${usage_code}; output: ${usage_out})"
  fi

  # The log file must contain a real chained traceback written by
  # logging.exception -- not just the message.
  local logfile out
  logfile="$(mktemp -t triage-log.XXXXXX)"
  python3 "${script}" "${samples}/bad-severity.jsonl" "${logfile}" >/dev/null 2>&1
  out="$(cat "${logfile}")"
  printf '%s' "${out}" | grep -qF "ERROR: rejected record on line 2" \
    && check "log: ERROR line for the rejected record" "yes" \
    || check "log: ERROR line for the rejected record" "no"
  printf '%s' "${out}" | grep -qF "Traceback (most recent call last):" \
    && check "log: full traceback recorded" "yes" \
    || check "log: full traceback recorded" "no"
  printf '%s' "${out}" | grep -qF "The above exception was the direct cause of the following exception" \
    && check "log: chaining preserved in the log" "yes" \
    || check "log: chaining preserved in the log" "no"
  printf '%s' "${out}" | grep -qF "ValueError: invalid literal for int()" \
    && check "log: the original ValueError is still there" "yes" \
    || check "log: the original ValueError is still there" "no"
  rm -f "${logfile}"
}

echo "Testing the anti-pattern in examples/swallowing.py ..."
swallow_out="$(python3 "${lab_dir}/examples/swallowing.py" "${samples}/no-such-file.jsonl" 2>&1)"
swallow_code=$?
if [ "${swallow_code}" -eq 0 ] && printf '%s' "${swallow_out}" | grep -qF "done"; then
  check "bare except hides a missing file and still exits 0 (the bug we are fixing)" "yes"
else
  check "bare except hides a missing file and still exits 0 (the bug we are fixing)" "no"
fi

echo "Testing that examples/raw_triage.py really raises the three errors ..."
for pair in "no-such-file.jsonl:FileNotFoundError" "bad-severity.jsonl:ValueError" "missing-field.jsonl:KeyError"; do
  sample="${pair%%:*}"
  wanted="${pair##*:}"
  raw_out="$(python3 "${lab_dir}/examples/raw_triage.py" "${samples}/${sample}" 2>&1)"
  raw_code=$?
  if [ "${raw_code}" -ne 0 ] && printf '%s' "${raw_out}" | grep -qF "${wanted}:"; then
    check "raw_triage on ${sample} raises ${wanted}" "yes"
  else
    check "raw_triage on ${sample} raises ${wanted}" "no"
  fi
done

# --- Reference: always tested strictly ---
run_unit_checks "${lab_dir}/examples"
run_end_to_end_checks "${lab_dir}/examples/triage.py"

# --- Learner starter ---
echo "Testing starter/triage.py ..."
starter="${lab_dir}/starter/triage.py"
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/triage.py still has unfinished exercises — testing structure only."
  grep -q 'def parse_record' "${starter}" && check "starter defines parse_record" "yes" || check "starter defines parse_record" "no"
  grep -q 'def load_records' "${starter}" && check "starter defines load_records" "yes" || check "starter defines load_records" "no"
  grep -q 'def retry' "${starter}" && check "starter defines retry" "yes" || check "starter defines retry" "no"
elif grep -qE '^[[:space:]]*except[[:space:]]*:' "${starter}"; then
  check "starter has no bare except left" "no"
  echo "    (a bare 'except:' is still in starter/triage.py — replace it with narrow handlers)"
else
  check "starter has no bare except left" "yes"
  run_unit_checks "${lab_dir}/starter"
  run_end_to_end_checks "${lab_dir}/starter/triage.py"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
