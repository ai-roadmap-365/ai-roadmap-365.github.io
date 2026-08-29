#!/usr/bin/env bash
# Day 019 lab — completed reference implementation.
# Inspects the TLS certificate and handshake for a public HTTPS host,
# showing the certificate subject, issuer, and validity dates, and the
# negotiated TLS version. Read-only: it opens a connection and reads the
# public certificate, sends no data, and writes no files.
#
# Usage:  bash examples/inspect_tls.sh [host]
# Default host is example.com — a stable, well-known test domain.
set -uo pipefail

host="${1:-example.com}"

echo "=== TLS inspection for ${host} ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo

# --- Offline guard -----------------------------------------------------------
# This lab needs the network. If we cannot reach the host, say so clearly
# and exit 0 so a reader offline still gets a graceful result.
if ! curl -sI --max-time 15 "https://${host}" >/dev/null 2>&1; then
  echo "OFFLINE or host unreachable: could not open https://${host}"
  echo "Connect to the internet and re-run. (This lab requires network access.)"
  echo "=== End of inspection ==="
  exit 0
fi

# --- 1. Certificate identity via openssl s_client + x509 ---------------------
# s_client opens the TLS connection; </dev/null feeds empty input so it does
# not hang waiting for an HTTP request. x509 prints the fields we care about.
echo "--- Certificate (openssl) ---"
openssl s_client -connect "${host}:443" -servername "${host}" </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
echo

# --- 2. Handshake summary via curl -v ----------------------------------------
# curl -vI makes a verbose, headers-only request; we keep just the TLS lines:
# the negotiated protocol/cipher, the certificate subject/issuer/expiry, and
# whether verification succeeded.
echo "--- Handshake summary (curl) ---"
curl -vI --max-time 15 "https://${host}" 2>&1 \
  | grep -Ei "SSL connection|subject:|issuer:|expire date|SSL certificate verify"
echo

echo "=== End of inspection ==="
