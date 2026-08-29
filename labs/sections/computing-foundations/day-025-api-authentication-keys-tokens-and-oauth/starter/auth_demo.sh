#!/usr/bin/env bash
# Day 025 lab — YOUR working file.
# Complete the 4 numbered exercises below. Each names the exact curl command
# to run. httpbin.org accepts ANY credentials, so no real key is needed —
# every value here is an obviously fake placeholder.
#
# Run it with:   bash starter/auth_demo.sh
# When you are done, none of the "NOT DONE YET" placeholder lines should remain.
set -uo pipefail

API="https://httpbin.org"
CURL=(curl -s --max-time 25 --retry 5 --retry-delay 2)

echo "=== API Authentication Demo (starter) ==="

# Skip the live requests when offline so the script never hangs.
if ! curl -s -o /dev/null --max-time 12 "${API}/status/200" 2>/dev/null; then
  echo "No network access — connect to the internet and re-run to complete the exercises."
  exit 0
fi

# ---------------------------------------------------------------------------
# Exercise 1: Basic auth with CORRECT credentials — expect HTTP 200.
#   Replace the placeholder echo below with a command that prints just the code:
#     "${CURL[@]}" -o /dev/null -w '%{http_code}\n' -u user:pass \
#       "${API}/basic-auth/user/pass"
echo "--- Exercise 1: Basic auth, correct credentials (expect 200) ---"
echo "NOT DONE YET — run the curl -u user:pass command described above"

# ---------------------------------------------------------------------------
# Exercise 2: Basic auth with WRONG credentials — expect HTTP 401.
#   Replace the placeholder echo below with the same command but a wrong password:
#     "${CURL[@]}" -o /dev/null -w '%{http_code}\n' -u user:wrongpass \
#       "${API}/basic-auth/user/pass"
echo "--- Exercise 2: Basic auth, wrong credentials (expect 401) ---"
echo "NOT DONE YET — run the curl -u user:wrongpass command described above"

# ---------------------------------------------------------------------------
# Exercise 3: Send a BEARER TOKEN in the Authorization header.
#   Replace the placeholder echo below with:
#     "${CURL[@]}" -H "Authorization: Bearer token-example-123" "${API}/bearer"
#   The endpoint should return JSON with "authenticated": true and your token.
echo "--- Exercise 3: Bearer token in the Authorization header ---"
echo "NOT DONE YET — run the curl -H 'Authorization: Bearer ...' command described above"

# ---------------------------------------------------------------------------
# Exercise 4: Read a bearer token from an ENVIRONMENT VARIABLE (the safe pattern).
#   Set a fake token in a variable, then reference the variable so the secret
#   never appears inline. Replace the placeholder echo below with these two lines:
#     export DEMO_TOKEN="token-example-123"
#     "${CURL[@]}" -H "Authorization: Bearer ${DEMO_TOKEN}" "${API}/bearer"
echo "--- Exercise 4: Bearer token from an environment variable ---"
echo "NOT DONE YET — export DEMO_TOKEN and run curl with \$DEMO_TOKEN as described above"

echo "=== End of demo ==="
