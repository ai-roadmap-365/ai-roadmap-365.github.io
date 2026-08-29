#!/usr/bin/env bash
# Day 023 lab — CRUD Against a REST API (completed reference implementation).
#
# Runs a full create-read-update-delete cycle against JSONPlaceholder
# (https://jsonplaceholder.typicode.com), a free public REST API that accepts
# CRUD requests and responds realistically. It *fakes* writes: a POST returns
# 201 and a new id, but nothing is actually stored — perfect for safe practice.
#
# Each section is one HTTP verb acting on a resource address, and prints the
# status code and the JSON body the server returned.
#
# Run from the lab directory:  bash examples/rest_crud.sh
#
# Requires network access. If the network (or the test server) is unreachable,
# each section degrades gracefully with a clear message and the script still
# exits 0, so it is safe to run offline.
set -u

API="https://jsonplaceholder.typicode.com"

rule() { printf '\n=== %s ===\n' "$1"; }

# Pretty-print JSON on stdin if python3 is available; otherwise pass it through.
pretty() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -m json.tool 2>/dev/null || cat
  else
    cat
  fi
}

# Return 0 if we appear to have network access to the API, else 1.
have_network() {
  curl -s -o /dev/null --max-time 12 "${API}/posts/1" 2>/dev/null
}

# ---------------------------------------------------------------------------
# READ (GET) one item: fetch a representation of post 1 by its address.
# ---------------------------------------------------------------------------
read_item() {
  rule "READ one item — GET /posts/1"
  echo "\$ curl -s ${API}/posts/1 | python3 -m json.tool"
  curl -s --max-time 20 "${API}/posts/1" | pretty \
    || echo "(could not reach ${API})"
}

# ---------------------------------------------------------------------------
# READ (GET) the collection: list posts (show the first few for brevity).
# ---------------------------------------------------------------------------
read_collection() {
  rule "READ the collection — GET /posts (first entries)"
  echo "\$ curl -s ${API}/posts | python3 -m json.tool | head -20"
  curl -s --max-time 20 "${API}/posts" | pretty | head -20 \
    || echo "(could not reach ${API})"
  # Report the total count so the learner sees it is a full collection.
  local count
  count="$(curl -s --max-time 20 "${API}/posts" \
    | grep -o '"id"' | wc -l | tr -d ' ')" || count="?"
  echo "... collection contains ${count} posts total."
}

# ---------------------------------------------------------------------------
# CREATE (POST) to the collection: the server assigns a new id, returns 201.
# ---------------------------------------------------------------------------
create_item() {
  rule "CREATE — POST /posts (returns 201 + the created resource)"
  echo "\$ curl -s -X POST -H 'Content-Type: application/json' -d '{...}' ${API}/posts"
  local body code
  body="$(curl -s --max-time 20 -X POST \
    -H "Content-Type: application/json" \
    -d '{"title":"my new post","body":"written today","userId":1}' \
    "${API}/posts")" || { echo "(could not reach ${API})"; return; }
  code="$(curl -s -o /dev/null --max-time 20 -X POST \
    -H "Content-Type: application/json" \
    -d '{"title":"my new post","body":"written today","userId":1}' \
    -w '%{http_code}' "${API}/posts")" || code="000"
  printf '%s' "${body}" | pretty
  echo "status: HTTP ${code}  (expect 201 Created — the server assigned the new id)"
}

# ---------------------------------------------------------------------------
# UPDATE (PUT) an item: replace post 1 entirely with the body we send.
# ---------------------------------------------------------------------------
update_item() {
  rule "UPDATE — PUT /posts/1 (replace the whole item)"
  echo "\$ curl -s -X PUT -H 'Content-Type: application/json' -d '{...}' ${API}/posts/1"
  local body code
  body="$(curl -s --max-time 20 -X PUT \
    -H "Content-Type: application/json" \
    -d '{"id":1,"title":"edited title","body":"edited body","userId":1}' \
    "${API}/posts/1")" || { echo "(could not reach ${API})"; return; }
  code="$(curl -s -o /dev/null --max-time 20 -X PUT \
    -H "Content-Type: application/json" \
    -d '{"id":1,"title":"edited title","body":"edited body","userId":1}' \
    -w '%{http_code}' "${API}/posts/1")" || code="000"
  printf '%s' "${body}" | pretty
  echo "status: HTTP ${code}  (expect 200 OK — the replaced representation)"
}

# ---------------------------------------------------------------------------
# DELETE an item: remove post 1. Idempotent — repeating it is harmless.
# ---------------------------------------------------------------------------
delete_item() {
  rule "DELETE — DELETE /posts/1 (remove the item)"
  echo "\$ curl -s -X DELETE ${API}/posts/1  -w 'HTTP %{http_code}'"
  local code
  code="$(curl -s -o /dev/null --max-time 20 -X DELETE \
    -w '%{http_code}' "${API}/posts/1")" || code="000"
  echo "status: HTTP ${code}  (expect 200 — an empty body; DELETE is idempotent)"
}

main() {
  echo "Day 023 — CRUD Against a REST API"
  echo "Target: ${API} (a free public REST API that fakes writes)"
  if ! have_network; then
    echo
    echo "OFFLINE: could not reach ${API}. The commands below need network"
    echo "access. Connect to the internet and re-run: bash examples/rest_crud.sh"
    exit 0
  fi
  read_item
  read_collection
  create_item
  update_item
  delete_item
  echo
  echo "Done. Two addresses (/posts and /posts/1) and five verbs drove the whole"
  echo "lifecycle. Note: JSONPlaceholder fakes writes, so the created id 101 is"
  echo "not re-fetchable — the status codes are real, the persistence is simulated."
}

main "$@"
