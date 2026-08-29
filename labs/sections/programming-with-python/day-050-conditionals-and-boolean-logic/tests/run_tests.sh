#!/usr/bin/env bash
# Tests for the Day 050 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Exercises the complete reference program (examples/triage.py) on known good
# and bad inputs, checking both the printed output and the process exit code,
# then imports two functions and checks their return values (the payoff of the
# main guard). Finally it checks the learner's starter: structurally while the
# exercises are unfinished, and to the same strict standard once complete.
# No network, non-interactive. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: do not let imported modules write __pycache__.
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

ref="${lab_dir}/examples/triage.py"
starter="${lab_dir}/starter/triage.py"
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

# check_run <label> <script> <expect_exit> <needle> <arg...>
# Runs the program, checks its exit code equals expect_exit and that its
# combined output contains needle.
check_run() {
  local label="$1" script="$2" expect_exit="$3" needle="$4"
  shift 4
  local out code
  out="$(python3 "${script}" "$@" 2>&1)"
  code=$?
  if [ "${code}" -eq "${expect_exit}" ] && printf '%s' "${out}" | grep -qF "${needle}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (exit ${code}, expected ${expect_exit}; output: ${out})"
  fi
}

run_program_checks() {
  local script="$1"
  echo "Testing ${script} ..."
  # Good inputs: correct decision, exit 0.
  check_run "0.95 verified -> AUTO_ACCEPT" "${script}" 0 "AUTO_ACCEPT (confidence: high)" 0.95 verified
  check_run "0.95 unverified -> REVIEW"    "${script}" 0 "REVIEW (confidence: high)"      0.95 unverified
  check_run "0.30 verified -> REJECT"      "${script}" 0 "REJECT (confidence: low)"       0.30 verified
  check_run "0.90 boundary -> AUTO_ACCEPT" "${script}" 0 "AUTO_ACCEPT"                     0.90 verified
  check_run "0.50 boundary -> REVIEW"      "${script}" 0 "REVIEW (confidence: medium)"    0.50 verified
  # Bad inputs: clear error, exit code 2.
  check_run "non-number score rejected"    "${script}" 2 "is not a number"                hot verified
  check_run "out-of-range score rejected"  "${script}" 2 "out of range"                   1.5 verified
  check_run "bad status rejected"          "${script}" 2 "status must be verified or unverified" 0.8 maybe
  check_run "wrong arg count rejected"     "${script}" 2 "expected 2 arguments"            0.8
}

# --- Reference program: always tested strictly ---
run_program_checks "${ref}"

# --- Import functions and check their return values (main-guard payoff) ---
echo "Testing importability of examples/triage.py ..."
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from triage import classify; \
assert classify(0.95, True) == 'AUTO_ACCEPT'; \
assert classify(0.95, False) == 'REVIEW'; \
assert classify(0.30, True) == 'REJECT'"; then
  check "import classify() returns correct decisions" "yes"
else
  check "import classify() returns correct decisions" "no"
fi
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from triage import confidence_band; \
assert confidence_band(0.95) == 'high'; \
assert confidence_band(0.50) == 'medium'; \
assert confidence_band(0.10) == 'low'"; then
  check "import confidence_band() returns correct bands" "yes"
else
  check "import confidence_band() returns correct bands" "no"
fi

# --- Learner starter ---
echo "Testing starter/triage.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/triage.py still has unfinished exercises — testing structure only."
  grep -q 'def classify' "${starter}" && check "starter defines classify" "yes" || check "starter defines classify" "no"
  grep -q 'def confidence_band' "${starter}" && check "starter defines confidence_band" "yes" || check "starter defines confidence_band" "no"
else
  # Learner finished: hold the starter to the same strict standard.
  run_program_checks "${starter}"
  grep -q '__name__ == "__main__"' "${starter}" && check "starter has the main guard" "yes" || check "starter has the main guard" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
