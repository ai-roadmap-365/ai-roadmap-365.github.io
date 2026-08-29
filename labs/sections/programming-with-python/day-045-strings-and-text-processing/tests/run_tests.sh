#!/usr/bin/env bash
# Tests for the Day 045 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Runs the completed reference program on the committed sample and checks the
# exact counts and formatted lines it must produce, then confirms a couple of
# slicing/method facts directly with python3. No network is used.
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

grep_check() {
  local label="$1" pattern="$2" text="$3"
  if printf '%s\n' "${text}" | grep -Eq "${pattern}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
}

echo "Running examples/text_report.py ..."
if ! output="$(python3 "${lab_dir}/examples/text_report.py" 2>&1)"; then
  check "reference program exits successfully" "no"
  printf '%s\n' "${output}" | sed 's/^/    /'
else
  check "reference program exits successfully" "yes"
  grep_check "title-cased heading present"      '^ *The River And The Reader *$'                 "${output}"
  grep_check "Lines count is 9"                  '^Lines +9$'                                     "${output}"
  grep_check "Words count is 105"               '^Words +105$'                                    "${output}"
  grep_check "Characters count is 556"          '^Characters +556$'                               "${output}"
  grep_check "Unique words count is 66"         '^Unique words +66$'                              "${output}"
  grep_check "most common word is river (11)"   'Most common word:  "river" \(11 times, 10\.5% of words\)' "${output}"
fi

echo "Checking slicing and string-method facts with python3 ..."
if python3 - <<'PY'
# Slicing: negative index, reverse, and a range slice.
h = "The River And The Reader"
assert h[0] == "T", "s[0] should be the first character"
assert h[-1] == "r", "s[-1] should be the last character"
assert h[4:9] == "River", "s[4:9] should slice out 'River'"
assert h[::-1] == "redaeR ehT dnA reviR ehT", "s[::-1] should reverse the string"
# Methods produce NEW strings; the original is unchanged (immutability).
assert "River,".strip(".,") == "River"
assert "  hi  ".strip() == "hi"
assert "a,b,c".split(",") == ["a", "b", "c"]
assert "-".join(["a", "b", "c"]) == "a-b-c"
assert "Hello".lower() == "hello" and "Hello".upper() == "HELLO"
assert "banana".count("a") == 3
assert f"{3.14159:.2f}" == "3.14"
assert f"{42:>5}" == "   42"
PY
then
  check "slicing/method assertions all hold" "yes"
else
  check "slicing/method assertions all hold" "no"
fi

echo "Checking the starter is present and runnable ..."
if python3 "${lab_dir}/starter/text_report.py" >/dev/null 2>&1; then
  check "starter program runs without crashing" "yes"
else
  check "starter program runs without crashing" "no"
fi
if grep -q 'text = None' "${lab_dir}/starter/text_report.py"; then
  echo "Note: starter/text_report.py still has unfinished exercises (that is expected before you complete them)."
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
