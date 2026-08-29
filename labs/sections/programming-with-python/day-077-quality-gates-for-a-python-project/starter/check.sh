#!/usr/bin/env bash
# check.sh — YOUR quality gate. Right now it is a gate with no stages, which
# means it is a command that always says yes. Your job is to give it teeth.
#
# Build it one stage at a time, in cost order, running it after every stage so
# you watch it grow. The tool resolution and the stage runner are written for
# you; the stages are exercises 1 to 5.
#
#   bash check.sh              run every stage, report all failures
#   bash check.sh --fail-fast  stop at the first failing stage
#
# Exit 0 means "safe to merge". Anything else means it is not.

set -u

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${project_dir}" || exit 1

fail_fast="no"
if [ "${1:-}" = "--fail-fast" ]; then
  fail_fast="yes"
fi

# --- Tool resolution (provided) --------------------------------------------
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

# --- Stage runner (provided) ------------------------------------------------
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

# ---------------------------------------------------------------------------
# EXERCISE 1 — the format stage (cheapest, so it goes first).
#
# Add, on the line below this comment block:
#     run_stage "format" "${ruff_bin}" format --check .
#
# Then add the matching config to pyproject.toml (exercise 1b there) and run
# `bash check.sh`. Ruff will tell you some files are not formatted; fix them
# with `ruff format .` and run the gate again. Note what --check buys you: the
# gate REPORTS, it never rewrites the code it is judging.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# EXERCISE 2 — the lint stage.
#
# Add:
#     run_stage "lint" "${ruff_bin}" check .
#
# Then fill in [tool.ruff.lint] in pyproject.toml (exercise 2b) with
# select = ["E", "W", "F", "I", "UP", "B"] and run the gate again. To watch
# this stage do its job, add `import os` to the top of pricekit/money.py, run
# the gate, read the F401 message, and remove the import.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# EXERCISE 3 — the type stage.
#
# Add:
#     run_stage "types" "${mypy_bin}"
#
# mypy reads [tool.mypy] from pyproject.toml, so it needs no arguments here.
# Fill in that table (exercise 3b) with files = ["pricekit"] and strict = true.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# EXERCISE 4 — the test stage, run UNDER coverage measurement.
#
# Add:
#     run_stage "tests" "${coverage_bin}" run -m pytest
#
# Running pytest through `coverage run` costs almost nothing and means
# exercise 5 needs no second test run. Fill in [tool.pytest.ini_options] and
# [tool.coverage.run] in pyproject.toml (exercise 4b).
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# EXERCISE 5 — the coverage floor.
#
# Add:
#     run_stage "coverage" "${coverage_bin}" report
#
# Fill in [tool.coverage.report] (exercise 5b) with show_missing = true and
# fail_under = 95, then run the gate. It will FAIL, and it should: this starter
# ships tests for pricekit/money.py and none for pricekit/receipt.py. Read the
# Missing column, write the tests it points at in tests/test_receipt.py, and
# run the gate until it goes green. That loop — report, read, cover, re-run —
# is the only honest way to use a coverage number.
# ---------------------------------------------------------------------------


# --- Verdict (provided) -----------------------------------------------------
if [ -n "${failed_stages}" ]; then
  printf '=== gate FAILED ===\n'
  printf 'failing stages:%s\n' "${failed_stages}"
  exit 1
fi

if [ "${stage_count}" -eq 0 ]; then
  printf '=== gate PASSED (with no stages) ===\n'
  printf 'A gate with nothing in it always says yes. Start with exercise 1.\n'
  exit 0
fi

printf '=== gate PASSED ===\n'
printf 'all %d stages green — this change is safe to merge\n' "${stage_count}"
exit 0
