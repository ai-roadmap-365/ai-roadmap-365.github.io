#!/usr/bin/env bash
# Tests for the Day 096 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# WHAT THIS SUITE ASSERTS, AND WHAT IT DELIBERATELY DOES NOT
#
# It never asserts a number of milliseconds. A millisecond figure is a fact
# about one machine on one day; it is flaky everywhere else and it teaches
# nothing. What this suite asserts is the SHAPE of the result, with margins
# wide enough to survive a slow laptop, a busy CI runner or a different
# operating system:
#
#   * waiting work gets much faster with threads, and with an event loop
#   * computing work does NOT get meaningfully faster with threads
#   * computing work DOES get faster with processes
#   * a blocking call inside a coroutine collapses the loop to serial, and
#     asyncio.to_thread repairs it
#   * an unprotected shared counter loses increments; a protected one does not
#   * two locks taken in opposite orders deadlock; taken in one order they do not
#   * the hand-written generator scheduler really interleaves its tasks
#
# The example scripts print machine-readable `RESULT name value` lines. This
# suite parses those and applies its own thresholds, rather than trusting the
# scripts' own `SHAPE` verdicts — a test that asks the code under test whether
# it passed is not a test.
#
# Nothing here touches the network: the only sockets are on 127.0.0.1. Nothing
# needs sudo. Everything is built in a temporary directory removed in a trap.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work=""
checks=0
failures=0

cleanup() {
  [ -n "${work}" ] && [ -d "${work}" ] && rm -rf "${work}"
  find "${lab_dir}" -type d -name __pycache__ -prune -exec rm -rf -- {} + 2>/dev/null
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

check_eq() {
  local label="$1" expected="$2" actual="$3"
  checks=$((checks + 1))
  if [ "${expected}" = "${actual}" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    echo "        expected: ${expected}"
    echo "        actual:   ${actual}"
    failures=$((failures + 1))
  fi
}

python_bin="${PYTHON:-$(command -v python3 || true)}"
if [ -z "${python_bin}" ] || [ ! -x "${python_bin}" ]; then
  echo "python3 was not found. Install Python 3.11+ or set PYTHON=/path/to/python3."
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
work="$(mktemp -d)"

# Clear any bytecode cache left by a hand-run of one of the scripts, so that
# the "nothing left behind" check at the end is an assertion about THIS suite
# rather than about whatever happened in this directory earlier.
find "${lab_dir}" -type d -name __pycache__ -prune -exec rm -rf -- {} + 2>/dev/null

# metric FILE NAME — pull one `RESULT name value` line out of a captured run.
metric() {
  grep "^RESULT $2 " "$1" 2>/dev/null | awk '{print $3}' | head -1
}

# ratio_at_least VALUE FLOOR — arithmetic in Python, because bash has no floats.
ratio_at_least() {
  "${python_bin}" -c '
import sys
try:
    print("yes" if float(sys.argv[1]) >= float(sys.argv[2]) else "no")
except (ValueError, IndexError):
    print("no")
' "${1:-}" "${2:-}"
}

ratio_below() {
  "${python_bin}" -c '
import sys
try:
    print("yes" if float(sys.argv[1]) < float(sys.argv[2]) else "no")
except (ValueError, IndexError):
    print("no")
' "${1:-}" "${2:-}"
}

cores="$("${python_bin}" -c 'import os; print(os.cpu_count() or 1)')"
gil_disabled="$("${python_bin}" -c 'import sysconfig; print(sysconfig.get_config_var("Py_GIL_DISABLED"))')"

echo "Day 096 — Concurrency and async Basics"
echo "python3:          $("${python_bin}" -c 'import sys; print(sys.version.split()[0])')"
echo "cpu_count:        ${cores}"
echo "Py_GIL_DISABLED:  ${gil_disabled}"
echo "switch interval:  $("${python_bin}" -c 'import sys; print(sys.getswitchinterval())') s"
echo "work:             a temporary directory, removed when this script exits"
echo

# ---------------------------------------------------------------------------
echo "0. The interpreter is the one these measurements assume"
# ---------------------------------------------------------------------------
check "python is 3.11 or newer (asyncio.timeout and TaskGroup are required)" \
  "$("${python_bin}" -c 'import sys; print("yes" if sys.version_info >= (3, 11) else "no")')"
check "at least two usable CPUs, or the process comparison cannot mean anything" \
  "$([ "${cores}" -ge 2 ] && echo yes || echo no)"
# This is a fact about the build, reported rather than assumed. On a
# free-threaded build (PEP 703) the threads-do-not-help check below is
# expected NOT to hold, and the suite says so instead of failing silently.
if [ "${gil_disabled}" = "1" ]; then
  echo "  note: this is a free-threaded build. The 'threads do not help computing"
  echo "        work' check is skipped, because on this build it should not hold."
fi

# ---------------------------------------------------------------------------
echo
echo "1. Waiting work: threads and an event loop both collapse it"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/01_waiting.py" > "${work}/waiting.txt" 2>&1
waiting_status=$?
check_eq "01_waiting.py exits 0" "0" "${waiting_status}"

seq_s="$(metric "${work}/waiting.txt" waiting_sequential_s)"
thr_speedup="$(metric "${work}/waiting.txt" waiting_threaded_speedup)"
aio_speedup="$(metric "${work}/waiting.txt" waiting_asyncio_speedup)"

check "the sequential baseline really did pay all 20 waits (>= 1.5s of waiting)" \
  "$(ratio_at_least "${seq_s}" 1.5)"
check "threads are at least 4x faster than sequential on waiting work" \
  "$(ratio_at_least "${thr_speedup}" 4.0)"
check "asyncio is at least 4x faster than sequential on waiting work" \
  "$(ratio_at_least "${aio_speedup}" 4.0)"
check "all three approaches returned 20 well-formed bodies" \
  "$([ "$(grep -c '20 bodies, all well formed: yes' "${work}/waiting.txt")" = "3" ] && echo yes || echo no)"
check "order is preserved: the first body is the one for /item/1" \
  "$(grep -q 'first body is for /item/1' "${work}/waiting.txt" && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
echo "2. Computing work: the answer flips, and that is the whole day"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/02_computing.py" > "${work}/computing.txt" 2>&1
computing_status=$?
check_eq "02_computing.py exits 0" "0" "${computing_status}"

cpu_thr="$(metric "${work}/computing.txt" computing_threaded_speedup)"
cpu_proc="$(metric "${work}/computing.txt" computing_processes_speedup)"
cpu_aio="$(metric "${work}/computing.txt" computing_asyncio_speedup)"

if [ "${gil_disabled}" = "1" ]; then
  check "skipped on a free-threaded build: threads may legitimately help here" yes
else
  check "threads do NOT meaningfully speed up computing work (< 1.5x)" \
    "$(ratio_below "${cpu_thr}" 1.5)"
fi
check "processes DO speed up computing work (>= 1.5x)" \
  "$(ratio_at_least "${cpu_proc}" 1.5)"
check "asyncio does NOT speed up computing work either (< 1.5x)" \
  "$(ratio_below "${cpu_aio}" 1.5)"
check "processes beat threads on this workload by a clear margin" \
  "$("${python_bin}" -c '
import sys
print("yes" if float(sys.argv[1]) >= float(sys.argv[2]) * 1.4 else "no")
' "${cpu_proc}" "${cpu_thr}")"
check "every approach still produced the right answer: 41538 primes below 500,000" \
  "$([ "$(grep -c 'correct: yes' "${work}/computing.txt")" = "4" ] && echo yes || echo no)"
check "the script reports the GIL status of the interpreter it actually ran on" \
  "$(grep -q "Py_GIL_DISABLED ${gil_disabled}" "${work}/computing.txt" && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
echo "3. A blocking call inside a coroutine, and its two repairs"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/03_blocking_coroutine.py" > "${work}/blocking.txt" 2>&1
blocking_status=$?
check_eq "03_blocking_coroutine.py exits 0" "0" "${blocking_status}"

blocked_s="$(metric "${work}/blocking.txt" blocking_gathered_s)"
await_speedup="$(metric "${work}/blocking.txt" blocking_vs_await_speedup)"
thread_speedup="$(metric "${work}/blocking.txt" blocking_vs_to_thread_speedup)"
blocked_gap="$(metric "${work}/blocking.txt" blocked_heartbeat_gap_ms)"
healthy_gap="$(metric "${work}/blocking.txt" healthy_heartbeat_gap_ms)"

check "gathering 5 blocking coroutines takes the SERIAL time (>= 0.9s for 5 x 0.2s)" \
  "$(ratio_at_least "${blocked_s}" 0.9)"
check "await asyncio.sleep makes the same five overlap (>= 2.5x faster)" \
  "$(ratio_at_least "${await_speedup}" 2.5)"
check "asyncio.to_thread does too, for code you cannot rewrite (>= 2.5x faster)" \
  "$(ratio_at_least "${thread_speedup}" 2.5)"
check "a blocking coroutine starves an unrelated task on the same loop (3x the gap)" \
  "$("${python_bin}" -c '
import sys
print("yes" if float(sys.argv[1]) >= float(sys.argv[2]) * 3 else "no")
' "${blocked_gap}" "${healthy_gap}")"
check "and the healthy loop kept its 10ms heartbeat roughly on time (< 50ms)" \
  "$(ratio_below "${healthy_gap}" 50)"
check "all three versions returned identical correct results — the failure is silent" \
  "$([ "$(grep -c 'correct: yes' "${work}/blocking.txt")" = "3" ] && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
echo "4. Shared state: a counter that loses increments, and three fixes"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/04_race.py" > "${work}/race.txt" 2>&1
race_status=$?
check_eq "04_race.py exits 0" "0" "${race_status}"

expected_total="$(metric "${work}/race.txt" expected_total)"
lost_tight="$(metric "${work}/race.txt" race_lost_at_tight_interval)"
locked="$(metric "${work}/race.txt" locked_total)"
queued="$(metric "${work}/race.txt" queued_total)"

check_eq "the counter should reach 400000: 8 threads x 50000" "400000" "${expected_total}"
check "the UNPROTECTED counter loses increments — and loses a lot of them (>= 1000)" \
  "$(ratio_at_least "${lost_tight}" 1000)"
check_eq "the LOCKED counter loses none: exactly 400000" "400000" "${locked}"
check_eq "the queue version loses none either: exactly 400000" "400000" "${queued}"
check "two locks taken in opposite orders really deadlock" \
  "$(grep -q 'opposite_lock_order_deadlocks yes' "${work}/race.txt" && echo yes || echo no)"
check "the same two locks taken in one consistent order do not" \
  "$(grep -q 'consistent_lock_order_does_not yes' "${work}/race.txt" && echo yes || echo no)"
check "the script restores the interpreter's switch interval when it is done" \
  "$("${python_bin}" - "${lab_dir}" <<'PY'
import importlib.util
import sys
from pathlib import Path

lab = Path(sys.argv[1])
sys.path.insert(0, str(lab / "examples"))
spec = importlib.util.spec_from_file_location("race", lab / "examples" / "04_race.py")
race = importlib.util.module_from_spec(spec)
spec.loader.exec_module(race)

before = sys.getswitchinterval()
race.unsafe_total(race.TIGHT_INTERVAL)   # runs at 1e-6 internally
after = sys.getswitchinterval()
print("yes" if after == before else f"no: left it at {after}")
PY
)"
check "and it says plainly what the DEFAULT switch interval produced on this machine" \
  "$(grep -q 'RESULT race_lost_at_default_interval' "${work}/race.txt" && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
echo "5. The scheduler built from generators actually interleaves"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/05_scheduler.py" > "${work}/scheduler.txt" 2>&1
scheduler_status=$?
check_eq "05_scheduler.py exits 0" "0" "${scheduler_status}"

check_eq "three tasks of 3, 2 and 1 steps interleave as a b c a b a" \
  "alpha,beta,gamma,alpha,beta,alpha" \
  "$(metric "${work}/scheduler.txt" round_robin_order)"
check_eq "a task that never yields runs to completion before any other starts" \
  "greedy,greedy,greedy,greedy,polite,polite,polite" \
  "$(metric "${work}/scheduler.txt" greedy_order)"
check "a sleeping task leaves the ready queue and the other task runs meanwhile" \
  "$(grep -q 'napper-start:0 worker:1 worker:2 worker:3 worker:4 napper-woke:5' "${work}/scheduler.txt" && echo yes || echo no)"
check "each task's return value is collected through StopIteration.value" \
  "$(grep -q 'returned: gamma did 1 step$' "${work}/scheduler.txt" && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
echo "6. Cancellation and timeouts"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/06_timeouts.py" > "${work}/timeouts.txt" 2>&1
timeouts_status=$?
check_eq "06_timeouts.py exits 0" "0" "${timeouts_status}"

timeout_s="$(metric "${work}/timeouts.txt" timeout_elapsed_s)"
survivors="$(metric "${work}/timeouts.txt" gather_survivors)"
cancelled="$(metric "${work}/timeouts.txt" taskgroup_cancelled_siblings)"

check "the timeout fired at the caller's budget, not at the work's length (< 0.35s)" \
  "$(ratio_below "${timeout_s}" 0.35)"
check "and it did fire rather than the request quietly succeeding (>= 0.10s)" \
  "$(ratio_at_least "${timeout_s}" 0.10)"
check "cancellation ran the task's finally block: the socket was closed, not leaked" \
  "$(grep -q 'report cleaned up' "${work}/timeouts.txt" && echo yes || echo no)"
check "the cancelled task saw CancelledError inside itself and re-raised it" \
  "$(grep -q 'report received CancelledError' "${work}/timeouts.txt" && echo yes || echo no)"
check_eq "gather(return_exceptions=True): 2 of 3 finish despite one raising" "2.0000" "${survivors}"
check "and the failure came back as a ValueError VALUE, not as a raise" \
  "$(grep -q '\[1\] ValueError b could not be fetched' "${work}/timeouts.txt" && echo yes || echo no)"
check_eq "TaskGroup: the same failure cancels both siblings instead" "2.0000" "${cancelled}"
check "the TaskGroup error arrives in an ExceptionGroup, caught with except*" \
  "$(grep -q 'caught in the ExceptionGroup: b could not be fetched' "${work}/timeouts.txt" && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
echo "7. The starter reports honest progress, and the reference completes it"
# ---------------------------------------------------------------------------
before="$(bash "${lab_dir}/starter/02_check.sh" 2>&1)"
before_status=$?
check "the untouched starter reports 0 of 8 exercises complete" \
  "$(printf '%s' "${before}" | grep -q '^0 of 8 exercises complete\.$' && echo yes || echo no)"
check_eq "and exits non-zero, so it cannot be mistaken for finished" "incomplete" \
  "$([ "${before_status}" -ne 0 ] && echo incomplete || echo "exit ${before_status}")"
check "it names the process-pool exercise among the work still to do" \
  "$(printf '%s' "${before}" | grep -q 'count_primes_with_processes' && echo yes || echo no)"

solved="${work}/solved"
mkdir -p "${solved}"
cp -R "${lab_dir}/examples" "${lab_dir}/starter" "${solved}/"
cp "${solved}/examples/07_solutions.py" "${solved}/starter/01_exercises.py"
after="$(bash "${solved}/starter/02_check.sh" 2>&1)"
after_status=$?
check "with the reference answers in place it reports 8 of 8" \
  "$(printf '%s' "${after}" | grep -q '^8 of 8 exercises complete\.$' && echo yes || echo no)"
check_eq "and exits 0" "0" "${after_status}"

# The suite must be able to fail, or it proves nothing. Break exercise 2 so it
# does the work sequentially, keeping every answer correct, and confirm the
# checker refuses it on speed alone.
"${python_bin}" - "${solved}" <<'PY'
import pathlib, sys
target = pathlib.Path(sys.argv[1]) / "starter" / "01_exercises.py"
source = target.read_text(encoding="utf-8")
broken = source.replace(
    "    with ThreadPoolExecutor(max_workers=workers) as pool:\n"
    "        return list(pool.map(labkit.fetch, urls))",
    "    return [labkit.fetch(url) for url in urls]",
    1,
)
assert broken != source, "the sabotage did not apply — the reference file changed shape"
target.write_text(broken, encoding="utf-8")
PY
sabotaged="$(bash "${solved}/starter/02_check.sh" 2>&1)"
check "a 'threaded' answer that is secretly sequential is caught, not waved through" \
  "$(printf '%s' "${sabotaged}" | grep -q '^8 of 8 exercises complete\.$' && echo no || echo yes)"
check "and it is caught on SPEED, not on correctness — the bodies were all right" \
  "$(printf '%s' "${sabotaged}" | grep -q 'fetch_all_with_threads' && \
     printf '%s' "${sabotaged}" | grep -q 'needs >= 2.5x' && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
echo "8. Hygiene: offline, no sudo, nothing left behind"
# ---------------------------------------------------------------------------
"${python_bin}" - "${lab_dir}" > "${work}/hygiene.txt" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
hosts, sudo_lines = set(), []
comment = re.compile(r"^\s*#")
for path in sorted(root.rglob("*")):
    if not path.is_file() or path.suffix not in {".py", ".sh"}:
        continue
    for number, line in enumerate(
        path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
    ):
        for host in re.findall(r"https?://([^/\s\"')]+)", line):
            # A literal loopback address, or an f-string placeholder that can
            # only ever be filled in from server_address, is fine. Anything
            # else is a URL this lab has no business containing.
            if host != "127.0.0.1" and not host.startswith("{"):
                hosts.add(f"{path.name}:{number} {host}")
        if re.search(r"(^|[;|&(]\s*)sudo\s", line) and not comment.match(line):
            sudo_lines.append(f"{path.name}:{number}")
print("HOSTS " + " ".join(sorted(hosts)))
print("SUDO " + " ".join(sudo_lines))
PY
check_eq "no URL in this lab names any host but the loopback address" \
  "HOSTS" \
  "$(grep '^HOSTS ' "${work}/hygiene.txt" | sed 's/ *$//')"
check_eq "no line in this lab would actually invoke sudo" "SUDO" \
  "$(grep '^SUDO ' "${work}/hygiene.txt" | sed 's/ *$//')"
check "every socket this lab opens is bound to 127.0.0.1" \
  "$(grep -q '"127.0.0.1", 0' "${lab_dir}/examples/labkit.py" && echo yes || echo no)"
check "no captured output leaks an absolute home path" \
  "$(grep -rl '/Users/\|/home/' "${lab_dir}/expected-output" >/dev/null 2>&1 && echo no || echo yes)"
check "no __pycache__ directory survives inside the lab" \
  "$(find "${lab_dir}" -type d -name __pycache__ | grep -q . && echo no || echo yes)"
check "nothing in this lab imports a third-party package" \
  "$("${python_bin}" - "${lab_dir}" <<'PY'
import ast
import sys
from pathlib import Path

STDLIB = set(sys.stdlib_module_names)
LOCAL = {"labkit"}
bad = []
for path in sorted(Path(sys.argv[1]).rglob("*.py")):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module.split(".")[0]]
        else:
            continue
        bad += [n for n in names if n not in STDLIB and n not in LOCAL]
print("yes" if not bad else "no: " + ", ".join(sorted(set(bad))))
PY
)"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
