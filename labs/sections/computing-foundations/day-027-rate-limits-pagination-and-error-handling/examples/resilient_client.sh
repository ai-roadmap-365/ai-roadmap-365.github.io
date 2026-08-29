#!/usr/bin/env bash
# Day 027 lab — Resilient API client (completed reference implementation).
#
# Demonstrates the three habits of consuming a real API robustly, against two
# free public test servers (no account or API key needed):
#   * https://httpbin.org           — returns any status you ask for
#   * https://jsonplaceholder.typicode.com — a paginated posts API
#
#   1. backoff_retry — retries a 429 / 5xx / network failure with an
#      exponential, jittered delay, up to a hard cap, then GIVES UP GRACEFULLY
#      (it never loops forever), honoring a Retry-After header when present.
#   2. decide        — reads a 500 and a 404 and decides which to retry
#      (retry 5xx server errors; do NOT retry 4xx client errors).
#   3. paginate      — walks two pages of posts with _page/_limit and collects
#      the results across pages.
#
# Run from the lab directory:  bash examples/resilient_client.sh
# Offline it degrades to a self-test of the backoff logic and still exits 0.
#
# Tunable via environment (used by the tests to run fast):
#   MAX_ATTEMPTS (default 5)  BASE_DELAY (default 1)  DELAY_CAP (default 8)
set -u

HTTPBIN="https://httpbin.org"
JSONPH="https://jsonplaceholder.typicode.com"
PROBE="https://example.com"

: "${MAX_ATTEMPTS:=5}"
: "${BASE_DELAY:=1}"
: "${DELAY_CAP:=8}"
: "${CURL_MAX_TIME:=15}"   # per-request timeout (a hung request must not stall us)
: "${STABLE_TRIES:=6}"     # how many times decide() rides through transient 5xx

# Set to non-empty by the offline self-test to simulate a failing server
# without any network call at all.
: "${STUB_STATUS:=}"

RETRIES_MADE=0   # set by backoff_retry so callers can report it

have_network() { curl -s -o /dev/null --max-time 12 "${PROBE}" 2>/dev/null; }

# Print the response class for a numeric status code.
classify_status() {
  case "$1" in
    2*)   echo "success" ;;
    429)  echo "rate-limited — back off and retry" ;;
    4*)   echo "client error — fix the request, do not retry" ;;
    5*)   echo "server error — retry with backoff" ;;
    *)    echo "no response — network failure or timeout" ;;
  esac
}

# Echo "CODE RETRY_AFTER" for a URL. If STUB_STATUS is set, return it without
# touching the network (used offline to prove the retry loop terminates).
fetch_status() {
  local url="$1"
  if [ -n "${STUB_STATUS}" ]; then
    echo "${STUB_STATUS} ${STUB_RETRY_AFTER:-}"
    return 0
  fi
  local tmp code ra
  tmp="$(mktemp)"
  code="$(curl -s -o /dev/null -D "${tmp}" -w '%{http_code}' --max-time "${CURL_MAX_TIME}" "${url}" 2>/dev/null)" || code="000"
  ra="$(grep -i '^retry-after:' "${tmp}" 2>/dev/null | head -1 | sed 's/[^0-9]//g')"
  rm -f "${tmp}"
  echo "${code:-000} ${ra}"
}

# Retry 429 / 5xx / network failures with exponential backoff + jitter, capped
# at MAX_ATTEMPTS. ALWAYS terminates: attempt increments every pass and the cap
# check returns. Honors Retry-After when the server sends it.
backoff_retry() {
  local url="$1" label="${2:-request}"
  local attempt=1 delay="${BASE_DELAY}" code ra wait
  RETRIES_MADE=0
  echo "  [${label}] up to ${MAX_ATTEMPTS} attempts, base ${BASE_DELAY}s, cap ${DELAY_CAP}s"
  while : ; do
    read -r code ra <<< "$(fetch_status "${url}")"
    echo "  attempt ${attempt}: HTTP ${code} ($(classify_status "${code}"))"

    case "${code}" in
      2*) echo "  -> success on attempt ${attempt}"; return 0 ;;
      429) : ;;                                   # retryable, fall through
      4*) echo "  -> client error; NOT retrying (fix the request)"; return 0 ;;
      5*|000) : ;;                                # retryable, fall through
    esac

    if [ "${attempt}" -ge "${MAX_ATTEMPTS}" ]; then
      echo "  -> reached the retry cap of ${MAX_ATTEMPTS}; giving up gracefully"
      return 0
    fi

    if [ -n "${ra}" ]; then
      wait="${ra}"
      echo "     obeying Retry-After: ${wait}s"
    else
      wait="$(awk -v d="${delay}" 'BEGIN { srand(); printf "%.2f", d + rand() }')"
      echo "     backoff: ~${delay}s (jittered to ${wait}s)"
    fi
    sleep "${wait}"

    RETRIES_MADE=$((RETRIES_MADE + 1))
    attempt=$((attempt + 1))
    delay=$((delay * 2))
    [ "${delay}" -gt "${DELAY_CAP}" ] && delay="${DELAY_CAP}"
  done
}

# Read a status, retrying ONLY on transient infrastructure failures — a
# no-response (000) or a gateway error (502/503/504) — to ride through the free
# test server's hiccups and reach its real, deliberate status. It does NOT
# retry a genuine 500, 4xx, or 2xx — that is the answer we came to read. (A 500
# is the origin's deliberate error; 502/503/504 are proxy/gateway errors that
# are usually transient.)
fetch_status_stable() {
  local url="$1" tries="${STABLE_TRIES}" i=1 code ra
  while [ "${i}" -le "${tries}" ]; do
    read -r code ra <<< "$(fetch_status "${url}")"
    case "${code}" in
      000|502|503|504) sleep 1 ;;               # transient — try again
      *) echo "${code} ${ra}"; return 0 ;;      # a real answer — take it
    esac
    i=$((i + 1))
  done
  echo "${code} ${ra}"
}

# Read one status and state the retry decision without acting on it.
decide() {
  local url="$1" code ra
  read -r code ra <<< "$(fetch_status_stable "${url}")"
  case "${code}" in
    5*) echo "  ${url}: HTTP ${code} — SERVER error -> RETRY with backoff" ;;
    429) echo "  ${url}: HTTP ${code} — rate-limited -> RETRY after waiting" ;;
    4*) echo "  ${url}: HTTP ${code} — CLIENT error -> do NOT retry" ;;
    2*) echo "  ${url}: HTTP ${code} — success -> nothing to retry" ;;
    *)  echo "  ${url}: no response -> network failure (retry only if idempotent)" ;;
  esac
}

# Walk two pages of posts with _page/_limit and collect the count across pages.
paginate() {
  local total=0 page body count
  for page in 1 2; do
    body="$(curl -s --max-time "${CURL_MAX_TIME}" "${JSONPH}/posts?_page=${page}&_limit=5" 2>/dev/null)" || body=""
    if [ -z "${body}" ]; then
      echo "  page ${page}: (could not fetch — transient error; try again)"
      continue
    fi
    count="$(printf '%s' "${body}" | python3 -c 'import sys, json; print(len(json.load(sys.stdin)))' 2>/dev/null)" || count=0
    echo "  page ${page}: ${count} items"
    total=$((total + count))
  done
  echo "  collected ${total} posts across 2 pages"
}

run_offline_selftest() {
  echo "Self-test: backoff against a stubbed always-503 server (no network)."
  STUB_STATUS=503 MAX_ATTEMPTS=3 BASE_DELAY=0 DELAY_CAP=0 backoff_retry "stub:always-fails" "selftest"
  echo "Self-test complete: the loop terminated after ${RETRIES_MADE} retries."
}

main() {
  echo "Day 027 — Resilient API client"
  echo "Test servers: ${HTTPBIN} and ${JSONPH}"

  if [ "${1:-}" = "--selftest" ]; then
    run_offline_selftest
    exit 0
  fi

  if ! have_network; then
    echo
    echo "OFFLINE: cannot reach ${PROBE}. Running the offline backoff self-test instead."
    run_offline_selftest
    echo "Reconnect to the internet and re-run for the live 429, error, and pagination demos."
    exit 0
  fi

  echo
  echo "== 1. Backoff against an endpoint that ALWAYS returns 429 =="
  backoff_retry "${HTTPBIN}/status/429" "429-demo"
  echo "   made ${RETRIES_MADE} retries before giving up"

  echo
  echo "== 2. Read a 500 and a 404 — decide whether to retry =="
  decide "${HTTPBIN}/status/500"
  decide "${HTTPBIN}/status/404"
  echo "   (a transient 502/503 in place of 500 is still a 5xx — same decision)"

  echo
  echo "== 3. Paginate posts with _page and _limit =="
  paginate

  echo
  echo "Done. Backoff terminated, errors were classified, and pages were collected."
}

main "$@"
