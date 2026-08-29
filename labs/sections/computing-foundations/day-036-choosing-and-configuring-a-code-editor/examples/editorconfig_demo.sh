#!/usr/bin/env bash
# Day 036 lab — completed reference implementation.
#
# Builds a small sample project with deliberately messy files, writes an
# .editorconfig with the standard formatting rules, then checks every file
# against those rules using grep/awk and reports the violations. This is a
# real, editor-agnostic config check: no editor and no network are needed.
#
# The sample project lives in a temporary directory that is deleted on exit,
# so this script writes nothing permanent to your machine.
set -euo pipefail

# --- 1. Create an isolated sample project (cleaned up on exit) ------------
project_dir="$(mktemp -d "${TMPDIR:-/tmp}/editorconfig-demo.XXXXXX")"
cleanup() {
  echo "Cleaning up temporary project."
  rm -rf "${project_dir}"
}
trap cleanup EXIT

echo "=== EditorConfig demo ==="
echo "Created sample project in: ${project_dir}"

# A clean file: two-space indentation, no trailing whitespace, ends in a newline.
printf 'def greet(name):\n  return "Hi " + name\n' >"${project_dir}/clean.py"

# A file indented with a TAB instead of spaces (breaks indent_style = space).
printf 'def greet(name):\n\treturn "Hi " + name\n' >"${project_dir}/tabs.py"

# A file with trailing whitespace on two lines (breaks trim_trailing_whitespace).
printf 'x = 1  \ny = 2 \n' >"${project_dir}/trailing.py"

# A file with NO final newline (breaks insert_final_newline).
printf 'z = 3' >"${project_dir}/no_newline.py"

# --- 2. Write the .editorconfig the whole team would share ----------------
cat >"${project_dir}/.editorconfig" <<'EOF'
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
charset = utf-8
EOF
echo "Wrote .editorconfig with 6 rules."
echo

# --- 3. Check each file against the rules using grep/awk ------------------
# The three checks below mirror three .editorconfig keys:
#   indent_style = space      -> no leading tabs
#   trim_trailing_whitespace  -> no trailing spaces/tabs
#   insert_final_newline      -> file ends with a newline
check_file() {
  local file="$1" name violations
  name="$(basename "${file}")"
  violations=""

  # indent_style = space: any line that begins with a tab is a violation.
  if awk 'index($0, "\t") == 1 { found = 1 } END { exit !found }' "${file}"; then
    violations="uses tabs (indent_style = space)"
  fi

  # trim_trailing_whitespace: count lines ending in a space or tab.
  local trailing
  trailing="$(awk '/[ \t]+$/ { c++ } END { print c + 0 }' "${file}")"
  if [ "${trailing}" -gt 0 ]; then
    if [ -n "${violations}" ]; then violations="${violations}; "; fi
    violations="${violations}trailing whitespace on ${trailing} line(s)"
  fi

  # insert_final_newline: if the last byte is not a newline, it is missing.
  if [ -n "$(tail -c 1 "${file}")" ]; then
    if [ -n "${violations}" ]; then violations="${violations}; "; fi
    violations="${violations}missing final newline"
  fi

  # Report, padded with dots so the columns line up.
  printf '  %s ' "${name}"
  local pad=$((20 - ${#name}))
  while [ "${pad}" -gt 0 ]; do printf '.'; pad=$((pad - 1)); done
  if [ -z "${violations}" ]; then
    printf ' OK\n'
    return 0
  else
    printf ' VIOLATION: %s\n' "${violations}"
    return 1
  fi
}

echo "Checking files against .editorconfig ..."
violation_count=0
clean_count=0
for file in "${project_dir}/clean.py" "${project_dir}/tabs.py" \
            "${project_dir}/trailing.py" "${project_dir}/no_newline.py"; do
  if check_file "${file}"; then
    clean_count=$((clean_count + 1))
  else
    violation_count=$((violation_count + 1))
  fi
done

echo
echo "${violation_count} file(s) with violations, ${clean_count} clean."
