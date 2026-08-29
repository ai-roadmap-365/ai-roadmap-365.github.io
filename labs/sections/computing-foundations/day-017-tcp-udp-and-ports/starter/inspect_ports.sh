#!/usr/bin/env bash
# Day 017 lab — See Ports and Connections (STARTER).
#
# Your job: complete the four numbered exercises below. Each one names the
# EXACT command to run. Replace the `EXERCISE N` placeholder lines (and the
# `echo` stand-ins) so the script prints the four required sections, exactly
# like examples/inspect_ports.sh. Try it yourself before peeking at the example.
#
# This script must stay READ-ONLY and LOCAL: only read the local list of
# listening sockets, and only ever probe the 127.0.0.1 loopback. Never
# connect to or scan an external host, and never use sudo.
set -euo pipefail

os="$(uname -s)"

echo "=== Ports and Connections ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo "Operating system kernel: ${os}"

# ===========================================================================
# EXERCISE 1 — List the listening TCP ports on this machine (READ-ONLY).
#
#   On macOS, run:   lsof -nP -iTCP -sTCP:LISTEN
#   On Linux, run:   ss -tlnp        (or, if ss is absent:  netstat -tln)
#
# Capture the raw listing into the variable `listening` below. The command
# substitution $( ... ) runs the command and stores its text output.
# Replace the placeholder line with the correct branch for your OS.
# ===========================================================================
echo
echo "--- Listening TCP ports ---"
if [ "${os}" = "Darwin" ]; then
  listening="$(echo 'EXERCISE 1: replace me with  lsof -nP -iTCP -sTCP:LISTEN')"
else
  listening="$(echo 'EXERCISE 1: replace me with  ss -tlnp   (or  netstat -tln)')"
fi
echo "${listening}"

# ===========================================================================
# EXERCISE 2 — Pull out just the port numbers, sorted and de-duplicated.
#
# The port is the number after the LAST colon of the local address. On macOS
# lsof, the address is the second-to-last field (e.g. "*:7000"); on Linux ss
# it is field 4 (e.g. "0.0.0.0:22"). Fill in the awk field and finish the
# pipeline with:   sort -n -u
#
# Hint (macOS):  awk 'NR>1 { n=split($(NF-1),p,":"); print p[n] }'
# Hint (Linux):  awk '{ n=split($4,p,":"); print p[n] }'
# ===========================================================================
echo
echo "--- Well-known vs ephemeral ---"
echo "EXERCISE 2: extract the port numbers here, then classify them:"
echo "  ports 0-1023 are WELL-KNOWN (22=SSH 53=DNS 80=HTTP 443=HTTPS)."
echo "  ports 1024-49151 are REGISTERED; 49152-65535 are EPHEMERAL."
# ports="$(echo "${listening}" | awk 'REPLACE_ME' | sort -n -u)"

# ===========================================================================
# EXERCISE 3 — Prove an OPEN port on the loopback with netcat.
#
# Pick a port number you saw in Exercise 1 that is bound to 127.0.0.1 or *,
# then test it WITHOUT sending data using the -z ("zero-I/O") flag:
#
#   nc -z -w 1 127.0.0.1 <PORT>
#
# nc exits 0 if the port is OPEN (something is listening) and non-zero if it
# is closed. Replace <PORT> below with a real port from your own output.
# ===========================================================================
echo
echo "--- Loopback connection test ---"
echo "127.0.0.1 is 'localhost' — this machine talking to itself, no network."
# if nc -z -w 1 127.0.0.1 <PORT> >/dev/null 2>&1; then
#   echo "Testing 127.0.0.1:<PORT> ... OPEN"
# else
#   echo "Testing 127.0.0.1:<PORT> ... closed"
# fi
echo "EXERCISE 3: run  nc -z -w 1 127.0.0.1 <PORT>  for a real open port."

# ===========================================================================
# EXERCISE 4 — Prove a CLOSED port ("connection refused").
#
# Probe a port that is almost certainly NOT listening (port 1 is a safe
# choice) and report the refusal:
#
#   nc -z -w 1 127.0.0.1 1
#
# "Connection refused" is exactly what a client sees when nothing is
# listening on the other side — the everyday cause of that error.
# ===========================================================================
echo "EXERCISE 4: run  nc -z -w 1 127.0.0.1 1  and report 'connection refused'."

echo "=== End of report ==="
