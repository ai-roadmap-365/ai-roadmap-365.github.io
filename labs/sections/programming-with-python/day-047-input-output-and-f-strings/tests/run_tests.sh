#!/usr/bin/env bash
# Tests for the Day 047 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that io_demo.py reads a pair of numbers from EITHER a command-line
# argument OR standard input, prints an aligned, two-decimal report, and — on
# bad input — writes a message to STDERR and exits non-zero. The reference is
# always held to a strict behavioral standard. The learner's starter is checked
# strictly once every FILL_ME_IN placeholder is gone, and structurally (does it
# still parse, does it still contain the scaffolding) before that.
#
# No network, no interactivity: every input is supplied via arg or pipe.
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

# Full behavioral checks — run against any COMPLETE program.
run_strict_checks() {
  local script="$1" arg_out stdin_out bad_code bad_stderr bad_stdout tmp_err tmp_out

  echo "Testing ${script} (strict behavior) ..."
  tmp_err="$(mktemp)"
  tmp_out="$(mktemp)"

  # 1. Argument mode: `io_demo.py 5 7` exits 0.
  if arg_out="$(python3 "${script}" 5 7 2>/dev/null)"; then
    check "runs with command-line arguments (exit 0)" "yes"
  else
    check "runs with command-line arguments (exit 0)" "no"
  fi

  # 2. Stdin mode: `echo "5 7" | io_demo.py` exits 0.
  if stdin_out="$(echo "5 7" | python3 "${script}" 2>/dev/null)"; then
    check "runs with piped stdin (exit 0)" "yes"
  else
    check "runs with piped stdin (exit 0)" "no"
  fi

  # 3. The two input modes must agree.
  if [ "${arg_out}" = "${stdin_out}" ]; then
    check "argument and stdin modes produce identical output" "yes"
  else
    check "argument and stdin modes produce identical output" "no"
  fi

  # 4. Report structure and aligned, two-decimal values.
  echo "${arg_out}" | grep -q '^Input values$' && check "prints 'Input values' header" "yes" || check "prints 'Input values' header" "no"
  echo "${arg_out}" | grep -q '^Results$' && check "prints 'Results' header" "yes" || check "prints 'Results' header" "no"
  echo "${arg_out}" | grep -qE '(^| )12\.00$' && check "sum of 5 and 7 shown as 12.00 (two decimals)" "yes" || check "sum of 5 and 7 shown as 12.00 (two decimals)" "no"
  echo "${arg_out}" | grep -qE '(^| )35\.00$' && check "product shown as 35.00" "yes" || check "product shown as 35.00" "no"
  echo "${arg_out}" | grep -qE '(^| )6\.00$' && check "mean shown as 6.00" "yes" || check "mean shown as 6.00" "no"

  # 5. Bad input -> non-zero exit, a message on STDERR, and nothing on stdout.
  echo "5 hello" | python3 "${script}" 1>"${tmp_out}" 2>"${tmp_err}"
  bad_code=$?
  bad_stderr="$(cat "${tmp_err}")"
  bad_stdout="$(cat "${tmp_out}")"
  rm -f "${tmp_err}" "${tmp_out}"

  [ "${bad_code}" -ne 0 ] && check "bad input exits non-zero" "yes" || check "bad input exits non-zero" "no"
  [ -n "${bad_stderr}" ] && check "bad input writes a message to stderr" "yes" || check "bad input writes a message to stderr" "no"
  [ -z "${bad_stdout}" ] && check "bad input prints nothing to stdout" "yes" || check "bad input prints nothing to stdout" "no"
}

# Structural checks — run against an UNFINISHED starter.
run_structural_checks() {
  local script="$1"
  echo "Testing ${script} (structure only) ..."
  python3 -c 'import sys; compile(open(sys.argv[1]).read(), sys.argv[1], "exec")' "${script}" 2>/dev/null && check "starter is valid Python (parses)" "yes" || check "starter is valid Python (parses)" "no"
  grep -q 'sys.argv' "${script}" && check "starter references sys.argv (reading an argument)" "yes" || check "starter references sys.argv (reading an argument)" "no"
  grep -q 'sys.stdin' "${script}" && check "starter references sys.stdin (reading a pipe)" "yes" || check "starter references sys.stdin (reading a pipe)" "no"
  grep -q 'sys.stderr' "${script}" && check "starter references sys.stderr (error channel)" "yes" || check "starter references sys.stderr (error channel)" "no"
}

# --- python -c sanity checks (the concepts the lab teaches) ---------------
echo "Concept checks (python3 -c) ..."
printf '5\n' | python3 -c 'import sys; assert type(sys.stdin.readline().rstrip("\n")) is str' && check "a line read from input is a str" "yes" || check "a line read from input is a str" "no"
python3 -c 'assert f"{7.5:>10.2f}" == "      7.50"' && check "f-string {7.5:>10.2f} right-aligns to width 10" "yes" || check "f-string {7.5:>10.2f} right-aligns to width 10" "no"
python3 -c 'assert f"{1234567.891:,.2f}" == "1,234,567.89"' && check "f-string thousands separator works" "yes" || check "f-string thousands separator works" "no"
python3 -c 'assert "5" + "7" == "57" and int("5") + int("7") == 12' && check "converting input turns concatenation into addition" "yes" || check "converting input turns concatenation into addition" "no"
echo

run_strict_checks "${lab_dir}/examples/io_demo.py"
echo

# The starter ships with FILL_ME_IN placeholders. Once the learner has replaced
# every one, hold their script to the same strict standard.
if grep -q 'FILL_ME_IN' "${lab_dir}/starter/io_demo.py"; then
  echo "Note: starter/io_demo.py still has unfinished exercises (FILL_ME_IN)."
  run_structural_checks "${lab_dir}/starter/io_demo.py"
else
  run_strict_checks "${lab_dir}/starter/io_demo.py"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
