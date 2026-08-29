#!/usr/bin/env bash
# Tests for the Day 012 lab. Run from anywhere:
#   bash tests/run_tests.sh
#
# Builds a temporary directory with a KNOWN set of files, runs the completed
# reference script (examples/backup_notes.sh) against it, and checks that the
# reported counts are exactly right. Also checks the empty-directory case and
# the "not a directory" error path. Cleans up the temp directory on exit.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script="${lab_dir}/examples/backup_notes.sh"
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

# A temp workspace we always clean up, even if a check fails.
work="$(mktemp -d)"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

# --- Fixture: a known set of files ----------------------------------------
# 3 x .txt, 2 x .md, 1 x .csv, 1 file with no extension  => 7 files total.
fixture="${work}/notes"
mkdir -p "${fixture}"
printf 'a\n' >"${fixture}/one.txt"
printf 'b\n' >"${fixture}/two.txt"
printf 'c\n' >"${fixture}/three.txt"
printf 'd\n' >"${fixture}/alpha.md"
printf 'e\n' >"${fixture}/beta.md"
printf 'f\n' >"${fixture}/data.csv"
printf 'g\n' >"${fixture}/README"
# A subdirectory that must NOT be counted as a file.
mkdir -p "${fixture}/subfolder"

echo "Testing ${script} against a known fixture ..."

if ! out="$(bash "${script}" "${fixture}" 2>&1)"; then
  check "script exits 0 on a valid directory" "no"
  echo "${out}" | sed 's/^/    /'
else
  check "script exits 0 on a valid directory" "yes"
fi

# Header and footer present.
echo "${out}" | grep -q '^=== Notes summary ===$' && check "prints header" "yes" || check "prints header" "no"
echo "${out}" | grep -q '^=== End of summary ===$' && check "prints footer" "yes" || check "prints footer" "no"

# Total files should be exactly 7 (the subfolder is excluded).
echo "${out}" | grep -q '^Total files: 7$' && check "counts 7 total files (excludes subdirectory)" "yes" || check "counts 7 total files (excludes subdirectory)" "no"

# Per-extension counts, exactly.
echo "${out}" | grep -q '^  txt: 3$' && check "counts 3 .txt files" "yes" || check "counts 3 .txt files" "no"
echo "${out}" | grep -q '^  md: 2$' && check "counts 2 .md files" "yes" || check "counts 2 .md files" "no"
echo "${out}" | grep -q '^  csv: 1$' && check "counts 1 .csv file" "yes" || check "counts 1 .csv file" "no"
echo "${out}" | grep -q '^  (no extension): 1$' && check "counts 1 file with no extension" "yes" || check "counts 1 file with no extension" "no"

# --- Empty directory: total 0, still exits 0 ------------------------------
empty="${work}/empty"
mkdir -p "${empty}"
if empty_out="$(bash "${script}" "${empty}" 2>&1)"; then
  check "empty directory exits 0" "yes"
else
  check "empty directory exits 0" "no"
fi
echo "${empty_out}" | grep -q '^Total files: 0$' && check "empty directory reports 0 files" "yes" || check "empty directory reports 0 files" "no"

# --- Error path: not a directory should exit non-zero ---------------------
if bash "${script}" "${work}/does-not-exist" >/dev/null 2>&1; then
  check "missing directory exits non-zero" "no"
else
  check "missing directory exits non-zero" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
