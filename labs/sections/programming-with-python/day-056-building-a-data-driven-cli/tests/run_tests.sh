#!/usr/bin/env bash
# Tests for the Day 056 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Exercises the complete reference CLI (examples/records.py) against a
# throwaway JSON store: add, list, find (found and not-found), delete
# (present and absent), plus input-validation and corrupt-store errors.
# Every check verifies BOTH the printed output and the process exit code.
# It then imports two functions from the module to check their return
# values, and finally checks the learner's starter — structurally while
# exercises are unfinished, and to the same strict standard once they are
# complete. No network, non-interactive. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: do not let imported modules write __pycache__.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ref="${lab_dir}/examples/records.py"
starter="${lab_dir}/starter/records.py"
failures=0
checks=0

# A fresh temporary store per run; removed on exit.
store="$(mktemp -t records-test.XXXXXX)"
rm -f "${store}"                       # start from "no store yet"
cleanup() { rm -f "${store}"; }
trap cleanup EXIT

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

# check_run <label> <script> <expect_exit> <needle> <arg...>
# Runs the CLI with --store, checks the exit code and that combined output
# contains needle.
check_run() {
  local label="$1" script="$2" expect_exit="$3" needle="$4"
  shift 4
  local out code
  out="$(python3 "${script}" --store "${store}" "$@" 2>&1)"
  code=$?
  if [ "${code}" -eq "${expect_exit}" ] && printf '%s' "${out}" | grep -qF "${needle}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (exit ${code}, expected ${expect_exit}; output: ${out})"
  fi
}

run_cli_checks() {
  local script="$1"
  echo "Testing ${script} ..."
  rm -f "${store}"                              # fresh store for this program
  # Empty store lists cleanly.
  check_run "empty store lists 'no records'" "${script}" 0 "no records" list
  # Add two records: exit 0 and a confirmation line each.
  check_run "add #1 (Ada)"   "${script}" 0 "added #1: Ada Lovelace" add --name "Ada Lovelace" --email ada@example.com
  check_run "add #2 (Alan)"  "${script}" 0 "added #2: Alan Turing"  add --name "Alan Turing"  --email alan@example.com
  # List shows both.
  check_run "list shows Ada"  "${script}" 0 "#1: Ada Lovelace" list
  check_run "list shows Alan" "${script}" 0 "#2: Alan Turing"  list
  # Find: match -> exit 0; no match -> exit 1.
  check_run "find match exits 0"    "${script}" 0 "#1: Ada Lovelace" find --field name --query ada
  check_run "find no-match exits 1" "${script}" 1 "no records match" find --field name --query zoe
  check_run "find by email field"   "${script}" 0 "#2: Alan Turing"  find --field email --query alan@example.com
  # Delete: present -> exit 0; then it is gone; absent -> exit 1.
  check_run "delete #1 exits 0"      "${script}" 0 "deleted #1"          delete --id 1
  check_run "deleted record is gone" "${script}" 1 "no records match"    find --field name --query ada
  check_run "delete absent exits 1"  "${script}" 1 "no record with id 99" delete --id 99
  # Validation: empty name and bad email are rejected with exit 1.
  check_run "empty name rejected" "${script}" 1 "name must not be empty"     add --name "  " --email x@example.com
  check_run "bad email rejected"  "${script}" 1 "is not a valid email"       add --name "Bad" --email noatsign
}

# --- Reference CLI: always tested strictly ---
run_cli_checks "${ref}"

# --- Corrupt store is reported, not crashed (reference only) ---
echo "Testing corrupt-store handling (examples/records.py) ..."
printf 'this is not json {' > "${store}"
corrupt_out="$(python3 "${ref}" --store "${store}" list 2>&1)"
corrupt_code=$?
if [ "${corrupt_code}" -eq 1 ] && printf '%s' "${corrupt_out}" | grep -qF "is not valid JSON"; then
  check "corrupt store -> error, exit 1" "yes"
else
  check "corrupt store -> error, exit 1" "no"
  echo "    (exit ${corrupt_code}; output: ${corrupt_out})"
fi
rm -f "${store}"

# --- Import functions and check return values (main-guard payoff) ---
echo "Testing importability of examples/records.py ..."
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from records import next_id; \
assert next_id([]) == 1; assert next_id([{'id': 4}, {'id': 7}]) == 8"; then
  check "import next_id computes 1 and 8" "yes"
else
  check "import next_id computes 1 and 8" "no"
fi
if python3 -c "import sys; sys.path.insert(0, '${lab_dir}/examples'); \
from records import load_records; \
assert load_records('${lab_dir}/does-not-exist.json') == []"; then
  check "import load_records handles a missing file" "yes"
else
  check "import load_records handles a missing file" "no"
fi

# --- Learner starter ---
echo "Testing starter/records.py ..."
if python3 -c "compile(open('${starter}').read(), '${starter}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter}"; then
  echo "Note: starter/records.py still has unfinished exercises — testing structure only."
  grep -q 'def load_records' "${starter}" && check "starter defines load_records" "yes" || check "starter defines load_records" "no"
  grep -q 'def cmd_add' "${starter}" && check "starter defines cmd_add" "yes" || check "starter defines cmd_add" "no"
else
  run_cli_checks "${starter}"
  grep -q '__name__ == "__main__"' "${starter}" && check "starter has the main guard" "yes" || check "starter has the main guard" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
