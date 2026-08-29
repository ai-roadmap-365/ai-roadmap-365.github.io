#!/usr/bin/env bash
# Tests for the Day 023 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Two kinds of checks:
#   * Structure checks always run and must pass (files present, both scripts
#     parse, the example exercises each CRUD verb, the starter names its four
#     exercises).
#   * Network checks run only when the API is reachable. They verify that a
#     GET returns 200 with the expected keys and that a POST returns 201.
#     Offline (or when the public server is transiently unavailable) the live
#     checks are SKIPPED with a message rather than failed — a third-party
#     outage is not the learner's bug.
#
# The script exits 0 when no structure check failed, whether online or offline.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API="https://jsonplaceholder.typicode.com"
failures=0
checks=0
skips=0

pass() { checks=$((checks + 1)); echo "  ok:   $1"; }
fail() { checks=$((checks + 1)); failures=$((failures + 1)); echo "  FAIL: $1"; }
skip() { skips=$((skips + 1)); echo "  skip: $1"; }

echo "== Structure checks =="
example="${lab_dir}/examples/rest_crud.sh"
starter="${lab_dir}/starter/rest_crud.sh"
worksheet="${lab_dir}/starter/rest-worksheet.md"

[ -s "${example}" ] && pass "example script exists" || fail "example script missing"
[ -s "${starter}" ] && pass "starter script exists" || fail "starter script missing"
[ -s "${worksheet}" ] && pass "worksheet exists" || fail "worksheet missing"

# The example must exercise every CRUD verb and the pretty-printer.
for needle in "GET /posts/1" "POST /posts" "PUT /posts/1" "DELETE /posts/1" "json.tool"; do
  if grep -q -- "${needle}" "${example}"; then pass "example uses '${needle}'"; else fail "example missing '${needle}'"; fi
done

# The starter must name its four numbered exercises.
ex_count="$(grep -cE 'Exercise [1-4]' "${starter}" 2>/dev/null || true)"
if [ "${ex_count:-0}" -ge 4 ]; then pass "starter has 4 numbered exercises"; else fail "starter has 4 numbered exercises (found ${ex_count:-0})"; fi

# Both scripts must be valid bash.
if bash -n "${example}" 2>/dev/null; then pass "example has valid bash syntax"; else fail "example has a syntax error"; fi
if bash -n "${starter}" 2>/dev/null; then pass "starter has valid bash syntax"; else fail "starter has a syntax error"; fi

echo
echo "== Network checks =="
if ! curl -s -o /dev/null --max-time 12 "${API}/posts/1" 2>/dev/null; then
  skip "no network access — skipping all live-request checks (expected offline)"
else
  pass "network reachable (${API} responded)"

  # Check 1: GET /posts/1 returns 200.
  code="$(curl -s -o /dev/null --max-time 20 --retry 3 --retry-delay 1 \
    -w '%{http_code}' "${API}/posts/1" 2>/dev/null)" || code="000"
  case "${code}" in
    200) pass "GET /posts/1 returned HTTP 200" ;;
    5* | 000) skip "GET check — server transiently unavailable (got '${code}'); retry later" ;;
    *) fail "GET /posts/1 should return HTTP 200 (got '${code}')" ;;
  esac

  # Check 2: GET /posts/1 body carries the expected resource keys.
  body="$(curl -s --max-time 20 --retry 3 --retry-delay 1 "${API}/posts/1" 2>/dev/null)" || body=""
  if [ -z "${body}" ]; then
    skip "GET-keys check — server transiently unavailable; retry later"
  elif printf '%s' "${body}" | grep -q '"id"' \
    && printf '%s' "${body}" | grep -q '"title"' \
    && printf '%s' "${body}" | grep -q '"userId"'; then
    pass "GET /posts/1 body has the expected keys (id, title, userId)"
  else
    fail "GET /posts/1 body should contain id, title, and userId"
  fi

  # Check 3: POST /posts returns 201 (create against the collection).
  pcode="$(curl -s -o /dev/null --max-time 20 --retry 3 --retry-delay 1 \
    -X POST -H "Content-Type: application/json" \
    -d '{"title":"t","body":"b","userId":1}' \
    -w '%{http_code}' "${API}/posts" 2>/dev/null)" || pcode="000"
  case "${pcode}" in
    201) pass "POST /posts returned HTTP 201 Created" ;;
    5* | 000) skip "POST check — server transiently unavailable (got '${pcode}'); retry later" ;;
    *) fail "POST /posts should return HTTP 201 (got '${pcode}')" ;;
  esac
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skip(s)."
[ "${failures}" -eq 0 ]
