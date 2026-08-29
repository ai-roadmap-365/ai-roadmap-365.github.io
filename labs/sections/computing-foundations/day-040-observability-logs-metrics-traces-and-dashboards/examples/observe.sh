#!/usr/bin/env bash
# Day 040 lab — completed reference: a mini observability pipeline.
#
# It builds all three pillars from nothing but plain log lines:
#   1. an "app" that does work and emits STRUCTURED JSON logs (with an ERROR level)
#   2. METRICS derived from those logs (total, errors, error rate, p95/p50 latency)
#   3. a tiny text DASHBOARD that prints the metrics
#   4. a TRACE: nested span start/end lines for one request, timing reconstructed
#
# Offline, no network, no API key. Uses only bash, grep/sed/awk, and python3
# (preinstalled on macOS and Linux) for the percentile computation.
# The temporary log file is removed automatically on exit.
set -euo pipefail

# --- temp log file, cleaned up on exit -------------------------------------
logfile="$(mktemp -t observe_log.XXXXXX)"
cleanup() { rm -f "${logfile}"; }
trap cleanup EXIT

# --- 1. the "app": do work and emit structured JSON logs -------------------
# 50 requests. Every 8th request fails (level ERROR) and is slow, so the error
# count is deterministic (6 errors). Latencies are deterministic so every run
# of this reference produces the same metrics.
emit_log() {
  # args: level event latency_ms request_id
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
      level="ERROR"
      latency=$(( 2000 + (i % 5) * 300 ))   # slow, failing requests
    else
      level="INFO"
      latency=$(( 90 + (i * 40) % 170 ))     # healthy requests: 90-259 ms
    fi
    emit_log "${level}" "request_complete" "${latency}" "${rid}"
  done
}

# --- 4. a trace: nested span start/end lines for ONE request ----------------
emit_span() {
  # args: phase(start|end) span at_ms
  printf '{"level":"INFO","event":"span_%s","trace_id":"trace-7f3a9c","span":"%s","at_ms":%d}\n' \
    "$1" "$2" "$3" >> "${logfile}"
}
run_traced_request() {
  emit_span start total_request 0
  emit_span start validate_input 0
  emit_span end   validate_input 12
  emit_span start db_query 12
  emit_span end   db_query 552
  emit_span start call_service 552
  emit_span end   call_service 800
  emit_span end   total_request 812
}

# --- 2. derive METRICS from the logs (the three pillars, by hand) ----------
compute_metrics() {
  local total errors rate
  total="$(grep -c '"event":"request_complete"' "${logfile}")"
  errors="$(grep -c '"level":"ERROR"' "${logfile}")"
  # error rate as a percentage, two decimals, computed with awk
  rate="$(awk -v e="${errors}" -v t="${total}" 'BEGIN{ printf "%.2f", (t>0)? (e/t)*100 : 0 }')"

  # p95 and p50 latency: extract the numeric latency_ms of every request, then
  # compute real nearest-rank percentiles in python3.
  local pcts p95 p50
  pcts="$(grep '"event":"request_complete"' "${logfile}" \
    | sed -n 's/.*"latency_ms":\([0-9]*\).*/\1/p' \
    | python3 -c '
import sys, math
vals = sorted(int(x) for x in sys.stdin.read().split())
n = len(vals)
def pct(p):
    if n == 0: return 0
    return vals[math.ceil(p/100*n) - 1]
print(pct(95), pct(50))
')"
  p95="${pcts%% *}"
  p50="${pcts##* }"

  # --- 3. the DASHBOARD ----------------------------------------------------
  echo "=== Observability Dashboard ==="
  printf 'Total requests:   %s\n' "${total}"
  printf 'Errors:           %s\n' "${errors}"
  printf 'Error rate:       %s%%\n' "${rate}"
  printf 'p95 latency (ms): %s\n' "${p95}"
  printf 'p50 latency (ms): %s\n' "${p50}"
}

# --- reconstruct the TRACE timing from the span start/end lines ------------
print_trace() {
  echo "=== Trace: request trace-7f3a9c ==="
  # For each span, pair its start and end at_ms and print the duration, indented
  # so children sit under the parent. python3 parses the JSON span lines (this
  # runs identically on macOS and Linux, unlike GNU-only awk extensions).
  grep '"event":"span_' "${logfile}" | python3 -c '
import sys, json
start, dur, order = {}, {}, []
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    name = r["span"]
    if r["event"] == "span_start":
        start[name] = r["at_ms"]
        order.append(name)
    else:
        dur[name] = r["at_ms"] - start[name]
for name in order:
    indent = "  " if name == "total_request" else "    "
    print("%sspan %-16s %4d ms" % (indent, name, dur[name]))
'
}

# --- run the pipeline ------------------------------------------------------
run_app
run_traced_request

# Show a few raw structured log lines so the format is visible, including one
# ERROR line so you can see how a failure is recorded.
echo "=== Sample structured logs (2 healthy, 1 error) ==="
grep '"level":"INFO"' "${logfile}" | grep '"event":"request_complete"' | head -n 2
grep '"level":"ERROR"' "${logfile}" | head -n 1
echo

compute_metrics
print_trace
echo "=== End of dashboard ==="
