# Day 027 lab — Handle Limits and Pages

Build and run a small **resilient API client** in shell against free public test
servers: back off from a `429`, decide correctly which errors to retry, and
paginate across pages — collecting results without missing or repeating a row.

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Rate Limits, Pagination, and Error Handling
- **Day number:** 27 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-027-rate-limits-pagination-and-error-handling
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-027-rate-limits-pagination-and-error-handling` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 27's lesson explains the three habits of consuming a real API robustly. This
lab makes them concrete and executable: you run a client that survives rate
limits and server hiccups, classifies failures, and walks a paginated endpoint —
then you complete a starter version yourself. Every request hits a live, free,
key-less test server, so the numbers are real. This is Day 27 of the course.

## Learning objectives

- Trigger a `429 Too Many Requests` response and read the status code back.
- Watch an exponential-backoff-with-jitter loop retry and then **give up
  gracefully** — proving it terminates rather than looping forever.
- Classify a `500` (retry) apart from a `404` (do not retry) and say why.
- Paginate an endpoint with `_page`/`_limit` and collect results across pages.
- Run an automated test suite that verifies termination and the collected count.

## Prerequisites

- The Day 27 lesson (read it first — it explains every concept this lab runs).
- Days 18-24: HTTP status codes and JSON.
- A terminal with `bash`, `curl`, and `python3`. Internet access for the live
  parts (offline is supported and degrades gracefully).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with curl 8.7.1).
- **Linux** — fully supported (any distribution with `bash`, `curl`, `python3`).
- **Windows** — use WSL and follow the Linux instructions.

## Hardware requirements

Any computer from roughly the last 15 years. The lab only makes small HTTP
requests; it needs no particular RAM, disk, or GPU.

## Required software

- `bash` 3.2+, `curl`, and `python3` (used only to count JSON items).
- Standard utilities `awk`, `sed`, `grep`, `mktemp` — all preinstalled.
- See `requirements/README.md` for one-step install commands per platform.

## Free and open-source options

Everything here is free and needs no account or API key. `curl` and `python3`
are open source; the test servers (`httpbin.org`, `jsonplaceholder.typicode.com`)
are free public services. There is no paid component anywhere in this lab.

## Installation

None beyond the tools above. From the repository root:

```bash
cd labs/sections/computing-foundations/day-027-rate-limits-pagination-and-error-handling
```

## File structure

```text
day-027-rate-limits-pagination-and-error-handling/
├── README.md                              ← you are here
├── metadata.yml                           ← machine-readable lab metadata
├── starter/
│   ├── resilient_client.sh                ← YOUR working file (4 exercises)
│   └── resilience-worksheet.md            ← record your real numbers here
├── examples/
│   └── resilient_client.sh                ← completed reference implementation
├── tests/
│   └── run_tests.sh                       ← automated checks (with a watchdog)
├── expected-output/
│   ├── sample-run.txt                     ← a real captured run (online + offline)
│   └── FIELDS.md                          ← required lines on every platform
├── requirements/
│   └── README.md                          ← dependency statement
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished client first (online: live demos; offline: self-test)
bash examples/resilient_client.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/resilient_client.sh

# 3. Check your work
bash tests/run_tests.sh
```

To move faster while experimenting, shrink the delays:

```bash
BASE_DELAY=0 DELAY_CAP=0 bash examples/resilient_client.sh
```

## What the commands do

- `bash examples/resilient_client.sh` — runs the reference client: a
  backoff-retry loop against `httpbin.org/status/429` that retries with growing,
  jittered delays up to a cap and then gives up gracefully (honoring
  `Retry-After` when present); a `decide` step that reads a `500` and a `404` and
  states which to retry; and a paginator that walks two pages of
  `jsonplaceholder.typicode.com/posts` with `_page`/`_limit` and sums the items.
  Offline, it runs a no-network self-test of the backoff logic and exits 0.
- `bash starter/resilient_client.sh` — the same skeleton with four spots blanked
  out (marked `FILL_ME`); each numbered exercise names the exact change to make.
- `bash tests/run_tests.sh` — structure checks, plus a watchdog-guarded run that
  proves the backoff terminates and the pagination collects the expected count.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) for a real
captured run (online and offline). The key lines: the backoff prints several
`attempt N: HTTP ...` lines and exactly one `giving up gracefully`; the decide
step marks `/status/500` as `RETRY` and `/status/404` as `do NOT retry`; and the
paginator prints `collected 10 posts across 2 pages`. Your exact statuses, jitter
values, and retry counts will differ — that is the nature of a real API.

## Validation steps

1. Run `bash examples/resilient_client.sh` — it must finish on its own (never
   hang) and end with `Done.` (online) or the offline self-test message.
2. Confirm the backoff prints exactly one `giving up gracefully` line.
3. Confirm `/status/500` is classified as retry and `/status/404` as do-not-retry.
4. Confirm the paginator reports the total it collected across two pages.
5. Complete the four exercises in the starter and record your numbers on the
   worksheet, then run the tests below.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `17 checks, 0 failure(s), 0 skip(s).` online, or with some
`skip(s)` offline. Each script run is wrapped in a watchdog that kills and
**fails** any run that does not terminate — so a passing suite is proof the retry
loop cannot spin forever. The command exits 0 on success, non-zero on any
failure, so it can run in CI.

## Cleanup

Nothing to clean up: the scripts make read-only HTTP requests and write only a
short-lived temp file that they delete. To reset your work, restore the starter
from git: `git checkout -- starter/resilient_client.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md). Short version: transient `503`/`504`
or timeouts from the shared test server are **expected** and are exactly what
your client is built to survive — re-run in a minute for a cleaner picture.

## Security notes

See [security.md](security.md). Short version: be a polite client — honor rate
limits, add jitter, and cap your retries. Hammering an API can get your key or IP
blocked, and an uncapped retry storm is indistinguishable from an attack.

## Extension exercises

1. Make the client honor `Retry-After`: fetch
   `https://httpbin.org/response-headers?Retry-After=3`, read the header, and
   wait exactly that long instead of using the doubling delay.
2. Add a third page to the paginator and confirm the collected total rises
   accordingly; stop when a page returns zero items.
3. Add an idempotency check: print a warning before retrying anything that is not
   a `GET`, since non-idempotent writes are unsafe to repeat blindly.

## Navigation

- **Previous day:** Day 26 — Webhooks and Event-Driven APIs
  (`labs/sections/computing-foundations/day-026-webhooks-and-event-driven-apis/`).
- **Next day:** Day 28 — Consuming a Public API from the Command Line
  (`labs/sections/computing-foundations/day-028-consuming-a-public-api-from-the/`).
