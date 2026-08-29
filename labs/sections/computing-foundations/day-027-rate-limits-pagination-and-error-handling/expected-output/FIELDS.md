# Required fields in a run of `resilient_client.sh`

These lines must appear on every platform (macOS or Linux) and in both network
states. The exact status codes, jitter values, and retry counts vary run to
run — that variability is the point — but the *structure* is fixed.

## Online (network reachable)

| Section | Must contain |
| --- | --- |
| Header | `Day 027 — Resilient API client` |
| 1. Backoff | one or more `attempt N: HTTP ...` lines |
| 1. Backoff | exactly one `giving up gracefully` line (the loop MUST terminate) |
| 1. Backoff | a `made N retries before giving up` summary |
| 2. Decide | a `/status/500` line ending in `RETRY with backoff` |
| 2. Decide | a `/status/404` line ending in `do NOT retry` |
| 3. Paginate | two `page N: M items` lines |
| 3. Paginate | a `collected T posts across 2 pages` line (T is the sum) |
| Footer | `Done.` |

## Offline (network unreachable) or `--selftest`

| Must contain |
| --- |
| `OFFLINE:` (only in the auto-detected offline path) or `Self-test:` |
| a stubbed `attempt N: HTTP 503` sequence |
| exactly one `giving up gracefully` line — proof the loop terminates without a network |
| `loop terminated` |

## Platform notes

- The script needs only `bash`, `curl`, `awk`, `sed`, and (for the item count)
  `python3`. All ship with macOS and are one package install away on Linux.
- The public test servers (`httpbin.org`, `jsonplaceholder.typicode.com`) are
  shared and occasionally return transient 5xx or time out. The client is
  built to survive exactly that, so a run during a hiccup is still a valid run.
