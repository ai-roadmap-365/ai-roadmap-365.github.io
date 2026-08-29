#!/usr/bin/env bash
# Day 015 lab — completed reference implementation.
# Trace the first stops of a web page's request journey for one host:
#   1. DNS lookup    (dig +short)      name -> IP address
#   2. Round-trip time (ping -c 2)     how long a back-and-forth takes
#   3. Connection stages (curl -w)     DNS / TCP / TLS / total timings
#
# Usage:  bash examples/trace_page_load.sh [hostname]
# Default host is example.com (a safe, standard test domain).
#
# Requires a network connection. If a step's tool is missing or the
# network is unavailable, the script prints a clear note and continues,
# so it never crashes mid-report.
set -uo pipefail

host="${1:-example.com}"

echo "=== Request Journey Report ==="
echo "Host: ${host}"
echo "Generated on: $(date '+%Y-%m-%d')"
echo

# --- Stop 1: DNS lookup (name -> IP address) ---
echo "--- Stop 1: DNS lookup (name -> IP) ---"
if command -v dig >/dev/null 2>&1; then
  ips="$(dig +short "${host}" 2>/dev/null)"
  if [ -n "${ips}" ]; then
    echo "Resolved IP address(es):"
    echo "${ips}" | sed 's/^/  /'
  else
    echo "DNS lookup returned no address (offline, or name not found)."
  fi
else
  echo "dig not installed — try: nslookup ${host}  or  host ${host}"
fi
echo

# --- Stop 2: Round-trip time (ping) ---
echo "--- Stop 2: Round-trip time (ping -c 2) ---"
if command -v ping >/dev/null 2>&1; then
  if ping_out="$(ping -c 2 "${host}" 2>&1)"; then
    echo "${ping_out}" | sed 's/^/  /'
  else
    echo "  ping failed or was blocked (many networks block ICMP)."
    echo "  A blocked ping does NOT mean the site is down — see the curl step."
  fi
else
  echo "  ping not installed on this system."
fi
echo

# --- Stop 3: Connection stage timings (curl) ---
echo "--- Stop 3: Connection stages (curl -w timings) ---"
if command -v curl >/dev/null 2>&1; then
  fmt='dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s total=%{time_total}s\n'
  timing="$(curl -sS --max-time 15 -o /dev/null -w "${fmt}" "https://${host}" 2>/dev/null)"
  rc=$?
  if [ "${rc}" -eq 0 ]; then
    echo "  ${timing}"
    echo "  Read each value as the elapsed time from the start at which that"
    echo "  stage finished. Subtract consecutive values to get each stop's cost:"
    echo "    time_namelookup = when DNS resolved"
    echo "    time_connect    = when the TCP connection opened"
    echo "    time_appconnect = when the TLS handshake finished"
    echo "    time_total      = when the full response arrived"
  else
    echo "  curl could not complete the request (offline, or the host refused"
    echo "  the connection). This often just means no network right now —"
    echo "  reconnect and retry. A failed curl does not prove the site is down."
  fi
else
  echo "  curl not installed on this system."
fi
echo

echo "=== End of report ==="
