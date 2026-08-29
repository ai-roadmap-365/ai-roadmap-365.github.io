#!/usr/bin/env bash
# quality_check.sh — a tiny, editor-agnostic quality gate for shell scripts.
#
# Runs three checks on a target script and prints a report:
#   1. Syntax check with `bash -n` (the shell's own built-in check).
#   2. Lint with `shellcheck` IF it is installed; otherwise it reports that
#      clearly and describes what shellcheck would catch (graceful degrade).
#   3. Formatting check with `grep`: trailing whitespace and tab indentation.
#
# It is a REPORT, not a gate: it always exits 0 so it never blocks your work.
# Usage:  bash quality_check.sh [path/to/script.sh]
set -u

target="${1:-examples/samples/buggy.sh}"

if [ ! -f "$target" ]; then
  echo "Error: file not found: $target" >&2
  echo "Usage: bash quality_check.sh [path/to/script.sh]" >&2
  exit 2
fi

tab="$(printf '\t')"
syntax_state="OK"
lint_state="reported"
fmt_state="clean"

echo "=== Quality check: ${target} ==="
echo

# ---- 1. Syntax ------------------------------------------------------------
echo "[1/3] Syntax check (bash -n)..."
syntax_err="$(bash -n "$target" 2>&1)"
if [ -z "$syntax_err" ]; then
  echo "  ok: script is syntactically valid."
else
  echo "  FAIL: syntax error(s):"
  printf '%s\n' "$syntax_err" | sed 's/^/    /'
  syntax_state="errors"
fi
echo

# ---- 2. Lint --------------------------------------------------------------
echo "[2/3] Lint check (shellcheck)..."
if command -v shellcheck >/dev/null 2>&1; then
  if shellcheck "$target"; then
    echo "  ok: shellcheck found no issues."
    lint_state="clean"
  else
    echo "  (shellcheck findings above — each SCxxxx code links to an explanation.)"
    lint_state="findings"
  fi
else
  echo "  SKIP: shellcheck is not installed on this machine."
  echo "        Install it (free) to catch bugs like:"
  echo "        - SC2086: unquoted \$variable may word-split or glob"
  echo "        - SC2034: variable appears unused"
  echo "        - using [ ] where [[ ]] is safer"
  echo "        See requirements/README.md for install instructions."
  lint_state="skipped (shellcheck absent)"
fi
echo

# ---- 3. Formatting --------------------------------------------------------
echo "[3/3] Formatting check (trailing whitespace / tabs)..."
ws_hits="$(grep -nE '[[:space:]]+$' "$target" || true)"
tab_hits="$(grep -n "$tab" "$target" || true)"

if [ -n "$ws_hits" ]; then
  count="$(printf '%s\n' "$ws_hits" | grep -c .)"
  echo "  FAIL: found ${count} line(s) with trailing whitespace."
  printf '%s\n' "$ws_hits" | sed 's/^/    /'
  fmt_state="issues found"
else
  echo "  ok: no trailing whitespace."
fi

if [ -n "$tab_hits" ]; then
  count="$(printf '%s\n' "$tab_hits" | grep -c .)"
  echo "  FAIL: found ${count} line(s) containing tab indentation."
  printf '%s\n' "$tab_hits" | sed 's/^/    /'
  fmt_state="issues found"
else
  echo "  ok: no tab indentation."
fi
echo

echo "Summary: syntax ${syntax_state}; lint ${lint_state}; formatting ${fmt_state}."
exit 0
