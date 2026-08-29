#!/usr/bin/env bash
# Tests for the Day 073 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Three things are being checked here, and the third is the point of the day:
#
#   1. the finished suite passes (pytest exits 0);
#   2. the suite has teeth — a reference implementation broken by one `sed`
#      substitution in a throwaway copy makes pytest exit non-zero;
#   3. the RECORDED HISTORY in examples/cycles/ is genuine — every RED capture
#      really reports a failure, every GREEN capture really reports a pass, and
#      each cycle's pass count is exactly what a real red-green sequence would
#      have produced at that point. A suite written after the fact cannot
#      produce a consistent chain of those counts.
#
# No network, non-interactive, deterministic. Exits 0 only if every check
# passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cycles_dir="${lab_dir}/examples/cycles"
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
  # run_pytest <dir> — run every test in one directory, quietly. Prints
  # pytest's output; the caller reads the exit code.
  local dir="$1"
  (cd "${dir}" && "${pytest_bin}" -p no:cacheprovider -q . 2>&1)
}

echo "Using pytest: $("${pytest_bin}" --version 2>&1 | head -1)"

# --- 1. The finished suite passes ------------------------------------------
echo "Testing the reference suite ..."

out="$(run_pytest "${lab_dir}/examples")"
code=$?
if [ "${code}" -eq 0 ] && printf '%s' "${out}" | grep -qE '9 passed'; then
  check "examples/test_bowling.py: 9 tests, all passing" "yes"
else
  check "examples/test_bowling.py: 9 tests, all passing" "no"
  echo "    (exit ${code}; output: ${out})"
fi

collected="$(cd "${lab_dir}/examples" && "${pytest_bin}" -p no:cacheprovider --collect-only -q . 2>/dev/null)"
for name in test_a_gutter_game_scores_zero \
  test_a_strike_adds_the_next_two_rolls \
  test_a_spare_adds_the_next_roll \
  test_a_roll_outside_zero_to_ten_is_refused \
  test_a_game_with_the_wrong_number_of_rolls_is_refused \
  test_a_perfect_game_scores_three_hundred; do
  if printf '%s' "${collected}" | grep -qF "${name}"; then
    check "the suite collects ${name}" "yes"
  else
    check "the suite collects ${name}" "no"
  fi
done

# --- 2. The suite has teeth -------------------------------------------------
# A test suite that cannot fail is not a test suite. Break the reference
# implementation one substitution at a time, in a throwaway copy, and insist
# that pytest notices.
echo "Testing that the suite fails on a broken implementation ..."

mutate() {
  local label="$1" expression="$2" work_dir out code
  work_dir="$(mktemp -d "${TMPDIR:-/tmp}/bowling-mutant.XXXXXX")"
  cp "${lab_dir}/examples/test_bowling.py" "${work_dir}/test_bowling.py"
  sed "${expression}" "${lab_dir}/examples/bowling.py" > "${work_dir}/bowling.py"
  if cmp -s "${lab_dir}/examples/bowling.py" "${work_dir}/bowling.py"; then
    check "${label}" "no"
    echo "    (the sed expression changed nothing — the reference no longer has that line)"
    rm -rf "${work_dir}"
    return
  fi
  out="$(cd "${work_dir}" && "${pytest_bin}" -p no:cacheprovider -q . 2>&1)"
  code=$?
  if [ "${code}" -ne 0 ] && printf '%s' "${out}" | grep -qE '[0-9]+ failed'; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (a broken implementation still passed; exit ${code})"
  fi
  rm -rf "${work_dir}"
}

mutate "an off-by-one in the total is caught" 's/^    return total$/    return total + 1/'
mutate "removing the frame-size refusal is caught" 's/if pins > 10:/if pins > 99:/'
mutate "removing the per-roll refusal is caught" 's/if pins < 0 or pins > 10:/if False:/'
mutate "treating every strike as an open frame is caught" 's/if _is_strike(rolls, roll):/if False:/'

# --- 3. The recorded history is genuine -------------------------------------
# This is the check that belongs to this day and no other. For each cycle:
#
#   * the RED capture must report exactly one failing test, and (from cycle 2
#     on) exactly the number of already-passing tests the earlier cycles left
#     behind;
#   * the GREEN capture must report that same number plus one passing, with no
#     failures at all.
#
# Those counts chain: cycle 5's red can only say "4 passed" if cycles 1-4 were
# really written first and really ended green. A history assembled after the
# code was finished does not produce that chain by accident.
echo "Testing that examples/cycles/ is a genuine red-green record ..."

summary_line() {
  grep -E '^=+ .*(passed|failed|error).* =+$' "$1" | tail -1
}

check_red() {
  local n="$1" file="${cycles_dir}/cycle-$1-red.txt" line already
  already=$((n - 1))
  if [ ! -f "${file}" ]; then
    check "cycle ${n} RED capture exists" "no"
    return
  fi
  line="$(summary_line "${file}")"
  if ! printf '%s' "${line}" | grep -qE '(^| )1 failed(,| )'; then
    check "cycle ${n} RED really failed" "no"
    echo "    (summary line was: ${line})"
    return
  fi
  if [ "${already}" -gt 0 ] && ! printf '%s' "${line}" | grep -qE "(^| )${already} passed"; then
    check "cycle ${n} RED shows the ${already} earlier cycles still green" "no"
    echo "    (summary line was: ${line})"
    return
  fi
  check "cycle ${n} RED: 1 failed, ${already} passed" "yes"
}

check_green() {
  local n="$1" label="${2:-green}" expected="$3" file line
  file="${cycles_dir}/cycle-$1-${label}.txt"
  if [ ! -f "${file}" ]; then
    check "cycle ${n} ${label} capture exists" "no"
    return
  fi
  line="$(summary_line "${file}")"
  if printf '%s' "${line}" | grep -qE '(failed|error)'; then
    check "cycle ${n} ${label} really passed" "no"
    echo "    (summary line was: ${line})"
    return
  fi
  if ! printf '%s' "${line}" | grep -qE "(^| )${expected} passed"; then
    check "cycle ${n} ${label} shows ${expected} passing" "no"
    echo "    (summary line was: ${line})"
    return
  fi
  check "cycle ${n} ${label}: ${expected} passed, 0 failed" "yes"
}

for n in 1 2 3 4 5 6 7; do
  check_red "${n}"
  check_green "${n}" green "${n}"
done

# The refactor after cycle 4 must leave the count untouched — that is what
# makes it a refactor rather than an edit.
check_green 4 refactor 4

# Cycle 8 is the day's punchline: two tests that passed on the first run, and
# then the same two tests failing against a deliberately broken copy. Without
# the second file the first proves nothing.
check_green 8 passed-immediately 9

mutant_line="$(summary_line "${cycles_dir}/cycle-8-mutant.txt" 2>/dev/null)"
if printf '%s' "${mutant_line}" | grep -qE '[0-9]+ failed' \
  && grep -qF 'test_a_perfect_game_scores_three_hundred' "${cycles_dir}/cycle-8-mutant.txt" \
  && grep -qF 'test_a_real_game_scores_133' "${cycles_dir}/cycle-8-mutant.txt"; then
  check "cycle 8 mutant: both tests that passed immediately were shown to fail" "yes"
else
  check "cycle 8 mutant: both tests that passed immediately were shown to fail" "no"
  echo "    (summary line was: ${mutant_line})"
fi

# A capture nobody can read is a capture nobody checked. Every recorded run
# must name the pytest that produced it, so the record is attributable.
bad_version=0
for file in "${cycles_dir}"/cycle-*.txt; do
  grep -qF 'pytest-9.1.1' "${file}" || bad_version=$((bad_version + 1))
done
if [ "${bad_version}" -eq 0 ]; then
  check "every capture records the pytest version that produced it" "yes"
else
  check "every capture records the pytest version that produced it" "no"
  echo "    (${bad_version} capture(s) without a version banner)"
fi

# --- 4. The starter ---------------------------------------------------------
echo "Testing starter/ ..."

for f in "${lab_dir}/starter/bowling.py" "${lab_dir}/starter/test_bowling.py"; do
  if python3 -c "import sys; compile(open(sys.argv[1]).read(), sys.argv[1], 'exec')" "${f}" 2>/dev/null; then
    check "$(basename "${f}") is valid Python" "yes"
  else
    check "$(basename "${f}") is valid Python" "no"
  fi
done

for heading in 'Cycle 1' 'Cycle 2' 'Cycle 3' 'Cycle 4' 'Cycle 5' 'Cycle 6' 'Cycle 7' 'Cycle 8'; do
  if grep -qF "## ${heading}" "${lab_dir}/starter/cycles.md"; then
    check "cycles.md dictates ${heading}" "yes"
  else
    check "cycles.md dictates ${heading}" "no"
  fi
done

if grep -qE '^def score' "${lab_dir}/starter/bowling.py"; then
  # The learner has done the work. Hold their implementation to exactly the
  # same standard as the reference: run THEIR module against the reference
  # suite, so a weaker set of tests cannot let a weaker implementation past.
  echo "starter/bowling.py defines score() — grading it against the reference suite ..."
  work_dir="$(mktemp -d "${TMPDIR:-/tmp}/bowling-starter.XXXXXX")"
  cp "${lab_dir}/starter/bowling.py" "${work_dir}/bowling.py"
  cp "${lab_dir}/examples/test_bowling.py" "${work_dir}/test_bowling.py"
  out="$(cd "${work_dir}" && "${pytest_bin}" -p no:cacheprovider -q . 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ]; then
    check "starter/bowling.py passes the reference suite" "yes"
  else
    check "starter/bowling.py passes the reference suite" "no"
    echo "    (exit ${code}; output: ${out})"
  fi
  rm -rf "${work_dir}"

  own="$(cd "${lab_dir}/starter" && "${pytest_bin}" -p no:cacheprovider -q . 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ] && printf '%s' "${own}" | grep -qE '[0-9]+ passed'; then
    check "your own suite in starter/ passes" "yes"
  else
    check "your own suite in starter/ passes" "no"
    echo "    (exit ${code}; output: ${own})"
  fi
else
  echo "Note: starter/bowling.py is still empty — the kata has not been started."
  if [ ! -s "${lab_dir}/starter/bowling.py" ] || ! grep -qE '^(def|class) ' "${lab_dir}/starter/bowling.py"; then
    check "starter/bowling.py is the empty module the kata begins from" "yes"
  else
    check "starter/bowling.py is the empty module the kata begins from" "no"
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
