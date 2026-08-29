#!/usr/bin/env bash
# Tests for the Day 036 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the reference demo writes an .editorconfig with the required
# keys and that its checker detects the known trailing-whitespace and
# missing-final-newline violations (and the tab and clean cases too). If the
# learner has finished the starter, it is held to the same standard.
# No network, no privileges, writes nothing outside temp dirs.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
example="${lab_dir}/examples/editorconfig_demo.sh"
starter="${lab_dir}/starter/editorconfig_demo.sh"
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

# --- The .editorconfig the demo writes must contain the required keys -----
echo "Checking the demo defines all required .editorconfig keys ..."
for key in indent_style indent_size end_of_line insert_final_newline \
           trim_trailing_whitespace charset; do
  if grep -q "^${key} = " "${example}"; then
    check "demo writes '${key}' rule" "yes"
  else
    check "demo writes '${key}' rule" "no"
  fi
done

# --- The checker must detect the known violations -------------------------
run_checker_checks() {
  local script="$1" output
  echo "Running ${script##*/} and inspecting its report ..."
  if ! output="$(bash "${script}" 2>&1)"; then
    check "${script##*/} exits successfully" "no"
    echo "${output}" | sed 's/^/    /'
    return
  fi
  check "${script##*/} exits successfully" "yes"
  echo "${output}" | grep -Eq 'Wrote .editorconfig' \
    && check "reports the .editorconfig was written" "yes" \
    || check "reports the .editorconfig was written" "no"
  echo "${output}" | grep -Eq 'trailing\.py .*VIOLATION: trailing whitespace on 2 line' \
    && check "detects the trailing-whitespace violation" "yes" \
    || check "detects the trailing-whitespace violation" "no"
  echo "${output}" | grep -Eq 'no_newline\.py .*VIOLATION: missing final newline' \
    && check "detects the missing-final-newline violation" "yes" \
    || check "detects the missing-final-newline violation" "no"
  echo "${output}" | grep -Eq 'tabs\.py .*VIOLATION: uses tabs' \
    && check "detects the tab-indentation violation" "yes" \
    || check "detects the tab-indentation violation" "no"
  echo "${output}" | grep -Eq 'clean\.py .*OK' \
    && check "passes the clean file" "yes" \
    || check "passes the clean file" "no"
}

run_checker_checks "${example}"

# The starter ships with FILL-IN placeholders; once the learner has replaced
# them all, run and inspect their version too.
if grep -q 'FILL-IN' "${starter}"; then
  echo "Note: starter still has FILL-IN exercises — skipping its run (structure only)."
else
  echo "Running the completed starter and inspecting its report ..."
  if out="$(bash "${starter}" 2>&1)"; then
    check "completed starter exits successfully" "yes"
    echo "${out}" | grep -Eq 'trailing\.py .*OK' \
      && check "starter's fix makes trailing.py clean" "yes" \
      || check "starter's fix makes trailing.py clean" "no"
  else
    check "completed starter exits successfully" "no"
    echo "${out}" | sed 's/^/    /'
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
