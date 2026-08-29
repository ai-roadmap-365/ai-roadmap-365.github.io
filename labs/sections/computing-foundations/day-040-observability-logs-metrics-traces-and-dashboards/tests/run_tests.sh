#!/usr/bin/env bash
# Tests for the Day 040 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies the observability pipeline: structured JSON logs are emitted, the
# error count and rate match the known injected errors (6 of 50 = 12.00%), and
# a numeric p95 latency is computed. Runs fully offline; exits 0 on success.
set -u

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

run_pipeline_checks() {
  local script="$1" strict="$2" output
  echo "Testing ${script} ..."
  if ! output="$(bash "${script}" 2>&1)"; then
    check "script exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "script exits successfully" "yes"

  # Pillar 1: structured JSON logs are emitted (a line with the required keys).
  if echo "${output}" | grep -Eq '\{"ts":".*","level":".*","event":"request_complete".*"latency_ms":[0-9]+\}'; then
    check "emits structured JSON request logs with latency_ms" "yes"
  else
    check "emits structured JSON request logs with latency_ms" "no"
  fi
  # At least one ERROR-level line exists in the emitted logs.
  echo "${output}" | grep -q '"level":"ERROR"' && \
    check "emits at least one ERROR-level log line" "yes" || \
    check "emits at least one ERROR-level log line" "no"

  # Dashboard shape: all five metric lines present.
  for field in "Total requests:" "Errors:" "Error rate:" "p95 latency (ms):" "p50 latency (ms):"; do
    echo "${output}" | grep -q "^${field}" && check "dashboard prints '${field}'" "yes" || check "dashboard prints '${field}'" "no"
  done

  # Trace: nested spans reconstructed.
  echo "${output}" | grep -q "span total_request" && \
    check "trace reconstructs the total_request span" "yes" || \
    check "trace reconstructs the total_request span" "no"

  if [ "${strict}" = "strict" ]; then
    # Pillar 2: metrics match the known injected errors (6 of 50).
    total="$(echo "${output}" | sed -n 's/^Total requests:[[:space:]]*//p')"
    errors="$(echo "${output}" | sed -n 's/^Errors:[[:space:]]*//p')"
    rate="$(echo "${output}" | sed -n 's/^Error rate:[[:space:]]*//p')"
    p95="$(echo "${output}" | sed -n 's/^p95 latency (ms):[[:space:]]*//p')"

    [ "${total}" = "50" ] && check "total requests is 50" "yes" || check "total requests is 50 (got '${total}')" "no"
    [ "${errors}" = "6" ] && check "error count matches known injected errors (6)" "yes" || check "error count is 6 (got '${errors}')" "no"
    [ "${rate}" = "12.00%" ] && check "error rate is 12.00%" "yes" || check "error rate is 12.00% (got '${rate}')" "no"
    case "${p95}" in
      '' | *[!0-9]*) check "p95 latency is a number (got '${p95}')" "no" ;;
      *)             check "p95 latency is a number" "yes" ;;
    esac
  fi
}

# The completed reference must pass every strict check.
run_pipeline_checks "${lab_dir}/examples/observe.sh" strict

# The starter ships with FILL_ME placeholders; once the learner has replaced
# them all, hold their script to the same strict standard.
if grep -q 'FILL_ME' "${lab_dir}/starter/observe.sh"; then
  echo "Note: starter/observe.sh still has unfinished exercises (FILL_ME) — testing structure only."
  run_pipeline_checks "${lab_dir}/starter/observe.sh" lenient
else
  run_pipeline_checks "${lab_dir}/starter/observe.sh" strict
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
