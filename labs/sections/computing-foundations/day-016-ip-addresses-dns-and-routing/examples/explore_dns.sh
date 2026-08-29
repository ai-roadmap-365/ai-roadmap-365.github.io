#!/usr/bin/env bash
# Day 016 lab — completed reference: explore DNS and routing.
#
# Resolves a name to its IPv4/IPv6 addresses, reads its MX record, notes how
# to walk the full DNS hierarchy, traces the route to it (a few hops, with a
# timeout so it never hangs), and classifies each resolved address as public
# or private. Uses example.com — a domain reserved for documentation and
# testing (RFC 2606) — so the lab probes nobody's private systems.
#
# Requires network access. If offline (or dig is missing) it says so plainly
# and still exits cleanly, so you can read the structure before you are online.
set -uo pipefail

DOMAIN="${1:-example.com}"

echo "=== DNS and Routing Report ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo "Target domain: ${DOMAIN}"
echo

# --- helper: is this IPv4 address in a private / loopback range? -------------
classify_ipv4() {
  local ip="$1"
  case "${ip}" in
    10.*) echo "private (10.0.0.0/8)" ;;
    192.168.*) echo "private (192.168.0.0/16)" ;;
    127.*) echo "loopback (127.0.0.0/8)" ;;
    172.1[6-9].* | 172.2[0-9].* | 172.3[0-1].*) echo "private (172.16.0.0/12)" ;;
    *) echo "public" ;;
  esac
}

# --- preflight: do we have a DNS tool, and are we online? --------------------
have_dig="no"
command -v dig >/dev/null 2>&1 && have_dig="yes"

online="no"
if [ "${have_dig}" = "yes" ]; then
  if dig +time=3 +tries=1 +short A "${DOMAIN}" >/dev/null 2>&1; then
    # A successful command does not guarantee an answer; check for one below.
    online="yes"
  fi
fi

if [ "${have_dig}" != "yes" ]; then
  echo "NOTE: 'dig' is not installed — install it (see requirements/README.md)"
  echo "      or use 'nslookup ${DOMAIN}' by hand. Skipping live DNS queries."
fi

# --- 1. A record (IPv4) ------------------------------------------------------
echo "1. A record (IPv4 addresses)"
a_records=""
if [ "${have_dig}" = "yes" ]; then
  a_records="$(dig +time=3 +tries=1 +short A "${DOMAIN}" 2>/dev/null | grep -E '^[0-9]+\.' || true)"
fi
if [ -n "${a_records}" ]; then
  while IFS= read -r ip; do
    [ -z "${ip}" ] && continue
    echo "   ${ip}   -> $(classify_ipv4 "${ip}")"
  done <<< "${a_records}"
  first_a="$(echo "${a_records}" | head -n 1)"
  echo "   A record IP (first): ${first_a}"
else
  echo "   (no A record retrieved — offline, no dig, or no such record)"
fi
echo

# --- 2. AAAA record (IPv6) ---------------------------------------------------
echo "2. AAAA record (IPv6 addresses)"
aaaa_records=""
if [ "${have_dig}" = "yes" ]; then
  aaaa_records="$(dig +time=3 +tries=1 +short AAAA "${DOMAIN}" 2>/dev/null | grep -E ':' || true)"
fi
if [ -n "${aaaa_records}" ]; then
  echo "${aaaa_records}" | sed 's/^/   /'
  echo "   (IPv6 present)"
else
  echo "   (no AAAA record retrieved — this name may have none, or you are offline)"
fi
echo

# --- 3. MX record (mail exchange) --------------------------------------------
echo "3. MX record (mail exchange)"
mx_records=""
if [ "${have_dig}" = "yes" ]; then
  mx_records="$(dig +time=3 +tries=1 +short MX "${DOMAIN}" 2>/dev/null || true)"
fi
if [ -n "${mx_records}" ]; then
  echo "${mx_records}" | sed 's/^/   /'
else
  echo "   (none — the domain may have no MX record, or a null MX '0 .')"
fi
echo

# --- 4. Walking the full hierarchy (note) ------------------------------------
echo "4. Walking the hierarchy"
echo "   To watch the resolver walk root -> TLD -> authoritative yourself, run:"
echo "       dig +trace ${DOMAIN}"
echo "   It prints every referral from the root servers down to the"
echo "   authoritative name servers. (Not run here to keep output short.)"
echo

# --- 5. traceroute (a few hops, with a timeout) ------------------------------
echo "5. Route to ${DOMAIN} (first few hops)"
if command -v traceroute >/dev/null 2>&1; then
  # -m 8: stop after 8 hops.  -w 2: wait at most 2s per hop.  -q 1: one probe.
  # Wrapped so a slow/blocked network never hangs the whole script.
  if hops="$(traceroute -m 8 -w 2 -q 1 "${DOMAIN}" 2>/dev/null)"; then
    echo "${hops}" | sed 's/^/   /'
    hop_count="$(echo "${hops}" | grep -Ec '^[[:space:]]*[0-9]+')"
    echo "   Hops shown: ${hop_count} (capped at 8; '* * *' means a silent router)"
  else
    echo "   (traceroute did not complete — network may block probes; that is normal)"
  fi
else
  echo "   (traceroute not installed — see requirements/README.md; on Windows use 'tracert')"
fi
echo

echo "=== End of report ==="
