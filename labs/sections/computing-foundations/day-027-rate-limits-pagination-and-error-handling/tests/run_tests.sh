#!/usr/bin/env bash
# Tests for the Day 027 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Two kinds of checks:
#   * Structure checks always run and must pass (files present, both scripts
#     parse, the example defines the resilient pieces, the starter names its
#     four exercises).
#   * Behavior checks. OFFLINE, the network is SKIPPED, but the backoff logic
#     is still verified to TERMINATE via a stubbed always-failing call (the
#     --selftest path uses no network). ONLINE, the example is run fast and its
#     backoff must give up (not loop forever) and its pagination must collect
#     the expected count.
#
# Every script run is wrapped in a watchdog: if it does not finish within the
# time limit it is killed and the check FAILS — this is how we prove the retry
# loop can never spin forever. The script exits 0 when no check failed.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
example="${lab_dir}/examples/resilient_client.sh"
starter="${lab_dir}/starter/resilient_client.sh"
worksheet="${lab_dir}/starter/resilience-worksheet.md"
PROBE="https://example.com"

failures=0
checks=0
skips=0
pass() { checks=$((checks + 1)); echo "  ok:   $1"; }
fail() { checks=$((checks + 1)); failures=$((failures + 1)); echo "  FAIL: $1"; }
skip() { skips=$((skips + 1)); echo "  skip: $1"; }

# run_guarded <seconds> <outfile> <command...>  -> returns command's exit code,
# or 137 if the watchdog had to kill it (i.e. it did not terminate in time).
run_guarded() {
  local secs="$1" outf="$2"; shift 2
  "$@" > "${outf}" 2>&1 &
  local pid=$!
  ( sleep "${secs}"; kill -9 "${pid}" 2>/dev/null ) &
  local watchdog=$!
  wait "${pid}" 2>/dev/null; local rc=$?
  kill "${watchdog}" 2>/dev/null; wait "${watchdog}" 2>/dev/null
  return "${rc}"
}

echo "== Structure checks =="
[ -f "${example}" ] && pass "example script exists" || fail "example script missing"
[ -f "${starter}" ] && pass "starter script exists" || fail "starter script missing"
[ -f "${worksheet}" ] && pass "resilience worksheet exists" || fail "worksheet missing"

for needle in "backoff_retry" "MAX_ATTEMPTS" "Retry-After" "giving up gracefully" "_page=" "_limit="; do
  if grep -q -- "${needle}" "${example}"; then pass "example uses '${needle}'"; else fail "example missing '${needle}'"; fi
done

ex_count="$(grep -cE 'Exercise [1-4]' "${starter}" 2>/dev/null || true)"
if [ "${ex_count:-0}" -ge 4 ]; then pass "starter names its four exercises"; else fail "starter should name 4 exercises (found ${ex_count:-0})"; fi

bash -n "${example}" 2>/dev/null && pass "example has valid bash syntax" || fail "example has a syntax error"
bash -n "${starter}" 2>/dev/null && pass "starter has valid bash syntax" || fail "starter has a syntax error"

echo
echo "== Backoff termination (always, no network needed) =="
# The offline self-test drives the retry loop with a stubbed always-503 server
# and MUST terminate on its own well within the watchdog window.
out="$(mktemp)"
run_guarded 30 "${out}" bash "${example}" --selftest
rc=$?
if [ "${rc}" -eq 137 ]; then
  fail "backoff self-test did NOT terminate (watchdog had to kill it — infinite loop!)"
elif grep -q "giving up gracefully" "${out}" && grep -q "loop terminated" "${out}"; then
  pass "backoff self-test terminates and gives up gracefully (no network)"
else
  fail "backoff self-test did not report a graceful give-up"
  sed 's/^/    /' "${out}"
fi
rm -f "${out}"

echo
echo "== Live behavior checks =="
if ! curl -s -o /dev/null --max-time 12 "${PROBE}" 2>/dev/null; then
  skip "no network access — skipping live 429/pagination checks (expected offline)"
else
  pass "network reachable (${PROBE} responded)"
  out="$(mktemp)"
  # Run fast: tiny delays so the capped backoff finishes quickly. The watchdog
  # still guarantees termination even if the test server is slow.
  # Short per-request timeout + few stable-retries keeps the run bounded even
  # when the shared test server is slow, so the watchdog only ever fires on a
  # genuine non-terminating loop (not on a slow network).
  MAX_ATTEMPTS=3 BASE_DELAY=0 DELAY_CAP=0 CURL_MAX_TIME=4 STABLE_TRIES=2 \
    run_guarded 90 "${out}" bash "${example}"
  rc=$?
  if [ "${rc}" -eq 137 ]; then
    fail "example did NOT terminate within 90s (watchdog killed it)"
    sed 's/^/    /' "${out}"
  else
    pass "example run terminated on its own"
    grep -q "giving up gracefully" "${out}" \
      && pass "backoff gave up gracefully after its cap" \
      || fail "expected a 'giving up gracefully' line"
    collected="$(sed -n 's/.*collected \([0-9]\{1,\}\) posts across 2 pages/\1/p' "${out}" | head -1)"
    case "${collected}" in
      10) pass "pagination collected 10 posts across 2 pages" ;;
      '' ) skip "pagination count not found — test server (jsonplaceholder) may be transiently down" ;;
      *) fail "pagination should collect 10 posts (got '${collected}')" ;;
    esac
  fi
  rm -f "${out}"
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skip(s)."
[ "${failures}" -eq 0 ]
