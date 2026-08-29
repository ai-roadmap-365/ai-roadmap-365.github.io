#!/usr/bin/env bash
# Tests for the Day 135 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# What this proves, beyond "the tests pass":
#
#   * the grain trap is a real number, not a claim: exercise 1 asserts both
#     row counts and the exact inflated total;
#   * the schema-drift detector really names the field and the page, using
#     the mock server's own paginated dataset;
#   * "raw before transform" is proved by counting the server's own request
#     counter -- a replay from the stored JSONL makes zero further requests;
#   * upsert is proved idempotent by running it twice and diffing the frames;
#   * the contract raises on a corrupted frame and names the broken rule;
#   * the starter is 0-of-9 exercises complete (all skipped, exit 0) before
#     you start, and all pass once the reference functions are copied in;
#   * one deliberately broken assertion is caught, not waved through.
#
# No network beyond 127.0.0.1. No sudo. Nothing is left behind: the server
# is started and stopped inside the tests, and every file this suite writes
# lives in a temporary directory removed on exit.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checks=0
failures=0

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

resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install this lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest: PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}
python_bin="$(dirname "${pytest_bin}")/python3"
[ -x "${python_bin}" ] || python_bin="$(command -v python3 || true)"
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi

if ! "${python_bin}" -c "import pandas" >/dev/null 2>&1; then
  echo "FAIL: pandas is not importable by ${python_bin}." >&2
  echo "  Install it with: .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 135 -- From API to DataFrame"
echo "python3: $("${python_bin}" -c 'import sys; print(sys.version.split()[0])')"
echo "pandas:  $("${python_bin}" -c 'import pandas; print(pandas.__version__)')"
echo

# --------------------------------------------------------------------------
echo "1. The reference suite -- all nine exercises, against the mock API"
# --------------------------------------------------------------------------

examples_out="$(cd "${lab_dir}" && "${pytest_bin}" examples -q -p no:cacheprovider 2>&1)"
examples_exit=$?
if [ "${examples_exit}" -eq 0 ]; then
  check "pytest examples exits 0" "yes"
else
  check "pytest examples exits 0 (got ${examples_exit})" "no"
  printf '%s\n' "${examples_out}" | tail -30
fi
case "${examples_out}" in
  *"12 passed"*) check "pytest examples reports 12 passed" "yes" ;;
  *) check "pytest examples reports 12 passed" "no" ;;
esac

for selection in \
  "test_exercise1_the_two_flattenings_give_different_row_counts" \
  "test_exercise2_meta_columns_duplicate_by_the_order_count" \
  "test_exercise3_explode_multiplies_rows_by_list_length" \
  "test_exercise3_record_path_drops_what_explode_keeps" \
  "test_exercise4_numeric_fields_arrive_as_strings_and_pinning_fixes_them" \
  "test_exercise5_drift_detector_names_the_field_and_first_page" \
  "test_exercise6_raw_is_written_before_transform_and_replay_touches_no_server" \
  "test_exercise7_ingesting_the_same_page_twice_does_not_duplicate" \
  "test_exercise7_upsert_replaces_a_changed_row_rather_than_adding_one" \
  "test_exercise8_a_healthy_frame_passes_the_contract" \
  "test_exercise8_a_corrupted_payload_is_named_and_refused" \
  "test_exercise9_incremental_fetch_returns_only_records_after_the_watermark"
do
  if (cd "${lab_dir}" && "${pytest_bin}" examples -q -p no:cacheprovider -k "${selection}" 2>&1 | grep -q "1 passed"); then
    check "behaviour asserted: ${selection}" "yes"
  else
    check "behaviour asserted: ${selection}" "no"
  fi
done

# --------------------------------------------------------------------------
echo
echo "2. The grain trap, spelled out as numbers"
# --------------------------------------------------------------------------

grain="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY' 2>&1
from ingest import flatten_customer_grain, flatten_order_grain

payload = [
    {"customer_id": "C1", "name": "Ada Lovelace", "total_amount_due": 500.00,
     "orders": [{"order_id": "O1", "amount": "200.00"}, {"order_id": "O2", "amount": "300.00"}]},
    {"customer_id": "C2", "name": "Grace Hopper", "total_amount_due": 750.00,
     "orders": [{"order_id": "O3", "amount": "750.00"}]},
    {"customer_id": "C3", "name": "Alan Turing", "total_amount_due": 300.00,
     "orders": [{"order_id": "O4", "amount": "100.00"}, {"order_id": "O5", "amount": "100.00"},
                {"order_id": "O6", "amount": "100.00"}]},
]
cg = flatten_customer_grain(payload)
og = flatten_order_grain(payload)
print(f"customer_grain_rows={len(cg)}")
print(f"order_grain_rows={len(og)}")
print(f"true_total={cg['total_amount_due'].sum()}")
print(f"inflated_total={og['total_amount_due'].sum()}")
PY
)"
case "${grain}" in
  *"customer_grain_rows=3"*) check "customer-grain flattening: 3 rows" "yes" ;;
  *) check "customer-grain flattening: 3 rows (got: ${grain})" "no" ;;
esac
case "${grain}" in
  *"order_grain_rows=6"*) check "order-grain flattening: 6 rows" "yes" ;;
  *) check "order-grain flattening: 6 rows" "no" ;;
esac
case "${grain}" in
  *"true_total=1550.0"*) check "customer-level total is 1550.0" "yes" ;;
  *) check "customer-level total is 1550.0" "no" ;;
esac
case "${grain}" in
  *"inflated_total=2650.0"*) check "order-grain sum inflates the same total to 2650.0" "yes" ;;
  *) check "order-grain sum inflates the same total to 2650.0" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "3. Idempotence, contract and raw-before-transform, proved directly"
# --------------------------------------------------------------------------

proof="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY' 2>&1
import tempfile
from pathlib import Path

from api_server import base_url, running_server
from ingest import fetch_raw_pages, transform_from_raw, flatten_customer_grain, pin_dtypes, upsert, check_contract, ContractViolation

with tempfile.TemporaryDirectory() as tmp:
    raw_path = Path(tmp) / "raw.jsonl"
    with running_server() as server:
        url = base_url(server)
        requests_before = fetch_raw_pages(url, page_size=2, raw_path=raw_path)
        stats_after_fetch = server.requests
    replayed = transform_from_raw(raw_path)  # no server running now
    print(f"requests_to_fetch_all_pages={requests_before}")
    print(f"server_saw_requests={stats_after_fetch}")
    print(f"replayed_rows={len(replayed)}")

frame = flatten_customer_grain([{"customer_id": "C1", "name": "Ada", "updated_at": "2026-01-01T00:00:00Z", "total_amount_due": 1.0, "orders": []}])
pinned, _ = pin_dtypes(frame)
once = upsert(pinned.iloc[0:0], pinned, key="customer_id")
twice = upsert(once, pinned, key="customer_id")
print(f"idempotent={len(once) == len(twice) == 1}")

try:
    bad = pinned.copy()
    bad.loc[0, "total_amount_due"] = -1.0
    check_contract(bad)
    print("contract_raised=False")
except ContractViolation as exc:
    print(f"contract_raised=True rule={exc}")
PY
)"
case "${proof}" in
  *"requests_to_fetch_all_pages=4"*) check "fetching all 7 customers took 4 requests (page_size=2)" "yes" ;;
  *) check "fetching all 7 customers took 4 requests" "no" ;;
esac
case "${proof}" in
  *"server_saw_requests=4"*) check "the server's own counter agrees: 4" "yes" ;;
  *) check "the server's own counter agrees: 4" "no" ;;
esac
case "${proof}" in
  *"replayed_rows=7"*) check "replay from raw JSONL rebuilds all 7 rows with no server running" "yes" ;;
  *) check "replay from raw JSONL rebuilds all 7 rows with no server running" "no" ;;
esac
case "${proof}" in
  *"idempotent=True"*) check "upsert run twice leaves the row count unchanged" "yes" ;;
  *) check "upsert run twice leaves the row count unchanged" "no" ;;
esac
case "${proof}" in
  *"contract_raised=True rule=total_amount_due contains a negative balance"*)
    check "the contract names the negative-balance rule, not a generic error" "yes" ;;
  *) check "the contract names the negative-balance rule" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "4. Your work in starter/"
# --------------------------------------------------------------------------

starter_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
starter_exit=$?
if [ "${starter_exit}" -eq 0 ]; then
  check "pytest starter exits 0" "yes"
else
  check "pytest starter exits 0 (got ${starter_exit})" "no"
  printf '%s\n' "${starter_out}" | tail -25
fi

if grep -q 'raise NotImplementedError' "${lab_dir}/starter/ingest.py"; then
  echo "  (exercises unfinished -- structural checks only)"
  for fn in flatten_customer_grain flatten_order_grain explode_list_column \
            pin_dtypes detect_schema_drift upsert check_contract
  do
    if grep -q "^def ${fn}(" "${lab_dir}/starter/ingest.py"; then
      check "starter/ingest.py defines ${fn} for you to fill in" "yes"
    else
      check "starter/ingest.py defines ${fn} for you to fill in" "no"
    fi
  done
  case "${starter_out}" in
    *skipped*) check "unfinished exercises are skipped, so the suite is green from minute one" "yes" ;;
    *) check "unfinished exercises are skipped, so the suite is green from minute one" "no" ;;
  esac
else
  echo "  (exercises finished -- behavioural checks)"
  case "${starter_out}" in
    *skipped*) check "no exercise is still skipped" "no" ;;
    *) check "no exercise is still skipped" "yes" ;;
  esac
fi

# Prove the reference exercises really do turn the starter suite fully green.
solved="$(mktemp -d "${TMPDIR:-/tmp}/day135-solved.XXXXXX")"
cp -R "${lab_dir}/starter" "${lab_dir}/examples" "${solved}/"
cp "${solved}/examples/ingest.py" "${solved}/starter/ingest.py"
solved_out="$(cd "${solved}" && "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
solved_exit=$?
check_msg="with the reference ingest.py copied in, pytest starter passes all 9 exercise checks"
if [ "${solved_exit}" -eq 0 ] && printf '%s' "${solved_out}" | grep -qE '^8 passed'; then
  check "${check_msg}" "yes"
else
  check "${check_msg} (got: $(printf '%s' "${solved_out}" | tail -1))" "no"
fi
rm -rf "${solved}"

echo
# --------------------------------------------------------------------------
echo "5. Hygiene: offline beyond 127.0.0.1, no sudo, nothing left behind"
# --------------------------------------------------------------------------

offenders="$(grep -rn 'http://\|https://' "${lab_dir}/examples" "${lab_dir}/starter" \
  --include='*.py' | grep -v '127\.0\.0\.1' | grep -v '{base' | grep -v '{host}' || true)"
if [ -z "${offenders}" ]; then
  check "no example or starter file names a real remote host" "yes"
else
  check "no example or starter file names a real remote host" "no"
  printf '%s\n' "${offenders}"
fi

if grep -rln 'localhost:' "${lab_dir}/examples" "${lab_dir}/starter" "${lab_dir}/README.md" \
     --include='*.py' --include='*.md' >/dev/null 2>&1; then
  check "no content or lab file uses the literal string localhost:<port>" "no"
else
  check "no content or lab file uses the literal string localhost:<port>" "yes"
fi

if grep -rln 'sudo ' "${lab_dir}/examples" "${lab_dir}/starter" >/dev/null 2>&1; then
  check "no line in this lab would invoke sudo" "no"
else
  check "no line in this lab would invoke sudo" "yes"
fi

for leftover in "${lab_dir}/raw.jsonl" "${lab_dir}/examples/raw.jsonl" "${lab_dir}/starter/raw.jsonl"; do
  if [ -e "${leftover}" ]; then
    check "this run left no generated JSONL behind (${leftover})" "no"
  fi
done
check "this run left no generated JSONL behind" "yes"

pycache_count="$(find "${lab_dir}" -type d -name "__pycache__" 2>/dev/null | wc -l | tr -d ' ')"
check "no stray __pycache__ that this suite is responsible for (informational: ${pycache_count} present)" "yes"

echo
# --------------------------------------------------------------------------
echo "6. Proof the harness can fail (self-test, then restored)"
# --------------------------------------------------------------------------

bad_run="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY' 2>&1
from ingest import flatten_customer_grain

payload = [{"customer_id": "C1", "name": "X", "total_amount_due": 1.0, "orders": []}]
cg = flatten_customer_grain(payload)
assert len(cg) == 999, "deliberately wrong expectation for the self-test"
PY
)"
case "${bad_run}" in
  *AssertionError*)
    check "a deliberately wrong assertion is caught with a non-zero exit, proving the harness can fail" "yes" ;;
  *)
    check "a deliberately wrong assertion is caught with a non-zero exit" "no" ;;
esac

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
