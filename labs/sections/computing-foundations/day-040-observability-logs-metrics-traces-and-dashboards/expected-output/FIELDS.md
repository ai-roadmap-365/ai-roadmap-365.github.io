# Expected output — Day 040 lab

`sample-run.txt` is a real captured run of `examples/observe.sh` on the
authoring machine (macOS, Apple Silicon, 2026-07-12). `test-run.txt` is the
captured result of `tests/run_tests.sh`.

The workload is **deterministic**, so a correct run on any platform (macOS or
Linux, bash + python3) produces the same metrics:

| Field | Value | Why |
| --- | --- | --- |
| Total requests | `50` | The app emits 50 `request_complete` log lines |
| Errors | `6` | Every 8th request fails: requests 8, 16, 24, 32, 40, 48 |
| Error rate | `12.00%` | 6 ÷ 50 = 0.12 |
| p95 latency (ms) | `2900` | Nearest-rank p95 over the 50 latencies falls in the slow error tail |
| p50 latency (ms) | `180` | The median of the healthy 90–259 ms requests |
| Trace spans | `total_request` (812 ms) with 3 nested children | Durations reconstructed from span start/end lines |

The only line that legitimately varies between platforms is nothing in the
metrics — the numbers above are fixed. The sample structured log lines show
the exact JSON shape every entry uses: `ts`, `level`, `event`, `request_id`,
and `latency_ms`.

A completed `starter/observe.sh` (all four `FILL_ME` exercises finished)
produces the same Dashboard and Trace blocks as the reference.
