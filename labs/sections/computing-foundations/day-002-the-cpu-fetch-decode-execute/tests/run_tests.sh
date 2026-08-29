#!/usr/bin/env bash
# Tests for the Day 002 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the toy CPU simulator produces exactly the outputs, step
# counts, and final register states the lesson and worksheet promise, that
# the learner's program in starter/my_program.txt runs to HALT, and that
# the simulator rejects bad programs with a non-zero exit code.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cpu="${lab_dir}/examples/toy_cpu.sh"
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

contains() {
  # contains <haystack> <needle-regex-free-fixed-string>
  case "$1" in *"$2"*) return 0 ;; *) return 1 ;; esac
}

run_program_checks() {
  # run_program_checks <program> <label> <steps> <final-regs> <output-values...>
  local program="$1" label="$2" steps="$3" regs="$4"
  shift 4
  local output
  echo "Testing ${label} ..."
  if ! output="$(bash "${cpu}" "${program}" 2>&1)"; then
    check "${label}: simulator exits 0" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "${label}: simulator exits 0" "yes"

  local fetches
  fetches="$(printf '%s\n' "${output}" | grep -c '^PC=[0-9]*  FETCH')"
  if [ "${fetches}" = "${steps}" ]; then
    check "${label}: ${steps} instructions fetched" "yes"
  else
    check "${label}: ${steps} instructions fetched (got ${fetches})" "no"
  fi

  if contains "${output}" "HALT reached after ${steps} instructions."; then
    check "${label}: halts after ${steps} instructions" "yes"
  else
    check "${label}: halts after ${steps} instructions" "no"
  fi

  if contains "${output}" "Final registers: ${regs}"; then
    check "${label}: final registers are '${regs}'" "yes"
  else
    check "${label}: final registers are '${regs}'" "no"
  fi

  local expected_outputs actual_outputs
  expected_outputs=""
  for v in "$@"; do
    expected_outputs="${expected_outputs}OUTPUT: ${v}
"
  done
  actual_outputs="$(printf '%s\n' "${output}" | grep '^OUTPUT: ' || true)
"
  if [ "${actual_outputs}" = "${expected_outputs}" ]; then
    check "${label}: output lines are exactly [$*]" "yes"
  else
    check "${label}: output lines are exactly [$*]" "no"
  fi
}

# --- 1. the reference programs, against the values on the worksheet -----
run_program_checks "${lab_dir}/examples/programs/add-two-numbers.txt" \
  "add-two-numbers" 5 "R1=5 R2=3 R3=8 R4=0" 8
run_program_checks "${lab_dir}/examples/programs/trace-01.txt" \
  "trace-01" 5 "R1=4 R2=7 R3=11 R4=0" 11
run_program_checks "${lab_dir}/examples/programs/trace-02.txt" \
  "trace-02" 5 "R1=10 R2=40 R3=0 R4=0" 40
run_program_checks "${lab_dir}/examples/programs/trace-03.txt" \
  "trace-03" 7 "R1=10 R2=2 R3=0 R4=0" 8 10

# --- 2. the learner's own program ---------------------------------------
echo "Testing starter/my_program.txt ..."
if my_out="$(bash "${cpu}" "${lab_dir}/starter/my_program.txt" 2>&1)"; then
  check "my_program: runs to completion (exit 0)" "yes"
else
  check "my_program: runs to completion (exit 0)" "no"
  echo "${my_out}" | sed 's/^/    /'
  my_out=""
fi
if printf '%s\n' "${my_out}" | grep -q '^OUTPUT: '; then
  check "my_program: produces at least one OUTPUT line" "yes"
else
  check "my_program: produces at least one OUTPUT line" "no"
fi
if contains "${my_out}" "HALT reached after"; then
  check "my_program: ends with HALT" "yes"
else
  check "my_program: ends with HALT" "no"
fi

# --- 3. the simulator must reject broken programs ------------------------
echo "Testing error handling ..."
tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

printf 'FLY R1,3\nHALT\n' > "${tmp_dir}/bad-opcode.txt"
if bash "${cpu}" "${tmp_dir}/bad-opcode.txt" >/dev/null 2>&1; then
  check "unknown opcode is rejected (non-zero exit)" "no"
else
  check "unknown opcode is rejected (non-zero exit)" "yes"
fi

printf 'LOAD R9,1\nHALT\n' > "${tmp_dir}/bad-register.txt"
if bash "${cpu}" "${tmp_dir}/bad-register.txt" >/dev/null 2>&1; then
  check "unknown register is rejected (non-zero exit)" "no"
else
  check "unknown register is rejected (non-zero exit)" "yes"
fi

printf 'LOAD R1,1\nPRINT R1\n' > "${tmp_dir}/no-halt.txt"
if bash "${cpu}" "${tmp_dir}/no-halt.txt" >/dev/null 2>&1; then
  check "program without HALT is rejected (non-zero exit)" "no"
else
  check "program without HALT is rejected (non-zero exit)" "yes"
fi

if bash "${cpu}" "${tmp_dir}/does-not-exist.txt" >/dev/null 2>&1; then
  check "missing program file is rejected (non-zero exit)" "no"
else
  check "missing program file is rejected (non-zero exit)" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
