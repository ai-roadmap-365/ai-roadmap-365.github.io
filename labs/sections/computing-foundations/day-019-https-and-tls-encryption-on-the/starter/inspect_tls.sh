#!/usr/bin/env bash
# Day 019 lab — inspect a TLS certificate yourself.
#
# This starter already handles the host argument and the offline guard and
# prints the report skeleton. Your job (README, "How to run") is to fill in
# the four exercises below, each of which names the exact command to use.
# The completed reference version is in examples/inspect_tls.sh — try to
# write yours first, then compare.
set -uo pipefail

host="${1:-example.com}"

echo "=== TLS inspection for ${host} ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo

# Offline guard — leave this as is. It exits cleanly if there is no network.
if ! curl -sI --max-time 15 "https://${host}" >/dev/null 2>&1; then
  echo "OFFLINE or host unreachable: could not open https://${host}"
  echo "Connect to the internet and re-run. (This lab requires network access.)"
  echo "=== End of inspection ==="
  exit 0
fi

echo "--- Certificate (openssl) ---"
# Exercise 1: print the certificate SUBJECT, ISSUER, and DATES.
#   Pipe an s_client connection into x509. Use exactly:
#   openssl s_client -connect "${host}:443" -servername "${host}" </dev/null 2>/dev/null \
#     | openssl x509 -noout -subject -issuer -dates
echo "REPLACE ME: exercise 1 (openssl subject/issuer/dates)"
echo

echo "--- Handshake summary (curl) ---"
# Exercise 2: show the negotiated TLS VERSION and the certificate summary.
#   Run a verbose headers-only request and keep the TLS lines. Use exactly:
#   curl -vI --max-time 15 "https://${host}" 2>&1 \
#     | grep -Ei "SSL connection|subject:|issuer:|expire date|SSL certificate verify"
echo "REPLACE ME: exercise 2 (curl handshake summary)"
echo

echo "--- Just the expiry date (openssl) ---"
# Exercise 3: print ONLY the not-after (expiry) date of the certificate.
#   Use the -enddate flag. Use exactly:
#   openssl s_client -connect "${host}:443" -servername "${host}" </dev/null 2>/dev/null \
#     | openssl x509 -noout -enddate
echo "REPLACE ME: exercise 3 (openssl expiry date only)"
echo

echo "--- The certificate chain (openssl) ---"
# Exercise 4: show the chain of subjects (s:) and issuers (i:) the server sends.
#   Add -showcerts and keep the s: / i: lines. Use exactly:
#   openssl s_client -connect "${host}:443" -servername "${host}" -showcerts </dev/null 2>/dev/null \
#     | grep -E "s:|i:"
echo "REPLACE ME: exercise 4 (openssl -showcerts chain)"
echo

echo "=== End of inspection ==="
