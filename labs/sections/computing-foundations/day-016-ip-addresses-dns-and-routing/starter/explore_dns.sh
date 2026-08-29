#!/usr/bin/env bash
# Day 016 lab — STARTER: explore DNS and routing.
#
# Your task: complete the four exercises below by replacing each `REPLACE_ME`
# with the exact command named in its comment (keep the surrounding "$( )" so
# the command's output is captured into the variable). Then run:
#
#     bash starter/explore_dns.sh
#
# A completed reference version is in examples/explore_dns.sh — try it first.
# This uses example.com, a domain reserved for documentation and testing.
set -uo pipefail

DOMAIN="${1:-example.com}"

echo "=== DNS and Routing Report ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo "Target domain: ${DOMAIN}"
echo

# --- Exercise 1: resolve the A record (IPv4 address) -------------------------
# Command:  dig +short A "${DOMAIN}"
# Replace REPLACE_ME below with:  $(dig +short A "${DOMAIN}")
a_records="REPLACE_ME"
echo "1. A record (IPv4 addresses)"
echo "${a_records}" | sed 's/^/   /'
echo

# --- Exercise 2: resolve the AAAA record (IPv6 address) ---------------------
# Command:  dig +short AAAA "${DOMAIN}"
# Replace REPLACE_ME below with:  $(dig +short AAAA "${DOMAIN}")
aaaa_records="REPLACE_ME"
echo "2. AAAA record (IPv6 addresses)"
echo "${aaaa_records}" | sed 's/^/   /'
echo

# --- Exercise 3: read the MX record (mail exchange) -------------------------
# Command:  dig +short MX "${DOMAIN}"
# Replace REPLACE_ME below with:  $(dig +short MX "${DOMAIN}")
mx_records="REPLACE_ME"
echo "3. MX record (mail exchange)"
echo "${mx_records}" | sed 's/^/   /'
echo

# --- Exercise 4: trace the route to the domain (first few hops) -------------
# Command:  traceroute -m 8 -w 2 -q 1 "${DOMAIN}"
#   -m 8 stops after 8 hops, -w 2 waits at most 2s per hop, -q 1 sends one
#   probe per hop — so it finishes quickly and never hangs.
# Replace REPLACE_ME below with:  $(traceroute -m 8 -w 2 -q 1 "${DOMAIN}" 2>&1)
route_output="REPLACE_ME"
echo "4. Route to ${DOMAIN} (first few hops)"
echo "${route_output}" | sed 's/^/   /'
echo

echo "Tip: to watch the DNS hierarchy walk from root to authoritative, run:"
echo "     dig +trace ${DOMAIN}"
echo
echo "=== End of report ==="
