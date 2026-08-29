#!/usr/bin/env bash
# Day 015 lab — YOUR working file. Trace the request journey for one host.
#
# The report skeleton is already here. Your job is the four numbered
# exercises below: replace each `PENDING-exercise-N` echo line with the real
# command named in its comment, so the report prints genuine values. The
# completed reference version is examples/trace_page_load.sh — run that first
# to see the finished result, then rebuild it here yourself.
#
# Usage:  bash starter/trace_page_load.sh [hostname]
# Default host is example.com (a safe, standard test domain).
set -uo pipefail

host="${1:-example.com}"

echo "=== Request Journey Report ==="
echo "Host: ${host}"
echo "Generated on: $(date '+%Y-%m-%d')"
echo

# --- Stop 1: DNS lookup (name -> IP address) ---
echo "--- Stop 1: DNS lookup (name -> IP) ---"
# Exercise 1: resolve the host to its IP address(es).
#   Replace the echo line below with:  dig +short "${host}"
echo "PENDING-exercise-1: run dig +short on the host"
echo

# --- Stop 2: Round-trip time (ping) ---
echo "--- Stop 2: Round-trip time (ping -c 2) ---"
# Exercise 2: measure the round-trip time with two ping packets.
#   Replace the echo line below with:  ping -c 2 "${host}"
echo "PENDING-exercise-2: run ping -c 2 on the host"
echo

# --- Stop 3: Connection stage timings (curl) ---
echo "--- Stop 3: Connection stages (curl -w timings) ---"
# Exercise 3: print curl's per-stage timings for https://<host>.
#   Replace the echo line below with a curl command that uses -w with the
#   fields time_namelookup, time_connect, time_appconnect, time_total, e.g.:
#     curl -sS -o /dev/null \
#       -w "dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s total=%{time_total}s\n" \
#       "https://${host}"
echo "PENDING-exercise-3: run the curl -w timing command for the host"
echo

# --- Stop 4: your reading of the timeline ---
echo "--- Stop 4: which stop cost the most? ---"
# Exercise 4: after running Stop 3, subtract consecutive curl values and
# write, in the string below, which stop (DNS, TCP connect, TLS, or server)
# took the most time for your host. Replace the placeholder text.
echo "PENDING-exercise-4: replace with your finding, e.g. 'TLS took the most, about 0.02s'"
echo

echo "=== End of report ==="
