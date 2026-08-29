#!/usr/bin/env bash
# pipeline.sh — a tiny fail-fast pipeline.
#
# It runs four stages in order: lint, test, build, deploy. Each stage prints a
# line and "passes" — unless you name a stage as the first argument, in which
# case that stage fails, the pipeline stops there, and the later stages never
# run. This demonstrates the core property of a real CI pipeline: fail fast.
#
# Usage:
#   bash pipeline.sh          # every stage passes, exit 0
#   bash pipeline.sh test     # the 'test' stage fails, pipeline stops, exit 1
#
# Runs offline; writes nothing outside its own console output.
set -uo pipefail

fail_stage="${1:-none}"   # the stage to simulate a failure at (default: none)

run_stage() {
  local name="$1"
  echo "==> stage: ${name}"
  if [ "${name}" = "${fail_stage}" ]; then
    echo "    ${name}: FAILED" >&2
    return 1
  fi
  return 0
}

for stage in lint test build deploy; do
  if ! run_stage "${stage}"; then
    echo "Pipeline stopped at '${stage}'. Later stages did not run." >&2
    exit 1
  fi
done

echo "Pipeline succeeded: every stage green."
exit 0
