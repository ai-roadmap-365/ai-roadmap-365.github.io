#!/usr/bin/env bash
# Tests for the Day 134 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the day's claims by driving the real client functions
# against a real mock HTTP server on 127.0.0.1 and an ephemeral port --
# never by reading source and never by asserting on a timing:
#
#   * a naive dtype-and-range check passes on two unemployment_rate
#     columns with different definitions, and a dictionary-aware check
#     refuses the join between the same two columns;
#   * pagination follows the source's own has_more flag until exhaustion,
#     and the assembled row count equals the advertised total;
#   * a 429 triggers bounded backoff and eventual success against a source
#     that relents, with a named attempt count; a source that never
#     relents is refused after a bounded number of attempts, not retried
#     forever;
#   * a second request carrying the stored ETag returns 304 and is served
#     from cache at zero bytes over the wire, reported as byte counts;
#   * the SHA-256 of a fixture matches a recorded value, and a single
#     altered byte changes it;
#   * the five-minute source assessment returns a structured verdict for
#     a well-documented source and a deficient one;
#   * a licence gate passes CC0 for redistribution and refuses "all rights
#     reserved", with a reason rather than a bare boolean;
#   * a dataset claiming national coverage is missing a documented region,
#     detected by comparing key sets against the dictionary;
#   * a provenance record carries url, retrieval timestamp and checksum,
#     and regenerating it from the same fixture with the same pinned
#     timestamp is stable;
#   * the reference suite (examples/) passes in full;
#   * the exercise suite (starter/) is all-skip on an untouched checkout,
#     and the harness proves it can genuinely FAIL by solving every
#     exercise in a scratch copy, breaking one assertion on purpose,
#     confirming a non-zero exit and a printed failure, then restoring it;
#   * nothing is left listening, and no __pycache__ or .pytest_cache
#     survives the run.
#
# Everything after the one-time install runs offline. The mock server
# binds 127.0.0.1 on an ephemeral port and is shut down inside every
# fixture, including on failure. Deterministic, non-interactive, exits 0
# only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

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

resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest:" >&2
  echo "    PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

python_bin="$(dirname "${pytest_bin}")/python3"
if [ ! -x "${python_bin}" ]; then
  python_bin="$(command -v python3 || true)"
fi
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi

if ! "${python_bin}" -c "import pandas" >/dev/null 2>&1; then
  echo "FAIL: pandas is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 134 — Judge the Source Before the Data"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
from importlib.metadata import version

print(f"python     {platform.python_version()}")
for name in ("pandas", "pytest"):
    try:
        print(f"{name:<10} {version(name)}")
    except Exception as exc:  # pragma: no cover
        print(f"{name:<10} NOT INSTALLED ({exc})")
PY
)"
echo "${versions}"
echo

mismatch=0
while IFS= read -r line; do
  [ -z "${line}" ] && continue
  pkg="${line%%==*}"
  pinned="${line#*==}"
  installed="$("${python_bin}" -c "from importlib.metadata import version; print(version('${pkg}'))" 2>/dev/null || echo "MISSING")"
  if [ "${installed}" != "${pinned}" ]; then
    mismatch=1
    echo "  version mismatch: ${pkg} pinned ${pinned}, installed ${installed}"
  fi
done < "${lab_dir}/requirements/requirements.txt"
check "installed packages match requirements.txt exactly" "$( [ ${mismatch} -eq 0 ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "2. The client and judgement functions, exercised directly against a"
echo "   real mock HTTP server on 127.0.0.1 and an ephemeral port"
# --------------------------------------------------------------------------

behaviour="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY'
"""Drive datasource.py against mock_server.py and print one machine-readable
line per claim, including the attempt and byte counts the day brief asks for."""
import hashlib
from datetime import datetime, timezone

import datasource as ds
import fixtures as fx
import mock_server as ms

results = {}


def record(key, value):
    results[key] = value


# -- exercise 1: the definition trap ----------------------------------------
series_a = fx.unemployment_series_a()
series_b = fx.unemployment_series_b()
naive = ds.naive_join_check(series_a, series_b)
record("naive_dtype_match", "yes" if naive["dtype_match"] else "no")
record("naive_ranges_overlap", "yes" if naive["ranges_overlap"] else "no")
record("naive_would_pass", "yes" if naive["would_pass_naive_check"] else "no")
aware = ds.dictionary_aware_join_check(fx.DICTIONARY_A, fx.DICTIONARY_B, "unemployment_rate")
record("dictionary_aware_safe_to_join", "yes" if aware["safe_to_join"] else "no")
record("dictionary_aware_reason_has_differ", "yes" if "differ" in aware["reason"] else "no")

with ms.serve_mock_api(rate_limit_trigger_count=2) as api:
    # -- exercise 2: pagination to exhaustion -------------------------------
    rows = ds.fetch_all_pages(api.base_url, "/dataset")
    record("rows_fetched", str(len(rows)))
    record("rows_are_advertised_total", "yes" if len(rows) == ms.TOTAL_ROWS else "no")
    record("row_ids_in_order", "yes" if [r["id"] for r in rows] == list(range(ms.TOTAL_ROWS)) else "no")
    expected_pages = -(-ms.TOTAL_ROWS // ms.PAGE_SIZE)
    record("dataset_requests_made", str(api.request_log.count("/dataset")))
    record("dataset_requests_matches_pages_needed", "yes" if api.request_log.count("/dataset") == expected_pages else "no")

    # -- exercise 3: rate limiting (relenting source) -----------------------
    body, attempts = ds.fetch_with_backoff(api.base_url, "/ratelimited", max_attempts=5, base_delay=0.01)
    record("relenting_attempts", str(attempts))
    record("relenting_rejections_logged", ",".join(str(x) for x in api.rate_limit_hits))

with ms.serve_mock_api(rate_limit_trigger_count=10) as stubborn:
    # -- exercise 3: rate limiting (a source that never relents in budget) -
    gave_up = False
    attempts_before_giving_up = None
    try:
        ds.fetch_with_backoff(stubborn.base_url, "/ratelimited", max_attempts=3, base_delay=0.01)
    except ds.RateLimitExceeded:
        gave_up = True
        attempts_before_giving_up = len(stubborn.rate_limit_hits)
    record("gave_up_rather_than_retry_forever", "yes" if gave_up else "no")
    record("stubborn_attempts_made", str(attempts_before_giving_up))

with ms.serve_mock_api() as api:
    # -- exercise 4: conditional request -------------------------------------
    cache = {}
    first_body, first_cached, first_bytes = ds.fetch_with_etag(api.base_url, "/etag-resource", cache)
    second_body, second_cached, second_bytes = ds.fetch_with_etag(api.base_url, "/etag-resource", cache)
    record("first_fetch_from_cache", "yes" if first_cached else "no")
    record("first_fetch_bytes", str(first_bytes))
    record("second_fetch_from_cache", "yes" if second_cached else "no")
    record("second_fetch_bytes", str(second_bytes))
    record("cached_body_matches_original", "yes" if second_body == first_body else "no")

    # -- pandas.read_csv reading a URL, against the local mock ---------------
    import pandas as pd
    frame = pd.read_csv(f"{api.base_url}/dataset.csv")
    record("read_csv_row_count", str(len(frame)))
    record("read_csv_matches_total_rows", "yes" if len(frame) == ms.TOTAL_ROWS else "no")

# -- exercise 5: checksum pinning -------------------------------------------
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix="d134-checksum-") as tmp:
    original = Path(tmp) / "dataset.csv"
    original.write_text("id,value\n1,10\n2,20\n3,30\n")
    digest = ds.sha256_of(original)
    record("checksum_matches_recorded", "yes" if digest == "4c0610aa92b75ca794ceec30068934fc6bc3d2fbff87969a15977f8fcf96f13f" else "no")
    altered = Path(tmp) / "altered.csv"
    altered.write_text("id,value\n1,10\n2,20\n3,31\n")
    altered_digest = ds.sha256_of(altered)
    record("altered_checksum_differs", "yes" if altered_digest != digest else "no")

# -- exercise 6: five-minute source assessment -------------------------------
good = ds.assess_source(fx.GOOD_SOURCE_METADATA)
deficient = ds.assess_source(fx.DEFICIENT_SOURCE_METADATA)
record("good_source_ready", "yes" if good.ready else "no")
record("deficient_source_ready", "yes" if deficient.ready else "no")
record("deficient_problem_count", str(len(deficient.problems)))

# -- exercise 7: licence gate -------------------------------------------------
cc0 = ds.check_licence("CC0")
arr = ds.check_licence("All rights reserved")
record("cc0_allowed", "yes" if cc0["allowed"] else "no")
record("all_rights_reserved_allowed", "yes" if arr["allowed"] else "no")
record("all_rights_reserved_has_reason", "yes" if arr["reason"] else "no")

# -- exercise 8: coverage check -----------------------------------------------
coverage = ds.check_coverage(fx.DICTIONARY_A, fx.NATIONAL_DATASET_KEYS)
record("coverage_complete", "yes" if coverage["complete"] else "no")
record("coverage_missing", ",".join(coverage["missing"]))

# -- exercise 9: provenance record --------------------------------------------
fixed = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)
p1 = ds.record_provenance("http://example.test/dataset.csv", digest, retrieved_at=fixed)
p2 = ds.record_provenance("http://example.test/dataset.csv", digest, retrieved_at=fixed)
record("provenance_stable_with_pinned_clock", "yes" if p1 == p2 else "no")
record("provenance_has_required_keys", "yes" if set(p1) == {"url", "retrieved_at", "sha256"} else "no")

for key, value in results.items():
    print(f"{key}={value}")
PY
)"
behaviour_status=$?
echo "${behaviour}"
echo

value_of() { echo "${behaviour}" | grep "^$1=" | cut -d= -f2-; }

check "the behaviour script ran without error" "$( [ ${behaviour_status} -eq 0 ] && echo yes || echo no )"
check "naive check: dtype matches and ranges overlap on the two unemployment_rate columns" "$( [ "$(value_of naive_dtype_match)" = yes ] && [ "$(value_of naive_ranges_overlap)" = yes ] && echo yes || echo no )"
check "naive check would pass the join -- nothing mechanical flags it" "$( [ "$(value_of naive_would_pass)" = yes ] && echo yes || echo no )"
check "dictionary-aware check refuses the same join" "$( [ "$(value_of dictionary_aware_safe_to_join)" = no ] && [ "$(value_of dictionary_aware_reason_has_differ)" = yes ] && echo yes || echo no )"
check "pagination assembled $(value_of rows_fetched) rows, matching the advertised total" "$( [ "$(value_of rows_are_advertised_total)" = yes ] && echo yes || echo no )"
check "row ids arrived in order" "$( [ "$(value_of row_ids_in_order)" = yes ] && echo yes || echo no )"
check "dataset requests made ($(value_of dataset_requests_made)) match pages actually needed" "$( [ "$(value_of dataset_requests_matches_pages_needed)" = yes ] && echo yes || echo no )"
check "rate limiting: relenting source succeeded after $(value_of relenting_attempts) attempts (rejections logged: $(value_of relenting_rejections_logged))" "$( [ "$(value_of relenting_attempts)" = 3 ] && [ "$(value_of relenting_rejections_logged)" = "1,2" ] && echo yes || echo no )"
check "rate limiting: client gave up against a source that never relents, after $(value_of stubborn_attempts_made) attempts" "$( [ "$(value_of gave_up_rather_than_retry_forever)" = yes ] && [ "$(value_of stubborn_attempts_made)" = 3 ] && echo yes || echo no )"
check "conditional request: first fetch was not from cache, $(value_of first_fetch_bytes) bytes over the wire" "$( [ "$(value_of first_fetch_from_cache)" = no ] && [ "$(value_of first_fetch_bytes)" -gt 0 ] && echo yes || echo no )"
check "conditional request: second fetch was served from cache at $(value_of second_fetch_bytes) bytes over the wire" "$( [ "$(value_of second_fetch_from_cache)" = yes ] && [ "$(value_of second_fetch_bytes)" = 0 ] && echo yes || echo no )"
check "the cached body matches the original" "$( [ "$(value_of cached_body_matches_original)" = yes ] && echo yes || echo no )"
check "pandas.read_csv against the local mock returned $(value_of read_csv_row_count) rows" "$( [ "$(value_of read_csv_matches_total_rows)" = yes ] && echo yes || echo no )"
check "checksum of the fixture matches the recorded SHA-256" "$( [ "$(value_of checksum_matches_recorded)" = yes ] && echo yes || echo no )"
check "a single altered byte changes the checksum" "$( [ "$(value_of altered_checksum_differs)" = yes ] && echo yes || echo no )"
check "the well-documented source assesses as ready" "$( [ "$(value_of good_source_ready)" = yes ] && echo yes || echo no )"
check "the deficient source assesses as not ready, with $(value_of deficient_problem_count) named problems" "$( [ "$(value_of deficient_source_ready)" = no ] && [ "$(value_of deficient_problem_count)" -ge 5 ] && echo yes || echo no )"
check "CC0 is allowed for redistribution" "$( [ "$(value_of cc0_allowed)" = yes ] && echo yes || echo no )"
check "'all rights reserved' is refused, with a reason rather than a bare boolean" "$( [ "$(value_of all_rights_reserved_allowed)" = no ] && [ "$(value_of all_rights_reserved_has_reason)" = yes ] && echo yes || echo no )"
check "coverage check finds the national dataset incomplete, missing: $(value_of coverage_missing)" "$( [ "$(value_of coverage_complete)" = no ] && [ "$(value_of coverage_missing)" = "west" ] && echo yes || echo no )"
check "the provenance record is stable once the clock is pinned" "$( [ "$(value_of provenance_stable_with_pinned_clock)" = yes ] && echo yes || echo no )"
check "the provenance record has exactly url, retrieved_at and sha256" "$( [ "$(value_of provenance_has_required_keys)" = yes ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "3. Reference suite -- examples/ must pass in full"
# --------------------------------------------------------------------------

examples_output="$(cd "${lab_dir}" && "${pytest_bin}" examples -q 2>&1)"
examples_status=$?
echo "${examples_output}" | tail -5
check "examples/ exits 0" "$( [ ${examples_status} -eq 0 ] && echo yes || echo no )"
examples_passed_line="$(echo "${examples_output}" | grep -E '^[0-9]+ passed' || true)"
check "examples/ reports 9 passed, 0 failed" "$( echo "${examples_passed_line}" | grep -qE '^9 passed' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "4. Exercise suite -- starter/ is all-skip on an untouched checkout"
# --------------------------------------------------------------------------

starter_output="$(cd "${lab_dir}" && "${pytest_bin}" starter -q 2>&1)"
starter_status=$?
echo "${starter_output}" | tail -5
check "starter/ (untouched) exits 0" "$( [ ${starter_status} -eq 0 ] && echo yes || echo no )"
check "starter/ (untouched) reports 9 skipped, 0 failed" "$( echo "${starter_output}" | grep -qE '^9 skipped' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "5. Never run 'pytest examples starter' in one invocation -- both"
echo "   directories define a module named test_datasource.py, and pytest"
echo "   collects by dotted module name. Documented, and run as two commands."
# --------------------------------------------------------------------------

combined_output="$(cd "${lab_dir}" && "${pytest_bin}" examples starter -q 2>&1)"
combined_status=$?
check "'pytest examples starter' aborts rather than silently passing" "$( [ ${combined_status} -ne 0 ] && echo yes || echo no )"
check "the collision is reported as an import file mismatch" "$( echo "${combined_output}" | grep -qi 'import file mismatch' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "6. Prove the suite can genuinely FAIL: solve every exercise in a"
echo "   scratch copy, confirm green, break one assertion on purpose,"
echo "   confirm a non-zero exit and a printed failure, then restore."
# --------------------------------------------------------------------------

scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/d134-scratch.XXXXXX")"
cleanup_scratch() { rm -rf "${scratch_dir}"; }
trap cleanup_scratch EXIT

for module in test_datasource.py datasource.py mock_server.py fixtures.py conftest.py; do
  cp "${lab_dir}/examples/${module}" "${scratch_dir}/${module}"
done

solved_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
solved_status=$?
check "scratch copy of the solved suite exits 0" "$( [ ${solved_status} -eq 0 ] && echo yes || echo no )"
check "scratch copy reports 9 passed" "$( echo "${solved_output}" | grep -qE '^9 passed' && echo yes || echo no )"

# Break exercise 8's exact missing-region assertion on purpose.
sed -i.bak "s/result\[\"missing\"\] == \[\"west\"\]/result[\"missing\"] == [\"nowhere\"]/" "${scratch_dir}/test_datasource.py"

broken_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
broken_status=$?
check "broken scratch copy exits non-zero" "$( [ ${broken_status} -ne 0 ] && echo yes || echo no )"
check "broken scratch copy prints a failure" "$( echo "${broken_output}" | grep -qiE 'failed|assert' && echo yes || echo no )"

mv "${scratch_dir}/test_datasource.py.bak" "${scratch_dir}/test_datasource.py"
restored_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
restored_status=$?
check "restored scratch copy exits 0 again" "$( [ ${restored_status} -eq 0 ] && echo yes || echo no )"
check "restored scratch copy reports 9 passed again" "$( echo "${restored_output}" | grep -qE '^9 passed' && echo yes || echo no )"

cleanup_scratch
trap - EXIT
echo

# --------------------------------------------------------------------------
echo "7. Offline, and nothing left behind"
# --------------------------------------------------------------------------

localhost_hits="$(grep -rl 'localhost:' "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null || true)"
check "no literal 'localhost:port' string anywhere -- 127.0.0.1 only" "$( [ -z "${localhost_hits}" ] && echo yes || echo no )"

find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

stray="$(find "${lab_dir}" -name '.venv' -prune -o \( -type d -name '__pycache__' -print -o -type d -name '.pytest_cache' -print \) 2>/dev/null || true)"
check "no __pycache__ or .pytest_cache left behind" "$( [ -z "${stray}" ] && echo yes || echo no )"

leftover_tmp="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'd134-*' -print 2>/dev/null || true)"
check "no d134 temporary directory left in the system temp directory" "$( [ -z "${leftover_tmp}" ] && echo yes || echo no )"
echo

echo "-------------------------------------------------------------"
echo "${checks} checks, ${failures} failure(s)"
if [ "${failures}" -gt 0 ]; then
  exit 1
fi
exit 0
