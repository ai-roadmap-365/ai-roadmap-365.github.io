#!/usr/bin/env bash
# Tests for the Day 098 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This harness checks the five promises the pipeline makes, and it checks each
# one by observing behaviour rather than by reading the source:
#
#   * INGEST     a source that fails twice recovers on the third attempt; a 404
#                is attempted exactly once; a permanently failing source does
#                not take the run down with it.
#   * VALIDATE   two deliberately bad records are rejected, counted and
#                explained, and the seven good ones still get through — and the
#                record that is valid but wrong passes the gate, because no
#                field-level rule can see it.
#   * STORE      the pipeline is run twice against one database and the second
#                run inserts nothing. The UNIQUE constraint is then attacked
#                directly, to prove the guarantee is the database's and not the
#                application's good intentions.
#   * REPORT     built at a fixed instant, so its numbers are assertable, and
#                the implausible jump is flagged rather than dropped.
#   * OBSERVE    exactly one structured log line per stage, every line carrying
#                the same run id, configuration provenance printed correctly,
#                the API token absent from every byte of the log, and an exit
#                code of 3 for partial success.
#
# Plus: the starter skeleton runs, the nine exercises are proved achievable by
# running the same suite against the completed reference, the captures still
# match a live run, and the lab leaves nothing behind.
#
# Everything runs offline against a fixture server bound to 127.0.0.1 on a port
# the kernel chooses. Deterministic, non-interactive, exits 0 only if every
# check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. The README
# documents `pytest starter -q`, and running it writes .pyc files that would
# then fail the cleanliness check at the end of this script -- failing the
# reader for following the instructions. Clearing them here makes that final
# check measure what it claims to: what THIS run left behind. `.venv` is
# untouched, because the packages' own bytecode is theirs, not ours.
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

check_eq() {
  local label="$1" want="$2" got="$3"
  checks=$((checks + 1))
  if [ "${want}" = "${got}" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    echo "        expected: ${want}"
    echo "        actual  : ${got}"
    failures=$((failures + 1))
  fi
}

check_grep() {
  local label="$1" file="$2" pattern="$3"
  checks=$((checks + 1))
  if grep -qE "${pattern}" "${file}"; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    echo "        no line in $(basename "${file}") matched: ${pattern}"
    failures=$((failures + 1))
  fi
}

check_absent() {
  local label="$1" file="$2" pattern="$3"
  checks=$((checks + 1))
  if grep -qF "${pattern}" "${file}"; then
    echo "  FAIL: ${label}"
    echo "        found in $(basename "${file}"): ${pattern}"
    failures=$((failures + 1))
  else
    echo "  ok: ${label}"
  fi
}

# Resolve a tool: an explicit override, then this lab's .venv, then PATH.
# Fails loudly with install instructions rather than skipping quietly.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

install_hint() {
  echo "  Install the pinned dependencies with:" >&2
  echo "    cd ${lab_dir}" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing interpreter:" >&2
  echo "    PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
}

python_bin="$(resolve_tool python3 "${PYTHON:-}")" || {
  echo "FAIL: python3 not found." >&2
  install_hint
  exit 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  install_hint
  exit 1
}

for module in sqlalchemy pydantic; do
  if ! "${python_bin}" -c "import ${module}" >/dev/null 2>&1; then
    echo "FAIL: ${module} is not importable from ${python_bin}." >&2
    echo "  This lab is a pipeline built on it, so there is nothing to fall back to." >&2
    install_hint
    exit 1
  fi
done

work="$(mktemp -d)"
server_pid=""
cleanup() {
  if [ -n "${server_pid}" ]; then
    kill "${server_pid}" >/dev/null 2>&1
    # Reap it quietly: without the wait, bash prints its own "Terminated" line
    # to stderr after this script has already reported its result.
    wait "${server_pid}" >/dev/null 2>&1
  fi
  rm -rf "${work}"
}
trap cleanup EXIT

export PYTHONPATH="${lab_dir}/examples"
TOKEN="demo-token-value"

echo "Day 098 — Section Project: A Complete Data Pipeline"
echo

# ---------------------------------------------------------------------------
echo "1. Environment — the versions actually in use"
# ---------------------------------------------------------------------------
"${python_bin}" - > "${work}/versions.txt" <<'PY'
import platform
import sqlite3

import pydantic
import sqlalchemy

print(f"python {platform.python_version()}")
print(f"sqlalchemy {sqlalchemy.__version__}")
print(f"pydantic {pydantic.VERSION}")
print(f"sqlite {sqlite3.sqlite_version}")
PY
sed 's/^/    /' "${work}/versions.txt"

pinned_sqla="$(grep -iE '^SQLAlchemy==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
pinned_pyd="$(grep -iE '^pydantic==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
check_eq "the installed SQLAlchemy is the version requirements.txt pins" \
  "${pinned_sqla}" "$(awk '/^sqlalchemy /{print $2}' "${work}/versions.txt")"
check_eq "the installed pydantic is the version requirements.txt pins" \
  "${pinned_pyd}" "$(awk '/^pydantic /{print $2}' "${work}/versions.txt")"

# The lesson states plainly that no orchestrator is exercised here. Prove the
# claim is still true rather than letting the text go quietly stale.
for orchestrator in airflow dagster prefect dbt; do
  check "the lesson's claim that ${orchestrator} is not installed here holds" \
    "$("${python_bin}" -c "import ${orchestrator}" >/dev/null 2>&1 && echo no || echo yes)"
done

# ---------------------------------------------------------------------------
echo
echo "2. The whole pipeline, twice — the demo run"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/demo_run.py" > "${work}/demo.txt" 2>&1
demo_status=$?
check_eq "demo_run.py exits 0" "0" "${demo_status}"

check_grep "run 1 fetched nine records from the two sources that answered" \
  "${work}/demo.txt" '"event": "stage.ingest", "sources_ok": 2, "sources_failed": 1, "failed_sources": \["charlie"\], "records_fetched": 9, "attempts_total": 7'
check_grep "bravo recovered on its third attempt" \
  "${work}/demo.txt" '"event": "ingest.source_recovered", "source": "bravo", "attempts": 3'
check_grep "charlie failed permanently after three attempts" \
  "${work}/demo.txt" '"event": "ingest.source_failed", "source": "charlie", "attempts": 3, "status": 500'
check_grep "the validation gate accepted 7 and rejected 2, and said why" \
  "${work}/demo.txt" '"event": "stage.validate", "records_in": 9, "accepted": 7, "rejected": 2, "reasons": \{"humidity_pct": 1, "temperature_c": 1\}'
check_grep "run 1 stored 6 rows and skipped the in-payload duplicate" \
  "${work}/demo.txt" '"event": "stage.store", "considered": 7, "inserted": 6, "duplicates_skipped": 1, "total_rows": 6'
check_grep "run 2 stored NOTHING — the idempotence key held" \
  "${work}/demo.txt" '"event": "stage.store", "considered": 7, "inserted": 0, "duplicates_skipped": 7, "total_rows": 6'
check_grep "both runs exited 3, not 0 — one source is dark" \
  "${work}/demo.txt" '"event": "run.end", "status": "partial_success", "exit_code": 3, "stored_total": 6'
check_grep "the two runs produced identical reports" \
  "${work}/demo.txt" '^  reports identical    True$'
check_grep "and identical exit codes" \
  "${work}/demo.txt" '^  exit codes identical True$'
check_grep "bravo was worth three attempts" \
  "${work}/demo.txt" '^  bravo    attempts=3  ok=True  status=200'
check_grep "delta was worth exactly one — a 404 will be a 404 next time" \
  "${work}/demo.txt" '^  delta    attempts=1  ok=False  status=404'
check_grep "the fixture server really did echo the token back in an error body" \
  "${work}/demo.txt" 'raw error body from charlie : upstream credentials rejected for token demo-token-value'
check_grep "and the redactor caught it" \
  "${work}/demo.txt" 'after the log redactor      : upstream credentials rejected for token \*\*\*redacted\*\*\*'
check_grep "exactly five stage summaries, in pipeline order" \
  "${work}/demo.txt" '^  stage summaries    : 5 -> stage\.ingest, stage\.validate, stage\.store, stage\.report, stage\.observe$'
check_grep "the demo removed its temporary database" \
  "${work}/demo.txt" '^temporary database removed: True$'
check_absent "no absolute home path leaked into the demo output" \
  "${work}/demo.txt" "/Users/"

# ---------------------------------------------------------------------------
echo
echo "3. The report — fixed instant, exact values, and the record that is"
echo "   valid but wrong"
# ---------------------------------------------------------------------------
check_grep "alpha: 2 readings, 18.4 to 19.0, mean 18.7" \
  "${work}/demo.txt" '^    alpha               2      18\.4      19\.0      18\.7$'
check_grep "bravo: 3 readings, 13.6 to 41.3, mean 23.3" \
  "${work}/demo.txt" '^    bravo               3      13\.6      41\.3      23\.3$'
check_grep "charlie: 0 readings, and it is REPORTED rather than omitted" \
  "${work}/demo.txt" '^    charlie             0         -         -         -$'
check_grep "5 of the 6 stored readings fall inside the 12-hour window" \
  "${work}/demo.txt" '^    in window    5 of 6 stored readings$'
check_grep "the implausible jump is flagged, not deleted" \
  "${work}/demo.txt" '^    bravo: \+26\.3 C in 5 minutes \(2026-08-16T11:45:00Z -> 2026-08-16T11:50:00Z\)$'

# The window boundary is a decision, not an accident: b-1 at 23:30 the previous
# day is stored and deliberately outside a 12-hour window ending at noon.
"${python_bin}" - > "${work}/window.txt" <<'PY'
from datetime import datetime, timedelta, timezone

end = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
for hours in (12, 24):
    start = end - timedelta(hours=hours)
    stored = {
        "a-1": "2026-08-16T09:00:00Z",
        "a-2": "2026-08-16T10:00:00Z",
        "b-1": "2026-08-15T23:30:00Z",
        "b-2": "2026-08-16T08:15:00Z",
        "b-3": "2026-08-16T11:45:00Z",
        "b-4": "2026-08-16T11:50:00Z",
    }
    inside = [
        key
        for key, text in stored.items()
        if start <= datetime.fromisoformat(text.replace("Z", "+00:00")) <= end
    ]
    print(f"WINDOW {hours} {len(inside)} {' '.join(sorted(inside))}")
PY
check_grep "a 12-hour window holds 5 readings" "${work}/window.txt" '^WINDOW 12 5 a-1 a-2 b-2 b-3 b-4$'
check_grep "a 24-hour window holds all 6 — the window is the parameter" \
  "${work}/window.txt" '^WINDOW 24 6 a-1 a-2 b-1 b-2 b-3 b-4$'

# ---------------------------------------------------------------------------
echo
echo "4. Idempotence, attacked directly"
# ---------------------------------------------------------------------------
"${python_bin}" - > "${work}/idempotence.txt" 2>&1 <<'PY'
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from store import StoredReading, build_engine, store_readings
from validate import Reading

raw = {
    "station_id": "alpha",
    "reading_id": "a-1",
    "observed_at": "2026-08-16T09:00:00Z",
    "temperature_c": 18.4,
    "humidity_pct": 61,
}
reading = Reading.model_validate(raw)
engine = build_engine("sqlite://")
with Session(engine) as session:
    first = store_readings(session, [reading], run_id="r1")
    second = store_readings(session, [reading], run_id="r2")
    third = store_readings(session, [reading, reading], run_id="r3")
    print(f"FIRST inserted={first.inserted} total={first.total_rows}")
    print(f"SECOND inserted={second.inserted} duplicates={second.duplicates} total={second.total_rows}")
    print(f"BATCH inserted={third.inserted} duplicates={third.duplicates} total={third.total_rows}")

    # Now go around the application entirely and ask the database to break it.
    try:
        session.add(
            StoredReading(
                station_id="alpha",
                reading_id="a-1",
                observed_at="2026-08-16T09:00:00Z",
                temperature_dc=184,
                humidity_pct=61,
                ingested_by_run="rogue",
            )
        )
        session.commit()
        print("CONSTRAINT enforced=False")
    except IntegrityError as exc:
        session.rollback()
        first = str(exc).splitlines()[0]
        print(f"CONSTRAINT enforced=True says={first.split(') ', 1)[1]}")

    # And prove the CHECK constraints are real too.
    try:
        session.execute(
            StoredReading.__table__.insert().values(
                station_id="alpha",
                reading_id="rogue-1",
                observed_at="2026-08-16T09:00:00Z",
                temperature_dc=184,
                humidity_pct=155,
                ingested_by_run="rogue",
            )
        )
        session.commit()
        print("CHECK humidity_enforced=False")
    except IntegrityError:
        session.rollback()
        print("CHECK humidity_enforced=True")
engine.dispose()
PY
check_grep "the first store inserts the row" "${work}/idempotence.txt" '^FIRST inserted=1 total=1$'
check_grep "the second store inserts nothing and says so" \
  "${work}/idempotence.txt" '^SECOND inserted=0 duplicates=1 total=1$'
check_grep "a duplicate INSIDE one batch is caught too" \
  "${work}/idempotence.txt" '^BATCH inserted=0 duplicates=2 total=1$'
check_grep "the UNIQUE constraint refuses a write that bypasses the application" \
  "${work}/idempotence.txt" '^CONSTRAINT enforced=True says=UNIQUE constraint failed: readings\.station_id, readings\.reading_id$'
check_grep "and the humidity CHECK constraint refuses an impossible percentage" \
  "${work}/idempotence.txt" '^CHECK humidity_enforced=True$'

# ---------------------------------------------------------------------------
echo
echo "5. Validation — collected, counted, explained; and what it cannot see"
# ---------------------------------------------------------------------------
"${python_bin}" - > "${work}/validation.txt" <<'PY'
from validate import validate_all

records = [
    {"station_id": "x", "reading_id": "ok", "observed_at": "2026-08-16T09:00:00Z",
     "temperature_c": 18.4, "humidity_pct": 61},
    {"station_id": "x", "reading_id": "bad-temp", "observed_at": "2026-08-16T09:00:00Z",
     "temperature_c": "warm", "humidity_pct": 61},
    {"station_id": "x", "reading_id": "bad-hum", "observed_at": "2026-08-16T09:00:00Z",
     "temperature_c": 18.4, "humidity_pct": 155},
    {"station_id": "x", "reading_id": "naive", "observed_at": "2026-08-16T09:00:00",
     "temperature_c": 18.4, "humidity_pct": 61},
    {"station_id": "x", "reading_id": "extra", "observed_at": "2026-08-16T09:00:00Z",
     "temperature_c": 18.4, "humidity_pct": 61, "battery_pct": 90},
    {"station_id": "x", "reading_id": "valid-but-wrong", "observed_at": "2026-08-16T09:05:00Z",
     "temperature_c": 41.3, "humidity_pct": 61},
]
outcome = validate_all({"x": records})
print(f"CONSIDERED {outcome.considered} ACCEPTED {len(outcome.accepted)} REJECTED {len(outcome.rejected)}")
for rejection in outcome.rejected:
    print(f"REJECT {rejection}")
print(f"REASONS {outcome.reasons()}")
print(f"DECI {[r.temperature_dc for r in outcome.accepted]}")
PY
check_grep "six records in, two accepted, four rejected — and the run continued" \
  "${work}/validation.txt" '^CONSIDERED 6 ACCEPTED 2 REJECTED 4$'
check_grep "a non-numeric temperature is named with its field and its reason" \
  "${work}/validation.txt" '^REJECT x\[1\] bad-temp: temperature_c: Input should be a valid number'
check_grep "an out-of-range humidity is named too" \
  "${work}/validation.txt" '^REJECT x\[2\] bad-hum: humidity_pct: Input should be less than or equal to 100$'
check_grep "a timestamp with no offset is refused — it is not an instant" \
  "${work}/validation.txt" '^REJECT x\[3\] naive: observed_at: Value error, observed_at must carry a UTC offset'
check_grep "an unexpected field is refused rather than silently ignored" \
  "${work}/validation.txt" '^REJECT x\[4\] extra: battery_pct: Extra inputs are not permitted$'
check_grep "the reasons are counted per field, so a source owner can be told" \
  "${work}/validation.txt" "^REASONS \{'battery_pct': 1, 'humidity_pct': 1, 'observed_at': 1, 'temperature_c': 1\}$"
check_grep "the record that is valid but WRONG passes the gate — 41.3 C is legal" \
  "${work}/validation.txt" '^DECI \[184, 413\]$'

# ---------------------------------------------------------------------------
echo
echo "6. Configuration — four layers, resolved and printed"
# ---------------------------------------------------------------------------
(cd "${lab_dir}" && PIPELINE_LOG_LEVEL=warning PIPELINE_API_TOKEN="${TOKEN}" \
  "${python_bin}" examples/pipeline.py \
  --config-file examples/pipeline.toml --window-hours 24 --explain-config \
  > "${work}/provenance.txt" 2>&1)
provenance_status=$?
check_eq "--explain-config exits 0" "0" "${provenance_status}"
check_grep "a value nobody set is reported as a default" \
  "${work}/provenance.txt" '^retry_backoff_seconds  0\.05                   default$'
check_grep "a value from the TOML file is attributed to the file" \
  "${work}/provenance.txt" '^timeout_seconds        3\.0                    file$'
check_grep "the environment outranks the file" \
  "${work}/provenance.txt" '^log_level              warning                environment$'
check_grep "and an explicit flag outranks the environment" \
  "${work}/provenance.txt" '^window_hours           24                     command line$'
check_grep "the secret's SOURCE is reported and its VALUE is not" \
  "${work}/provenance.txt" '^api_token              \*\*\*redacted\*\*\*         environment$'
check_absent "the token never appears in the provenance table" \
  "${work}/provenance.txt" "${TOKEN}"

# ---------------------------------------------------------------------------
echo
echo "7. The command-line pipeline against a real server, and its exit code"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/fixture_server.py" --token "${TOKEN}" \
  > "${work}/port.txt" 2>"${work}/server.err" &
server_pid=$!
port=""
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  port="$(head -1 "${work}/port.txt" 2>/dev/null)"
  [ -n "${port}" ] && break
  "${python_bin}" -c "import time; time.sleep(0.1)"
done
check "the fixture server started and announced a port" \
  "$([ -n "${port}" ] && echo yes || echo no)"

if [ -z "${port}" ]; then
  echo "  (skipping the live-server section: no port)" >&2
else
  run_dir="${work}/run"
  mkdir -p "${run_dir}"
  (cd "${run_dir}" && PIPELINE_API_TOKEN="${TOKEN}" "${python_bin}" \
    "${lab_dir}/examples/pipeline.py" \
    --base-url "http://127.0.0.1:${port}" \
    --sources alpha,bravo,charlie \
    --report-at 2026-08-16T12:00:00Z \
    --window-hours 12 \
    --run-id run-cli000001 \
    --fixed-clock \
    > "${work}/cli-stdout.txt" 2> "${work}/cli-stderr.txt")
  cli_status=$?
  check_eq "a partially successful run exits 3, not 0 and not 1" "3" "${cli_status}"

  check_grep "the report went to stdout" \
    "${work}/cli-stdout.txt" '^Station readings report$'
  check_grep "with the same numbers the demo produced" \
    "${work}/cli-stdout.txt" '^  in window    5 of 6 stored readings$'
  check_absent "nothing but the report went to stdout" \
    "${work}/cli-stdout.txt" '"event":'

  stage_lines="$(grep -c '"event": "stage\.' "${work}/cli-stderr.txt")"
  check_eq "exactly five stage lines, one per stage" "5" "${stage_lines}"
  run_ids="$("${python_bin}" - "${work}/cli-stderr.txt" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    ids = {json.loads(line)["run_id"] for line in handle if line.strip()}
print(len(ids), " ".join(sorted(ids)))
PY
)"
  check_eq "every line carries the one run id" "1 run-cli000001" "${run_ids}"
  check_grep "every line is valid JSON with a timestamp and a level" \
    "${work}/cli-stderr.txt" '^\{"ts": "2026-08-16T12:00:0[0-9]Z", "level": "(info|warning)", "run_id": "run-cli000001"'
  check_absent "the API token appears nowhere in the log" \
    "${work}/cli-stderr.txt" "${TOKEN}"
  check_grep "and the place it would have leaked shows the redaction instead" \
    "${work}/cli-stderr.txt" 'upstream credentials rejected for token \*\*\*redacted\*\*\*'

  # A second run of the same command must change nothing at all.
  (cd "${run_dir}" && PIPELINE_API_TOKEN="${TOKEN}" "${python_bin}" \
    "${lab_dir}/examples/pipeline.py" \
    --base-url "http://127.0.0.1:${port}" \
    --sources alpha,bravo,charlie \
    --report-at 2026-08-16T12:00:00Z \
    --window-hours 12 \
    --run-id run-cli000002 \
    --fixed-clock \
    > "${work}/cli-stdout-2.txt" 2> "${work}/cli-stderr-2.txt")
  second_status=$?
  check_eq "the second run also exits 3" "3" "${second_status}"
  checks=$((checks + 1))
  if diff -q "${work}/cli-stdout.txt" "${work}/cli-stdout-2.txt" >/dev/null 2>&1; then
    echo "  ok: the second run's report is byte-for-byte identical"
  else
    echo "  FAIL: the second run's report differs"
    diff "${work}/cli-stdout.txt" "${work}/cli-stdout-2.txt" | head -8 | sed 's/^/        /'
    failures=$((failures + 1))
  fi
  check_grep "and it inserted nothing, because everything was already held" \
    "${work}/cli-stderr-2.txt" '"event": "stage.store", "considered": 7, "inserted": 0, "duplicates_skipped": 7, "total_rows": 6'

  # The runs table is the record that makes a bad backfill undoable.
  runs="$("${python_bin}" - "${run_dir}/pipeline.db" <<'PY'
import sqlite3
import sys

connection = sqlite3.connect(sys.argv[1])
rows = connection.execute(
    "SELECT run_id, status, records_inserted, records_duplicate FROM runs ORDER BY run_id"
).fetchall()
for row in rows:
    print("RUN", *row)
owners = connection.execute(
    "SELECT ingested_by_run, count(*) FROM readings GROUP BY ingested_by_run ORDER BY 1"
).fetchall()
for row in owners:
    print("OWNER", *row)
connection.close()
PY
)"
  printf '%s\n' "${runs}" > "${work}/runs.txt"
  check_grep "the first run's row records six inserts" \
    "${work}/runs.txt" '^RUN run-cli000001 partial_success 6 1$'
  check_grep "the second run's row records none" \
    "${work}/runs.txt" '^RUN run-cli000002 partial_success 0 7$'
  check_grep "and every stored row still names the run that wrote it" \
    "${work}/runs.txt" '^OWNER run-cli000001 6$'

  # Point it at nothing at all: no source answers, and that is a failure, not
  # a partial success.
  (cd "${run_dir}" && PIPELINE_API_TOKEN="${TOKEN}" "${python_bin}" \
    "${lab_dir}/examples/pipeline.py" \
    --base-url "http://127.0.0.1:${port}" \
    --sources delta \
    --report-at 2026-08-16T12:00:00Z \
    --run-id run-cli000003 \
    --fixed-clock \
    > "${work}/cli-stdout-3.txt" 2> "${work}/cli-stderr-3.txt")
  third_status=$?
  check_eq "a run where no source answers exits 1, not 3" "1" "${third_status}"
  check_grep "and says so at error level" \
    "${work}/cli-stderr-3.txt" '"level": "error", "run_id": "run-cli000003", "event": "run.end", "status": "failure"'
  check_grep "a 404 source is attempted once, not three times" \
    "${work}/cli-stderr-3.txt" '"event": "stage.ingest", "sources_ok": 0, "sources_failed": 1, "failed_sources": \["delta"\], "records_fetched": 0, "attempts_total": 1'
fi

# ---------------------------------------------------------------------------
echo
echo "8. The starter — a skeleton that runs, and nine reachable exercises"
# ---------------------------------------------------------------------------
(cd "${lab_dir}" && "${pytest_bin}" starter -q > "${work}/starter.txt" 2>&1)
starter_status=$?
check_eq "pytest starter exits 0 on the unmodified skeleton" "0" "${starter_status}"
check_grep "one baseline test passes and nine exercises wait" \
  "${work}/starter.txt" '1 passed, 9 skipped'

exercise_markers="$(grep -c 'EXERCISE [0-9]' "${lab_dir}/starter/stages.py")"
check_eq "stages.py carries ten exercise markers (stage 3 has two parts)" "10" "${exercise_markers}"
named_tests="$(grep -c '^@exercise(' "${lab_dir}/starter/test_stages.py")"
check_eq "and each has a test that names it" "9" "${named_tests}"

(cd "${lab_dir}" && DAY098_SOLUTION=1 "${pytest_bin}" starter -q > "${work}/solved.txt" 2>&1)
solved_status=$?
check_eq "the completed reference passes the same suite" "0" "${solved_status}"
check_grep "all ten tests pass against examples/stages_solved.py" \
  "${work}/solved.txt" '10 passed'

# ---------------------------------------------------------------------------
echo
echo "9. Captured output still matches a live run"
# ---------------------------------------------------------------------------
# Compare a capture against a live run. The optional third argument is a sed
# expression applied to BOTH sides first, for the one capture that legitimately
# contains a duration: pytest prints "in 0.64s", and asserting on a stopwatch is
# how a suite becomes flaky on somebody else's machine.
compare() {
  local name="$1" live="$2" normalise="${3:-}"
  local stored="${lab_dir}/expected-output/${name}"
  checks=$((checks + 1))
  if [ ! -f "${stored}" ]; then
    echo "  FAIL: expected-output/${name} is missing"
    failures=$((failures + 1))
  else
    local a="${work}/cmp-stored-${name}" b="${work}/cmp-live-${name}"
    if [ -n "${normalise}" ]; then
      sed "${normalise}" "${stored}" > "${a}"
      sed "${normalise}" "${live}" > "${b}"
    else
      cp "${stored}" "${a}"
      cp "${live}" "${b}"
    fi
    if diff -q "${a}" "${b}" >/dev/null 2>&1; then
      echo "  ok: expected-output/${name} matches this run"
    else
      echo "  FAIL: expected-output/${name} differs from this run"
      diff "${a}" "${b}" | head -12 | sed 's/^/        /'
      failures=$((failures + 1))
    fi
  fi
}
compare "demo.txt" "${work}/demo.txt"
compare "config-provenance.txt" "${work}/provenance.txt"
compare "starter-progress.txt" "${work}/starter.txt" 's/ in [0-9.]*s$/ in <duration>/'
if [ -n "${port}" ]; then
  cat "${work}/cli-stdout.txt" > "${work}/cli-run.txt"
  echo "--- structured log (stderr) ---" >> "${work}/cli-run.txt"
  cat "${work}/cli-stderr.txt" >> "${work}/cli-run.txt"
  compare "cli-run.txt" "${work}/cli-run.txt"
fi

# ---------------------------------------------------------------------------
echo
echo "10. Hygiene — offline, self-contained, leaving nothing behind"
# ---------------------------------------------------------------------------
"${python_bin}" - "${lab_dir}" > "${work}/hygiene.txt" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
skip = {".venv", "__pycache__", ".pytest_cache"}
urls, sudo_lines = set(), []
comment = re.compile(r"^\s*(#|--)")
for path in sorted(root.rglob("*")):
    if not path.is_file() or path.suffix not in {".py", ".sh", ".ini", ".toml"}:
        continue
    if skip & set(path.parts):
        continue
    for number, line in enumerate(
        path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
    ):
        for url in re.findall(r"https?://[^\s\"')]+", line):
            urls.add(url)
        if re.search(r"(^|[;|&(]\s*)sudo\s", line) and not comment.match(line):
            sudo_lines.append(f"{path.name}:{number}")
offsite = sorted(u for u in urls if not u.startswith("http://127.0.0.1"))
print("OFFSITE " + " ".join(offsite))
print("SUDO " + " ".join(sudo_lines))
PY
check_eq "every URL in this lab points at 127.0.0.1 and nowhere else" "OFFSITE" \
  "$(grep '^OFFSITE ' "${work}/hygiene.txt" | sed 's/ *$//')"
check_eq "no line in this lab would actually invoke sudo" "SUDO" \
  "$(grep '^SUDO ' "${work}/hygiene.txt" | sed 's/ *$//')"

check "no captured output leaks an absolute home path" \
  "$(grep -rl '/Users/\|/home/' "${lab_dir}/expected-output" >/dev/null 2>&1 && echo no || echo yes)"
check "this suite created no database file inside the lab directory" \
  "$(find "${lab_dir}" -name '*.db' -not -path '*/.venv/*' | grep -q . && echo no || echo yes)"
check "and left no __pycache__ behind" \
  "$(find "${lab_dir}" -type d -name '__pycache__' -not -path '*/.venv/*' | grep -q . && echo no || echo yes)"
check "the fixture server binds 127.0.0.1 on port 0, never a fixed port" \
  "$(grep -q '("127.0.0.1", 0)' "${lab_dir}/examples/fixture_server.py" && echo yes || echo no)"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
