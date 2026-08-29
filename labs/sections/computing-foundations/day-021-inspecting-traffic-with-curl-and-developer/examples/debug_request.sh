#!/usr/bin/env bash
# Day 021 lab — Debug a Request with curl (completed reference implementation).
#
# Demonstrates the core traffic-inspection skills against two public test
# servers: https://httpbin.org (echoes requests, returns any status you ask
# for) and https://example.com. Every section maps to a stage of the
# failed-request decision tree from the lesson.
#
# Run from the lab directory:  bash examples/debug_request.sh
#
# Requires network access. If the network (or the test server) is
# unreachable, each section degrades gracefully with a clear message and the
# script still exits 0, so it is safe to run offline.
set -u

HTTPBIN="https://httpbin.org"
EXAMPLE="https://example.com"

rule() { printf '\n=== %s ===\n' "$1"; }

# Return 0 if we appear to have network access to the test host, else 1.
have_network() {
  curl -s -o /dev/null --max-time 12 "${EXAMPLE}" 2>/dev/null
}

# ---------------------------------------------------------------------------
# 1. curl -v : see the whole conversation (DNS, TCP, TLS, request, response).
# ---------------------------------------------------------------------------
show_verbose() {
  rule "1. curl -v — the full request/response conversation"
  echo "\$ curl -v ${EXAMPLE}   (connection notes and headers shown)"
  # -v prints to stderr; keep the * (connection), > (request) and < (response
  # header) lines and drop the noisy download-progress meter and body.
  curl -v -o /dev/null --max-time 15 "${EXAMPLE}" 2>&1 \
    | grep -E '^[*<>]' \
    | grep -vE 'Trying|Establish|schannel|CApath|CAfile|TLSv.*handshake' \
    || echo "(could not reach ${EXAMPLE})"
}

# ---------------------------------------------------------------------------
# 2. curl -IL : follow a redirect to its final destination, headers only.
# ---------------------------------------------------------------------------
show_redirect() {
  rule "2. curl -IL — follow a redirect (httpbin/redirect/1 -> /get)"
  echo "\$ curl -IL ${HTTPBIN}/redirect/1"
  # Shown as two explicit steps so the output is always clean regardless of
  # httpbin's transient gateway hiccups. -w writes its line ONCE after the
  # final transfer (not per retry), and -o /dev/null discards the header dump,
  # so there are never duplicate lines. A real 302 is not a transient error,
  # so --retry returns it as-is; a transient 5xx is retried away.
  local hop1 code1 loc final
  hop1="$(curl -sI -o /dev/null --max-time 25 --retry 5 --retry-delay 1 \
    -w '%{http_code} %{redirect_url}' "${HTTPBIN}/redirect/1" 2>/dev/null)" || hop1=""
  if [ -z "${hop1}" ]; then echo "(could not reach ${HTTPBIN})"; return; fi
  read -r code1 loc <<< "${hop1}"
  echo "first request:  HTTP ${code1}  ->  location: ${loc:-<none>}"
  final="$(curl -o /dev/null -sIL --max-time 25 --retry 5 --retry-delay 1 \
    -w '%{http_code}' "${HTTPBIN}/redirect/1" 2>/dev/null)" || final="000"
  echo "after -L follows the location header, final status: HTTP ${final}"
}

# Describe a status code by its class — always truthful about what came back.
classify_status() {
  case "$1" in
    2*) echo "success" ;;
    3*) echo "a redirect — follow it with -L" ;;
    4*) echo "a CLIENT error — fix your request (URL, auth, or body)" ;;
    5*) echo "a SERVER error — the server failed a valid request" ;;
    *)  echo "no valid response (timeout or connection failure)" ;;
  esac
}

# ---------------------------------------------------------------------------
# 3. curl -w : timing breakdown — which stage was slow?
# ---------------------------------------------------------------------------
show_timing() {
  rule "3. curl -w — timing breakdown (seconds)"
  echo "\$ curl -o /dev/null -s -w '...' ${EXAMPLE}"
  curl -o /dev/null -s --max-time 15 \
    -w 'dns:%{time_namelookup}  connect:%{time_connect}  tls:%{time_appconnect}  ttfb:%{time_starttransfer}  total:%{time_total}\n' \
    "${EXAMPLE}" \
    || echo "(could not reach ${EXAMPLE})"
}

# ---------------------------------------------------------------------------
# 4. curl -H : prove which headers you actually sent (echoed back).
# ---------------------------------------------------------------------------
show_headers_echo() {
  rule "4. curl -H — the headers endpoint echoes what you sent"
  echo "\$ curl -H 'Accept: application/json' ${HTTPBIN}/headers"
  # -f (--fail) makes curl print nothing and return non-zero on an HTTP error,
  # so a transient 503 page is never dumped; --retry rides through the hiccup.
  curl -sf --max-time 25 --retry 4 --retry-delay 2 -H "Accept: application/json" "${HTTPBIN}/headers" \
    || echo "(could not reach ${HTTPBIN} — transient server error; try again in a moment)"
  echo
}

# ---------------------------------------------------------------------------
# 5. Read status codes deliberately: a 4xx (client) and a 5xx (server).
# ---------------------------------------------------------------------------
show_status_codes() {
  rule "5. Reading status codes — a deliberate 404 and 500"
  echo "\$ curl -o /dev/null -s -w '%{http_code}' ${HTTPBIN}/status/404"
  local code404 code500
  # --retry 5 rides through httpbin's transient gateway 5xx (502/503/504) to
  # get the deterministic 404; a real 404 is NOT a transient error, so curl
  # returns it without retrying.
  code404="$(curl -o /dev/null -s --max-time 25 --retry 5 --retry-delay 1 -w '%{http_code}' "${HTTPBIN}/status/404")" || code404="000"
  printf '404 endpoint returned: HTTP %s  — %s\n' "${code404}" "$(classify_status "${code404}")"
  # No --retry here: curl treats 5xx as transient and would retry it away;
  # we WANT to see the server error, whatever 5xx httpbin returns this run.
  echo "\$ curl -o /dev/null -s -w '%{http_code}' ${HTTPBIN}/status/500"
  code500="$(curl -o /dev/null -s --max-time 25 -w '%{http_code}' "${HTTPBIN}/status/500")" || code500="000"
  printf '500 endpoint returned: HTTP %s  — %s\n' "${code500}" "$(classify_status "${code500}")"
  echo "Note: httpbin's error endpoints can themselves return 502/503/504 under load — still a 5xx, same lesson."
}

# ---------------------------------------------------------------------------
# 6. A systematic diagnose function: walk the decision tree for any URL.
# ---------------------------------------------------------------------------
diagnose() {
  local url="$1"
  rule "6. diagnose() — walk the decision tree for ${url}"
  # Ask curl for the status code and each timing gate in one shot.
  local out code namelookup connect appconnect
  out="$(curl -o /dev/null -s --max-time 25 \
    -w '%{http_code} %{time_namelookup} %{time_connect} %{time_appconnect}' \
    "${url}" 2>/dev/null)" || out=""

  if [ -z "${out}" ]; then
    echo "Gate 1 (DNS/connect): FAILED — host did not resolve or connect. Check the name and your network."
    return
  fi
  read -r code namelookup connect appconnect <<< "${out}"

  # Gate 1: DNS resolved if namelookup time is > 0.
  if awk "BEGIN{exit !(${namelookup} > 0)}"; then
    echo "Gate 1 (DNS):     ok  — resolved in ${namelookup}s"
  else
    echo "Gate 1 (DNS):     FAILED — hostname did not resolve"; return
  fi
  # Gate 2: TCP connected.
  if awk "BEGIN{exit !(${connect} > 0)}"; then
    echo "Gate 2 (connect): ok  — TCP connected in ${connect}s"
  else
    echo "Gate 2 (connect): FAILED — could not open a connection"; return
  fi
  # Gate 3: TLS handshake (only for https URLs).
  case "${url}" in
    https://*)
      if awk "BEGIN{exit !(${appconnect} > 0)}"; then
        echo "Gate 3 (TLS):     ok  — handshake done in ${appconnect}s"
      else
        echo "Gate 3 (TLS):     FAILED — certificate or handshake problem"; return
      fi ;;
    *) echo "Gate 3 (TLS):     n/a — not an https URL" ;;
  esac
  # Gate 4: status class.
  case "${code}" in
    2*) echo "Gate 4 (status):  ok  — HTTP ${code} (success)" ;;
    3*) echo "Gate 4 (status):  HTTP ${code} — a redirect; re-run with -L to follow it" ;;
    4*) echo "Gate 4 (status):  HTTP ${code} — CLIENT error: fix your request (URL, auth, or body)" ;;
    5*) echo "Gate 4 (status):  HTTP ${code} — SERVER error: the server failed a valid request" ;;
    *)  echo "Gate 4 (status):  HTTP ${code} — no valid response" ;;
  esac
}

main() {
  echo "Day 021 — Debug a Request with curl"
  echo "Test servers: ${EXAMPLE} and ${HTTPBIN}"
  if ! have_network; then
    echo
    echo "OFFLINE: could not reach ${EXAMPLE}. The commands below need network"
    echo "access. Connect to the internet and re-run: bash examples/debug_request.sh"
    exit 0
  fi
  show_verbose
  show_redirect
  show_timing
  show_headers_echo
  show_status_codes
  diagnose "${EXAMPLE}"
  diagnose "${HTTPBIN}/status/404"
  echo
  echo "Done. Every section above maps to a stage of the failed-request decision tree."
}

main "$@"
