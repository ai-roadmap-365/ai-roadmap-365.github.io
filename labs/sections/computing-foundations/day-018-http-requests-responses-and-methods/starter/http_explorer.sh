#!/usr/bin/env bash
# Day 018 lab — Speak HTTP by Hand (YOUR working file).
#
# Complete the FOUR numbered exercises below by replacing each
#   : "EXERCISE n — ..."      (a no-op placeholder line)
# with the exact curl command named in its comment. The finished reference
# version is in examples/http_explorer.sh — run that first to see the goal.
#
# Run from the lab directory:
#   bash starter/http_explorer.sh
set -u

GOOD_URL="https://example.com"
HTTPBIN="https://httpbin.org"

echo "=== HTTP Explorer (starter) ==="

# A quick network gate so the script degrades gracefully offline.
if ! curl -s -o /dev/null --max-time 8 "${GOOD_URL}"; then
  echo "OFFLINE — no network reachable. Reconnect and rerun to do the exercises."
  echo "=== End (offline) ==="
  exit 0
fi
echo "Network reachable: yes"
echo "------------------------------------------------------------"

# ---------------------------------------------------------------------------
# EXERCISE 1 — See BOTH messages with the verbose flag.
#   Run:  curl -v https://example.com
#   Lines starting '>' are your request; lines starting '<' are the response,
#   beginning with the status line. (This prints the HTML body too — that's ok.)
echo "EXERCISE 1 — curl -v ${GOOD_URL}"
: "EXERCISE 1 — replace this line with: curl -v \"${GOOD_URL}\""
echo "------------------------------------------------------------"

# ---------------------------------------------------------------------------
# EXERCISE 2 — Read ONLY the status code.
#   Run:  curl -s -o /dev/null -w "%{http_code}\n" https://example.com
#   -s silences the meter, -o /dev/null throws the body away, -w prints the code.
#   You should see 200.
echo "EXERCISE 2 — status code only for ${GOOD_URL}"
: "EXERCISE 2 — replace this line with the curl -s -o /dev/null -w command above"
echo "------------------------------------------------------------"

# ---------------------------------------------------------------------------
# EXERCISE 3 — POST a JSON body and watch it echoed back.
#   Run:  curl -X POST -H "Content-Type: application/json" \
#              -d '{"hello":"world"}' https://httpbin.org/post
#   -X POST sets the method, -H adds a header, -d supplies the body (and makes
#   it a POST). Look for your data in the response's "json" field.
#   (If httpbin.org is busy and returns 503, retry, or use https://httpbingo.org/post.)
echo "EXERCISE 3 — POST a JSON body to ${HTTPBIN}/post"
: "EXERCISE 3 — replace this line with the curl -X POST ... command above"
echo "------------------------------------------------------------"

# ---------------------------------------------------------------------------
# EXERCISE 4 — Trigger a 404 on purpose.
#   Run:  curl -s -o /dev/null -w "%{http_code}\n" https://httpbin.org/status/404
#   The test service returns whatever status you ask for. You should see 404.
echo "EXERCISE 4 — deliberately request a 404 from ${HTTPBIN}/status/404"
: "EXERCISE 4 — replace this line with the curl -s -o /dev/null -w 404 command above"
echo "------------------------------------------------------------"

echo "=== End of HTTP Explorer (starter) ==="
