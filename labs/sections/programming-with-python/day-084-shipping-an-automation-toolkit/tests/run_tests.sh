#!/usr/bin/env bash
# Tests for the Day 084 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This suite checks the OPERATIONAL properties of an automation, not its happy
# path. The happy path is one check out of the whole file. The rest ask the
# questions that decide whether a tool can be left running unattended:
#
#   * does running it twice process each item once?
#   * does one broken item get skipped and REPORTED while the others succeed —
#     and does the exit code say "partial", not "fine"?
#   * does --dry-run leave the state file byte-identical?
#   * does the four-layer configuration precedence actually resolve that way?
#   * does a secret supplied in the environment stay out of the log? (This is
#     the leak check, and it is the most important assertion in the lab.)
#   * does an interrupted state write leave the previous state intact?
#   * does the INSTALLED console script run?
#
# Nothing here touches the internet. A fixture server is started on 127.0.0.1
# on an ephemeral port, waited for, and killed in a trap. Nothing is installed
# into any real scheduler and no background process outlives this script.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0
server_pid=""
work_root=""

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

cleanup() {
  if [ -n "${server_pid}" ] && kill -0 "${server_pid}" 2>/dev/null; then
    kill "${server_pid}" 2>/dev/null || true
    wait "${server_pid}" 2>/dev/null || true
  fi
  [ -n "${work_root}" ] && [ -d "${work_root}" ] && rm -rf "${work_root}"
}
trap cleanup EXIT INT TERM

# Resolve tools: an explicit override, then this lab's .venv, then PATH.
# Fails loudly with instructions rather than silently skipping a check.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

install_hint() {
  echo "  Install this lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  install_hint
  echo "  Or point this suite at an existing pytest: PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}
python_bin="$(resolve_tool python "${PYTHON:-}")" || python_bin="$(command -v python3 || true)"
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi
pip_bin="$(resolve_tool pip "${PIP:-}")" || {
  echo "FAIL: pip not found." >&2
  install_hint
  exit 1
}

if ! "${python_bin}" -c "import requests" >/dev/null 2>&1; then
  echo "FAIL: the 'requests' package is not importable by ${python_bin}." >&2
  install_hint
  exit 1
fi

work_root="$(mktemp -d "${TMPDIR:-/tmp}/feedkit-tests.XXXXXX")"

# The secret. Invented here, used for real (the fixture server rejects any
# request without it), and never written to any file in this repository.
export FEEDKIT_TEST_TOKEN="lab-token-9f2b7c41d0"

echo "Day 084 — Ship the Toolkit"
echo

# --------------------------------------------------------------------------
echo "1. The local fixture server (127.0.0.1, ephemeral port, no internet)"
# --------------------------------------------------------------------------

server_out="${work_root}/server.port"
"${python_bin}" "${lab_dir}/tests/fixture_server.py" --token "${FEEDKIT_TEST_TOKEN}" \
  > "${server_out}" 2>"${work_root}/server.err" &
server_pid=$!

# Wait for readiness by polling, not by sleeping a fixed time. A fixed sleep is
# either too short on a slow machine or wasted time on a fast one.
port=""
for _ in $(seq 1 100); do
  if [ -s "${server_out}" ]; then
    port="$(head -1 "${server_out}" | tr -d '[:space:]')"
    [ -n "${port}" ] && break
  fi
  sleep 0.05
done

if [ -n "${port}" ]; then
  check "the fixture server chose an ephemeral port (${port}, not a hard-coded one)" "yes"
else
  check "the fixture server started and reported its port" "no"
  echo "${checks} checks, ${failures} failure(s)."
  exit 1
fi

export FEEDKIT_TEST_BASE_URL="http://127.0.0.1:${port}"
export FEEDKIT_BASE_URL="${FEEDKIT_TEST_BASE_URL}"

ready="no"
for _ in $(seq 1 100); do
  if "${python_bin}" - "${port}" <<'PY' >/dev/null 2>&1
import sys, urllib.request
port = sys.argv[1]
with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
    sys.exit(0 if response.read() == b"ok" else 1)
PY
  then ready="yes"; break; fi
  sleep 0.05
done
check "the fixture server answers /health before any test runs" "${ready}"

auth_status="$("${python_bin}" - "${port}" <<'PY'
import sys, urllib.error, urllib.request
port = sys.argv[1]
try:
    urllib.request.urlopen(f"http://127.0.0.1:{port}/feed/notes.json", timeout=2)
    print("200")
except urllib.error.HTTPError as exc:
    print(exc.code)
PY
)"
if [ "${auth_status}" = "401" ]; then
  check "the fixture server really requires the token (401 without it)" "yes"
else
  check "the fixture server really requires the token (got ${auth_status})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "2. The property suite (pytest over examples/src/feedkit)"
# --------------------------------------------------------------------------

pytest_out="$(cd "${lab_dir}" && "${pytest_bin}" tests/test_toolkit.py -q 2>&1)"
pytest_exit=$?
if [ "${pytest_exit}" -eq 0 ]; then
  check "the property suite passes (exit 0)" "yes"
else
  check "the property suite passes (exit ${pytest_exit})" "no"
  echo "${pytest_out}" | tail -30
fi
pytest_tail="$(printf '%s\n' "${pytest_out}" | grep -E '[0-9]+ passed' | tail -1)"
case "${pytest_tail}" in
  *passed*) check "pytest reports: ${pytest_tail}" "yes" ;;
  *) check "pytest reports a passed count" "no" ;;
esac

# The suite must not be vacuous: break the idempotence rule and demand red.
broken_src="${work_root}/broken-src"
mkdir -p "${broken_src}"
cp -R "${lab_dir}/examples/src/feedkit" "${broken_src}/feedkit"
"${python_bin}" - "${broken_src}/feedkit/core.py" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1])
text = path.read_text()
old = "fresh = [entry for entry in entries if entry.id not in already]"
new = "fresh = list(entries)  # deliberately broken: ignores what has been seen"
assert old in text, "the line to break was not found"
path.write_text(text.replace(old, new))
PY
broken_out="$(cd "${lab_dir}" && FEEDKIT_SRC="${broken_src}" "${pytest_bin}" \
  tests/test_toolkit.py -q -p no:cacheprovider 2>&1)"
broken_exit=$?
if [ "${broken_exit}" -ne 0 ]; then
  check "breaking the idempotence rule makes the suite FAIL (exit ${broken_exit})" "yes"
else
  check "breaking the idempotence rule makes the suite FAIL — it did not, so the suite is vacuous" "no"
fi
case "${broken_out}" in
  *test_running_fetch_twice_processes_each_entry_once*)
    check "the failing run names the idempotence test" "yes" ;;
  *) check "the failing run names the idempotence test" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "3. The command line, end to end, as a real process"
# --------------------------------------------------------------------------

run_dir="${work_root}/run"
mkdir -p "${run_dir}"
cp "${lab_dir}/examples/feedkit.toml" "${run_dir}/feedkit.toml"

feedkit() {
  (cd "${run_dir}" && PYTHONPATH="${lab_dir}/examples/src" \
     FEEDKIT_TOKEN="${FEEDKIT_TEST_TOKEN}" \
     "${python_bin}" -m feedkit.cli "$@")
}

first_log="${work_root}/fetch-1.log"
feedkit --log-level info fetch > "${first_log}" 2>&1
first_exit=$?
if [ "${first_exit}" -eq 0 ]; then
  check "a first fetch of three good sources exits 0" "yes"
else
  check "a first fetch of three good sources exits 0 (got ${first_exit})" "no"
  tail -20 "${first_log}"
fi
if grep -q 'new entries: 7' "${first_log}"; then
  check "the first run collects 7 entries from notes, links and papers" "yes"
else
  check "the first run collects 7 entries from notes, links and papers" "no"
fi

second_log="${work_root}/fetch-2.log"
feedkit fetch > "${second_log}" 2>&1
second_exit=$?
if [ "${second_exit}" -eq 0 ] && grep -q 'new entries: 0' "${second_log}"; then
  check "running fetch again collects 0 new entries and exits 0 (idempotence)" "yes"
else
  check "running fetch again collects 0 new entries and exits 0 (idempotence)" "no"
  tail -10 "${second_log}"
fi

# Dry run must not write. Compare the bytes.
state_file="${run_dir}/feedkit-state.json"
before_hash="$("${python_bin}" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${state_file}")"
dry_log="${work_root}/dry.log"
feedkit --sources notes,links,papers,flaky fetch --dry-run > "${dry_log}" 2>&1
dry_exit=$?
after_hash="$("${python_bin}" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${state_file}")"
if [ "${before_hash}" = "${after_hash}" ]; then
  check "--dry-run leaves the state file byte-identical" "yes"
else
  check "--dry-run leaves the state file byte-identical" "no"
fi
if grep -q 'dry run — nothing was written' "${dry_log}"; then
  check "--dry-run says plainly that nothing was written" "yes"
else
  check "--dry-run says plainly that nothing was written" "no"
fi
if [ "${dry_exit}" -eq 0 ]; then
  check "--dry-run exits 0" "yes"
else
  check "--dry-run exits 0 (got ${dry_exit})" "no"
fi
if [ -z "$(find "${run_dir}" -name '*.tmp' -print -quit)" ]; then
  check "no temporary state files are left behind anywhere" "yes"
else
  check "no temporary state files are left behind anywhere" "no"
fi

# Partial success: one source is broken, the rest still work, exit code is 2.
partial_log="${work_root}/partial.log"
feedkit --sources notes,broken,papers fetch > "${partial_log}" 2>&1
partial_exit=$?
if [ "${partial_exit}" -eq 3 ]; then
  check "partial success exits 3, not 0 (it does not pretend everything worked)" "yes"
else
  check "partial success exits 3, not 0 (got ${partial_exit})" "no"
fi
if grep -q 'FAILED: broken' "${partial_log}"; then
  check "the failing source is named in the run summary" "yes"
else
  check "the failing source is named in the run summary" "no"
fi
if grep -q 'sources: 2 ok, 1 failed' "${partial_log}"; then
  check "the summary counts 2 ok and 1 failed" "yes"
else
  check "the summary counts 2 ok and 1 failed" "no"
fi
if grep -q '"level": "error"' "${partial_log}" && grep -q '"source": "broken"' "${partial_log}"; then
  check "the structured log records WHICH source failed, at error level" "yes"
else
  check "the structured log records WHICH source failed, at error level" "no"
fi

# Total failure: every source broken.
total_log="${work_root}/total.log"
feedkit --sources broken fetch > "${total_log}" 2>&1
total_exit=$?
if [ "${total_exit}" -eq 1 ]; then
  check "a run where every source fails exits 1" "yes"
else
  check "a run where every source fails exits 1 (got ${total_exit})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "4. The leak check — a supplied secret must never reach the log"
# --------------------------------------------------------------------------

leak_log="${work_root}/leak.log"
feedkit --log-level debug --sources notes,broken fetch > "${leak_log}" 2>&1 || true
if grep -q "${FEEDKIT_TEST_TOKEN}" "${leak_log}"; then
  check "the token supplied in FEEDKIT_TOKEN never appears in the log" "no"
else
  check "the token supplied in FEEDKIT_TOKEN never appears in the log" "yes"
fi
if grep -rq "${FEEDKIT_TEST_TOKEN}" "${run_dir}" 2>/dev/null; then
  check "the token never reaches the state file or the config file" "no"
else
  check "the token never reaches the state file or the config file" "yes"
fi
explain_log="${work_root}/explain.log"
feedkit status --explain-config > "${explain_log}" 2>&1
if grep -q "${FEEDKIT_TEST_TOKEN}" "${explain_log}"; then
  check "even --explain-config does not print the token" "no"
else
  check "even --explain-config does not print the token" "yes"
fi
if grep -q 'set (never printed)' "${explain_log}"; then
  check "--explain-config says the token is set without showing it" "yes"
else
  check "--explain-config says the token is set without showing it" "no"
fi
# And the token is genuinely required: without it every source 401s.
noauth_log="${work_root}/noauth.log"
(cd "${run_dir}" && PYTHONPATH="${lab_dir}/examples/src" \
   "${python_bin}" -m feedkit.cli --sources notes fetch > "${noauth_log}" 2>&1)
noauth_exit=$?
if [ "${noauth_exit}" -eq 1 ] && grep -q 'HTTP 401' "${noauth_log}"; then
  check "without the token every request is refused — the secret is real, not decorative" "yes"
else
  check "without the token every request is refused (exit ${noauth_exit})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "5. Configuration precedence: flag beats environment beats file beats default"
# --------------------------------------------------------------------------

prec_dir="${work_root}/precedence"
mkdir -p "${prec_dir}"
printf '[feedkit]\nmax_items = 10\n' > "${prec_dir}/feedkit.toml"

# One command, one setting, four different sources for its value. Each call
# below adds exactly one layer to the one before it, so the four assertions
# together pin the whole precedence rather than just its ends.
precedence_value() {
  local where="$1"
  shift
  (cd "${where}" && PYTHONPATH="${lab_dir}/examples/src" "${python_bin}" -m feedkit.cli \
     "$@" status --explain-config 2>/dev/null | awk '$1=="max_items"{print $2, $3}')
}

empty_dir="${work_root}/no-config"
mkdir -p "${empty_dir}"

got="$(precedence_value "${empty_dir}")"
if [ "${got}" = "5 default" ]; then
  check "layer 1: with no file, no environment and no flag, max_items is 5 (default)" "yes"
else
  check "layer 1: max_items is 5 from the default (got '${got}')" "no"
fi

got="$(precedence_value "${prec_dir}")"
if [ "${got}" = "10 file" ]; then
  check "layer 2: the configuration file beats the default (10, file)" "yes"
else
  check "layer 2: the configuration file beats the default (got '${got}')" "no"
fi

got="$(FEEDKIT_MAX_ITEMS=20 precedence_value "${prec_dir}")"
if [ "${got}" = "20 environment" ]; then
  check "layer 3: the environment beats the file (20, environment)" "yes"
else
  check "layer 3: the environment beats the file (got '${got}')" "no"
fi

got="$(FEEDKIT_MAX_ITEMS=20 precedence_value "${prec_dir}" --max-items 40)"
if [ "${got}" = "40 flag" ]; then
  check "layer 4: a flag beats the environment (40, flag) — all four confirmed" "yes"
else
  check "layer 4: a flag beats the environment (got '${got}')" "no"
fi

# An absent flag must mean "no opinion", not "override with nothing" — the bug
# that makes every default silently win over the configuration file.
got="$(precedence_value "${prec_dir}")"
if [ "${got}" = "10 file" ]; then
  check "an unsupplied flag does not override the file" "yes"
else
  check "an unsupplied flag does not override the file (got '${got}')" "no"
fi

# A typo in a config file is an error, not a shrug.
typo_dir="${work_root}/typo"
mkdir -p "${typo_dir}"
printf '[feedkit]\nmax_itmes = 10\n' > "${typo_dir}/feedkit.toml"
typo_out="$( (cd "${typo_dir}" && PYTHONPATH="${lab_dir}/examples/src" \
  "${python_bin}" -m feedkit.cli status 2>&1) )"
typo_exit=$?
if [ "${typo_exit}" -ne 0 ] && printf '%s' "${typo_out}" | grep -q "unknown setting"; then
  check "a misspelled setting in the configuration file stops the run" "yes"
else
  check "a misspelled setting in the configuration file stops the run" "no"
fi

# --------------------------------------------------------------------------
echo
echo "6. status, report, and the watchdog that notices silence"
# --------------------------------------------------------------------------

report_log="${work_root}/report.log"
feedkit report --limit 3 > "${report_log}" 2>&1
if grep -q 'entries collected; showing 3' "${report_log}"; then
  check "report renders the collected entries" "yes"
else
  check "report renders the collected entries" "no"
fi

status_log="${work_root}/status.log"
feedkit status > "${status_log}" 2>&1
status_exit=$?
if [ "${status_exit}" -eq 0 ] && grep -q 'watchdog:     fresh' "${status_log}"; then
  check "status exits 0 while the last success is recent" "yes"
else
  check "status exits 0 while the last success is recent (got ${status_exit})" "no"
fi

stale_log="${work_root}/stale.log"
feedkit status --max-age-minutes 0 > "${stale_log}" 2>&1
stale_exit=$?
if [ "${stale_exit}" -eq 3 ] && grep -q 'STALE' "${stale_log}"; then
  check "the watchdog exits non-zero when the last success is too old" "yes"
else
  check "the watchdog exits non-zero when the last success is too old (got ${stale_exit})" "no"
fi

fresh_dir="${work_root}/never-run"
mkdir -p "${fresh_dir}"
never_log="${work_root}/never.log"
(cd "${fresh_dir}" && PYTHONPATH="${lab_dir}/examples/src" "${python_bin}" -m feedkit.cli status \
   > "${never_log}" 2>&1)
never_exit=$?
if [ "${never_exit}" -eq 3 ] && grep -q 'last success: never' "${never_log}"; then
  check "a toolkit that has never run reports 'never' and exits non-zero" "yes"
else
  check "a toolkit that has never run reports 'never' and exits non-zero (got ${never_exit})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "7. Two runs must not overlap"
# --------------------------------------------------------------------------

touch "${run_dir}/feedkit-state.json.lock"
locked_log="${work_root}/locked.log"
feedkit fetch > "${locked_log}" 2>&1
locked_exit=$?
rm -f "${run_dir}/feedkit-state.json.lock"
if [ "${locked_exit}" -eq 75 ]; then
  check "a run that finds the lock held exits 75 and does nothing" "yes"
else
  check "a run that finds the lock held exits 75 (got ${locked_exit})" "no"
fi
if grep -q '"status": "locked"' "${locked_log}"; then
  check "the overlapping run says so in the log" "yes"
else
  check "the overlapping run says so in the log" "no"
fi

# --------------------------------------------------------------------------
echo
echo "8. The installed console script"
# --------------------------------------------------------------------------

# The install goes into a THROWAWAY environment under the work directory, never
# into whatever pip happens to be on PATH. Running a lab's tests must never
# install a package into the caller's environment as a side effect — and
# resolving the console script from PATH afterwards would only find it because
# of that pollution.
#
# The package is built into a wheel FIRST, using the interpreter that already
# has a build backend, and only the finished wheel is installed into the
# throwaway environment. Installing a wheel needs no build backend at all, so
# the throwaway environment can be a plain empty venv and the whole step stays
# offline. (A --system-site-packages venv would NOT help here: it inherits the
# base interpreter's site-packages, not those of the virtualenv it was created
# from, so setuptools would still be missing.)
install_env="${work_root}/install-env"
wheel_dir="${work_root}/wheels"
install_log="${work_root}/install.log"
mkdir -p "${wheel_dir}"

built_wheel=""
if "${python_bin}" -m pip wheel --no-deps --no-build-isolation --no-index \
     -w "${wheel_dir}" "${lab_dir}/examples" -q > "${install_log}" 2>&1; then
  built_wheel="$(find "${wheel_dir}" -maxdepth 1 -name 'feedkit-*.whl' -print -quit)"
fi
if [ -n "${built_wheel}" ] && [ -f "${built_wheel}" ]; then
  check "the package builds into a wheel offline (--no-build-isolation --no-index)" "yes"
else
  check "the package builds into a wheel offline (--no-build-isolation --no-index)" "no"
  tail -15 "${install_log}"
fi

if [ -n "${built_wheel}" ] &&
   "${python_bin}" -m venv "${install_env}" >> "${install_log}" 2>&1 &&
   "${install_env}/bin/pip" install --no-index --no-deps "${built_wheel}" -q \
     >> "${install_log}" 2>&1; then
  check "the wheel installs into a throwaway environment, not the caller's" "yes"
else
  check "the wheel installs into a throwaway environment, not the caller's" "no"
  tail -15 "${install_log}"
fi

console_bin="${install_env}/bin/feedkit"
if [ -x "${console_bin}" ]; then
  check "the console script 'feedkit' is created by the installation" "yes"
else
  check "the console script 'feedkit' is created by the installation" "no"
  console_bin=""
fi

# The wheel was installed with --no-deps, so the throwaway environment has
# feedkit but not its runtime dependency. Rather than reach for an index, the
# dependency is made importable from the environment that already has it. That
# keeps the step offline while still proving the INSTALLED console script — the
# one pip generated from the entry point — is what runs.
deps_site="$("${python_bin}" -c 'import site; print(site.getsitepackages()[0])' 2>/dev/null || true)"

if [ -n "${console_bin}" ]; then
  console_log="${work_root}/console.log"
  (cd "${run_dir}" && PYTHONPATH="${deps_site}" FEEDKIT_TOKEN="${FEEDKIT_TEST_TOKEN}" "${console_bin}" fetch \
     > "${console_log}" 2>&1)
  console_exit=$?
  if [ "${console_exit}" -eq 0 ]; then
    check "the installed console script runs a real fetch and exits 0" "yes"
  else
    check "the installed console script runs a real fetch and exits 0 (got ${console_exit})" "no"
    tail -10 "${console_log}"
  fi

  version_line="$(PYTHONPATH="${deps_site}" "${console_bin}" --version 2>&1 | head -1)"
  case "${version_line}" in
    "feedkit 1.0.0") check "feedkit --version reports 1.0.0" "yes" ;;
    *) check "feedkit --version reports 1.0.0 (got '${version_line}')" "no" ;;
  esac

  scheduled_bin="${install_env}/bin/feedkit-scheduled"
  [ -x "${scheduled_bin}" ] || scheduled_bin=""
  if [ -n "${scheduled_bin}" ]; then
    (cd "${run_dir}" && PYTHONPATH="${deps_site}" FEEDKIT_TOKEN="${FEEDKIT_TEST_TOKEN}" "${scheduled_bin}" \
       > "${work_root}/scheduled.log" 2>&1)
    scheduled_exit=$?
    if [ "${scheduled_exit}" -eq 0 ]; then
      check "the scheduled entry point 'feedkit-scheduled' runs and exits 0" "yes"
    else
      check "the scheduled entry point runs and exits 0 (got ${scheduled_exit})" "no"
    fi
  else
    check "the scheduled entry point 'feedkit-scheduled' exists" "no"
  fi
fi

# --------------------------------------------------------------------------
echo
echo "9. The starter is runnable, and the shipped files behave"
# --------------------------------------------------------------------------

starter_help="$(cd "${lab_dir}/starter" && PYTHONPATH="${lab_dir}/starter/src" \
  "${python_bin}" -m feedkit.cli --help 2>&1)"
starter_exit=$?
if [ "${starter_exit}" -eq 0 ]; then
  check "the starter's --help works before you write a line" "yes"
else
  check "the starter's --help works before you write a line (got ${starter_exit})" "no"
fi
exercise_count="$(grep -rc 'Exercise ' "${lab_dir}/starter/src/feedkit/" 2>/dev/null | \
  awk -F: '{total += $2} END {print total+0}')"
if [ "${exercise_count}" -ge 6 ]; then
  check "the starter carries its numbered exercises (${exercise_count} markers)" "yes"
else
  check "the starter carries its numbered exercises (found ${exercise_count})" "no"
fi
if (cd "${lab_dir}/starter" && PYTHONPATH="${lab_dir}/starter/src" \
    "${python_bin}" -c "import feedkit.core, feedkit.cli" >/dev/null 2>&1); then
  check "the starter package imports cleanly" "yes"
else
  check "the starter package imports cleanly" "no"
fi

# The schedule files are references and must never be installed. The strongest
# available proof is that nothing in this lab can spawn a process at all: no
# Python file imports subprocess or calls os.system, so no code path exists
# that could reach crontab, launchctl or systemctl.
if "${python_bin}" - "${lab_dir}" <<'PY' >/dev/null 2>&1
import re, sys
from pathlib import Path

root = Path(sys.argv[1])
banned = re.compile(r"^\s*import subprocess|^\s*from subprocess|os\.system\(|os\.exec")
offenders = []
for directory in ("examples/src", "starter/src", "tests"):
    for path in (root / directory).rglob("*.py"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if banned.search(line):
                offenders.append(f"{path.name}:{number}")
for line in offenders:
    print(line, file=sys.stderr)
sys.exit(1 if offenders else 0)
PY
then
  check "no Python file can spawn a process, so nothing can touch a scheduler" "yes"
else
  check "no Python file can spawn a process, so nothing can touch a scheduler" "no"
fi
for schedule_file in feedkit.cron com.example.feedkit.plist feedkit.service feedkit.timer; do
  schedule_path="${lab_dir}/examples/schedule/${schedule_file}"
  if [ -f "${schedule_path}" ] && grep -q 'NOT INSTALLED BY THIS LAB' "${schedule_path}"; then
    check "examples/schedule/${schedule_file} ships as a reference and says so" "yes"
  else
    check "examples/schedule/${schedule_file} ships as a reference and says so" "no"
  fi
done

# --------------------------------------------------------------------------
echo
echo "10. Nothing in this lab reaches the internet"
# --------------------------------------------------------------------------

if "${python_bin}" - "${lab_dir}" <<'PY' >/dev/null 2>&1
import re, sys
from pathlib import Path

root = Path(sys.argv[1])
pattern = re.compile(r"https?://(?!127\.0\.0\.1)[A-Za-z0-9.-]+")
offenders = []
for directory in ("examples/src", "starter/src", "tests"):
    for path in (root / directory).rglob("*.py"):
        for match in pattern.finditer(path.read_text(encoding="utf-8")):
            offenders.append(f"{path.name}: {match.group(0)}")
for line in offenders:
    print(line, file=sys.stderr)
sys.exit(1 if offenders else 0)
PY
then
  check "no executable file names any host but 127.0.0.1" "yes"
else
  check "no executable file names any host but 127.0.0.1" "no"
fi

if "${python_bin}" - "${lab_dir}" <<'PY' >/dev/null 2>&1
import sys
from pathlib import Path

root = Path(sys.argv[1])
offenders = []
for directory in ("examples", "starter"):
    for path in (root / directory).rglob("*"):
        if path.is_file() and ".venv" not in path.parts and "8000" in path.read_text(
            encoding="utf-8", errors="ignore"
        ):
            offenders.append(path.name)
for candidate in ("fixture_server.py", "test_toolkit.py", "conftest.py"):
    path = root / "tests" / candidate
    if "8000" in path.read_text(encoding="utf-8"):
        offenders.append(candidate)
for name in offenders:
    print(name, file=sys.stderr)
sys.exit(1 if offenders else 0)
PY
then
  check "nothing hard-codes port 8000 — the port everyone already has in use" "yes"
else
  check "nothing hard-codes port 8000" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
