#!/usr/bin/env bash
# Day 036 lab — YOUR working file.
#
# Complete the four numbered exercises below. Each one names the exact lines
# to write. The completed reference version is in
# examples/editorconfig_demo.sh — run that first to see the goal, then do
# these yourself. When you are finished, run:  bash tests/run_tests.sh
#
# The sample project is built in a temporary directory and deleted on exit,
# so nothing permanent is written to your machine.
set -euo pipefail

project_dir="$(mktemp -d "${TMPDIR:-/tmp}/editorconfig-starter.XXXXXX")"
cleanup() { rm -rf "${project_dir}"; }
trap cleanup EXIT

echo "=== EditorConfig starter ==="
echo "Sample project: ${project_dir}"

# A clean file (correct already) and three messy ones to check against rules.
printf 'def greet(name):\n  return "Hi " + name\n' >"${project_dir}/clean.py"
printf 'def greet(name):\n\treturn "Hi " + name\n'  >"${project_dir}/tabs.py"
printf 'x = 1  \ny = 2 \n'                          >"${project_dir}/trailing.py"
printf 'z = 3'                                      >"${project_dir}/no_newline.py"

# A reusable checker (already written for you) — it reports whether a file
# obeys indent_style = space, trim_trailing_whitespace, and insert_final_newline.
check_file() {
  local file="$1" name violations trailing pad
  name="$(basename "${file}")"
  violations=""
  if awk 'index($0, "\t") == 1 { found = 1 } END { exit !found }' "${file}"; then
    violations="uses tabs (indent_style = space)"
  fi
  trailing="$(awk '/[ \t]+$/ { c++ } END { print c + 0 }' "${file}")"
  if [ "${trailing}" -gt 0 ]; then
    [ -n "${violations}" ] && violations="${violations}; "
    violations="${violations}trailing whitespace on ${trailing} line(s)"
  fi
  if [ -n "$(tail -c 1 "${file}")" ]; then
    [ -n "${violations}" ] && violations="${violations}; "
    violations="${violations}missing final newline"
  fi
  printf '  %s ' "${name}"
  pad=$((20 - ${#name})); while [ "${pad}" -gt 0 ]; do printf '.'; pad=$((pad - 1)); done
  if [ -z "${violations}" ]; then printf ' OK\n'; return 0
  else printf ' VIOLATION: %s\n' "${violations}"; return 1; fi
}

# ---------------------------------------------------------------------------
# Exercise 1: WRITE AN .editorconfig RULE.
# Inside the [*] section below, replace the single placeholder line with the
# six standard rules, one per line:
#   indent_style = space
#   indent_size = 2
#   end_of_line = lf
#   insert_final_newline = true
#   trim_trailing_whitespace = true
#   charset = utf-8
cat >"${project_dir}/.editorconfig" <<'EOF'
root = true

[*]
FILL-IN-EX1
EOF
echo "Wrote .editorconfig."
echo

# ---------------------------------------------------------------------------
# Exercise 2: CHECK A FILE against the rules.
# Replace the placeholder below so it calls the checker on the trailing file:
#   check_file "${project_dir}/trailing.py"
echo "Checking trailing.py before the fix:"
FILL-IN-EX2 || true
echo

# ---------------------------------------------------------------------------
# Exercise 3: FIX A VIOLATION.
# Rewrite trailing.py without the trailing spaces. Replace the placeholder
# below with:
#   printf 'x = 1\ny = 2\n' >"${project_dir}/trailing.py"
FILL-IN-EX3
echo "Fixed trailing.py."
echo

# ---------------------------------------------------------------------------
# Exercise 4: VERIFY the fix.
# Check trailing.py again — it should now report OK. Replace the placeholder
# below with:
#   check_file "${project_dir}/trailing.py"
echo "Checking trailing.py after the fix:"
FILL-IN-EX4
echo
echo "Done. Compare your run with examples/editorconfig_demo.sh."
