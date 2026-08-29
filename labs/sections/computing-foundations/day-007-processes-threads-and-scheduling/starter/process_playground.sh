#!/usr/bin/env bash
# Day 007 lab — spawn, watch, and signal a process of your own.
#
# This starter script runs as-is, but five steps are left for you. Each
# exercise comment names the exact command to use — replace the `unknown`
# assignment (or follow the instruction) and run the script again. The
# completed reference version is in examples/process_playground.sh — try
# it yourself first.
#
# Safety rule (see security.md): only ever signal the process YOU started,
# whose PID you captured from $!. Never type PIDs you found elsewhere.
set -u

echo "=== Process Playground ==="
echo "Generated on: $(date '+%Y-%m-%d')"

# Exercise 1: count the processes on this machine using:
#   ps -e | tail -n +2 | wc -l | tr -d ' '
# (ps -e lists every process; tail -n +2 drops the header; wc -l counts lines)
process_count="unknown"
echo "Processes running right now: ${process_count}"

# Exercise 2: print this script's own PID (the special variable $$), then
# show its process-table row and its parent's row using:
#   ps -o pid,ppid,command -p $$
echo "This script's PID: $$"
echo "Parent chain (this script and its parent):"
# --- add your ps command below this line ---

# Exercise 3: start a background worker with `sleep 300 &` and IMMEDIATELY
# capture its PID from $! into worker_pid (worker_pid=$!). The skeleton
# below only runs the remaining steps once you have done so.
worker_pid="unknown"

if [ "${worker_pid}" != "unknown" ]; then
  # Safety net: if this script dies early, take the worker along.
  trap 'kill "${worker_pid}" 2>/dev/null' EXIT
  echo "Started background worker: sleep 300 (PID ${worker_pid})"

  echo "The worker as seen by jobs:"
  jobs -l | sed 's/^/  /'
  echo "The worker as seen by ps:"
  # Exercise 4a: find your worker in the process table using:
  #   ps -o pid,ppid,stat,command -p "${worker_pid}"
  # --- add your ps command below this line ---

  # Exercise 4b: terminate the worker POLITELY (SIGTERM, the default) using:
  #   kill "${worker_pid}"
  # then collect its exit status with:
  #   wait "${worker_pid}" 2>/dev/null; exit_status=$?
  # --- add your kill and wait commands below this line ---
  exit_status="unknown"
  echo "Sent SIGTERM to ${worker_pid}; wait reported exit status ${exit_status}"

  # Exercise 5: verify the worker is gone using:
  #   ps -p "${worker_pid}"
  # (it should find nothing — test with: if ! ps -p "${worker_pid}" > /dev/null 2>&1; then ...)
  # Print exactly:  Verified: PID ${worker_pid} is gone
  # --- add your verification below this line ---
else
  echo "Exercise 3 not completed yet: no background worker was started."
fi

echo "=== End of playground ==="
