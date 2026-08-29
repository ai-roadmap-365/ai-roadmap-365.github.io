#!/usr/bin/env bash
# Day 022 starter — Call Your First APIs.
# Complete the four exercises below. Each names the exact curl command to run.
# Run from the lab directory:  bash starter/call_apis.sh
# The completed reference is in ../examples/call_apis.sh — try it yourself first.
set -u

JSONPH="https://jsonplaceholder.typicode.com"
HTTPBIN="https://httpbin.org"
ISS="http://api.open-notify.org/iss-now.json"
rule() { printf '\n=== %s ===\n' "$1"; }

echo "Day 022 starter — Call Your First APIs"
echo "Tip: pipe any command through '| python3 -m json.tool' to pretty-print JSON."

# Exercise 1: fetch a single to-do from JSONPlaceholder.
# Replace the echo with:
#   curl -s "$JSONPH/todos/1" | python3 -m json.tool
rule "1. JSONPlaceholder — GET /todos/1"
echo "EXERCISE — your turn: GET $JSONPH/todos/1 and pretty-print the JSON."
echo "Record the 'title' field on the worksheet."

# Exercise 2: fetch a single user from JSONPlaceholder.
# Replace with:
#   curl -s "$JSONPH/users/1" | python3 -m json.tool
rule "2. JSONPlaceholder — GET /users/1"
echo "EXERCISE — your turn: GET $JSONPH/users/1 and pretty-print the JSON."
echo "Record ONE field of your choice (e.g. 'name' or 'email') on the worksheet."

# Exercise 3: echo your request with httpbin, including a query parameter.
# Replace with:
#   curl -s "$HTTPBIN/get?course=365-days-of-ai&day=22" | python3 -m json.tool
rule "3. httpbin — GET /get with a query parameter"
echo "EXERCISE — your turn: GET $HTTPBIN/get?course=365-days-of-ai&day=22"
echo "Find your 'course' and 'day' in the echoed 'args' object."

# Exercise 4: read the LIVE position of the space station from Open Notify.
# Replace with:
#   curl -s "$ISS" | python3 -m json.tool
rule "4. Open Notify — GET iss-now.json (live ISS position)"
echo "EXERCISE — your turn: GET $ISS  (note: plain http://, not https://)"
echo "Record the current latitude and longitude on the worksheet."

echo
echo "When all four are done, compare your output with ../examples/call_apis.sh"
