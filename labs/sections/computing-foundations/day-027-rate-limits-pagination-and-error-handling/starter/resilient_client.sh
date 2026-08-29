#!/usr/bin/env bash
# Day 027 lab — Resilient API client (STARTER).
#
# Your job: complete the four numbered exercises below, then run this file:
#     bash starter/resilient_client.sh
# Compare it against the finished reference in ../examples/resilient_client.sh
# only after you have tried each exercise yourself.
#
# The helper functions are provided. You fill in the four decisions that make a
# client resilient: the retry cap, the jitter, the retry decision, and the
# pagination URL. Each exercise ships with a safe placeholder so the file runs,
# marked with the sentinel FILL_ME so the tests can see what is unfinished.
set -u

HTTPBIN="https://httpbin.org"
JSONPH="https://jsonplaceholder.typicode.com"
PROBE="https://example.com"

# ---------------------------------------------------------------------------
# Exercise 1 — Give the retry loop a HARD CAP and a starting delay.
#   A retry loop with no cap becomes an infinite loop the moment a failure is
#   permanent. Set:
#     MAX_ATTEMPTS to 5   (stop after 5 tries)
#     BASE_DELAY   to 1   (first backoff wait, in seconds)
#     DELAY_CAP    to 8   (never wait longer than this)
#   Replace each 0 below.
# ---------------------------------------------------------------------------
MAX_ATTEMPTS=0   # FILL_ME (Exercise 1): set to 5
BASE_DELAY=0     # FILL_ME (Exercise 1): set to 1
DELAY_CAP=0      # FILL_ME (Exercise 1): set to 8

: "${STUB_STATUS:=}"
RETRIES_MADE=0

have_network() { curl -s -o /dev/null --max-time 12 "${PROBE}" 2>/dev/null; }

classify_status() {
  case "$1" in
    2*)  echo "success" ;;
    429) echo "rate-limited — back off and retry" ;;
    4*)  echo "client error — fix the request, do not retry" ;;
    5*)  echo "server error — retry with backoff" ;;
    *)   echo "no response — network failure or timeout" ;;
  esac
}

fetch_status() {
  local url="$1"
  if [ -n "${STUB_STATUS}" ]; then echo "${STUB_STATUS} ${STUB_RETRY_AFTER:-}"; return 0; fi
  local tmp code ra
  tmp="$(mktemp)"
  code="$(curl -s -o /dev/null -D "${tmp}" -w '%{http_code}' --max-time 15 "${url}" 2>/dev/null)" || code="000"
  ra="$(grep -i '^retry-after:' "${tmp}" 2>/dev/null | head -1 | sed 's/[^0-9]//g')"
  rm -f "${tmp}"
  echo "${code:-000} ${ra}"
}

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
      429) : ;;
      4*) echo "  -> client error; NOT retrying (fix the request)"; return 0 ;;
      5*|000) : ;;
    esac

    if [ "${attempt}" -ge "${MAX_ATTEMPTS}" ]; then
      echo "  -> reached the retry cap of ${MAX_ATTEMPTS}; giving up gracefully"
      return 0
    fi

    if [ -n "${ra}" ]; then
      wait="${ra}"
      echo "     obeying Retry-After: ${wait}s"
    else
      # -----------------------------------------------------------------------
      # Exercise 2 — Add JITTER to the backoff wait.
      #   A fixed wait makes a crowd of clients retry in lockstep and stampede
      #   the server again. Replace the line below so `wait` becomes the delay
      #   PLUS a small random fraction of a second, e.g.:
      #     wait="$(awk -v d="${delay}" 'BEGIN { srand(); printf "%.2f", d + rand() }')"
      # -----------------------------------------------------------------------
      wait="${delay}"   # FILL_ME (Exercise 2): add jitter to this delay
      echo "     backoff: ~${delay}s (waiting ${wait}s)"
    fi
    sleep "${wait}"

    RETRIES_MADE=$((RETRIES_MADE + 1))
    attempt=$((attempt + 1))
    delay=$((delay * 2))
    [ "${delay}" -gt "${DELAY_CAP}" ] && delay="${DELAY_CAP}"
  done
}

fetch_status_stable() {
  local url="$1" tries=6 i=1 code ra
  while [ "${i}" -le "${tries}" ]; do
    read -r code ra <<< "$(fetch_status "${url}")"
    case "${code}" in
      000|502|503|504) sleep 1 ;;
      *) echo "${code} ${ra}"; return 0 ;;
    esac
    i=$((i + 1))
  done
  echo "${code} ${ra}"
}

decide() {
  local url="$1" code ra
  read -r code ra <<< "$(fetch_status_stable "${url}")"
  # ---------------------------------------------------------------------------
  # Exercise 3 — Classify the status and state the retry DECISION.
  #   Fill the two branches marked FILL_ME so that:
  #     a 5xx  -> "SERVER error -> RETRY with backoff"
  #     a 4xx  -> "CLIENT error -> do NOT retry"
  # ---------------------------------------------------------------------------
  case "${code}" in
    5*) echo "  ${url}: HTTP ${code} — FILL_ME (Exercise 3): SERVER error -> RETRY with backoff" ;;
    429) echo "  ${url}: HTTP ${code} — rate-limited -> RETRY after waiting" ;;
    4*) echo "  ${url}: HTTP ${code} — FILL_ME (Exercise 3): CLIENT error -> do NOT retry" ;;
    2*) echo "  ${url}: HTTP ${code} — success -> nothing to retry" ;;
    *)  echo "  ${url}: no response -> network failure (retry only if idempotent)" ;;
  esac
}

paginate() {
  local total=0 page body count
  for page in 1 2; do
    # -------------------------------------------------------------------------
    # Exercise 4 — Build the PAGINATED URL and collect across pages.
    #   Replace the URL below so it requests page ${page} with 5 items:
    #     "${JSONPH}/posts?_page=${page}&_limit=5"
    #   (The starter fetches only page 1 with no limit, so it does not paginate.)
    # -------------------------------------------------------------------------
    body="$(curl -s --max-time 15 "${JSONPH}/posts?_limit=5" 2>/dev/null)" || body=""   # FILL_ME (Exercise 4): add _page=${page}
    if [ -z "${body}" ]; then echo "  page ${page}: (could not fetch)"; continue; fi
    count="$(printf '%s' "${body}" | python3 -c 'import sys, json; print(len(json.load(sys.stdin)))' 2>/dev/null)" || count=0
    echo "  page ${page}: ${count} items"
    total=$((total + count))
  done
  echo "  collected ${total} posts across 2 pages"
}

run_offline_selftest() {
  echo "Self-test: backoff against a stubbed always-503 server (no network)."
  STUB_STATUS=503 backoff_retry "stub:always-fails" "selftest"
  echo "Self-test complete: the loop terminated after ${RETRIES_MADE} retries."
}

main() {
  echo "Day 027 — Resilient API client (starter)"
  if [ "${1:-}" = "--selftest" ]; then run_offline_selftest; exit 0; fi
  if ! have_network; then
    echo "OFFLINE: cannot reach ${PROBE}. Running the offline backoff self-test instead."
    run_offline_selftest
    exit 0
  fi
  echo; echo "== 1. Backoff against an endpoint that ALWAYS returns 429 =="
  backoff_retry "${HTTPBIN}/status/429" "429-demo"
  echo "   made ${RETRIES_MADE} retries before giving up"
  echo; echo "== 2. Read a 500 and a 404 — decide whether to retry =="
  decide "${HTTPBIN}/status/500"
  decide "${HTTPBIN}/status/404"
  echo; echo "== 3. Paginate posts with _page and _limit =="
  paginate
  echo; echo "Done."
}

main "$@"
