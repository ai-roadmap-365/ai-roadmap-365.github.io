#!/usr/bin/env bash
# Tests for the Day 025 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Two kinds of checks:
#   * Structure checks always run and must pass (files present, the example
#     script exercises each scheme, the starter names its exercises, both
#     scripts parse, and no realistic long key-shaped string is present).
#   * Network checks run only when the internet is reachable. Offline, they
#     are SKIPPED with a message. When online but the public test server
#     (httpbin.org) is transiently returning 5xx, the affected check is also
#     SKIPPED rather than failed — an external outage is not the learner's bug.
#
# The script exits 0 when no structure check failed, whether online or offline.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API="https://httpbin.org"
failures=0
checks=0
skips=0

pass() { checks=$((checks + 1)); echo "  ok:   $1"; }
fail() { checks=$((checks + 1)); failures=$((failures + 1)); echo "  FAIL: $1"; }
skip() { skips=$((skips + 1)); echo "  skip: $1"; }

echo "== Structure checks =="
example="${lab_dir}/examples/auth_demo.sh"
starter="${lab_dir}/starter/auth_demo.sh"

[ -f "${example}" ] && pass "example script exists" || fail "example script missing"
[ -f "${starter}" ] && pass "starter script exists" || fail "starter script missing"
[ -f "${lab_dir}/starter/auth-worksheet.md" ] && pass "worksheet exists" || fail "worksheet missing"

# The example must exercise each scheme.
for needle in "user:pass" "user:wrongpass" "Authorization: Bearer" "X-API-Key" "DEMO_TOKEN"; do
  if grep -q -- "${needle}" "${example}"; then pass "example uses '${needle}'"; else fail "example missing '${needle}'"; fi
done

# The starter must name its four numbered exercises.
ex_count="$(grep -cE 'Exercise [1-4]:' "${starter}" 2>/dev/null || true)"
if [ "${ex_count:-0}" -ge 4 ]; then pass "starter has 4 numbered exercises"; else fail "starter has 4 numbered exercises (found ${ex_count:-0})"; fi

# Both scripts must be valid bash.
if bash -n "${example}" 2>/dev/null; then pass "example has valid bash syntax"; else fail "example has a syntax error"; fi
if bash -n "${starter}" 2>/dev/null; then pass "starter has valid bash syntax"; else fail "starter has a syntax error"; fi

# Safety: no realistic long key-shaped string should appear anywhere in the lab.
# (Fake placeholders like token-example-123 are short and hyphenated; a real
# key is a long unbroken run of letters/digits. Flag any 32+ char run.)
if grep -rInE '[A-Za-z0-9]{32,}' "${lab_dir}" >/dev/null 2>&1; then
  fail "a long key-shaped string is present — use only short fake placeholders"
else
  pass "no realistic long key-shaped strings present"
fi

echo
echo "== Network checks =="
if ! curl -s -o /dev/null --max-time 12 "${API}/status/200" 2>/dev/null; then
  skip "no network access — skipping all live-request checks (expected offline)"
else
  pass "network reachable (${API} responded)"

  # Check 1: correct Basic auth returns 200.
  ok="$(curl -o /dev/null -s --max-time 25 --retry 5 --retry-delay 2 \
    -w '%{http_code}' -u user:pass "${API}/basic-auth/user/pass" 2>/dev/null)" || ok="000"
  case "${ok}" in
    200) pass "correct Basic auth returned HTTP 200" ;;
    5* | 000) skip "Basic-auth-correct check — httpbin transiently unavailable (got '${ok}'); retry later" ;;
    *) fail "correct Basic auth should return 200 (got '${ok}')" ;;
  esac

  # Check 2: wrong Basic auth returns 401. A 401 is not a transient error, so
  # --retry returns it without retrying; a 5xx means the server is overloaded.
  bad="$(curl -o /dev/null -s --max-time 25 --retry 5 --retry-delay 2 \
    -w '%{http_code}' -u user:wrongpass "${API}/basic-auth/user/pass" 2>/dev/null)" || bad="000"
  case "${bad}" in
    401) pass "wrong Basic auth returned HTTP 401" ;;
    5* | 000) skip "Basic-auth-wrong check — httpbin transiently unavailable (got '${bad}'); retry later" ;;
    *) fail "wrong Basic auth should return 401 (got '${bad}')" ;;
  esac

  # Check 3: the bearer endpoint accepts a token and returns 200.
  br="$(curl -o /dev/null -s --max-time 25 --retry 5 --retry-delay 2 \
    -w '%{http_code}' -H "Authorization: Bearer token-example-123" "${API}/bearer" 2>/dev/null)" || br="000"
  case "${br}" in
    200) pass "bearer endpoint accepted the token (HTTP 200)" ;;
    5* | 000) skip "bearer check — httpbin transiently unavailable (got '${br}'); retry later" ;;
    *) fail "bearer endpoint should return 200 (got '${br}')" ;;
  esac
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skip(s)."
[ "${failures}" -eq 0 ]
