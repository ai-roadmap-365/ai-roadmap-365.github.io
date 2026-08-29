#!/usr/bin/env bash
# Day 023 starter — CRUD Against a REST API.
# Complete the four exercises below. Each names the exact curl command to use.
# Run from the lab directory:  bash starter/rest_crud.sh
# The completed reference is in ../examples/rest_crud.sh — try it yourself first.
set -u

API="https://jsonplaceholder.typicode.com"
rule() { printf '\n=== %s ===\n' "$1"; }

echo "Day 023 starter — CRUD Against a REST API"
echo "Target: ${API}"

# Exercise 1 (READ): fetch one item and pretty-print its JSON representation.
# Replace the echo with:
#   curl -s "$API/posts/1" | python3 -m json.tool
rule "1. READ — GET /posts/1"
echo "EXERCISE — your turn: GET $API/posts/1 and pretty-print the JSON body"

# Exercise 2 (CREATE): POST a new post to the COLLECTION and print the status.
# Replace with:
#   curl -s -w '\nHTTP %{http_code}\n' -X POST \
#     -H "Content-Type: application/json" \
#     -d '{"title":"my post","body":"hello","userId":1}' \
#     "$API/posts"
rule "2. CREATE — POST /posts"
echo "EXERCISE — your turn: POST a JSON body to $API/posts and confirm HTTP 201"

# Exercise 3 (UPDATE): PUT a full replacement to the ITEM and print the status.
# Replace with:
#   curl -s -w '\nHTTP %{http_code}\n' -X PUT \
#     -H "Content-Type: application/json" \
#     -d '{"id":1,"title":"edited","body":"changed","userId":1}' \
#     "$API/posts/1"
rule "3. UPDATE — PUT /posts/1"
echo "EXERCISE — your turn: PUT a full new representation to $API/posts/1 (HTTP 200)"

# Exercise 4 (DELETE): DELETE the ITEM and print the status code.
# Replace with:
#   curl -s -w '\nHTTP %{http_code}\n' -X DELETE "$API/posts/1"
rule "4. DELETE — DELETE /posts/1"
echo "EXERCISE — your turn: DELETE $API/posts/1 and read the status code (HTTP 200)"

echo
echo "When all four are done, compare your output with ../examples/rest_crud.sh"
echo "Remember: POST targets the COLLECTION (/posts); GET, PUT, DELETE target an ITEM (/posts/1)."
