#!/usr/bin/env bash
# Tests for the Day 021 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Two kinds of checks:
#   * Structure checks always run and must pass (files present, the example
#     script defines the expected sections, the starter names its exercises,
#     both scripts parse).
#   * Network checks run only when the internet is reachable. Offline, they
#     are SKIPPED with a message. When online but the public test server
#     (httpbin.org) is transiently unavailable, the affected check is also
#     SKIPPED rather than failed — an external outage is not the learner's bug.
#
# The script exits 0 when no structure check failed, whether online or offline.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HTTPBIN="https://httpbin.org"
EXAMPLE="https://example.com"
failures=0
checks=0
skips=0

pass() { checks=$((checks + 1)); echo "  ok:   $1"; }
fail() { checks=$((checks + 1)); failures=$((failures + 1)); echo "  FAIL: $1"; }
skip() { skips=$((skips + 1)); echo "  skip: $1"; }

echo "== Structure checks =="
example="${lab_dir}/examples/debug_request.sh"
starter="${lab_dir}/starter/debug_request.sh"

[ -f "${example}" ] && pass "example script exists" || fail "example script missing"
[ -f "${starter}" ] && pass "starter script exists" || fail "starter script missing"
[ -f "${lab_dir}/starter/debug-worksheet.md" ] && pass "worksheet exists" || fail "worksheet missing"

# The example must exercise each core flag/section.
for needle in "curl -v" "curl -IL" "%{http_code}" "time_namelookup" "diagnose"; do
  if grep -q -- "${needle}" "${example}"; then pass "example uses '${needle}'"; else fail "example missing '${needle}'"; fi
done

# The starter must name its five numbered exercises.
ex_count="$(grep -cE 'Exercise [1-5]' "${starter}" 2>/dev/null || true)"
if [ "${ex_count:-0}" -ge 5 ]; then pass "starter has 5 numbered exercises"; else fail "starter has 5 numbered exercises (found ${ex_count:-0})"; fi

# Both scripts must be valid bash.
if bash -n "${example}" 2>/dev/null; then pass "example has valid bash syntax"; else fail "example has a syntax error"; fi
if bash -n "${starter}" 2>/dev/null; then pass "starter has valid bash syntax"; else fail "starter has a syntax error"; fi

echo
echo "== Network checks =="
if ! curl -s -o /dev/null --max-time 12 "${EXAMPLE}" 2>/dev/null; then
  skip "no network access — skipping all live-request checks (expected offline)"
else
  pass "network reachable (${EXAMPLE} responded)"

  # Check 1: curl follows a redirect through to a final 200 (redirect/1 -> /get).
  final="$(curl -o /dev/null -sIL --max-time 25 --retry 5 --retry-delay 1 \
    -w '%{http_code}' "${HTTPBIN}/redirect/1" 2>/dev/null)" || final="000"
  case "${final}" in
    200) pass "curl -L followed the redirect to a final HTTP 200" ;;
    5* | 000) skip "redirect check — httpbin transiently unavailable (got '${final}'); retry later" ;;
    *) fail "curl -L should reach HTTP 200 (got '${final}')" ;;
  esac

  # Check 2: reads a 404 status correctly. --retry rides past transient 5xx;
  # a real 404 is not a transient error, so curl returns it without retrying.
  code404="$(curl -o /dev/null -s --max-time 25 --retry 5 --retry-delay 1 \
    -w '%{http_code}' "${HTTPBIN}/status/404" 2>/dev/null)" || code404="000"
  case "${code404}" in
    404) pass "curl read the deliberate 404 status correctly" ;;
    5* | 000) skip "404 check — httpbin transiently unavailable (got '${code404}'); retry later" ;;
    *) fail "curl should read HTTP 404 (got '${code404}')" ;;
  esac

  # Check 3: the headers endpoint echoes back a header we set with -H.
  echoed="$(curl -sf --max-time 25 --retry 5 --retry-delay 1 \
    -H "X-Day-21-Test: inspecting" "${HTTPBIN}/headers" 2>/dev/null)" || echoed=""
  if [ -z "${echoed}" ]; then
    skip "headers-echo check — httpbin transiently unavailable; retry later"
  elif printf '%s' "${echoed}" | grep -q "X-Day-21-Test"; then
    pass "the headers endpoint echoed back the header sent with -H"
  else
    fail "the headers endpoint should echo the -H header we sent"
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skip(s)."
[ "${failures}" -eq 0 ]
