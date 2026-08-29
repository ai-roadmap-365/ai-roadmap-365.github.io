#!/usr/bin/env bash
# Tests for the Day 010 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Strategy: the counts in the committed sample log are FIXED and known, so we
# assert the reference script prints exactly those numbers. Then we run the
# learner's starter script; once they have replaced every REPLACE_ME, we hold
# it to the same known-good counts.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
log="${lab_dir}/examples/samples/access.log"
failures=0
checks=0

# Known-correct answers for the committed sample log (examples/samples/access.log).
EXPECT_TOTAL=40
EXPECT_TOP_IP="10.0.0.14"
EXPECT_TOP_COUNT=10
EXPECT_404=7
EXPECT_UNIQUE_PATHS=13

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

# --- Sanity: the sample data is present and unmodified in shape. --------------
echo "Checking the sample log ..."
if [ -f "${log}" ]; then
  check "sample log exists" "yes"
else
  check "sample log exists" "no"
  echo "${checks} checks, ${failures} failure(s)."
  exit 1
fi
lines="$(wc -l < "${log}" | tr -d ' ')"
[ "${lines}" = "${EXPECT_TOTAL}" ] && check "sample log has ${EXPECT_TOTAL} lines" "yes" || check "sample log has ${EXPECT_TOTAL} lines (got ${lines})" "no"

# --- Independent recomputation of the ground truth from the raw log. ----------
# The tests do NOT trust the scripts; they recompute the answers here and
# compare against the fixed EXPECT_* values, then compare the scripts too.
top_ip="$(awk '{print $1}' "${log}" | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')"
top_count="$(awk '{print $1}' "${log}" | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')"
count_404="$(awk '$9 == 404' "${log}" | wc -l | tr -d ' ')"
unique_paths="$(awk '{print $7}' "${log}" | sort -u | wc -l | tr -d ' ')"

check "top IP is ${EXPECT_TOP_IP}" "$([ "${top_ip}" = "${EXPECT_TOP_IP}" ] && echo yes || echo no)"
check "top IP count is ${EXPECT_TOP_COUNT}" "$([ "${top_count}" = "${EXPECT_TOP_COUNT}" ] && echo yes || echo no)"
check "404 count is ${EXPECT_404}" "$([ "${count_404}" = "${EXPECT_404}" ] && echo yes || echo no)"
check "unique paths is ${EXPECT_UNIQUE_PATHS}" "$([ "${unique_paths}" = "${EXPECT_UNIQUE_PATHS}" ] && echo yes || echo no)"

# --- The reference script must report the same known-good numbers. -----------
run_report_checks() {
  local script="$1" strict="$2" output
  echo "Testing ${script} ..."
  if ! output="$(bash "${script}" 2>&1)"; then
    check "script exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "script exits successfully" "yes"
  echo "${output}" | grep -q '^=== Log Analysis Report ===$' && check "prints report header" "yes" || check "prints report header" "no"
  echo "${output}" | grep -q '^=== End of report ===$' && check "prints report footer" "yes" || check "prints report footer" "no"

  if [ "${strict}" = "strict" ]; then
    echo "${output}" | grep -q "^Total requests: ${EXPECT_TOTAL}$" && check "reports Total requests: ${EXPECT_TOTAL}" "yes" || check "reports Total requests: ${EXPECT_TOTAL}" "no"
    # The top IP line is "  10 10.0.0.14" (leading spaces from uniq -c).
    echo "${output}" | grep -Eq "^[[:space:]]*${EXPECT_TOP_COUNT}[[:space:]]+${EXPECT_TOP_IP}$" && check "shows top IP ${EXPECT_TOP_IP} with ${EXPECT_TOP_COUNT}" "yes" || check "shows top IP ${EXPECT_TOP_IP} with ${EXPECT_TOP_COUNT}" "no"
    echo "${output}" | grep -q "^404 responses: ${EXPECT_404}$" && check "reports 404 responses: ${EXPECT_404}" "yes" || check "reports 404 responses: ${EXPECT_404}" "no"
    echo "${output}" | grep -q "^Unique paths: ${EXPECT_UNIQUE_PATHS}$" && check "reports Unique paths: ${EXPECT_UNIQUE_PATHS}" "yes" || check "reports Unique paths: ${EXPECT_UNIQUE_PATHS}" "no"
  fi
}

run_report_checks "${lab_dir}/examples/analyze_log.sh" strict

# --- The learner's starter: structure-only until they finish the exercises. --
if grep -q 'REPLACE_ME' "${lab_dir}/starter/analyze_log.sh"; then
  echo "Note: starter/analyze_log.sh still has unfinished exercises (REPLACE_ME) — testing structure only."
  run_report_checks "${lab_dir}/starter/analyze_log.sh" lenient
else
  run_report_checks "${lab_dir}/starter/analyze_log.sh" strict
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
