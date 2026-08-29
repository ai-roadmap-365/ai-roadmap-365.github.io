#!/usr/bin/env bash
# Tests for the Day 018 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Structure checks always run. Network checks (a real 200 from a known-good URL
# and a real POST-body echo) run only when the network is reachable; offline
# they are SKIPPED with a clear message. The script exits 0 unless a check that
# actually ran failed.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0
skips=0

GOOD_URL="https://example.com"
HTTPBIN="https://httpbin.org"
HTTPBIN_MIRROR="https://httpbingo.org"

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

skip() {
  skips=$((skips + 1))
  echo "  skip: $1"
}

echo "Structure checks ..."
# The three scripts/worksheet the learner needs must exist and be non-trivial.
for f in "examples/http_explorer.sh" "starter/http_explorer.sh" "starter/http-worksheet.md"; do
  if [ -s "${lab_dir}/${f}" ]; then check "${f} exists and is non-empty" "yes"; else check "${f} exists and is non-empty" "no"; fi
done
# The example script must reference curl and the good URL.
if grep -q "curl" "${lab_dir}/examples/http_explorer.sh"; then check "example uses curl" "yes"; else check "example uses curl" "no"; fi
if grep -q "example.com" "${lab_dir}/examples/http_explorer.sh"; then check "example references the known-good URL" "yes"; else check "example references the known-good URL" "no"; fi

echo
echo "Network checks ..."
# Is the network up? Probe the rock-solid host with a short timeout.
if curl -s -o /dev/null --max-time 8 "${GOOD_URL}"; then
  # Check 1: a known-good URL returns 200.
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "${GOOD_URL}")"
  if [ "${code}" = "200" ]; then check "GET ${GOOD_URL} returns 200" "yes"; else check "GET ${GOOD_URL} returns 200 (got ${code})" "no"; fi

  # Check 2: a POST body is echoed back. Try the ACTUAL POST against httpbin.org
  # first, then its mirror — a GET probe can succeed while the echo still fails,
  # because these shared free services flap under load. Pass on the first host
  # that genuinely echoes the body. If NEITHER echoes, SKIP (a third-party
  # outage is not the learner's fault) rather than fail the suite.
  echoed="no"
  echoed_by=""
  for base in "${HTTPBIN}" "${HTTPBIN_MIRROR}"; do
    body="$(curl -s -X POST -H "Content-Type: application/json" -d '{"hello":"world"}' --max-time 15 "${base}/post" 2>/dev/null)"
    if printf '%s' "${body}" | grep -q '"hello"' && printf '%s' "${body}" | grep -q '"world"'; then
      echoed="yes"; echoed_by="${base}"; break
    fi
  done

  if [ "${echoed}" = "yes" ]; then
    check "POST body is echoed back by ${echoed_by}" "yes"
  else
    skip "POST echo — httpbin.org and its mirror are both busy right now; rerun later (network and GET are fine)"
  fi
else
  skip "network unreachable — 200 and POST-echo checks skipped (offline is fine)"
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skip(s)."
[ "${failures}" -eq 0 ]
