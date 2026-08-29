#!/usr/bin/env bash
# Tests for the Day 063 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The point of this suite is to show what a well-designed program buys you:
# because the logic lives in a PURE core (summary_core.py) with no I/O, the
# core is tested with plain function calls — no fake files, no captured
# output. The thin imperative shell (summary.py) is then checked end to end
# through stdin, a file, and error cases. Finally the learner's starter is
# checked: structurally while exercises are unfinished, and to the same
# strict standard once they are complete. No network, non-interactive.
# Exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

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

# check_core <label> <core_dir> <python-body>
# Runs a small assertion body against summary_core imported from core_dir.
# A clean exit (all asserts pass) is a pass.
check_core() {
  local label="$1" core_dir="$2" body="$3"
  if PYTHONPATH="${core_dir}" python3 -c "import summary_core as c
${body}" 2>/dev/null; then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
}

# check_shell <label> <shell_script> <expect_exit> <needle> <stdin-text> [file-arg]
check_shell() {
  local label="$1" script="$2" expect_exit="$3" needle="$4" stdin_text="$5" file_arg="${6:-}"
  local out code
  if [ -n "${file_arg}" ]; then
    out="$(python3 "${script}" "${file_arg}" 2>&1)"
  else
    out="$(printf '%s' "${stdin_text}" | python3 "${script}" 2>&1)"
  fi
  code=$?
  if [ "${code}" -eq "${expect_exit}" ] && printf '%s' "${out}" | grep -qF "${needle}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (exit ${code}, expected ${expect_exit}; output: ${out})"
  fi
}

run_core_checks() {
  local core_dir="$1"
  echo "Testing the pure core in ${core_dir} (plain function calls, no I/O) ..."
  check_core "parse_numbers reads mixed separators" "${core_dir}" \
    "assert c.parse_numbers('1, 2\n3\t4') == [1.0, 2.0, 3.0, 4.0]"
  check_core "parse_numbers of blank text is []" "${core_dir}" \
    "assert c.parse_numbers('   ') == []"
  check_core "parse_numbers rejects a non-number" "${core_dir}" \
    "import summary_core
try:
    c.parse_numbers('1 two 3'); raise SystemExit(1)
except ValueError as e:
    assert 'two' in str(e)"
  check_core "summarize computes the six statistics" "${core_dir}" \
    "s = c.summarize([2, 4, 6, 8])
assert s['count'] == 4 and s['total'] == 20 and s['mean'] == 5.0
assert s['minimum'] == 2 and s['maximum'] == 8 and s['above_mean'] == 2"
  check_core "summarize rejects an empty list" "${core_dir}" \
    "try:
    c.summarize([]); raise SystemExit(1)
except ValueError:
    pass"
  check_core "format_summary returns aligned text" "${core_dir}" \
    "text = c.format_summary(c.summarize([10, 20, 30]))
assert 'count      3' in text
assert 'mean       20.00' in text
assert 'above mean 1' in text"
}

run_shell_checks() {
  local script="$1" core_dir="$2"
  echo "Testing the shell ${script} end to end ..."
  # The shell imports summary_core from its own directory; make sure the
  # matching core is the one next to it by running with that dir on the path.
  local tmpfile
  check_shell "stdin: three numbers summarized" "${script}" 0 "mean       20.00" "10 20 30"
  check_shell "stdin: bad token -> error, exit 1" "${script}" 1 "is not a number" "1 two 3"
  check_shell "stdin: empty input -> error, exit 1" "${script}" 1 "cannot summarize an empty list" ""
  tmpfile="$(mktemp -t summary-test.XXXXXX)"
  printf '5, 7, 9, 11\n' > "${tmpfile}"
  check_shell "file input summarized" "${script}" 0 "count      4" "" "${tmpfile}"
  rm -f "${tmpfile}"
  check_shell "missing file -> error, exit 1" "${script}" 1 "error:" "" "${lab_dir}/no-such-file.txt"
}

# --- Reference: always tested strictly ---
run_core_checks "${lab_dir}/examples"
run_shell_checks "${lab_dir}/examples/summary.py" "${lab_dir}/examples"

# --- Learner starter ---
echo "Testing starter/summary_core.py ..."
starter_core="${lab_dir}/starter/summary_core.py"
if python3 -c "compile(open('${starter_core}').read(), '${starter_core}', 'exec')" 2>/dev/null; then
  check "starter core is valid Python" "yes"
else
  check "starter core is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter_core}"; then
  echo "Note: starter/summary_core.py still has unfinished exercises — testing structure only."
  grep -q 'def parse_numbers' "${starter_core}" && check "starter defines parse_numbers" "yes" || check "starter defines parse_numbers" "no"
  grep -q 'def summarize' "${starter_core}" && check "starter defines summarize" "yes" || check "starter defines summarize" "no"
  grep -q 'def format_summary' "${starter_core}" && check "starter defines format_summary" "yes" || check "starter defines format_summary" "no"
else
  run_core_checks "${lab_dir}/starter"
  run_shell_checks "${lab_dir}/starter/summary.py" "${lab_dir}/starter"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
