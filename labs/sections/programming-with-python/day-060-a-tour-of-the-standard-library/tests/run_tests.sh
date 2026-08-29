#!/usr/bin/env bash
# Tests for the Day 060 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Exercises the reference Stdlib Toolkit (examples/toolkit.py) against a
# freshly built temporary directory with a KNOWN mix of files, so the run is
# deterministic. Every check parses the JSON report and asserts on the stable
# fields (total_files, by_extension, directory); the volatile "generated_at"
# timestamp is deliberately NOT checked. It then imports tally_extensions to
# check its return value directly, and finally checks the learner's starter —
# structurally while exercises are unfinished, and to the same strict standard
# once they are complete. No network, non-interactive. Exits 0 only if every
# check passes.
set -u

# Keep the working tree clean: do not let imported modules write __pycache__.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref="${lab_dir}/examples/toolkit.py"
starter="${lab_dir}/starter/toolkit.py"
failures=0
checks=0

# A fresh temporary directory tree per run; removed on exit.
tmp="$(mktemp -d -t toolkit-test.XXXXXX)"
cleanup() { rm -rf "${tmp}"; }
trap cleanup EXIT

# Build a KNOWN tree: 3 csv (one nested), 2 json, 1 txt, 1 no-extension,
# and one .CSV to prove the tally is case-insensitive.
mkdir -p "${tmp}/data/sub"
printf 'a\n' > "${tmp}/data/a.csv"
printf 'b\n' > "${tmp}/data/b.csv"
printf 'c\n' > "${tmp}/data/sub/c.CSV"       # uppercase on purpose
printf '{}\n' > "${tmp}/data/x.json"
printf '{}\n' > "${tmp}/data/y.json"
printf 'note\n' > "${tmp}/data/notes.txt"
printf 'readme\n' > "${tmp}/data/README"      # no extension -> "(none)"
# Expected: 7 files; .csv=3 (case-insensitive), .json=2, .txt=1, (none)=1

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

# field <json-text> <python-expr-on-d> : print the value of a report field.
field() {
  printf '%s' "$1" | python3 -c "import sys, json; d = json.load(sys.stdin); print($2)"
}

run_cli_checks() {
  local script="$1"
  echo "Testing ${script} ..."
  local out
  out="$(python3 "${script}" --dir "${tmp}/data")"
  local code=$?
  # Valid JSON and exit 0.
  if [ "${code}" -eq 0 ] && printf '%s' "${out}" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    check "report is valid JSON, exit 0" "yes"
  else
    check "report is valid JSON, exit 0" "no"
    echo "    (exit ${code}; output: ${out})"
    return
  fi
  # Deterministic fields.
  [ "$(field "${out}" 'd["total_files"]')" = "7" ] \
    && check "total_files is 7" "yes" || check "total_files is 7" "no"
  [ "$(field "${out}" 'd["by_extension"][".csv"]')" = "3" ] \
    && check ".csv counted 3 (case-insensitive)" "yes" || check ".csv counted 3 (case-insensitive)" "no"
  [ "$(field "${out}" 'd["by_extension"][".json"]')" = "2" ] \
    && check ".json counted 2" "yes" || check ".json counted 2" "no"
  [ "$(field "${out}" 'd["by_extension"][".txt"]')" = "1" ] \
    && check ".txt counted 1" "yes" || check ".txt counted 1" "no"
  [ "$(field "${out}" 'd["by_extension"]["(none)"]')" = "1" ] \
    && check "no-extension file counted as (none)" "yes" || check "no-extension file counted as (none)" "no"
  # Tally is ordered largest-first (.csv before .json before .txt).
  [ "$(field "${out}" 'list(d["by_extension"])[0]')" = ".csv" ] \
    && check "by_extension is largest-first" "yes" || check "by_extension is largest-first" "no"

  # --out writes a valid JSON file with the same total.
  local outfile="${tmp}/report.json"
  rm -f "${outfile}"
  python3 "${script}" --dir "${tmp}/data" --out "${outfile}" >/dev/null
  if [ -f "${outfile}" ] && python3 -c "import json; d = json.load(open('${outfile}')); assert d['total_files'] == 7" 2>/dev/null; then
    check "--out writes a valid JSON report" "yes"
  else
    check "--out writes a valid JSON report" "no"
  fi
  rm -f "${outfile}"
}

# --- Reference toolkit: always tested strictly ---
run_cli_checks "${ref}"

# --- Import tally_extensions and check return values ---
echo "Testing importability of examples/toolkit.py ..."
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from toolkit import tally_extensions; \
assert tally_extensions(['a.csv', 'b.csv', 'c.txt']) == {'.csv': 2, '.txt': 1}; \
assert tally_extensions(['A.CSV', 'b.csv']) == {'.csv': 2}; \
assert tally_extensions(['README']) == {'(none)': 1}"; then
  check "import tally_extensions computes correct tallies" "yes"
else
  check "import tally_extensions computes correct tallies" "no"
fi

# --- Learner starter ---
echo "Testing starter/toolkit.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/toolkit.py still has unfinished exercises — testing structure only."
  grep -q 'def walk_files' "${starter}" && check "starter defines walk_files" "yes" || check "starter defines walk_files" "no"
  grep -q 'def tally_extensions' "${starter}" && check "starter defines tally_extensions" "yes" || check "starter defines tally_extensions" "no"
  grep -q 'def build_report' "${starter}" && check "starter defines build_report" "yes" || check "starter defines build_report" "no"
  grep -q 'def write_report' "${starter}" && check "starter defines write_report" "yes" || check "starter defines write_report" "no"
else
  run_cli_checks "${starter}"
  grep -q '__name__ == "__main__"' "${starter}" && check "starter has the main guard" "yes" || check "starter has the main guard" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
