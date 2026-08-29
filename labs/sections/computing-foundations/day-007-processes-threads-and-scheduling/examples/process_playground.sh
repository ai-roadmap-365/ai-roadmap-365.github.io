#!/usr/bin/env bash
# Day 007 lab — completed reference implementation.
# Spawns a background process, observes it with jobs and ps, terminates it
# politely with SIGTERM, and verifies it is gone. Also counts the machine's
# processes and prints this script's own PID and parent chain.
#
# Safety rule (see security.md): this script only ever signals the one
# process it started itself, whose PID it captured from $!.
set -u

echo "=== Process Playground ==="
echo "Generated on: $(date '+%Y-%m-%d')"

# --- 1. How many processes exist right now? ---------------------------------
process_count="$(ps -e | tail -n +2 | wc -l | tr -d ' ')"
echo "Processes running right now: ${process_count}"

# --- 2. Who am I, and who spawned me? ----------------------------------------
echo "This script's PID: $$"
echo "Parent chain (this script and up to 5 ancestors):"
pid=$$
depth=0
while [ -n "${pid}" ] && [ "${pid}" -gt 0 ] && [ "${depth}" -lt 6 ]; do
  ps -o pid=,ppid=,command= -p "${pid}" 2>/dev/null | sed 's/^/  /'
  next="$(ps -o ppid= -p "${pid}" 2>/dev/null | tr -d ' ')"
  if [ -z "${next}" ] || [ "${next}" = "${pid}" ] || [ "${next}" -eq 0 ]; then
    break
  fi
  pid="${next}"
  depth=$((depth + 1))
done

# --- 3. Spawn a background worker and capture its PID from $! ----------------
sleep 300 &
worker_pid=$!
# Safety net: if this script dies early for any reason, take the worker along.
trap 'kill "${worker_pid}" 2>/dev/null' EXIT
echo "Started background worker: sleep 300 (PID ${worker_pid})"

echo "The worker as seen by jobs:"
jobs -l | sed 's/^/  /'
echo "The worker as seen by ps:"
ps -o pid,ppid,stat,command -p "${worker_pid}" | sed 's/^/  /'

# --- 4. Terminate it politely (SIGTERM, the kill default) --------------------
kill "${worker_pid}"
wait "${worker_pid}" 2>/dev/null
exit_status=$?
echo "Sent SIGTERM to ${worker_pid}; wait reported exit status ${exit_status} (143 = 128 + 15, death by SIGTERM)"

# --- 5. Verify the worker is really gone -------------------------------------
if ps -p "${worker_pid}" > /dev/null 2>&1; then
  echo "ERROR: worker ${worker_pid} is still alive" >&2
  exit 1
fi
echo "Verified: PID ${worker_pid} is gone"
echo "=== End of playground ==="
