#!/usr/bin/env bash
# check.sh — the whole quality gate, as one command.
#
#   bash check.sh              run every stage, report all failures
#   bash check.sh --fail-fast  stop at the first failing stage
#
# Exit code 0 means "this change is safe to merge". Any other exit code means
# it is not, and the output above says which stage disagreed.
#
# The stages run cheapest-first, so the feedback you get soonest is the
# feedback that costs least to produce:
#
#   1. format   — is the code laid out the agreed way?      (milliseconds)
#   2. lint     — any dead imports, bugs, unsorted imports?  (milliseconds)
#   3. types    — do the annotations actually hold?          (~a second)
#   4. tests    — does it still do what it claims?           (~a second here)
#   5. coverage — did any code sneak in unexecuted?          (instant, reuses 4)
#
# This script is deliberately plain bash. It needs no plugin system, no YAML,
# and no network, and it runs identically on your laptop and on a build server.

set -u

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${project_dir}" || exit 1

fail_fast="no"
if [ "${1:-}" = "--fail-fast" ]; then
  fail_fast="yes"
fi

# --- Tool resolution --------------------------------------------------------
# Resolve each tool: an explicit override first, then this project's .venv,
# then whatever is on PATH. Fails loudly with instructions rather than
# skipping a stage silently — a gate that quietly does nothing is worse than
# no gate at all, because people trust it.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${project_dir}/.venv/bin/${tool}" ]; then echo "${project_dir}/.venv/bin/${tool}"; return 0; fi
  if [ -x "${project_dir}/../.venv/bin/${tool}" ]; then echo "${project_dir}/../.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

require_tool() {
  local tool="$1" override="$2" path
  if ! path="$(resolve_tool "${tool}" "${override}")"; then
    echo "FAIL: ${tool} not found." >&2
    echo "  Install the gate's tools with:" >&2
    echo "    python3 -m venv .venv" >&2
    echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
    echo "  Or point this script at existing ones, e.g. RUFF=/path/to/ruff bash check.sh" >&2
    exit 1
  fi
  echo "${path}"
}

ruff_bin="$(require_tool ruff "${RUFF:-}")" || exit 1
mypy_bin="$(require_tool mypy "${MYPY:-}")" || exit 1
coverage_bin="$(require_tool coverage "${COVERAGE:-}")" || exit 1

# --- Stage runner -----------------------------------------------------------
failed_stages=""
stage_count=0

run_stage() {
  local name="$1"
  shift
  stage_count=$((stage_count + 1))
  printf '=== %s ===\n' "${name}"
  if "$@"; then
    printf 'PASS: %s\n\n' "${name}"
  else
    printf 'FAIL: %s\n\n' "${name}"
    failed_stages="${failed_stages} ${name}"
    if [ "${fail_fast}" = "yes" ]; then
      printf 'stopping at first failure (--fail-fast)\n'
      printf 'gate FAILED: %s\n' "${name}"
      exit 1
    fi
  fi
}

# 1. Formatting. --check reports rather than rewrites, which is what a gate
#    wants: it must never modify the thing it is judging.
run_stage "format" "${ruff_bin}" format --check .

# 2. Linting. Same tool, different job: rules about correctness and style
#    that a formatter cannot express.
run_stage "lint" "${ruff_bin}" check .

# 3. Types. Reads the annotations Day 69 taught you to write and proves the
#    claims they make, which Python itself never checks at runtime.
run_stage "types" "${mypy_bin}"

# 4. Tests, run under coverage measurement so stage 5 costs nothing extra.
run_stage "tests" "${coverage_bin}" run -m pytest

# 5. Coverage floor. `report` exits non-zero when total coverage is below
#    fail_under in pyproject.toml.
run_stage "coverage" "${coverage_bin}" report

# --- Verdict ----------------------------------------------------------------
if [ -n "${failed_stages}" ]; then
  printf '=== gate FAILED ===\n'
  printf 'failing stages:%s\n' "${failed_stages}"
  exit 1
fi

printf '=== gate PASSED ===\n'
printf 'all %d stages green — this change is safe to merge\n' "${stage_count}"
exit 0
