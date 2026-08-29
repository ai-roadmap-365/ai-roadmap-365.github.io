#!/usr/bin/env bash
# quality_check.sh — YOUR working file for the Day 37 lab.
#
# This starter already handles the plumbing: it takes a target script, checks
# the file exists, and prints the report headers. Your job is to fill in the
# four numbered exercises below with the exact command named in each comment.
# The completed reference version is examples/quality_check.sh — try the
# exercises yourself first, then compare.
set -u

target="${1:-examples/samples/buggy.sh}"

if [ ! -f "$target" ]; then
  echo "Error: file not found: $target" >&2
  echo "Usage: bash quality_check.sh [path/to/script.sh]" >&2
  exit 2
fi

tab="$(printf '\t')"

echo "=== Quality check: ${target} ==="
echo

# ---- 1. Syntax ------------------------------------------------------------
echo "[1/3] Syntax check (bash -n)..."
# Exercise 1: capture the output of `bash -n "$target" 2>&1` into syntax_err.
# `bash -n` checks syntax WITHOUT running the script; clean scripts print
# nothing. Replace the empty assignment below with the real command.
syntax_err=""   # <-- Exercise 1: syntax_err="$(bash -n "$target" 2>&1)"
if [ -z "$syntax_err" ]; then
  echo "  ok: script is syntactically valid."
else
  echo "  FAIL: syntax error(s):"
  printf '%s\n' "$syntax_err" | sed 's/^/    /'
fi
echo

# ---- 2. Lint --------------------------------------------------------------
echo "[2/3] Lint check (shellcheck)..."
# Exercise 2: detect shellcheck gracefully. Replace the word 'false' below
# with a real test for the command: command -v shellcheck >/dev/null 2>&1
if false; then   # <-- Exercise 2: if command -v shellcheck >/dev/null 2>&1; then
  shellcheck "$target" && echo "  ok: shellcheck found no issues."
else
  echo "  SKIP: shellcheck is not installed (or not detected)."
  echo "        Install it (free) to catch SC2086 (unquoted \$var),"
  echo "        SC2034 (unused variable), and [ ] vs [[ ]] issues."
  echo "        See requirements/README.md for install instructions."
fi
echo

# ---- 3. Formatting --------------------------------------------------------
echo "[3/3] Formatting check (trailing whitespace / tabs)..."
# Exercise 3: find trailing whitespace. Replace the empty assignment with:
#   grep -nE '[[:space:]]+$' "$target" || true
ws_hits=""      # <-- Exercise 3: ws_hits="$(grep -nE '[[:space:]]+$' "$target" || true)"
# Exercise 4: find tab indentation. Replace the empty assignment with:
#   grep -n "$tab" "$target" || true
tab_hits=""     # <-- Exercise 4: tab_hits="$(grep -n "$tab" "$target" || true)"

if [ -n "$ws_hits" ]; then
  echo "  FAIL: lines with trailing whitespace:"
  printf '%s\n' "$ws_hits" | sed 's/^/    /'
else
  echo "  ok: no trailing whitespace (or exercise 3 not yet done)."
fi
if [ -n "$tab_hits" ]; then
  echo "  FAIL: lines containing tab indentation:"
  printf '%s\n' "$tab_hits" | sed 's/^/    /'
else
  echo "  ok: no tab indentation (or exercise 4 not yet done)."
fi
echo

echo "Report complete (this script always exits 0 — it reports, it does not block)."
exit 0
