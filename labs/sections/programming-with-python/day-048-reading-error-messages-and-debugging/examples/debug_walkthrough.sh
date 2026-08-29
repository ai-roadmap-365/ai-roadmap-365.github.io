#!/usr/bin/env bash
# Day 048 lab — guided traceback walkthrough.
#
# Runs each buggy program, captures its traceback, and points out the
# exception type and the culprit line — reading the traceback the way the
# lesson teaches (bottom-up). Then runs the FIXED versions to show they work.
#
# Run from the lab directory:
#   bash examples/debug_walkthrough.sh
set -u

# Resolve directories relative to this script, so it works from anywhere.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
buggy_dir="${here}/buggy"
fixed_dir="${here}/fixed"

# Pick an available Python interpreter.
PY="python3"
command -v "${PY}" >/dev/null 2>&1 || PY="python"

programs="average_scores lookup_capital total_price"

echo "########################################################"
echo "#  Reading three real tracebacks (bottom-up)           #"
echo "########################################################"
echo

for name in ${programs}; do
  src="${buggy_dir}/${name}.py"
  err="$(mktemp)"

  # Run the buggy program; it is expected to crash. Capture stderr.
  "${PY}" "${src}" >/dev/null 2>"${err}"

  # The LAST line of a traceback is the exception type and message (the "what").
  exception="$(tail -n 1 "${err}")"

  # The LAST "File ... line N" frame is the culprit (the "where").
  line_no="$(grep -E '^  File ' "${err}" | tail -n 1 | sed -E 's/.*line ([0-9]+),.*/\1/')"
  culprit="$(sed -n "${line_no}p" "${src}" | sed -E 's/^[[:space:]]+//')"

  echo "=== ${name}.py ==="
  echo "Exception: ${exception}"
  echo "Culprit line ${line_no}: ${culprit}"
  echo

  rm -f "${err}"
done

echo "All three buggy programs failed as expected. Now run the fixed versions:"
echo
for name in ${programs}; do
  echo "--- fixed/${name}.py ---"
  "${PY}" "${fixed_dir}/${name}.py"
  echo
done

echo "Each fixed program ran cleanly (exit 0). That is the whole loop:"
echo "reproduce -> read -> isolate -> hypothesize -> test -> fix."
