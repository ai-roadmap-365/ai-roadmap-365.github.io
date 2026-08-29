#!/usr/bin/env bash
# Day 021 starter — Debug a Request with curl.
# Complete the five exercises below. Each names the exact curl command to use.
# Run from the lab directory:  bash starter/debug_request.sh
# The completed reference is in ../examples/debug_request.sh — try it yourself first.
set -u

EXAMPLE="https://example.com"
HTTPBIN="https://httpbin.org"
rule() { printf '\n=== %s ===\n' "$1"; }

echo "Day 021 starter — Debug a Request with curl"

# Exercise 1: show the full conversation.
# Replace the echo with: curl -v -o /dev/null --max-time 15 "$EXAMPLE" 2>&1 | grep -E '^[*<>]'
rule "1. Verbose conversation"
echo "EXERCISE — your turn: run curl -v against $EXAMPLE and show the * < > lines"

# Exercise 2: follow a redirect.
# Replace with: curl -o /dev/null -sIL --max-time 25 -w '%{http_code}\n' "$HTTPBIN/redirect/1"
rule "2. Follow a redirect"
echo "EXERCISE — your turn: follow $HTTPBIN/redirect/1 with -L and print the final status"

# Exercise 3: timing breakdown.
# Replace with: curl -o /dev/null -s --max-time 15 -w 'dns:%{time_namelookup} connect:%{time_connect} tls:%{time_appconnect} total:%{time_total}\n' "$EXAMPLE"
rule "3. Timing breakdown"
echo "EXERCISE — your turn: print the DNS/connect/TLS/total timings for $EXAMPLE"

# Exercise 4: echo the headers you sent.
# Replace with: curl -sf --max-time 25 --retry 4 -H "Accept: application/json" "$HTTPBIN/headers"
rule "4. Headers echo"
echo "EXERCISE — your turn: send an Accept header to $HTTPBIN/headers and show the echo"

# Exercise 5: read a deliberate 404 status code.
# Replace with: curl -o /dev/null -s --max-time 25 --retry 5 -w '%{http_code}\n' "$HTTPBIN/status/404"
rule "5. Read a status code"
echo "EXERCISE — your turn: print the status code returned by $HTTPBIN/status/404"

echo
echo "When all five are done, compare your output with ../examples/debug_request.sh"
