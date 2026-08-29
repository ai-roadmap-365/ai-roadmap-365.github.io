# Day 018 lab — Speak HTTP by Hand

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** HTTP: Requests, Responses, and Methods
- **Day number:** 18 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-018-http-requests-responses-and-methods
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-018-http-requests-responses-and-methods` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 18's lesson reads the two HTTP messages on paper. This lab makes them real: you use `curl` to **send actual requests** to free public test services and read the raw request and response — the status line, the headers, the body echoed back. By the end, a status code stops being a mystery and becomes information you act on, which is exactly the skill that turns a failing API call into a two-minute fix.

## Learning objectives

- Send an HTTP request with `curl` and read both the request (`>`) and response (`<`) in verbose mode.
- Print a bare status code, ignoring the body, with `-o /dev/null -w "%{http_code}"`.
- Send a `POST` with a JSON body and confirm the server received it by reading the echo.
- Trigger a `404` on purpose and classify it (`4xx` = your request was wrong).
- Explain, for a `401` versus a `429`, whose fault it is and what your code should do.

## Prerequisites

- The Day 18 lesson (read it first — it explains every message this lab sends).
- Comfort running commands in a terminal (Days 8–14).
- `curl` (preinstalled on macOS and Linux) and a working internet connection.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with curl 8.7.1).
- **Linux** — fully supported (any distribution with `curl` and `bash`).
- **Windows** — use WSL (Windows Subsystem for Linux) and follow the Linux path; `curl` also ships with modern PowerShell but the flags differ, so WSL is smoother.

## Hardware requirements

Any computer that can reach the internet. The lab sends a handful of tiny requests and needs no special hardware.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- `curl` (preinstalled on macOS and Linux; the one tool this lab depends on).
- Optional: HTTPie (`http`) for the friendlier alternative shown in the lesson.

## Free and open-source options

Everything here is free. `curl` is open source and ships with your OS; the test services (`https://httpbin.org` and its mirror `https://httpbingo.org`, plus `https://example.com`) are free public endpoints that need no account or API key. No purchase is required at any point.

## Installation

None beyond what your OS already has. From the repository root:

```bash
cd labs/sections/computing-foundations/day-018-http-requests-responses-and-methods
```

If `curl` is somehow missing, install it with your Day 13 package manager (`brew install curl` on macOS, `sudo apt install curl` on Debian/Ubuntu).

## File structure

```text
day-018-http-requests-responses-and-methods/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── http_explorer.sh            ← YOUR working file (4 exercises)
│   └── http-worksheet.md           ← worksheet for the practice assignment
├── examples/
│   └── http_explorer.sh            ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (structure + network)
├── expected-output/
│   ├── sample-run.txt              ← a real captured run
│   └── FIELDS.md                   ← what a correct run shows on any platform
├── requirements/
│   └── README.md                   ← dependency statement (just curl)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/http_explorer.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/http_explorer.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/http_explorer.sh` — the reference script. It probes the network, then (Step 1) runs `curl -v https://example.com` and shows the request/response lines, (Step 2) prints just the `200` status code, (Step 3) `POST`s `{"hello":"world"}` and shows the server echoing it back in its `json` field, and (Step 4) requests a `404` on purpose and prints the code. If `httpbin.org` is busy it falls back to the compatible mirror `httpbingo.org`; if there is no network it explains what each step would show and exits cleanly.
- `bash starter/http_explorer.sh` — the same skeleton with the four `curl` commands left as placeholder lines; each exercise comment names the exact command to paste in. Edit the file in any text editor.
- `bash tests/run_tests.sh` — runs structure checks always, and network checks (a real `200` from `example.com` and a real `POST` echo) when online, skipping them with a clear message when offline. Exits 0 unless a check that actually ran failed.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real captured run. The essentials:

```text
STEP 2 — status code only for https://example.com
Status code: 200
...
STEP 3 — POST a JSON body ...
  "json": {
    "hello": "world"
  }
...
STEP 4 — deliberately request a 404 ...
Status code: 404
```

Your dates, byte counts, and the negotiated HTTP version (`HTTP/2` or `HTTP/1.1`) will differ — see [`expected-output/FIELDS.md`](expected-output/FIELDS.md) for exactly which parts are fixed and which vary, including the httpbin.org/httpbingo.org fallback note.

## Validation steps

1. Run `bash examples/http_explorer.sh` — it must reach `Step 2` with `Status code: 200`.
2. Confirm Step 3 shows `"hello": "world"` echoed back in the `json` field.
3. Confirm Step 4 prints `Status code: 404`.
4. Complete the four exercises in `starter/http_explorer.sh` and run it — it should print a `200`, the echoed body, and a `404`.
5. Run the tests (next section) — all checks that run must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line online: `7 checks, 0 failure(s), 0 skip(s).` Offline it reads `5 checks, 0 failure(s), 1 skip(s).` — the network checks are skipped, not failed. The command exits 0 on success (including the offline path), so it is safe in CI.

## Cleanup

Nothing to clean up: the scripts send read-only and harmless test requests and write nothing outside their own console output. To reset your edits, restore the starter files from git: `git checkout -- starter/http_explorer.sh starter/http-worksheet.md`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (curl missing, httpbin returning 503, `-d` and the method, redirects, and the offline path).

## Security notes

See [security.md](security.md). Short version: the lab talks only to public test endpoints, the `{"hello":"world"}` body is non-sensitive sample data, and you must never send a real API key or secret to a public echo service — a rule that carries straight into your model-API work.

## Extension exercises

1. Use the `HEAD` method — `curl -I https://example.com` — and note it returns the response headers with no body; it is `GET` without the download.
2. Measure a round trip: `curl -w "time_total: %{time_total}s\n" -o /dev/null -s https://example.com`, and reason about what that time includes.
3. Walk every status class with the test service: request `/status/200`, `/status/301`, `/status/403`, and `/status/500` on `https://httpbin.org` (or the mirror), printing just the code, and map each to its class and to the "whose fault, what to do" rule.

## Navigation

- **Previous day:** Day 17 — the lesson before this one in the computing-foundations section.
- **Next day:** Day 19 — HTTPS and TLS: Encryption on the Wire (builds directly on today by encrypting the very messages you just sent).
