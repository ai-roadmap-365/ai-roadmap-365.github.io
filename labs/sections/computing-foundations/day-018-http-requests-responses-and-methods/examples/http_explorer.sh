#!/usr/bin/env bash
# Day 018 lab — Speak HTTP by Hand (reference implementation).
#
# Sends real HTTP requests with curl against free public test services and
# reads the raw request/response. Degrades gracefully:
#   * OFFLINE  -> skips the live requests, explains what each WOULD show, exits 0.
#   * httpbin.org busy (it is a shared free service and sometimes returns 503)
#     -> automatically falls back to its compatible mirror httpbingo.org so the
#        POST-echo and 404 demos still work.
#
# Run from the lab directory:
#   bash examples/http_explorer.sh
set -u

GOOD_URL="https://example.com"          # reliable, only serves GET/HEAD
HTTPBIN="https://httpbin.org"           # canonical test service (per the lesson)
HTTPBIN_MIRROR="https://httpbingo.org"  # compatible mirror, same JSON echo shape

hr() { printf '%s\n' "------------------------------------------------------------"; }

# Return a base URL for the echo/status demos: prefer httpbin.org, fall back to
# its mirror. We verify with the ACTUAL POST echo (not just a GET probe),
# because these shared free services sometimes answer GET while the echo still
# fails under load. Returns "" if neither host echoes right now.
pick_echo_service() {
  local base body
  for base in "${HTTPBIN}" "${HTTPBIN_MIRROR}"; do
    body="$(curl -s -X POST -H "Content-Type: application/json" -d '{"hello":"world"}' --max-time 10 "${base}/post" 2>/dev/null)"
    if printf '%s' "${body}" | grep -q '"hello"'; then
      printf '%s' "${base}"
      return 0
    fi
  done
  printf '%s' ""
}

# Network gate: a quick, time-limited request to a rock-solid host.
online="no"
if curl -s -o /dev/null --max-time 8 "${GOOD_URL}"; then
  online="yes"
fi

echo "=== HTTP Explorer ==="
echo "Network reachable: ${online}"
hr

if [ "${online}" != "yes" ]; then
  echo "OFFLINE MODE — no network reachable, so the live requests are skipped."
  echo "When online, this script would show you:"
  echo "  1. curl -v ${GOOD_URL}"
  echo "     -> your request lines (>) and the response's 'HTTP/.. 200' status line (<)."
  echo "  2. curl -s -o /dev/null -w '%{http_code}' ${GOOD_URL}"
  echo "     -> the bare status code 200, with the body thrown away."
  echo "  3. curl -X POST -H 'Content-Type: application/json' -d '{\"hello\":\"world\"}' ${HTTPBIN}/post"
  echo "     -> a JSON body echoing your payload back in its \"json\" field."
  echo "  4. curl -s -o /dev/null -w '%{http_code}' ${HTTPBIN}/status/404"
  echo "     -> the status code 404, produced on purpose."
  echo "=== End (offline) ==="
  exit 0
fi

# 1. Verbose: see BOTH messages. Request lines start with '>', response with '<'.
echo "STEP 1 — curl -v ${GOOD_URL}"
echo "(Request lines start with '>', response headers with '<'.)"
# -s hides the progress meter; 2>&1 merges curl's verbose stream (stderr) so we
# can filter it. We show only the request/status/header lines, not the HTML body.
curl -s -v "${GOOD_URL}" -o /dev/null 2>&1 | grep -E '^[<>]' | head -n 16
hr

# 2. Read ONLY the status code. -o /dev/null discards the body; -w prints the code.
echo "STEP 2 — status code only for ${GOOD_URL}"
code="$(curl -s -o /dev/null -w '%{http_code}' "${GOOD_URL}")"
echo "Status code: ${code}"
hr

# Choose the echo/status service for steps 3 and 4.
ECHO_BASE="$(pick_echo_service)"
if [ -z "${ECHO_BASE}" ]; then
  echo "NOTE: both httpbin.org and its mirror are busy right now (a shared free"
  echo "service, so this happens). Steps 3-4 are skipped; rerun in a minute."
  echo "The GET checks above already succeeded, so your network and curl are fine."
  echo "=== End of HTTP Explorer ==="
  exit 0
fi
echo "Using echo service: ${ECHO_BASE}"
hr

# 3. POST a JSON body and watch the service echo it back.
echo "STEP 3 — POST a JSON body to ${ECHO_BASE}/post"
echo "Request body sent: {\"hello\":\"world\"}"
echo "Server echoed the 'json' field back as:"
curl -s -X POST -H "Content-Type: application/json" -d '{"hello":"world"}' "${ECHO_BASE}/post" \
  | grep -A2 '"json"'
hr

# 4. Trigger a 404 on purpose so a failing status becomes information, not alarm.
echo "STEP 4 — deliberately request a 404 from ${ECHO_BASE}/status/404"
code404="$(curl -s -o /dev/null -w '%{http_code}' "${ECHO_BASE}/status/404")"
echo "Status code: ${code404}  (4xx = client error: the resource was not found)"
hr

echo "=== End of HTTP Explorer ==="
