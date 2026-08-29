#!/usr/bin/env bash
# Tests for the Day 013 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the detector runs, produces a well-formed report that either
# lists at least one manager or states clearly that none were detected, and
# exits 0. It ALSO statically checks that the scripts contain no install,
# remove, upgrade, or sudo commands — this lab is strictly read-only.
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

run_report_checks() {
  local script="$1" output rc
  echo "Testing ${script} ..."
  output="$(bash "${script}" 2>&1)"
  rc=$?
  [ "${rc}" -eq 0 ] && check "script exits 0" "yes" || check "script exits 0" "no"
  echo "${output}" | grep -q '^=== Package Manager Report ===$' \
    && check "prints report header" "yes" || check "prints report header" "no"
  echo "${output}" | grep -q '^=== End of report ===$' \
    && check "prints report footer" "yes" || check "prints report footer" "no"
  echo "${output}" | grep -q '^Operating system kernel: ' \
    && check "prints OS kernel line" "yes" || check "prints OS kernel line" "no"
  # Either at least one manager was found, or a clear "none detected" message.
  if echo "${output}" | grep -q '^FOUND: ' \
    || echo "${output}" | grep -q 'No package managers detected'; then
    check "reports a manager OR a clear 'none detected' message" "yes"
  else
    check "reports a manager OR a clear 'none detected' message" "no"
  fi
}

# Static safety check: no mutating or privileged commands anywhere in the lab
# scripts. This lab must never install, remove, upgrade, or use sudo.
check_read_only() {
  local script="$1"
  echo "Safety-scanning ${script} ..."
  # Strip comment lines, then look for dangerous verbs as commands.
  local body
  body="$(grep -v '^[[:space:]]*#' "${script}")"
  if echo "${body}" | grep -Eq '\b(sudo)\b'; then
    check "no sudo in ${script##*/}" "no"
  else
    check "no sudo in ${script##*/}" "yes"
  fi
  if echo "${body}" | grep -Eq '(brew|apt|apt-get|winget|pip|pip3|npm)[[:space:]]+(install|remove|uninstall|upgrade|update)\b'; then
    check "no install/remove/upgrade in ${script##*/}" "no"
  else
    check "no install/remove/upgrade in ${script##*/}" "yes"
  fi
}

run_report_checks "${lab_dir}/examples/detect_pkg_manager.sh"
run_report_checks "${lab_dir}/starter/detect_pkg_manager.sh"
check_read_only "${lab_dir}/examples/detect_pkg_manager.sh"
check_read_only "${lab_dir}/starter/detect_pkg_manager.sh"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
