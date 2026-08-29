#!/usr/bin/env bash
# Tests for the Day 061 lab — "Refactor for Readability". Run from the lab
# directory:
#   bash tests/run_tests.sh
#
# The central claim of refactoring is: behaviour does not change, only
# readability does. So these tests characterise the behaviour of the score
# summariser with a fixed golden output, then assert that BOTH the messy
# starter and the clean reference produce exactly that output and the same
# exit codes. They pass before you refactor (messy starter) and after you
# refactor (your cleaned-up starter) — that is the whole point.
#
# The suite also checks the reference for the readability markers this lesson
# teaches (type hints, docstrings, small functions, a named constant), and
# once your starter is refactored it holds it to the same standard.
#
# Finally, if a formatter (Black) or linter (Ruff / flake8) happens to be
# installed, it runs them on the reference as a bonus; if they are not
# installed, those checks are SKIPPED, never failed — the lab must run on a
# plain Python install with nothing extra to download.
#
# No network, non-interactive. Exits 0 only if every non-skipped check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref="${lab_dir}/examples/report.py"
starter="${lab_dir}/starter/messy.py"
failures=0
checks=0
skips=0

# The golden behaviour: for the input below, every correct version of the
# tool must print exactly these seven lines and exit 0.
golden_input=(70 85 90 55 60)
golden_output="count: 5
mean: 72.00
median: 70.00
min: 55.00
max: 90.00
stdev: 13.64
passing: 80.0%"

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

skip() {
  echo "  skip: $1 (tool not installed — optional)"
  skips=$((skips + 1))
}

# behaviour_checks <label-prefix> <script>
# Asserts the golden output + exit 0, the empty-input path, and an even-count
# median — the behaviour that refactoring must preserve.
behaviour_checks() {
  local name="$1" script="$2"
  local out code

  out="$(python3 "${script}" "${golden_input[@]}")"
  code=$?
  if [ "${code}" -eq 0 ] && [ "${out}" = "${golden_output}" ]; then
    check "${name}: golden report matches, exit 0" "yes"
  else
    check "${name}: golden report matches, exit 0" "no"
    echo "    (exit ${code}; output was:)"
    printf '%s\n' "${out}" | sed 's/^/      /'
  fi

  out="$(python3 "${script}" 2>&1)"
  code=$?
  if [ "${code}" -eq 1 ] && [ "${out}" = "no data" ]; then
    check "${name}: empty input prints 'no data', exit 1" "yes"
  else
    check "${name}: empty input prints 'no data', exit 1" "no"
    echo "    (exit ${code}; output: ${out})"
  fi

  # Even count: sorted [55,70,85,90] -> median (70+85)/2 = 77.50.
  out="$(python3 "${script}" 70 85 90 55)"
  if printf '%s\n' "${out}" | grep -qF "median: 77.50"; then
    check "${name}: even-count median is 77.50" "yes"
  else
    check "${name}: even-count median is 77.50" "no"
    echo "    (output: ${out})"
  fi
}

# readability_checks <label-prefix> <script>
# The markers this lesson teaches: type hints, docstrings, several small
# functions, and a named constant instead of a bare magic number.
readability_checks() {
  local name="$1" script="$2"
  grep -q -- '->' "${script}" \
    && check "${name}: uses type hints (->)" "yes" \
    || check "${name}: uses type hints (->)" "no"
  grep -q '"""' "${script}" \
    && check "${name}: has docstrings" "yes" \
    || check "${name}: has docstrings" "no"
  local func_count
  func_count="$(grep -c '^def ' "${script}")"
  if [ "${func_count}" -ge 4 ]; then
    check "${name}: decomposed into >= 4 functions (${func_count})" "yes"
  else
    check "${name}: decomposed into >= 4 functions (${func_count})" "no"
  fi
  if grep -qE '^def [a-z]\(' "${script}"; then
    check "${name}: no single-letter function names" "no"
  else
    check "${name}: no single-letter function names" "yes"
  fi
}

echo "Testing the clean reference (examples/report.py) ..."
behaviour_checks "reference" "${ref}"
readability_checks "reference" "${ref}"

echo "Testing the starter (starter/messy.py) ..."
# Behaviour must hold whether or not the learner has refactored yet.
behaviour_checks "starter" "${starter}"
if grep -qE '^def d\(' "${starter}"; then
  echo "Note: starter/messy.py is not refactored yet — checking behaviour only."
  echo "      Refactor it (see starter/refactor-worksheet.md), then rerun to be"
  echo "      held to the readability standard too."
else
  echo "Starter looks refactored — applying the readability standard to it too."
  readability_checks "starter" "${starter}"
fi

# --- Optional formatter / linter (bonus; never a hard failure) ---
echo "Optional style tools (skipped cleanly if not installed) ..."
if command -v black >/dev/null 2>&1; then
  if black --check --quiet "${ref}" 2>/dev/null; then
    check "black --check: reference is already formatted" "yes"
  else
    check "black --check: reference is already formatted" "no"
    echo "    (run 'black ${ref}' to see the suggested formatting)"
  fi
else
  skip "black"
fi

if command -v ruff >/dev/null 2>&1; then
  if ruff check "${ref}" >/dev/null 2>&1; then
    check "ruff check: reference is clean" "yes"
  else
    check "ruff check: reference is clean" "no"
  fi
elif command -v flake8 >/dev/null 2>&1; then
  if flake8 --max-line-length=100 "${ref}" >/dev/null 2>&1; then
    check "flake8: reference is clean" "yes"
  else
    check "flake8: reference is clean" "no"
  fi
else
  skip "ruff / flake8"
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skipped."
[ "${failures}" -eq 0 ]
