#!/usr/bin/env bash
# Tests for the Day 003 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the completed reference script produces a well-formed
# measurements report (structure + behavior: warm read not slower than the
# cold read beyond a noise tolerance, test file cleaned up), and — once the
# learner has finished the starter script — checks their version the same way.
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

run_measurement_checks() {
  local script="$1" strict="$2" output
  echo "Testing ${script} ..."
  if ! output="$(bash "${script}" 2>&1)"; then
    check "script exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "script exits successfully" "yes"
  echo "${output}" | grep -q '^=== Memory Hierarchy Measurements ===$' && check "prints report header" "yes" || check "prints report header" "no"
  echo "${output}" | grep -q '^=== End of measurements ===$' && check "prints report footer" "yes" || check "prints report footer" "no"
  for field in "L1 data cache:" "L2 cache:" "RAM:" "Cold read (first pass):" "Warm read (second pass):"; do
    echo "${output}" | grep -q "^${field}" && check "prints '${field}'" "yes" || check "prints '${field}'" "no"
  done
  if [ "${strict}" = "strict" ]; then
    if echo "${output}" | grep -q "unknown"; then
      check "no field is left 'unknown'" "no"
    else
      check "no field is left 'unknown'" "yes"
    fi
    # Behavior: the warm (page-cached) read must not be meaningfully slower
    # than the cold read. Tolerance factor 1.5 absorbs timer noise on very
    # fast machines where both reads are served from the page cache.
    cold="$(echo "${output}" | sed -n 's/^Cold read (first pass):[[:space:]]*\([0-9.]*\) s.*/\1/p')"
    warm="$(echo "${output}" | sed -n 's/^Warm read (second pass):[[:space:]]*\([0-9.]*\) s.*/\1/p')"
    if [ -n "${cold}" ] && [ -n "${warm}" ] && awk -v c="${cold}" -v w="${warm}" 'BEGIN { exit !(c > 0 && w > 0 && w <= c * 1.5) }'; then
      check "warm read <= 1.5x cold read (page-cache effect, with tolerance)" "yes"
    else
      check "warm read <= 1.5x cold read (page-cache effect, with tolerance)" "no"
    fi
    if [ ! -f "${lab_dir}/read-speed-testfile.bin" ]; then
      check "test file cleaned up after run" "yes"
    else
      check "test file cleaned up after run" "no"
      rm -f "${lab_dir}/read-speed-testfile.bin"
    fi
  fi
}

run_measurement_checks "${lab_dir}/examples/measure_read_speed.sh" strict

# The starter ships with 'unknown' values on purpose; once the learner has
# replaced them all, hold their script to the same strict standard.
if grep -q '"unknown"' "${lab_dir}/starter/measure_read_speed.sh"; then
  echo "Note: starter/measure_read_speed.sh still has unfilled exercises — testing structure only."
  run_measurement_checks "${lab_dir}/starter/measure_read_speed.sh" lenient
else
  run_measurement_checks "${lab_dir}/starter/measure_read_speed.sh" strict
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
