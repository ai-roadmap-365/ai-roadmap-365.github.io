# Day 021 lab — Debug a Request with curl

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Inspecting Traffic with curl and Developer Tools
- **Day number:** 21 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-021-inspecting-traffic-with-curl-and-developer
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-021-inspecting-traffic-with-curl-and-developer` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 21's lesson showed how to *see* what happens on the wire. This lab puts
the tools in your hands: you use `curl` to inspect a full request/response
conversation, follow a redirect, break down timing, prove which headers you
sent, read status codes deliberately, and walk a systematic decision tree
that diagnoses any failing request.

## Learning objectives

- Read a `curl -v` conversation and tell the connection notes, request, and
  response headers apart.
- Follow a redirect with `-L` and read the final status.
- Break a request's time into DNS, connect, TLS, and total with `-w`.
- Classify status codes (2xx/3xx/4xx/5xx) and know what each tells you to do.
- Apply a DNS → connect → TLS → status decision tree to diagnose a failure.

## Prerequisites

- The Day 21 lesson, and days 15–20 (the networking category).
- A terminal with `curl` and network access.

## Supported operating systems

- **macOS** and **Linux** — fully supported (`curl` preinstalled).
- **Windows** — `curl` ships with Windows 10+; or run under WSL.

## Hardware requirements

Any computer with an internet connection. The lab only makes ordinary web
requests.

## Required software

`curl` only — preinstalled everywhere. See `requirements/README.md`.

## Free and open-source options

Everything here is free: `curl` is open source, and the two test services
(`example.com`, `httpbin.org`) are free public endpoints. No accounts or API
keys.

## Installation

None. Change into this directory:

```bash
cd labs/sections/computing-foundations/day-021-inspecting-traffic-with-curl-and-developer
```

## File structure

```text
day-021-.../
├── README.md
├── metadata.yml
├── starter/
│   ├── debug_request.sh          ← YOUR working file (5 exercises)
│   └── debug-worksheet.md        ← record your captured values
├── examples/
│   └── debug_request.sh          ← completed reference implementation
├── tests/
│   └── run_tests.sh
├── expected-output/
│   └── sample-run.txt            ← real captured run
├── requirements/README.md
├── troubleshooting.md
└── security.md
```

## How to run

```bash
# 1. See the finished tool first (needs network)
bash examples/debug_request.sh

# 2. Complete the five exercises in the starter, then run it
bash starter/debug_request.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/debug_request.sh` — runs six inspections against
  `example.com` and `httpbin.org`: a full `curl -v` conversation, a followed
  redirect (`-IL`), a timing breakdown (`-w`), a headers echo (`-H` against
  `/headers`), deliberate 404/500 status reads, and a `diagnose()` function
  that walks the DNS → connect → TLS → status decision tree. It degrades
  gracefully offline.
- `bash starter/debug_request.sh` — the same skeleton with five numbered
  exercises; each names the exact `curl` command to use.
- `bash tests/run_tests.sh` — always verifies structure (files present, both
  scripts parse, the example exercises each core flag, the starter names five
  exercises), then — when online — checks the three key behaviours: `curl -L`
  follows the redirect to a 200, `curl` reads the deliberate 404 correctly,
  and the `/headers` endpoint echoes a header sent with `-H`. Offline, the
  live checks are skipped (never failed). Exits 0 on success.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) for a
real captured run. Your IPs, timings, and (for httpbin) transient statuses
will differ.

## Validation steps

1. `bash examples/debug_request.sh` prints all six sections without errors.
2. You can point at each `*`, `>`, `<` line in the `-v` output and say
   whether it is a connection note, your request, or the response.
3. The redirect section shows a 3xx first, then a 200 after `-L`.
4. The tests pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `11 checks, 0 failure(s), 0 skip(s).` online (some
checks skip, never fail, when offline). Exit 0 on success.

## Cleanup

Nothing to clean up — the scripts only make web requests and write no files.
Reset your edited starter with `git checkout -- starter/debug_request.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) — httpbin 503s, reading `-v`
output, redirects, timing interpretation, offline behavior.

## Security notes

See [security.md](security.md). Only public test endpoints; never send real
secrets to an echo service; redact `curl -v` headers before sharing.

## Extension exercises

1. Add a `diagnose()` call for a deliberately broken URL (a made-up hostname)
   and confirm it reports the DNS gate as FAILED.
2. Use `curl -w` to compare the total time of a cold request versus an
   immediate second request to the same host, and explain the difference.
3. Reproduce a `401` by calling `https://httpbin.org/basic-auth/user/pass`
   without credentials, then with `-u user:pass`, and read both status codes.

## Navigation

- **Previous day:** Day 20 — How Browsers Render: HTML, CSS, and JavaScript.
- **Next day:** Day 22 — What an API Is and Why Everything Has One.
