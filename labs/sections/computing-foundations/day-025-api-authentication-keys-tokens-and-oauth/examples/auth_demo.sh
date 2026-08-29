#!/usr/bin/env bash
# Day 025 lab — completed reference implementation.
# Authenticate to a public test API (httpbin.org) with each common scheme:
#   1. Basic auth, correct credentials      -> 200
#   2. Basic auth, wrong credentials        -> 401
#   3. Bearer token in the Authorization header
#   4. An API key in a custom header, echoed back
#   5. A bearer token read from an environment variable (the safe pattern)
#
# httpbin's auth endpoints accept ANY credentials, so no real key is needed.
# Every credential in this script is an obviously fake placeholder.
# If the network is unavailable, the script says so and exits 0 (nothing to prove offline).
set -uo pipefail

API="https://httpbin.org"
# curl options: fail quietly on server errors, cap the wait, ride past transient 5xx.
CURL=(curl -s --max-time 25 --retry 5 --retry-delay 2)

echo "=== API Authentication Demo ==="
echo "Target: ${API} (public test server; accepts any credentials)"
echo

# Bail out gracefully when offline so the demo never hangs or errors.
if ! curl -s -o /dev/null --max-time 12 "${API}/status/200" 2>/dev/null; then
  echo "No network access — skipping the live requests."
  echo "Online, this script sends Basic auth, a bearer token, and a key header to ${API}."
  echo "=== End of demo ==="
  exit 0
fi

echo "--- 1. Basic auth with CORRECT credentials (expect 200) ---"
echo "\$ curl -u user:pass ${API}/basic-auth/user/pass"
code="$("${CURL[@]}" -o /dev/null -w '%{http_code}' -u user:pass "${API}/basic-auth/user/pass")"
echo "HTTP status: ${code}"
echo

echo "--- 2. Basic auth with WRONG credentials (expect 401) ---"
echo "\$ curl -u user:wrongpass ${API}/basic-auth/user/pass"
code="$("${CURL[@]}" -o /dev/null -w '%{http_code}' -u user:wrongpass "${API}/basic-auth/user/pass")"
echo "HTTP status: ${code}"
echo

echo "--- 3. Bearer token in the Authorization header ---"
echo "\$ curl -H 'Authorization: Bearer token-example-123' ${API}/bearer"
"${CURL[@]}" -H "Authorization: Bearer token-example-123" "${API}/bearer"
echo

echo "--- 4. API key in a custom header, echoed back by the server ---"
echo "\$ curl -H 'X-API-Key: demo-key' ${API}/headers"
"${CURL[@]}" -H "X-API-Key: demo-key" "${API}/headers"
echo

echo "--- 5. Bearer token READ FROM AN ENVIRONMENT VARIABLE (the safe pattern) ---"
# The secret lives in a variable, not inline in the command. Here it is a fake value;
# for a real API you would 'export' the key from a gitignored .env, never hard-code it.
export DEMO_TOKEN="token-from-env-example"
echo "\$ export DEMO_TOKEN=...   (kept out of code and git)"
echo "\$ curl -H \"Authorization: Bearer \$DEMO_TOKEN\" ${API}/bearer"
"${CURL[@]}" -H "Authorization: Bearer ${DEMO_TOKEN}" "${API}/bearer"
echo

echo "=== End of demo ==="
