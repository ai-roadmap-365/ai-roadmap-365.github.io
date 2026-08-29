#!/usr/bin/env bash
# Tests for the Day 078 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The suite asserts real behaviour, not the presence of files. The five checks
# worth reading before the rest:
#
#   * "the whole example suite passes with the internet blocked" runs every
#     example test under tests/sitecustomize.py, which replaces
#     socket.connect and socket.getaddrinfo so that any attempt to resolve a
#     name or reach a non-loopback address raises. That turns "this lab is
#     offline" from a promise into a fact;
#   * "the fake-session suite passes with no server module present at all"
#     copies three files to a temporary directory — client.py,
#     fake_session.py and test_without_a_server.py — leaving demo_server.py
#     and conftest.py behind, and runs pytest there. It passes because every
#     client function takes `session` as a parameter. That is Day 74's
#     argument, proved rather than asserted;
#   * "a read timeout really fires" asserts that a request against a
#     three-second endpoint gives up in well under two seconds;
#   * "retry succeeds on exactly the third attempt" pins the count, not just
#     the outcome;
#   * "one Session opens one connection where five bare calls open five"
#     reads the server's own accept counter.
#
# No network, non-interactive, deterministic. Exits 0 only if every check
# passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

# Resolve a tool: an explicit override, then this lab's .venv, then PATH.
# Fails loudly with install instructions rather than skipping silently.
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

# python3 must be the SAME environment pytest lives in, or `import requests`
# will fail in the demo scripts. Prefer the venv interpreter beside pytest.
python_bin="$(dirname "${pytest_bin}")/python3"
[ -x "${python_bin}" ] || python_bin="$(command -v python3 || true)"
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi

if ! "${python_bin}" -c "import requests" >/dev/null 2>&1; then
  echo "FAIL: the 'requests' package is not importable by ${python_bin}." >&2
  echo "  Install it with: .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 078 — Talk to a Server You Control"
echo

# --------------------------------------------------------------------------
echo "1. The tools"
# --------------------------------------------------------------------------

version_line="$("${pytest_bin}" --version 2>&1 | head -1)"
case "${version_line}" in
  pytest*) check "pytest --version reports a pytest ( ${version_line} )" "yes" ;;
  *) check "pytest --version reports a pytest ( ${version_line} )" "no" ;;
esac

requests_version="$("${python_bin}" -c "import requests; print(requests.__version__)" 2>&1)"
case "${requests_version}" in
  2.*) check "requests is importable ( ${requests_version} )" "yes" ;;
  *) check "requests is importable ( ${requests_version} )" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "2. The local test server behaves as the lab claims"
# --------------------------------------------------------------------------

server_probe="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY' 2>&1
import json
import requests
from demo_server import base_url, running_server

with running_server() as srv:
    root = base_url(srv)
    host, port = srv.server_address[:2]
    s = requests.Session()
    out = {
        "host": host,
        "ephemeral": port != 0 and port != 8000,
        "readings": s.get(f"{root}/api/readings", timeout=5).status_code,
        "missing": s.get(f"{root}/api/missing", timeout=5).status_code,
        "broken": s.get(f"{root}/api/broken", timeout=5).status_code,
        "redirect": s.get(f"{root}/old/readings", timeout=5, allow_redirects=False).status_code,
        "echo": s.post(f"{root}/api/echo", json={"a": 1}, timeout=5).status_code,
    }
    s.get(f"{root}/control/reset", params={"fail": 1}, timeout=5)
    limited = s.get(f"{root}/api/flaky", timeout=5)
    out["flaky"] = limited.status_code
    out["retry_after"] = limited.headers.get("Retry-After")
    out["large"] = len(s.get(f"{root}/api/large?kb=8", timeout=5).content)
    s.close()
print(json.dumps(out))
PY
)"

expect_field() {
  local field="$1" want="$2" label="$3"
  case "${server_probe}" in
    *"\"${field}\": ${want}"*|*"\"${field}\": \"${want}\""*) check "${label}" "yes" ;;
    *) check "${label} (probe said: ${server_probe})" "no" ;;
  esac
}

expect_field host "127.0.0.1" "the server binds 127.0.0.1 and nothing else"
expect_field ephemeral "true" "the port is ephemeral, not a hard-coded 8000"
expect_field readings "200" "/api/readings answers 200"
expect_field missing "404" "/api/missing answers 404"
expect_field broken "500" "/api/broken answers 500"
expect_field redirect "301" "/old/readings answers 301"
expect_field echo "201" "POST /api/echo answers 201"
expect_field flaky "429" "/api/flaky answers 429 once armed"
expect_field retry_after "1" "the 429 carries a Retry-After header"
expect_field large "8192" "/api/large?kb=8 returns exactly 8192 bytes"

# --------------------------------------------------------------------------
echo
echo "3. The demonstrations run"
# --------------------------------------------------------------------------

raw_out="$(cd "${lab_dir}" && "${python_bin}" examples/raw_socket_demo.py 2>&1)"
raw_exit=$?
if [ "${raw_exit}" -eq 0 ]; then
  check "examples/raw_socket_demo.py exits 0" "yes"
else
  check "examples/raw_socket_demo.py exits 0 (got ${raw_exit})" "no"
fi
case "${raw_out}" in
  *"GET /api/readings?station=ALPHA HTTP/1.1"*)
    check "the hand-typed request line really is HTTP text" "yes" ;;
  *) check "the hand-typed request line really is HTTP text" "no" ;;
esac
case "${raw_out}" in
  *"HTTP/1.1 200 OK"*) check "the raw response begins with a status line" "yes" ;;
  *) check "the raw response begins with a status line" "no" ;;
esac

stdlib_out="$(cd "${lab_dir}" && "${python_bin}" examples/stdlib_demo.py 2>&1)"
stdlib_exit=$?
if [ "${stdlib_exit}" -eq 0 ]; then
  check "examples/stdlib_demo.py exits 0 — the standard library really can do this" "yes"
else
  check "examples/stdlib_demo.py exits 0 (got ${stdlib_exit})" "no"
fi
case "${stdlib_out}" in
  *"raised      : HTTPError"*)
    check "urllib.request raises on a 404 where requests returns a response" "yes" ;;
  *) check "urllib.request raises on a 404 where requests returns a response" "no" ;;
esac
case "${stdlib_out}" in
  *"connections : 1 opened for those 2 requests"*)
    check "http.client reuses one connection for two requests" "yes" ;;
  *) check "http.client reuses one connection for two requests" "no" ;;
esac

demo_out="$(cd "${lab_dir}" && "${python_bin}" examples/demo.py 2>&1)"
demo_exit=$?
if [ "${demo_exit}" -eq 0 ]; then
  check "examples/demo.py exits 0" "yes"
else
  check "examples/demo.py exits 0 (got ${demo_exit})" "no"
  printf '%s\n' "${demo_out}" | tail -20
fi
case "${demo_out}" in
  *"5 calls, one Session      : 1 TCP connection(s)"*)
    check "demo.py shows one Session using one connection for five calls" "yes" ;;
  *) check "demo.py shows one Session using one connection for five calls" "no" ;;
esac
case "${demo_out}" in
  *"5 calls, requests.get()   : 5 TCP connection(s)"*)
    check "demo.py shows five bare calls opening five connections" "yes" ;;
  *) check "demo.py shows five bare calls opening five connections" "no" ;;
esac
case "${demo_out}" in
  *"ReadTimeout"*) check "demo.py's timeout section really raises ReadTimeout" "yes" ;;
  *) check "demo.py's timeout section really raises ReadTimeout" "no" ;;
esac
case "${demo_out}" in
  *"station=ALPHA+ONE%26station%3DBRAVO"*)
    check "params= percent-encodes a value containing a space and an ampersand" "yes" ;;
  *) check "params= percent-encodes a value containing a space and an ampersand" "no" ;;
esac
case "${demo_out}" in
  *"chunks read      : 64 of at most 8192 bytes"*)
    check "streaming reads 512 KiB as 64 chunks, not one body" "yes" ;;
  *) check "streaming reads 512 KiB as 64 chunks, not one body" "no" ;;
esac

# httpx is NOT a dependency of this lab. If it happens to be installed the
# comparison runs; if not, the demo says so and exits 0 either way.
httpx_out="$(cd "${lab_dir}" && "${python_bin}" examples/httpx_demo.py 2>&1)"
httpx_exit=$?
if [ "${httpx_exit}" -eq 0 ]; then
  check "examples/httpx_demo.py exits 0 whether or not httpx is installed" "yes"
else
  check "examples/httpx_demo.py exits 0 (got ${httpx_exit})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "4. The reference suite"
# --------------------------------------------------------------------------

examples_out="$(cd "${lab_dir}" && "${pytest_bin}" examples -q -p no:cacheprovider 2>&1)"
examples_exit=$?
if [ "${examples_exit}" -eq 0 ]; then
  check "pytest examples exits 0" "yes"
else
  check "pytest examples exits 0 (got ${examples_exit})" "no"
  printf '%s\n' "${examples_out}" | tail -25
fi
case "${examples_out}" in
  *"48 passed"*) check "pytest examples reports 48 passed" "yes" ;;
  *) check "pytest examples reports 48 passed" "no" ;;
esac

for selection in \
  "a_read_timeout_fires_against_the_slow_endpoint" \
  "retry_succeeds_after_exactly_the_expected_number_of_attempts" \
  "a_missing_station_raises_a_domain_error_with_a_clean_message" \
  "one_session_reuses_one_connection_for_many_requests" \
  "streaming_writes_the_whole_body_in_many_small_chunks"
do
  if (cd "${lab_dir}" && "${pytest_bin}" examples -q -p no:cacheprovider \
        -k "${selection}" >/dev/null 2>&1); then
    check "behaviour asserted: ${selection}" "yes"
  else
    check "behaviour asserted: ${selection}" "no"
  fi
done

# The timeout check is worth timing as well as running: it must give up on
# its own schedule (0.4 s) rather than waiting for the server's 3 s.
timeout_seconds="$(cd "${lab_dir}" && "${python_bin}" - <<'PY' 2>&1
import time
import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path("examples").resolve()))
from demo_server import base_url, running_server

with running_server() as srv:
    started = time.monotonic()
    try:
        requests.get(f"{base_url(srv)}/api/slow", params={"seconds": 3}, timeout=(3.05, 0.4))
        print("NO-TIMEOUT-RAISED")
    except requests.exceptions.Timeout:
        print(f"{time.monotonic() - started:.2f}")
PY
)"
awk_ok="$("${python_bin}" -c "
v='''${timeout_seconds}'''.strip()
try:
    print('yes' if 0.1 < float(v) < 2.0 else 'no')
except ValueError:
    print('no')
")"
check "a read timeout of 0.4s fires in ${timeout_seconds}s against a 3s endpoint" "${awk_ok}"

# --------------------------------------------------------------------------
echo
echo "5. Nothing here touches the internet — proved, not promised"
# --------------------------------------------------------------------------

guarded_out="$(cd "${lab_dir}" && PYTHONPATH="${lab_dir}/tests" \
  "${pytest_bin}" examples -q -p no:cacheprovider 2>&1)"
guarded_exit=$?
if [ "${guarded_exit}" -eq 0 ]; then
  check "the whole example suite passes with all non-loopback sockets blocked" "yes"
else
  check "the whole example suite passes with all non-loopback sockets blocked" "no"
  printf '%s\n' "${guarded_out}" | tail -25
fi

# And the guard is not vacuous: with it loaded, a real request must fail.
if (cd "${lab_dir}" && PYTHONPATH="${lab_dir}/tests" "${python_bin}" -c "
import requests
requests.get('https://example.com', timeout=2)
" >/dev/null 2>&1); then
  check "the offline guard is real (a request to a public site is blocked)" "no"
else
  check "the offline guard is real (a request to a public site is blocked)" "yes"
fi

# No lab file may name a real remote host. `example.invalid` is allowed: the
# .invalid top-level domain is reserved by RFC 2606 precisely so that it can
# never resolve, which is why the fake-session tests use it.
offenders="$(grep -rn 'http://\|https://' "${lab_dir}/examples" "${lab_dir}/starter" \
  --include='*.py' \
  | grep -v '127\.0\.0\.1' | grep -v 'example\.invalid' | grep -v '{base' | grep -v '{root' \
  | grep -v '{host}' || true)"
if [ -z "${offenders}" ]; then
  check "no example or starter file names a real remote host" "yes"
else
  check "no example or starter file names a real remote host" "no"
  printf '%s\n' "${offenders}"
fi

if grep -rn ':8000' "${lab_dir}/examples" "${lab_dir}/starter" >/dev/null 2>&1; then
  check "no file hard-codes port 8000 (the collision waiting to happen)" "no"
else
  check "no file hard-codes port 8000 (the collision waiting to happen)" "yes"
fi

# --------------------------------------------------------------------------
echo
echo "6. The Day 74 payoff: tests that need no server at all"
# --------------------------------------------------------------------------

# Copy three files — and deliberately NOT demo_server.py or conftest.py — to a
# temporary directory, and run the fake-session suite there. If it passes, the
# client genuinely has an injectable boundary.
solo="$(mktemp -d "${TMPDIR:-/tmp}/day078-solo.XXXXXX")"
cp "${lab_dir}/examples/client.py" "${lab_dir}/examples/fake_session.py" \
   "${lab_dir}/examples/test_without_a_server.py" "${solo}/"
solo_out="$(cd "${solo}" && "${pytest_bin}" . -q -p no:cacheprovider 2>&1)"
solo_exit=$?
if [ "${solo_exit}" -eq 0 ]; then
  check "the fake-session suite passes with no server module present at all" "yes"
else
  check "the fake-session suite passes with no server module present at all" "no"
  printf '%s\n' "${solo_out}" | tail -25
fi
case "${solo_out}" in
  *"20 passed"*) check "that suite is 20 real tests, not a placeholder" "yes" ;;
  *) check "that suite is 20 real tests, not a placeholder (got: $(printf '%s' "${solo_out}" | tail -1))" "no" ;;
esac
if [ -e "${solo}/demo_server.py" ] || [ -e "${solo}/conftest.py" ]; then
  check "the isolated directory really lacks the server" "no"
else
  check "the isolated directory really lacks the server" "yes"
fi
# And it must run under the offline guard too.
if (cd "${solo}" && PYTHONPATH="${lab_dir}/tests" "${pytest_bin}" . -q -p no:cacheprovider \
      >/dev/null 2>&1); then
  check "and it passes with every non-loopback socket blocked" "yes"
else
  check "and it passes with every non-loopback socket blocked" "no"
fi
rm -rf "${solo}"

# The signatures that make all of that possible.
signature_report="$("${python_bin}" - "${lab_dir}" <<'PY' 2>&1
import inspect
import sys
sys.path.insert(0, f"{sys.argv[1]}/examples")
import client

problems = []
for name in ("fetch_readings", "get_with_retry", "stream_to_file"):
    params = inspect.signature(getattr(client, name)).parameters
    if "session" not in params:
        problems.append(f"{name} has no session parameter")
    if params.get("session") and params["session"].kind is not inspect.Parameter.KEYWORD_ONLY:
        problems.append(f"{name}'s session is not keyword-only")
for name in ("get_with_retry", "backoff_delays"):
    params = inspect.signature(getattr(client, name)).parameters
    if "jitter" not in params:
        problems.append(f"{name} has no injectable jitter")
if "sleep" not in inspect.signature(client.get_with_retry).parameters:
    problems.append("get_with_retry has no injectable sleep")
print("OK" if not problems else "; ".join(problems))
PY
)"
if [ "${signature_report}" = "OK" ]; then
  check "every networked function takes session (and sleep, and jitter) as parameters" "yes"
else
  check "every networked function takes session as a parameter (${signature_report})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "7. Retry policy: the statuses, checked one at a time"
# --------------------------------------------------------------------------

policy="$("${python_bin}" - "${lab_dir}" <<'PY' 2>&1
import sys
sys.path.insert(0, f"{sys.argv[1]}/examples")
from client import RETRY_STATUSES

should = {429, 500, 502, 503, 504}
should_not = {200, 201, 204, 301, 304, 400, 401, 403, 404, 409, 422}
wrong = [s for s in should if s not in RETRY_STATUSES]
wrong += [s for s in should_not if s in RETRY_STATUSES]
print("OK" if not wrong else f"wrong: {sorted(wrong)}")
PY
)"
if [ "${policy}" = "OK" ]; then
  check "429 and 5xx are retryable; 4xx and every success code are not" "yes"
else
  check "429 and 5xx are retryable; 4xx and every success code are not (${policy})" "no"
fi

schedule="$("${python_bin}" - "${lab_dir}" <<'PY' 2>&1
import sys
sys.path.insert(0, f"{sys.argv[1]}/examples")
from client import backoff_delays

full = backoff_delays(6, jitter=lambda: 1.0)
half = backoff_delays(4, jitter=lambda: 0.0)
ok = full == [0.5, 1.0, 2.0, 4.0, 8.0] and half == [0.25, 0.5, 1.0]
try:
    backoff_delays(0)
    ok = False
except ValueError:
    pass
print("OK" if ok else f"full={full} half={half}")
PY
)"
if [ "${schedule}" = "OK" ]; then
  check "the backoff doubles, caps at 8s, jitters into the top half of each slot" "yes"
else
  check "the backoff schedule is wrong (${schedule})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "8. Your work in starter/"
# --------------------------------------------------------------------------

starter_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
starter_exit=$?
if [ "${starter_exit}" -eq 0 ]; then
  check "pytest starter exits 0" "yes"
else
  check "pytest starter exits 0 (got ${starter_exit})" "no"
  printf '%s\n' "${starter_out}" | tail -25
fi

if grep -q 'raise NotImplementedError' "${lab_dir}/starter/client.py"; then
  echo "  (exercises unfinished — structural checks only)"
  for fn in fetch_readings describe_failure backoff_delays get_with_retry \
            make_session stream_to_file
  do
    if grep -q "^def ${fn}(\|^def ${fn}$" "${lab_dir}/starter/client.py"; then
      check "starter/client.py defines ${fn} for you to fill in" "yes"
    else
      check "starter/client.py defines ${fn} for you to fill in" "no"
    fi
  done
  case "${starter_out}" in
    *skipped*) check "unfinished exercises are skipped, so the suite is green from minute one" "yes" ;;
    *) check "unfinished exercises are skipped, so the suite is green from minute one" "no" ;;
  esac
  if grep -q 'exercise 7' "${lab_dir}/starter/test_client.py"; then
    check "starter/test_client.py carries the exercise-7 fake-session section" "yes"
  else
    check "starter/test_client.py carries the exercise-7 fake-session section" "no"
  fi
else
  echo "  (exercises finished — behavioural checks)"
  case "${starter_out}" in
    *skipped*) check "no exercise is still skipped" "no" ;;
    *) check "no exercise is still skipped" "yes" ;;
  esac
  # Your client must pass the reference suite's own fake-session tests.
  yours="$(mktemp -d "${TMPDIR:-/tmp}/day078-yours.XXXXXX")"
  cp "${lab_dir}/starter/client.py" "${lab_dir}/examples/fake_session.py" \
     "${lab_dir}/examples/test_without_a_server.py" "${yours}/"
  if (cd "${yours}" && "${pytest_bin}" . -q -p no:cacheprovider >/dev/null 2>&1); then
    check "YOUR client passes the reference fake-session suite, with no server" "yes"
  else
    check "YOUR client passes the reference fake-session suite, with no server" "no"
    (cd "${yours}" && "${pytest_bin}" . -q -p no:cacheprovider 2>&1 | tail -20)
  fi
  rm -rf "${yours}"
  if grep -qE '^\s*-\s*five requests through one .Session.: _{4,}' "${lab_dir}/starter/NOTES.md"; then
    check "starter/NOTES.md is filled in rather than left with blanks" "no"
  else
    check "starter/NOTES.md is filled in rather than left with blanks" "yes"
  fi
fi

# --------------------------------------------------------------------------
echo
echo "9. The captured output matches what the code does now"
# --------------------------------------------------------------------------

for capture in sample-run.txt pytest-runs.txt test-run.txt FIELDS.md; do
  if [ -s "${lab_dir}/expected-output/${capture}" ]; then
    check "expected-output/${capture} exists and is not empty" "yes"
  else
    check "expected-output/${capture} exists and is not empty" "no"
  fi
done

if grep -q '48 passed' "${lab_dir}/expected-output/pytest-runs.txt" 2>/dev/null; then
  check "the captured pytest run agrees with today's count of 48" "yes"
else
  check "the captured pytest run agrees with today's count of 48" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
