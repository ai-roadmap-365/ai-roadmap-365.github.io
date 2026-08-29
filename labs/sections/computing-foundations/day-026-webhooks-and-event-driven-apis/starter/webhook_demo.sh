#!/usr/bin/env bash
# Day 026 starter — Simulate a Webhook Delivery.
#
# Complete the FOUR exercises below. Each names the exact command to use.
# You will play both sides of a webhook: the SENDER that signs and delivers a
# payload, and the RECEIVER that verifies it. The completed reference is in
# ../examples/webhook_demo.sh — try to build it yourself first.
#
# Run from the lab directory:  bash starter/webhook_demo.sh
set -u

# The sample event. Use printf '%s' (NOT echo) so no trailing newline is added
# and the bytes you SIGN are exactly the bytes you SEND.
PAYLOAD='{"event":"invoice.paid","id":"evt_28a7","data":{"amount":4200,"currency":"usd"}}'

# A FAKE secret, for the demo only. Never hard-code a real secret (see security.md).
SECRET='whsec_demo_do_not_use_in_production'

HTTPBIN='https://httpbin.org'

rule() { printf '\n=== %s ===\n' "$1"; }

echo "Day 026 starter — Simulate a Webhook Delivery"

# ---------------------------------------------------------------------------
# Exercise 1: compute the signature (what the SENDER does).
# Replace the echo with:
#   printf '%s' "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET"
# It should print a 64-hex-character digest.
# ---------------------------------------------------------------------------
rule "1. Compute the signature"
echo "EXERCISE — your turn: HMAC-SHA-256 the PAYLOAD with the SECRET"

# ---------------------------------------------------------------------------
# Exercise 2: deliver the payload to the echo endpoint (what the RECEIVER sees).
# Replace the echo with a POST that carries the body and a signature header:
#   sig=$(printf '%s' "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.*= //')
#   curl -sf --max-time 25 --retry 6 --retry-delay 2 --retry-all-errors \
#     -X POST "$HTTPBIN/post" \
#     -H 'Content-Type: application/json' \
#     -H 'X-Webhook-Event: invoice.paid' \
#     -H "X-Webhook-Signature: sha256=$sig" \
#     -d "$PAYLOAD"
# httpbin echoes your body and headers back — that echo is what a receiver parses.
# ---------------------------------------------------------------------------
rule "2. Deliver to the echo endpoint"
echo "EXERCISE — your turn: POST the PAYLOAD to $HTTPBIN/post and read the echo"

# ---------------------------------------------------------------------------
# Exercise 3: verify by recomputing and comparing (what the RECEIVER does).
# Replace the echo with:
#   sent=$(printf '%s'   "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.*= //')
#   recomputed=$(printf '%s' "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.*= //')
#   [ "$sent" = "$recomputed" ] && echo "MATCH -> accept" || echo "MISMATCH -> reject"
# Then repeat with a TAMPERED payload (change 4200 to 999999) and confirm it MISMATCHES.
# ---------------------------------------------------------------------------
rule "3. Verify the signature"
echo "EXERCISE — your turn: recompute the signature and compare; then try a tampered body"

# ---------------------------------------------------------------------------
# Exercise 4: simulate a retry loop (what the SENDER does on a non-2xx).
# Replace the echo with a loop over simulated statuses that stops on a 2xx:
#   for code in 503 503 200; do
#     if [ "$code" -ge 200 ] && [ "$code" -lt 300 ]; then
#       echo "returned $code -> acknowledged, stop retrying"; break
#     else
#       echo "returned $code -> not 2xx, retrying after backoff..."
#     fi
#   done
# ---------------------------------------------------------------------------
rule "4. Retry on non-2xx"
echo "EXERCISE — your turn: loop over 503 503 200 and stop retrying on the 200"

echo
echo "When all four are done, compare your output with ../examples/webhook_demo.sh"
