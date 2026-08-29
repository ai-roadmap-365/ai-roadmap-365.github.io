#!/usr/bin/env bash
# Tests for the Day 081 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This suite proves the operational properties of a scheduled job WITHOUT
# scheduling anything. In particular, section 8 asserts the safety rule this
# lab is built around: nothing was installed into any real scheduler, and no
# background process was left running.
#
# The two checks worth reading first:
#
#   * "a second run under a held lock exits 75 and does no work" starts a
#     helper that takes the lock, waits for it to report READY, and then runs
#     the real job. The helper is always waited for, so the suite cannot leave
#     a process behind;
#   * "a hung job is killed by the timeout" runs a job that asks to sleep for
#     30 seconds with a 1-second budget, asserts exit 124, and asserts the
#     whole thing finished in under 10 seconds.
#
# No network, non-interactive, deterministic. Exits 0 only if every check
# passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0
helper_pid=""
work_dir=""

cleanup() {
  # Never leave anything running or lying about, whatever happened above.
  if [ -n "${helper_pid}" ] && kill -0 "${helper_pid}" 2>/dev/null; then
    kill "${helper_pid}" 2>/dev/null
    wait "${helper_pid}" 2>/dev/null
  fi
  [ -n "${work_dir}" ] && [ -d "${work_dir}" ] && rm -rf "${work_dir}"
  return 0
}
trap cleanup EXIT INT TERM

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

# Resolve pytest: an explicit override, then this lab's .venv, then whatever
# is on PATH. Fails loudly with instructions rather than silently skipping.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install it with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest: PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

python_bin="$(command -v python3 || true)"
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi

work_dir="$(mktemp -d "${TMPDIR:-/tmp}/day081.XXXXXX")"

echo "Day 081 — A Job That Survives Being Ignored"
echo

# --------------------------------------------------------------------------
echo "1. The tools"
# --------------------------------------------------------------------------

version_line="$("${pytest_bin}" --version 2>&1 | head -1)"
case "${version_line}" in
  pytest*) check "pytest --version reports a pytest ( ${version_line} )" "yes" ;;
  *) check "pytest --version reports a pytest ( ${version_line} )" "no" ;;
esac

if "${python_bin}" -c "import fcntl, sched, signal, zoneinfo" 2>/dev/null; then
  check "fcntl, sched, signal and zoneinfo are all standard library — nothing to install" "yes"
else
  check "fcntl, sched, signal and zoneinfo are all standard library" "no"
fi

# --------------------------------------------------------------------------
echo
echo "2. The reference suite"
# --------------------------------------------------------------------------

examples_out="$(cd "${lab_dir}" && "${pytest_bin}" examples -q -p no:cacheprovider 2>&1)"
examples_exit=$?
if [ "${examples_exit}" -eq 0 ]; then
  check "pytest examples exits 0" "yes"
else
  check "pytest examples exits 0 (got ${examples_exit})" "no"
  echo "${examples_out}" | tail -25
fi
case "${examples_out}" in
  *"61 passed"*) check "pytest examples reports 61 passed" "yes" ;;
  *) check "pytest examples reports 61 passed (got: $(printf '%s' "${examples_out}" | tail -1))" "no" ;;
esac

# The suite must run fast, because everything slow in it was injected away.
suite_seconds="$(printf '%s\n' "${examples_out}" | sed -n 's/.* in \([0-9.]*\)s.*/\1/p' | tail -1)"
if [ -n "${suite_seconds}" ] && "${python_bin}" -c "import sys; sys.exit(0 if float('${suite_seconds}') < 10 else 1)"; then
  check "the whole suite runs in ${suite_seconds}s — nothing in it waits for a schedule" "yes"
else
  check "the whole suite runs in under 10s (got ${suite_seconds:-unknown}s)" "no"
fi

# --------------------------------------------------------------------------
echo
echo "3. Idempotence — running it twice leaves exactly one result"
# --------------------------------------------------------------------------

out_dir="${work_dir}/out"
run_one="$(cd "${lab_dir}" && "${python_bin}" examples/job.py \
  --now 2026-07-20T02:30:00+00:00 run --output-dir "${out_dir}" \
  --log-file "${out_dir}/job.log" 2>&1)"
first_exit=$?
run_two="$(cd "${lab_dir}" && "${python_bin}" examples/job.py \
  --now 2026-07-20T02:35:00+00:00 run --output-dir "${out_dir}" \
  --log-file "${out_dir}/job.log" 2>&1)"
second_exit=$?

[ "${first_exit}" -eq 0 ] \
  && check "the first run exits 0" "yes" \
  || check "the first run exits 0 (got ${first_exit})" "no"
[ "${second_exit}" -eq 0 ] \
  && check "the second run also exits 0 — an idempotent no-op is a success" "yes" \
  || check "the second run also exits 0 (got ${second_exit})" "no"

case "${run_one}" in
  *'"action": "written"'*) check "the first run reports action=written" "yes" ;;
  *) check "the first run reports action=written" "no" ;;
esac
case "${run_two}" in
  *'"action": "skipped"'*) check "the second run reports action=skipped — it did NOT redo the work" "yes" ;;
  *) check "the second run reports action=skipped" "no" ;;
esac

report_count="$(find "${out_dir}" -maxdepth 1 -name 'report-*.json' | wc -l | tr -d ' ')"
if [ "${report_count}" -eq 1 ]; then
  check "two runs produced exactly one report file" "yes"
else
  check "two runs produced exactly one report file (got ${report_count})" "no"
fi

# The second run must not have rewritten the file: its timestamp is the first's.
if "${python_bin}" -c "
import json, sys
payload = json.load(open('${out_dir}/report-2026-07-19.json'))
sys.exit(0 if payload['generated_at'] == '2026-07-20T02:30:00+00:00'
         and payload['reading_count'] == 6 else 1)
"; then
  check "the report still carries the FIRST run's timestamp and 6 readings" "yes"
else
  check "the report still carries the first run's timestamp and 6 readings" "no"
fi

partials="$(find "${out_dir}" -maxdepth 1 -name '*.partial*' | wc -l | tr -d ' ')"
if [ "${partials}" -eq 0 ]; then
  check "no partial files were left behind (the write was atomic)" "yes"
else
  check "no partial files were left behind (found ${partials})" "no"
fi

log_lines="$(wc -l < "${out_dir}/job.log" | tr -d ' ')"
if [ "${log_lines}" -eq 2 ]; then
  check "the log has one JSON line per run (2 lines for 2 runs)" "yes"
else
  check "the log has one JSON line per run (got ${log_lines})" "no"
fi
if "${python_bin}" -c "
import json, sys
lines = open('${out_dir}/job.log').read().strip().splitlines()
events = [json.loads(line) for line in lines]
needed = {'job','run_id','status','exit_code','started_at','finished_at','duration_seconds'}
sys.exit(0 if all(needed <= set(e) for e in events) else 1)
"; then
  check "every log line carries job, run_id, status, exit_code, times and duration" "yes"
else
  check "every log line carries job, run_id, status, exit_code, times and duration" "no"
fi

# --------------------------------------------------------------------------
echo
echo "4. Overlap — a second run under a held lock refuses to start"
# --------------------------------------------------------------------------

lock_path="${out_dir}/daily-report.lock"
helper_fifo="${work_dir}/helper.out"
# Started as a direct child (no subshell) so that ${helper_pid} really is the
# python process and `kill` reaches it rather than a wrapper.
"${python_bin}" "${lab_dir}/examples/hold_lock.py" "${lock_path}" 6 > "${helper_fifo}" 2>&1 &
helper_pid=$!

# Wait for READY rather than sleeping a fixed time.
ready="no"
for _ in $(seq 1 100); do
  if [ -s "${helper_fifo}" ] && grep -q READY "${helper_fifo}" 2>/dev/null; then
    ready="yes"
    break
  fi
  "${python_bin}" -c "import time; time.sleep(0.05)"
done
check "the lock helper took the lock and reported READY" "${ready}"

locked_out="$(cd "${lab_dir}" && "${python_bin}" examples/job.py \
  --now 2026-07-21T02:30:00+00:00 run --output-dir "${out_dir}" \
  --date 2026-07-20 --lock-file "${lock_path}" 2>&1)"
locked_exit=$?

if [ "${locked_exit}" -eq 75 ]; then
  check "a run under a held lock exits 75 (EX_TEMPFAIL), not 0 and not 1" "yes"
else
  check "a run under a held lock exits 75 (got ${locked_exit})" "no"
fi
case "${locked_out}" in
  *'"status": "already-running"'*) check "it logs status=already-running" "yes" ;;
  *) check "it logs status=already-running" "no" ;;
esac
if [ ! -f "${out_dir}/report-2026-07-20.json" ]; then
  check "the refused run did NOT do the work — no report for 2026-07-20" "yes"
else
  check "the refused run did NOT do the work" "no"
fi

# Stop the helper and reap it. Nothing is left running.
kill "${helper_pid}" 2>/dev/null
wait "${helper_pid}" 2>/dev/null
sleep_probe=0
while kill -0 "${helper_pid}" 2>/dev/null && [ "${sleep_probe}" -lt 40 ]; do
  "${python_bin}" -c "import time; time.sleep(0.05)"
  sleep_probe=$((sleep_probe + 1))
done
if kill -0 "${helper_pid}" 2>/dev/null; then
  check "the lock helper is gone once the check finishes" "no"
else
  check "the lock helper is gone once the check finishes" "yes"
fi
helper_pid=""

# And the lock is usable again immediately afterwards.
after_out="$(cd "${lab_dir}" && "${python_bin}" examples/job.py \
  --now 2026-07-21T02:30:00+00:00 run --output-dir "${out_dir}" \
  --date 2026-07-20 --lock-file "${lock_path}" 2>&1)"
after_exit=$?
if [ "${after_exit}" -eq 0 ] && [ -f "${out_dir}/report-2026-07-20.json" ]; then
  check "once the holder exits, the next run takes the lock and does the work" "yes"
else
  check "once the holder exits, the next run takes the lock and does the work (exit ${after_exit})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "5. Timeouts — a hung job is killed, and does not block the next run"
# --------------------------------------------------------------------------

hang_start="$(date +%s)"
hang_out="$(cd "${lab_dir}" && "${python_bin}" examples/job.py \
  --now 2026-07-22T02:30:00+00:00 run --output-dir "${out_dir}" \
  --date 2026-07-17 --lock-file "${out_dir}/hang.lock" \
  --simulate-hang 30 --timeout 1 2>&1)"
hang_exit=$?
hang_elapsed=$(( $(date +%s) - hang_start ))

if [ "${hang_exit}" -eq 124 ]; then
  check "a job that hangs for 30s with a 1s budget exits 124, as GNU timeout does" "yes"
else
  check "a job that hangs for 30s with a 1s budget exits 124 (got ${hang_exit})" "no"
fi
if [ "${hang_elapsed}" -lt 10 ]; then
  check "it was killed after about a second, not after thirty (took ${hang_elapsed}s)" "yes"
else
  check "it was killed after about a second (took ${hang_elapsed}s)" "no"
fi
case "${hang_out}" in
  *'"error": "JobTimeout"'*) check "the timeout is logged as JobTimeout with its budget" "yes" ;;
  *) check "the timeout is logged as JobTimeout with its budget" "no" ;;
esac
if [ ! -f "${out_dir}/report-2026-07-17.json" ]; then
  check "the timed-out run produced no output" "yes"
else
  check "the timed-out run produced no output" "no"
fi

# The stronger form: supervise a child process and kill its whole group.
#
# The child is a uniquely named symlink to sleep rather than plain `sleep 30`.
# The orphan check below is a pattern match over the whole process table, so a
# generic name would match any unrelated process on the machine that happens to
# be sleeping — the check would then fail for reasons having nothing to do with
# this lab. The name carries this harness's own pid, so it can only match the
# child we started.
probe_name="day081-probe-sleep-$$"
probe_path="${work_dir}/${probe_name}"
ln -s "$(command -v sleep)" "${probe_path}"
sup_start="$(date +%s)"
(cd "${lab_dir}" && "${python_bin}" examples/supervise.py --timeout 1 -- "${probe_path}" 30 >/dev/null 2>&1)
sup_exit=$?
sup_elapsed=$(( $(date +%s) - sup_start ))
if [ "${sup_exit}" -eq 124 ] && [ "${sup_elapsed}" -lt 10 ]; then
  check "supervise.py kills an overrunning child process group and exits 124" "yes"
else
  check "supervise.py kills an overrunning child (exit ${sup_exit}, ${sup_elapsed}s)" "no"
fi
if pgrep -f "${probe_name}" >/dev/null 2>&1; then
  check "no supervised child survived the supervisor" "no"
else
  check "no supervised child survived the supervisor" "yes"
fi

# --------------------------------------------------------------------------
echo
echo "6. The watchdog — alerting on silence"
# --------------------------------------------------------------------------

heartbeat="${out_dir}/daily-report.heartbeat.json"
if [ -f "${heartbeat}" ]; then
  check "a successful run wrote a heartbeat" "yes"
else
  check "a successful run wrote a heartbeat" "no"
fi

(cd "${lab_dir}" && "${python_bin}" examples/job.py --now 2026-07-21T09:00:00+00:00 \
  watch --heartbeat-file "${heartbeat}" --max-age-minutes 1560 >/dev/null 2>&1)
fresh_exit=$?
[ "${fresh_exit}" -eq 0 ] \
  && check "the watchdog is quiet while the job is running (exit 0)" "yes" \
  || check "the watchdog is quiet while the job is running (got ${fresh_exit})" "no"

stale_out="$(cd "${lab_dir}" && "${python_bin}" examples/job.py --now 2026-08-01T09:00:00+00:00 \
  watch --heartbeat-file "${heartbeat}" --max-age-minutes 1560 2>&1)"
stale_exit=$?
if [ "${stale_exit}" -eq 1 ]; then
  check "eleven days later, with no run at all, the watchdog alerts (exit 1)" "yes"
else
  check "eleven days later the watchdog alerts (got ${stale_exit})" "no"
fi
case "${stale_out}" in
  *"stopped running"*) check "the alert says the job has stopped running" "yes" ;;
  *) check "the alert says the job has stopped running (got: ${stale_out})" "no" ;;
esac

missing_exit=0
(cd "${lab_dir}" && "${python_bin}" examples/job.py --now 2026-07-21T09:00:00+00:00 \
  watch --heartbeat-file "${work_dir}/never.json" >/dev/null 2>&1) || missing_exit=$?
[ "${missing_exit}" -eq 1 ] \
  && check "a job that has never succeeded also alerts" "yes" \
  || check "a job that has never succeeded also alerts (got ${missing_exit})" "no"

# --------------------------------------------------------------------------
echo
echo "7. The schedule files say what they claim"
# --------------------------------------------------------------------------

gen_out="$(cd "${lab_dir}" && "${python_bin}" examples/gen_schedules.py \
  --out "${work_dir}/schedules" --hour 2 --minute 30 2>&1)"
gen_exit=$?
[ "${gen_exit}" -eq 0 ] \
  && check "gen_schedules.py exits 0" "yes" \
  || check "gen_schedules.py exits 0 (got ${gen_exit})" "no"

for suffix in cron plist service timer; do
  if [ -s "${work_dir}/schedules/com.example.dailyreport.${suffix}" ]; then
    check "it wrote a non-empty .${suffix} file" "yes"
  else
    check "it wrote a non-empty .${suffix} file" "no"
  fi
done

case "${gen_out}" in
  *"NOTHING was installed"*) check "the generator states plainly that it installed nothing" "yes" ;;
  *) check "the generator states plainly that it installed nothing" "no" ;;
esac

if "${python_bin}" -c "
import sys
sys.path.insert(0, '${lab_dir}/examples')
import datetime as dt
from cronexpr import parse
line = [l for l in open('${work_dir}/schedules/com.example.dailyreport.cron')
        if l.strip() and not l.startswith('#') and ' ' in l and l.split()[0].isdigit()]
schedule = parse(' '.join(line[0].split()[:5]))
base = dt.datetime(2026, 7, 19, 0, 0, tzinfo=dt.timezone.utc)
first = schedule.next_run_after(base)
second = schedule.next_run_after(first)
sys.exit(0 if (first == dt.datetime(2026, 7, 19, 2, 30, tzinfo=dt.timezone.utc)
               and second == dt.datetime(2026, 7, 20, 2, 30, tzinfo=dt.timezone.utc)) else 1)
"; then
  check "the generated cron line parses to 02:30 daily, as intended" "yes"
else
  check "the generated cron line parses to 02:30 daily, as intended" "no"
fi

if grep -q 'PATH=/usr/local/bin:/usr/bin:/bin' "${work_dir}/schedules/com.example.dailyreport.cron" \
   && grep -q '^SHELL=' "${work_dir}/schedules/com.example.dailyreport.cron"; then
  check "the cron file sets PATH and SHELL explicitly — cron supplies almost nothing" "yes"
else
  check "the cron file sets PATH and SHELL explicitly" "no"
fi
if grep -q 'Persistent=true' "${work_dir}/schedules/com.example.dailyreport.timer"; then
  check "the systemd timer sets Persistent=true for catch-up after downtime" "yes"
else
  check "the systemd timer sets Persistent=true" "no"
fi
if grep -q '<key>RunAtLoad</key>' "${work_dir}/schedules/com.example.dailyreport.plist"; then
  check "the launchd plist declares RunAtLoad so loading does not mean running" "yes"
else
  check "the launchd plist declares RunAtLoad" "no"
fi

# --------------------------------------------------------------------------
echo
echo "8. SAFETY — nothing was installed, nothing was left running"
# --------------------------------------------------------------------------

# 8a. No lab code executes a scheduler command. This is the structural
#     guarantee: the install commands exist only as text to be read.
#     (This runner reads `crontab -l` in 8b, which is read-only and is the
#     check itself, so tests/ is deliberately outside the scan.)
if grep -rnE '(subprocess\.[A-Za-z_]+|os\.system|os\.exec[a-z]*)[^\n]*(crontab|launchctl|systemctl)' \
     "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null >/dev/null; then
  check "no learner-facing file executes crontab, launchctl or systemctl" "no"
else
  check "no learner-facing file executes crontab, launchctl or systemctl" "yes"
fi

# 8b. The user's real crontab does not contain this lab's job.
if command -v crontab >/dev/null 2>&1; then
  real_crontab="$(crontab -l 2>/dev/null || true)"
  case "${real_crontab}" in
    *dailyreport*|*"examples/job.py"*)
      check "the real crontab contains no entry from this lab" "no" ;;
    *) check "the real crontab contains no entry from this lab" "yes" ;;
  esac
else
  check "crontab is not installed here, so nothing could have been added to it" "yes"
fi

# 8c. No launchd agent and no systemd user unit was installed.
agents="${HOME}/Library/LaunchAgents"
if [ -d "${agents}" ] && ls "${agents}" 2>/dev/null | grep -q 'com.example.dailyreport'; then
  check "no launchd agent named com.example.dailyreport exists in the user's LaunchAgents" "no"
else
  check "no launchd agent named com.example.dailyreport exists in the user's LaunchAgents" "yes"
fi

units="${HOME}/.config/systemd/user"
if [ -d "${units}" ] && ls "${units}" 2>/dev/null | grep -q 'com.example.dailyreport'; then
  check "no systemd user unit named com.example.dailyreport was installed" "no"
else
  check "no systemd user unit named com.example.dailyreport was installed" "yes"
fi

# 8d. Nothing from this lab is still running.
if pgrep -f 'hold_lock.py' >/dev/null 2>&1; then
  check "no hold_lock.py process survived the suite" "no"
else
  check "no hold_lock.py process survived the suite" "yes"
fi
if pgrep -f 'examples/job.py' >/dev/null 2>&1; then
  check "no job.py process survived the suite" "no"
else
  check "no job.py process survived the suite" "yes"
fi

# 8e. The lab wrote nothing outside its own directory and the temporary one.
if [ -z "$(find "${lab_dir}" -maxdepth 1 -name 'report-*.json' 2>/dev/null)" ]; then
  check "no report file was left in the lab directory itself" "yes"
else
  check "no report file was left in the lab directory itself" "no"
fi

# --------------------------------------------------------------------------
echo
echo "9. The starter is runnable before you start"
# --------------------------------------------------------------------------

starter_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
starter_exit=$?
if [ "${starter_exit}" -eq 0 ]; then
  check "pytest starter exits 0 with the exercises unfinished" "yes"
else
  check "pytest starter exits 0 with the exercises unfinished (got ${starter_exit})" "no"
  echo "${starter_out}" | tail -15
fi
case "${starter_out}" in
  *"1 passed, 8 skipped"*) check "the starter has 1 worked test and 8 skipped exercises" "yes" ;;
  *) check "the starter has 1 worked test and 8 skipped exercises" "no" ;;
esac

for heading in "Exercise 5" "Exercise 6" "5a." "6b." "6c."; do
  if grep -q "${heading}" "${lab_dir}/starter/NOTES.md"; then
    check "NOTES.md asks the '${heading}' question" "yes"
  else
    check "NOTES.md asks the '${heading}' question" "no"
  fi
done

# --------------------------------------------------------------------------
echo
echo "10. Nothing here reaches the network"
# --------------------------------------------------------------------------

if grep -rqE '^\s*(import|from)\s+(socket|urllib|http|requests|ftplib|smtplib)\b' \
     "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null; then
  check "no networking module is imported anywhere in examples/ or starter/" "no"
else
  check "no networking module is imported anywhere in examples/ or starter/" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
