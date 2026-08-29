#!/usr/bin/env bash
# Tests for the Day 022 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Two kinds of checks:
#   * Structure checks always run and must pass (files present, the example
#     script calls each API, the starter names its four exercises, both scripts
#     parse, python3 is available for pretty-printing).
#   * Network checks run only when the internet is reachable. Offline, they are
#     SKIPPED with a message. When online but a public service is transiently
#     unavailable, the affected check is also SKIPPED rather than failed — an
#     external outage is not the learner's bug.
#
# The script exits 0 when no structure check failed, whether online or offline.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JSONPH="https://jsonplaceholder.typicode.com"
HTTPBIN="https://httpbin.org"
ISS="http://api.open-notify.org/iss-now.json"
failures=0
checks=0
skips=0

pass() { checks=$((checks + 1)); echo "  ok:   $1"; }
fail() { checks=$((checks + 1)); failures=$((failures + 1)); echo "  FAIL: $1"; }
skip() { skips=$((skips + 1)); echo "  skip: $1"; }

# Fetch a URL; echo the body on success, nothing on failure.
fetch() { curl -s --max-time 25 --retry 3 --retry-delay 2 "$1" 2>/dev/null; }
# True if the body parses as JSON.
is_json() { printf '%s' "$1" | python3 -m json.tool >/dev/null 2>&1; }
# True if the JSON body contains a top-level (or nested) key name.
has_key() { printf '%s' "$1" | python3 -c "import sys,json; d=json.dumps(json.load(sys.stdin)); sys.exit(0 if '\"$2\"' in d else 1)" 2>/dev/null; }

echo "== Structure checks =="
example="${lab_dir}/examples/call_apis.sh"
starter="${lab_dir}/starter/call_apis.sh"

[ -f "${example}" ] && pass "example script exists" || fail "example script missing"
[ -f "${starter}" ] && pass "starter script exists" || fail "starter script missing"
[ -f "${lab_dir}/starter/api-worksheet.md" ] && pass "worksheet exists" || fail "worksheet missing"

# python3 must be available (used to pretty-print without requiring jq).
if command -v python3 >/dev/null 2>&1; then pass "python3 available for JSON pretty-printing"; else fail "python3 not found"; fi

# The example must call each of the three APIs and NOT hard-require jq.
for needle in "jsonplaceholder.typicode.com" "httpbin.org" "api.open-notify.org" "python3 -m json.tool"; do
  if grep -q -- "${needle}" "${example}"; then pass "example uses '${needle}'"; else fail "example missing '${needle}'"; fi
done
if grep -qE '\| *jq' "${example}"; then fail "example should not pipe to jq (use python3 -m json.tool)"; else pass "example does not require jq (uses python3)"; fi

# The starter must name its four numbered exercises.
ex_count="$(grep -cE 'Exercise [1-4]' "${starter}" 2>/dev/null || true)"
if [ "${ex_count:-0}" -ge 4 ]; then pass "starter has 4 numbered exercises"; else fail "starter has 4 numbered exercises (found ${ex_count:-0})"; fi

# Both scripts must be valid bash.
if bash -n "${example}" 2>/dev/null; then pass "example has valid bash syntax"; else fail "example has a syntax error"; fi
if bash -n "${starter}" 2>/dev/null; then pass "starter has valid bash syntax"; else fail "starter has a syntax error"; fi

echo
echo "== Network checks =="
if ! curl -s -o /dev/null --max-time 12 "${JSONPH}/todos/1" 2>/dev/null; then
  skip "no network access — skipping all live-API checks (expected offline)"
else
  pass "network reachable (JSONPlaceholder responded)"

  # A network check only FAILS when a service returns valid JSON that is
  # missing the documented key (a real contract break). If the service is
  # unreachable or returns a non-JSON outage page, that is a transient outage,
  # not the learner's bug, so we SKIP.

  # Check 1: JSONPlaceholder /todos/1 returns JSON with the 'title' key.
  body="$(fetch "${JSONPH}/todos/1")"
  if [ -z "${body}" ] || ! is_json "${body}"; then skip "todos/1 — JSONPlaceholder transiently unavailable; retry later"
  elif has_key "${body}" "title"; then pass "GET /todos/1 returned JSON with a 'title' key"
  else fail "GET /todos/1 returned JSON but without the documented 'title' key"; fi

  # Check 2: JSONPlaceholder /users/1 returns JSON with the 'email' key.
  body="$(fetch "${JSONPH}/users/1")"
  if [ -z "${body}" ] || ! is_json "${body}"; then skip "users/1 — JSONPlaceholder transiently unavailable; retry later"
  elif has_key "${body}" "email"; then pass "GET /users/1 returned JSON with an 'email' key"
  else fail "GET /users/1 returned JSON but without the documented 'email' key"; fi

  # Check 3: httpbin /get echoes the query parameters in an 'args' object.
  body="$(fetch "${HTTPBIN}/get?course=365-days-of-ai&day=22")"
  if [ -z "${body}" ] || ! is_json "${body}"; then skip "httpbin /get — shared service transiently unavailable; retry later"
  elif has_key "${body}" "args" && printf '%s' "${body}" | grep -q "365-days-of-ai"; then
    pass "GET /get echoed the query parameters in 'args'"
  else fail "GET /get returned JSON but did not echo the query parameters in 'args'"; fi

  # Check 4: Open Notify ISS returns JSON with an 'iss_position' key.
  body="$(fetch "${ISS}")"
  if [ -z "${body}" ] || ! is_json "${body}"; then skip "ISS — Open Notify transiently unavailable; retry later"
  elif has_key "${body}" "iss_position"; then pass "GET iss-now.json returned JSON with 'iss_position'"
  else fail "GET iss-now.json returned JSON but without the documented 'iss_position' key"; fi
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skip(s)."
[ "${failures}" -eq 0 ]
