#!/usr/bin/env bash
# Day 022 lab — Call Your First APIs (completed reference implementation).
#
# Calls three free, public, no-key web APIs and explains each response:
#   * JSONPlaceholder (https://jsonplaceholder.typicode.com) — fake REST data
#   * httpbin        (https://httpbin.org)                    — echoes your request
#   * Open Notify    (http://api.open-notify.org)             — live ISS position
#
# JSON is pretty-printed with `python3 -m json.tool`, which is always available
# on macOS and Linux — jq is NOT required. If a call returns something that is
# not JSON (an outage page, say), we print the raw body instead of crashing.
#
# Run from the lab directory:  bash examples/call_apis.sh
#
# Requires network access. Offline (or if a service is transiently down), each
# section degrades gracefully with a clear message and the script still exits 0.
set -u

JSONPH="https://jsonplaceholder.typicode.com"
HTTPBIN="https://httpbin.org"
ISS="http://api.open-notify.org/iss-now.json"

rule() { printf '\n=== %s ===\n' "$1"; }

# Pretty-print stdin as JSON, or fall back to printing it raw if it is not JSON.
pretty() {
  local body; body="$(cat)"
  if printf '%s' "${body}" | python3 -m json.tool 2>/dev/null; then
    return 0
  fi
  echo "(response was not valid JSON — showing raw body / message):"
  printf '%s\n' "${body}"
}

# Return 0 if we appear to have network access, else 1.
have_network() {
  curl -s -o /dev/null --max-time 12 "${JSONPH}/todos/1" 2>/dev/null
}

# GET a URL with sane timeouts/retries; prints the body, or empty on failure.
fetch() {
  curl -s --max-time 25 --retry 3 --retry-delay 2 "$1" 2>/dev/null
}

# ---------------------------------------------------------------------------
# 1. JSONPlaceholder — a single to-do resource at /todos/1.
# ---------------------------------------------------------------------------
show_todo() {
  rule "1. JSONPlaceholder — GET /todos/1 (a single to-do item)"
  echo "\$ curl ${JSONPH}/todos/1"
  local body; body="$(fetch "${JSONPH}/todos/1")"
  if [ -z "${body}" ]; then echo "(could not reach ${JSONPH})"; return; fi
  printf '%s' "${body}" | pretty
  echo "Explanation: a GET to the /todos/1 endpoint returns one to-do as JSON."
  echo "The 'title' field is the to-do's text; 'completed' is true/false."
}

# ---------------------------------------------------------------------------
# 2. JSONPlaceholder — a single user resource at /users/1 (nested JSON).
# ---------------------------------------------------------------------------
show_user() {
  rule "2. JSONPlaceholder — GET /users/1 (a user, with nested objects)"
  echo "\$ curl ${JSONPH}/users/1"
  local body; body="$(fetch "${JSONPH}/users/1")"
  if [ -z "${body}" ]; then echo "(could not reach ${JSONPH})"; return; fi
  printf '%s' "${body}" | pretty
  echo "Explanation: same API, different endpoint -> different resource."
  echo "Note the nested 'address' and 'company' objects — JSON can nest."
}

# ---------------------------------------------------------------------------
# 3. httpbin — /get echoes back the request it received.
# ---------------------------------------------------------------------------
show_httpbin() {
  rule "3. httpbin — GET /get?course=365-days-of-ai&day=22 (echoes your request)"
  echo "\$ curl \"${HTTPBIN}/get?course=365-days-of-ai&day=22\""
  local body; body="$(fetch "${HTTPBIN}/get?course=365-days-of-ai&day=22")"
  if [ -z "${body}" ]; then
    echo "(could not reach ${HTTPBIN} — it is a shared free service and is"
    echo " sometimes overloaded; wait a minute and re-run. This is not your bug.)"
    return
  fi
  printf '%s' "${body}" | pretty
  echo "Explanation: the 'args' object shows the query parameters the server saw"
  echo "(course, day); the 'headers' object shows the headers curl sent."
}

# ---------------------------------------------------------------------------
# 4. Open Notify — the current position of the International Space Station.
# ---------------------------------------------------------------------------
show_iss() {
  rule "4. Open Notify — GET iss-now.json (LIVE space-station position)"
  echo "\$ curl ${ISS}"
  local body; body="$(fetch "${ISS}")"
  if [ -z "${body}" ]; then echo "(could not reach ${ISS})"; return; fi
  printf '%s' "${body}" | pretty
  echo "Explanation: 'iss_position' holds the latitude/longitude RIGHT NOW."
  echo "Run again in a minute and the numbers change — a real satellite is moving."
  echo "Note: this endpoint is served over plain http://, not https://."
}

main() {
  echo "Day 022 — Call Your First APIs"
  echo "Three free public APIs, no key required."
  if ! have_network; then
    echo
    echo "OFFLINE: could not reach ${JSONPH}. Every call below needs network"
    echo "access. Connect to the internet and re-run: bash examples/call_apis.sh"
    exit 0
  fi
  show_todo
  show_user
  show_httpbin
  show_iss
  echo
  echo "Done. Each section above was one API call: a request to an endpoint and"
  echo "a JSON response you read fields out of."
}

main "$@"
