#!/usr/bin/env bash
# Day 026 lab — Simulate a Webhook Delivery (completed reference implementation).
#
# A real webhook needs a public server that another company's system can reach.
# You do not have one, so this script plays BOTH roles on your own machine:
#   1. SENDER  — compute the HMAC signature for a sample event payload.
#   2. RECEIVER — POST the payload to a free echo service (httpbin.org) so you
#      can see exactly what a webhook receiver would receive, then recompute
#      and compare the signature (accept a genuine one, reject a forged one).
#   3. RELIABILITY — run a retry loop that re-POSTs on a simulated non-2xx
#      status and stops once it gets a 2xx acknowledgement.
#
# Run from the lab directory:  bash examples/webhook_demo.sh
#
# The signature and verify steps are LOCAL and need no network. The delivery
# step reaches https://httpbin.org; offline, it degrades with a clear message
# and the script still exits 0.
set -u

# The sample event. printf '%s' (below) prints it with NO trailing newline, so
# the bytes we SIGN are exactly the bytes we SEND — this matters for HMAC.
PAYLOAD='{"event":"invoice.paid","id":"evt_28a7","data":{"amount":4200,"currency":"usd"}}'

# A FAKE secret, for the demo only. A real secret is a credential: keep it out
# of source code and logs (see security.md).
SECRET='whsec_demo_do_not_use_in_production'

HTTPBIN='https://httpbin.org'

rule() { printf '\n=== %s ===\n' "$1"; }

# Compute HMAC-SHA-256 of stdin with the given key; print just the 64-hex digest.
hmac_sha256() {
  local key="$1"
  openssl dgst -sha256 -hmac "$key" | sed 's/^.*= //'
}

# Return 0 if httpbin appears reachable, else 1.
have_network() {
  curl -s -o /dev/null --max-time 12 "${HTTPBIN}/get" 2>/dev/null
}

# ---------------------------------------------------------------------------
# 1. What the SENDER does: sign the raw payload.
# ---------------------------------------------------------------------------
show_sign() {
  rule "1. Compute the webhook signature (what the SENDER does)"
  local sig
  sig="$(printf '%s' "${PAYLOAD}" | hmac_sha256 "${SECRET}")"
  echo "payload: ${PAYLOAD}"
  echo "signature: sha256=${sig}"
  echo "(${#sig} hex characters)"
}

# ---------------------------------------------------------------------------
# 2. What the RECEIVER sees: deliver to an echo endpoint.
# ---------------------------------------------------------------------------
show_deliver() {
  rule "2. Deliver the payload to an echo endpoint (what the RECEIVER sees)"
  local sig response
  sig="$(printf '%s' "${PAYLOAD}" | hmac_sha256 "${SECRET}")"
  if ! have_network; then
    echo "OFFLINE: could not reach ${HTTPBIN}. Skipping the live delivery."
    echo "(The signature and verify steps above and below need no network.)"
    return
  fi
  # A real webhook is exactly this: a POST with a JSON body, a Content-Type,
  # an event-type header, and a signature header. httpbin echoes it all back,
  # so its response shows what a receiver would parse. -f fails on HTTP errors;
  # --retry with --retry-all-errors rides past httpbin's frequent transient
  # gateway hiccups and transfer resets (a real sender retries too).
  response="$(curl -sf --max-time 25 --retry 6 --retry-delay 2 --retry-all-errors \
    -X POST "${HTTPBIN}/post" \
    -H 'Content-Type: application/json' \
    -H 'X-Webhook-Event: invoice.paid' \
    -H "X-Webhook-Signature: sha256=${sig}" \
    -d "${PAYLOAD}" 2>/dev/null)" || response=""
  if [ -z "${response}" ]; then
    echo "(could not reach ${HTTPBIN} — transient error; try again in a moment)"
    return
  fi
  # Pull the echoed body and signature header back out of httpbin's JSON with
  # grep/sed only (no jq dependency).
  echo "the receiver received this body:"
  printf '%s\n' "${response}" | sed -n 's/.*"data": "\(.*\)", *$/\1/p' | sed 's/\\"/"/g' | head -n 1
  echo "and this signature header:"
  printf '%s\n' "${response}" | sed -n 's/.*"X-Webhook-Signature": "\(sha256=[0-9a-f]*\)".*/\1/p' | head -n 1
}

# ---------------------------------------------------------------------------
# 3. Verify (recompute + compare) and retry on non-2xx.
# ---------------------------------------------------------------------------
show_verify_and_retry() {
  rule "3. Verify + retry"
  local sent_sig recomputed tampered_payload tampered_sig
  sent_sig="$(printf '%s' "${PAYLOAD}" | hmac_sha256 "${SECRET}")"

  # The RECEIVER recomputes the signature over the body it got and compares.
  recomputed="$(printf '%s' "${PAYLOAD}" | hmac_sha256 "${SECRET}")"
  if [ "${sent_sig}" = "${recomputed}" ]; then
    echo "receiver recomputes signature over the body it got... MATCH -> would reply 200 OK"
  else
    echo "receiver recomputes signature over the body it got... MISMATCH -> reject"
  fi

  # A forged/tampered body recomputes to a DIFFERENT signature -> rejected.
  tampered_payload='{"event":"invoice.paid","id":"evt_28a7","data":{"amount":999999,"currency":"usd"}}'
  tampered_sig="$(printf '%s' "${tampered_payload}" | hmac_sha256 "${SECRET}")"
  if [ "${sent_sig}" = "${tampered_sig}" ]; then
    echo "tampered payload recomputes to the SAME signature... (should not happen)"
  else
    echo "tampered payload recomputes to a different signature... MISMATCH -> reject (forged)"
  fi

  # A sender retries until it gets a 2xx. We SIMULATE a receiver that fails
  # twice (503) then succeeds (200), to show at-least-once retrying + backoff.
  local -a statuses=(503 503 200)
  local attempt=1 code
  for code in "${statuses[@]}"; do
    if [ "${code}" -ge 200 ] && [ "${code}" -lt 300 ]; then
      echo "attempt ${attempt}: server returned ${code} -> acknowledged, stop retrying"
      break
    else
      echo "attempt ${attempt}: server returned ${code} -> not 2xx, retrying after backoff..."
    fi
    attempt=$((attempt + 1))
  done
}

main() {
  echo "Day 026 — Simulate a Webhook Delivery"
  echo "Playing both sender and receiver locally; echo endpoint: ${HTTPBIN}/post"
  show_sign
  show_deliver
  show_verify_and_retry
  echo
  echo "Done. You signed a payload, saw what a receiver receives, verified a"
  echo "genuine signature, rejected a forged one, and watched retries back off."
}

main "$@"
