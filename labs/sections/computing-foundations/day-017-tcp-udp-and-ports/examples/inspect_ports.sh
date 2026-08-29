#!/usr/bin/env bash
# Day 017 lab — completed reference implementation.
# "See Ports and Connections": list the TCP ports this machine is LISTENING
# on, explain which are well-known, and prove a loopback connection with nc.
#
# This script is strictly READ-ONLY and LOCAL:
#   - it only reads the local list of listening sockets (lsof/ss/netstat)
#   - the only network action is a loopback (127.0.0.1) connectivity probe
#   - it never connects to, or scans, any external host, and needs no sudo.
set -euo pipefail

os="$(uname -s)"

echo "=== Ports and Connections ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo "Operating system kernel: ${os}"

# ---------------------------------------------------------------------------
# name_for_port PORT — a tiny well-known-port lookup table.
# Returns a human-readable guess for the service usually behind a port.
# ---------------------------------------------------------------------------
name_for_port() {
  case "$1" in
    22)   echo "SSH (secure shell login)" ;;
    53)   echo "DNS (domain name lookups)" ;;
    80)   echo "HTTP (unencrypted web)" ;;
    123)  echo "NTP (clock sync)" ;;
    443)  echo "HTTPS (encrypted web)" ;;
    631)  echo "IPP (printing)" ;;
    3000) echo "common dev server (Node/React)" ;;
    5000) echo "common dev server / AirPlay on macOS" ;;
    5432) echo "PostgreSQL database" ;;
    6379) echo "Redis database" ;;
    7000) echo "AirPlay receiver (macOS)" ;;
    8000) echo "common dev / model server" ;;
    8080) echo "common HTTP alternative" ;;
    *)    echo "-" ;;
  esac
}

# ---------------------------------------------------------------------------
# class_for_port PORT — which of the three IANA ranges a port falls in.
#   0-1023      : well-known (system) ports
#   1024-49151  : registered ports
#   49152-65535 : ephemeral / dynamic ports
# ---------------------------------------------------------------------------
class_for_port() {
  local p="$1"
  if   [ "$p" -le 1023 ];  then echo "well-known"
  elif [ "$p" -le 49151 ]; then echo "registered"
  else                          echo "ephemeral"
  fi
}

# ---------------------------------------------------------------------------
# list_listening — print "PORT PROCESS" lines for every listening TCP socket,
# choosing the best available tool for this OS. Read-only.
# ---------------------------------------------------------------------------
list_listening() {
  if [ "${os}" = "Darwin" ] && command -v lsof >/dev/null 2>&1; then
    # macOS: lsof reports the local address in the NAME column, e.g.
    # "*:7000 (LISTEN)" or "127.0.0.1:54815 (LISTEN)". Take the port after
    # the LAST colon of the second-to-last field; the command is field 1.
    lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | awk '
      NR > 1 {
        addr = $(NF - 1)
        n = split(addr, parts, ":")
        port = parts[n]
        if (port ~ /^[0-9]+$/) print port, $1
      }'
  elif command -v ss >/dev/null 2>&1; then
    # Linux: ss -tlnH lists listening TCP sockets with no header. The local
    # address:port is field 4; the port is after the last colon.
    ss -tlnH 2>/dev/null | awk '
      {
        addr = $4
        n = split(addr, parts, ":")
        port = parts[n]
        proc = $NF
        if (port ~ /^[0-9]+$/) print port, proc
      }'
  elif command -v netstat >/dev/null 2>&1; then
    # Fallback: netstat. -tln = TCP, listening, numeric.
    netstat -tln 2>/dev/null | awk '
      /LISTEN/ {
        addr = $4
        n = split(addr, parts, ":")
        port = parts[n]
        if (port ~ /^[0-9]+$/) print port, "(netstat)"
      }'
  else
    echo "NO_TOOL"
  fi
}

echo
echo "--- Listening TCP ports ---"
echo "A 'listening' port is a service waiting for incoming connections."

raw="$(list_listening | sort -n -u)"

ports_only=""
if [ "${raw}" = "NO_TOOL" ] || [ -z "${raw}" ]; then
  echo "(No listening-port tool found, or no listening TCP ports detected.)"
  echo "Install lsof (macOS) or iproute2/net-tools (Linux) to see more."
else
  printf '%-7s %-12s %-32s %s\n' "PORT" "CLASS" "LIKELY SERVICE" "PROCESS"
  while read -r port proc; do
    [ -z "${port}" ] && continue
    ports_only="${ports_only} ${port}"
    printf '%-7s %-12s %-32s %s\n' \
      "${port}" "$(class_for_port "${port}")" "$(name_for_port "${port}")" "${proc}"
  done <<EOF
${raw}
EOF
fi

echo
echo "--- Well-known vs ephemeral ---"
echo "Ports 0-1023 are WELL-KNOWN: reserved for standard services."
echo "  22=SSH  53=DNS  80=HTTP  443=HTTPS  123=NTP  631=IPP"
echo "Ports 1024-49151 are REGISTERED (databases, dev servers: 5432, 6379, 8000)."
echo "Ports 49152-65535 are EPHEMERAL: short-lived client-side port numbers."

echo
echo "--- Loopback connection test ---"
echo "127.0.0.1 is 'localhost' — this machine talking to itself, no network."
if command -v nc >/dev/null 2>&1; then
  # Find a port that actually answers on the IPv4 loopback, to demonstrate the
  # OPEN case. (Some services bind only to the IPv6 loopback [::1] and will
  # not answer on 127.0.0.1 — a real subtlety, not an error.)
  open_port=""
  for port in ${ports_only}; do
    if nc -z -w 1 127.0.0.1 "${port}" >/dev/null 2>&1; then
      open_port="${port}"
      break
    fi
  done
  if [ -n "${open_port}" ]; then
    echo "Testing 127.0.0.1:${open_port} ... OPEN (something is listening here)"
  else
    echo "No listed port answered on the 127.0.0.1 (IPv4) loopback to probe as OPEN."
    echo "(Services may be bound only to the IPv6 loopback [::1] — try ::1 instead.)"
  fi
  # Port 1 is virtually never a listening service on a normal machine, so it
  # demonstrates the 'connection refused' case that means "nothing is here".
  if nc -z -w 1 127.0.0.1 1 >/dev/null 2>&1; then
    echo "Testing 127.0.0.1:1 ... OPEN (unexpected, but honestly reported)"
  else
    echo "Testing 127.0.0.1:1 ... closed (connection refused — nothing listening)"
  fi
else
  echo "(nc not found — install it to run the loopback probe.)"
fi

echo "=== End of report ==="
