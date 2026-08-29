#!/usr/bin/env bash
# Tests for the Day 37 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies the quality-check pipeline behaves correctly:
#   - `bash -n` flags a broken variant of the sample
#   - the formatting check flags trailing whitespace in the buggy sample
#   - the quality check exits 0 whether or not shellcheck is installed
#     (lint is skipped, not failed, when shellcheck is absent)
# No network access is used anywhere.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sample="${lab_dir}/examples/samples/buggy.sh"
checker="${lab_dir}/examples/quality_check.sh"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/day37.XXXXXX")"
trap 'rm -rf "${tmp}"' EXIT

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

echo "Testing the Day 37 quality pipeline ..."

# 0. Fixtures exist.
[ -f "${sample}" ] && check "buggy sample exists" "yes" || check "buggy sample exists" "no"
[ -f "${checker}" ] && check "quality_check.sh exists" "yes" || check "quality_check.sh exists" "no"

# 1. The shipped sample is syntactically valid (bash -n exits 0, no output).
if bash -n "${sample}" >/dev/null 2>&1; then
  check "bash -n accepts the valid sample" "yes"
else
  check "bash -n accepts the valid sample" "no"
fi

# 2. bash -n FLAGS a broken variant (missing 'fi' → parse error, non-zero).
broken="${tmp}/broken.sh"
grep -v '^fi$' "${sample}" > "${broken}"
if bash -n "${broken}" >/dev/null 2>&1; then
  check "bash -n flags a broken variant" "no"
else
  check "bash -n flags a broken variant" "yes"
fi

# 3. The quality check flags trailing whitespace in the buggy sample.
out="$(bash "${checker}" "${sample}" 2>&1)"
echo "${out}" | grep -q "trailing whitespace" && \
  check "formatting check flags trailing whitespace" "yes" || \
  check "formatting check flags trailing whitespace" "no"

# 4. The quality check flags the tab-indented line.
echo "${out}" | grep -q "tab indentation" && \
  check "formatting check flags tab indentation" "yes" || \
  check "formatting check flags tab indentation" "no"

# 5. The quality check exits 0 (report, not gate) regardless of shellcheck.
if bash "${checker}" "${sample}" >/dev/null 2>&1; then
  check "quality check exits 0" "yes"
else
  check "quality check exits 0" "no"
fi

# 6. Lint is skipped-not-failed when shellcheck is absent; run when present.
if command -v shellcheck >/dev/null 2>&1; then
  echo "${out}" | grep -qi "shellcheck" && \
    check "lint step runs shellcheck (installed)" "yes" || \
    check "lint step runs shellcheck (installed)" "no"
else
  echo "${out}" | grep -q "SKIP: shellcheck is not installed" && \
    check "lint step skips gracefully (shellcheck absent)" "yes" || \
    check "lint step skips gracefully (shellcheck absent)" "no"
fi

# 7. On a clean file, the formatting check reports no issues.
clean="${tmp}/clean.sh"
printf '#!/bin/bash\necho "clean"\n' > "${clean}"
clean_out="$(bash "${checker}" "${clean}" 2>&1)"
echo "${clean_out}" | grep -q "no trailing whitespace" && \
  check "clean file passes the whitespace check" "yes" || \
  check "clean file passes the whitespace check" "no"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
