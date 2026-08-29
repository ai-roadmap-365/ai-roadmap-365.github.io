#!/usr/bin/env bash
# Day 040 lab — STARTER: build a mini observability pipeline.
#
# The "app" that emits structured JSON logs and the trace reconstruction are
# provided and working. YOUR JOB is the four numbered exercises below, which
# build the three pillars from those logs. Each exercise names the exact
# command to use. Replace every placeholder, then run:  bash starter/observe.sh
# Check the finished reference any time:               bash examples/observe.sh
set -euo pipefail

# --- temp log file, cleaned up on exit (provided) --------------------------
logfile="$(mktemp -t observe_log.XXXXXX)"
cleanup() { rm -f "${logfile}"; }
trap cleanup EXIT

# --- the "app": emits structured JSON logs, 6 of 50 requests fail (provided)
emit_log() {
  local level="$1" event="$2" latency="$3" rid="$4"
  local sec ts
  sec=$(( 10#${rid##*-} % 60 ))
  ts="$(printf '2026-07-12T14:00:%02dZ' "${sec}")"
  printf '{"ts":"%s","level":"%s","event":"%s","request_id":"%s","latency_ms":%d}\n' \
    "${ts}" "${level}" "${event}" "${rid}" "${latency}" >> "${logfile}"
}
run_app() {
  local i level latency rid
  for i in $(seq 1 50); do
    rid="$(printf 'req-%04d' "${i}")"
    if (( i % 8 == 0 )); then
      level="ERROR"; latency=$(( 2000 + (i % 5) * 300 ))
    else
      level="INFO";  latency=$(( 90 + (i * 40) % 170 ))
    fi
    emit_log "${level}" "request_complete" "${latency}" "${rid}"
  done
}

# --- the trace: nested span start/end lines for one request (provided) ------
emit_span() {
  printf '{"level":"INFO","event":"span_%s","trace_id":"trace-7f3a9c","span":"%s","at_ms":%d}\n' \
    "$1" "$2" "$3" >> "${logfile}"
}
run_traced_request() {
  emit_span start total_request 0
  emit_span start validate_input 0; emit_span end validate_input 12
  emit_span start db_query 12;      emit_span end db_query 552
  emit_span start call_service 552; emit_span end call_service 800
  emit_span end   total_request 812
}
print_trace() {
  echo "=== Trace: request trace-7f3a9c ==="
  grep '"event":"span_' "${logfile}" | python3 -c '
import sys, json
start, dur, order = {}, {}, []
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    r = json.loads(line)
    name = r["span"]
    if r["event"] == "span_start":
        start[name] = r["at_ms"]; order.append(name)
    else:
        dur[name] = r["at_ms"] - start[name]
for name in order:
    indent = "  " if name == "total_request" else "    "
    print("%sspan %-16s %4d ms" % (indent, name, dur[name]))
'
}

# ===========================================================================
# YOUR WORK STARTS HERE. Run the app first so the log file exists.
# ===========================================================================
run_app
run_traced_request

# Sample of the structured logs the app just wrote (provided, so you can see
# the format you are working with — two healthy lines and one error line).
echo "=== Sample structured logs (2 healthy, 1 error) ==="
grep '"level":"INFO"' "${logfile}" | grep '"event":"request_complete"' | head -n 2
grep '"level":"ERROR"' "${logfile}" | head -n 1
echo

# ---------------------------------------------------------------------------
# EXERCISE 1: emit ONE structured log line to prove you can produce the format.
# Replace the echo placeholder with a printf that prints a single JSON object with the keys
# ts, level, event, and latency_ms (any sample values are fine). Example shape:
#   printf '{"ts":"2026-07-12T14:00:00Z","level":"INFO","event":"demo","latency_ms":123}\n'
echo "=== Your structured log line (Exercise 1) ==="
echo 'FILL_ME'   # <- replace this echo with your printf that prints one JSON log line
echo

# total requests = number of request_complete lines (provided, uses grep -c)
total="$(grep -c '"event":"request_complete"' "${logfile}")"

# ---------------------------------------------------------------------------
# EXERCISE 2: count the ERROR requests.
# Set `errors` to the number of log lines whose level is ERROR, using:
#   grep -c '"level":"ERROR"' "${logfile}"
errors="FILL_ME"

# ---------------------------------------------------------------------------
# EXERCISE 3: compute the error RATE as a percentage with two decimals.
# Use awk with the two numbers you already have. Template:
#   awk -v e="${errors}" -v t="${total}" 'BEGIN{ printf "%.2f", (t>0)?(e/t)*100:0 }'
rate="FILL_ME"

# ---------------------------------------------------------------------------
# EXERCISE 4: compute the p95 latency (a real nearest-rank percentile).
# Extract the latency_ms of every request and pipe it to python3. Template:
#   grep '"event":"request_complete"' "${logfile}" \
#     | sed -n 's/.*"latency_ms":\([0-9]*\).*/\1/p' \
#     | python3 -c 'import sys,math; v=sorted(int(x) for x in sys.stdin.read().split()); print(v[math.ceil(0.95*len(v))-1])'
p95="FILL_ME"

# p50 (median) latency is provided as a worked example of the same technique.
p50="$(grep '"event":"request_complete"' "${logfile}" \
  | sed -n 's/.*"latency_ms":\([0-9]*\).*/\1/p' \
  | python3 -c 'import sys,math; v=sorted(int(x) for x in sys.stdin.read().split()); print(v[math.ceil(0.50*len(v))-1])')"

# --- the DASHBOARD (provided) ----------------------------------------------
echo "=== Observability Dashboard ==="
printf 'Total requests:   %s\n' "${total}"
printf 'Errors:           %s\n' "${errors}"
printf 'Error rate:       %s%%\n' "${rate}"
printf 'p95 latency (ms): %s\n' "${p95}"
printf 'p50 latency (ms): %s\n' "${p50}"
print_trace
echo "=== End of dashboard ==="
