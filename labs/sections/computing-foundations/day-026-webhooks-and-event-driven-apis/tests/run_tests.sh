#!/usr/bin/env bash
# Tests for the Day 026 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Two kinds of checks:
#   * Structure + LOCAL checks always run and must pass: files present, both
#     scripts parse, the example exercises each core step, the starter names
#     its four exercises, and — with NO network — the HMAC signature computes
#     to the known 64-hex value (this is pure openssl, no internet).
#   * The NETWORK check runs only when httpbin.org is reachable: it POSTs the
#     payload and confirms the echo contains it. Offline, or when httpbin is
#     transiently down, that check is SKIPPED (never failed).
#
# The script exits 0 when no non-skipped check failed, online or offline.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HTTPBIN='https://httpbin.org'
PAYLOAD='{"event":"invoice.paid","id":"evt_28a7","data":{"amount":4200,"currency":"usd"}}'
SECRET='whsec_demo_do_not_use_in_production'
EXPECTED_SIG='cadd3bf8973d72aec386c06d46c8803f68aa1f6936e9ee4a334adedace74e3c0'

failures=0
checks=0
skips=0

pass() { checks=$((checks + 1)); echo "  ok:   $1"; }
fail() { checks=$((checks + 1)); failures=$((failures + 1)); echo "  FAIL: $1"; }
skip() { skips=$((skips + 1)); echo "  skip: $1"; }

example="${lab_dir}/examples/webhook_demo.sh"
starter="${lab_dir}/starter/webhook_demo.sh"

echo "== Structure checks =="
[ -f "${example}" ] && pass "example script exists" || fail "example script missing"
[ -f "${starter}" ] && pass "starter script exists" || fail "starter script missing"
[ -f "${lab_dir}/starter/webhook-worksheet.md" ] && pass "worksheet exists" || fail "worksheet missing"

# The example must exercise each core step.
for needle in "openssl dgst -sha256 -hmac" "curl" "X-Webhook-Signature" "MISMATCH" "retrying"; do
  if grep -q -- "${needle}" "${example}"; then pass "example uses '${needle}'"; else fail "example missing '${needle}'"; fi
done

# The starter must name its four numbered exercises.
ex_count="$(grep -cE 'Exercise [1-4]' "${starter}" 2>/dev/null || true)"
if [ "${ex_count:-0}" -ge 4 ]; then pass "starter has 4 numbered exercises"; else fail "starter has 4 numbered exercises (found ${ex_count:-0})"; fi

# Both scripts must be valid bash.
if bash -n "${example}" 2>/dev/null; then pass "example has valid bash syntax"; else fail "example has a syntax error"; fi
if bash -n "${starter}" 2>/dev/null; then pass "starter has valid bash syntax"; else fail "starter has a syntax error"; fi

echo
echo "== Local HMAC checks (no network) =="
# Recompute the signature exactly as sender and receiver would.
sig="$(printf '%s' "${PAYLOAD}" | openssl dgst -sha256 -hmac "${SECRET}" | sed 's/^.*= //')"
# It must be exactly 64 lowercase hex characters.
if printf '%s' "${sig}" | grep -qE '^[0-9a-f]{64}$'; then
  pass "HMAC signature is a 64-hex-character string"
else
  fail "HMAC signature is not 64 hex characters (got '${sig}')"
fi
# It must equal the known, deterministic value for this payload+secret.
if [ "${sig}" = "${EXPECTED_SIG}" ]; then
  pass "HMAC signature matches the expected deterministic value"
else
  fail "HMAC signature != expected (got '${sig}')"
fi
# Tampering must change the signature (integrity property).
tampered="$(printf '%s' '{"event":"invoice.paid","id":"evt_28a7","data":{"amount":999999,"currency":"usd"}}' | openssl dgst -sha256 -hmac "${SECRET}" | sed 's/^.*= //')"
if [ "${sig}" != "${tampered}" ]; then
  pass "a tampered payload produces a different signature (rejected)"
else
  fail "tampered payload should not match the original signature"
fi

echo
echo "== Network check (httpbin echo) =="
if ! curl -s -o /dev/null --max-time 12 "${HTTPBIN}/get" 2>/dev/null; then
  skip "no network access — skipping the live delivery echo check (expected offline)"
else
  echoed="$(curl -sf --max-time 25 --retry 6 --retry-delay 2 --retry-all-errors \
    -X POST "${HTTPBIN}/post" \
    -H 'Content-Type: application/json' \
    -H "X-Webhook-Signature: sha256=${sig}" \
    -d "${PAYLOAD}" 2>/dev/null)" || echoed=""
  if [ -z "${echoed}" ]; then
    skip "delivery check — httpbin transiently unavailable; retry later"
  elif printf '%s' "${echoed}" | grep -q 'invoice.paid' \
    && printf '%s' "${echoed}" | grep -q "${sig}"; then
    pass "the echo endpoint returned our payload and signature header"
  else
    fail "the echo endpoint should echo our payload and signature"
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skip(s)."
[ "${failures}" -eq 0 ]
