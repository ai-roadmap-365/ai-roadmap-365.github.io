# Day 025 lab — Authenticate to an API

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** API Authentication: Keys, Tokens, and OAuth
- **Day number:** 25 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-025-api-authentication-keys-tokens-and-oauth
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-025-api-authentication-keys-tokens-and-oauth` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 25's lesson explains how APIs verify who is calling. This lab makes it
concrete: you use `curl` to send each common authentication scheme to a public
test server and watch it succeed and fail. You will see Basic auth return `200`
for the right password and `401` for the wrong one, send a bearer token, echo a
key header back off the server, and — the habit that matters most — read a
token from an environment variable instead of typing it inline. Every
credential here is an obviously fake placeholder, and the test server accepts
any of them, so **no API key and no account are required.**

## Learning objectives

- Send Basic auth, a bearer token, and an API key header with `curl`.
- Read authentication outcomes as HTTP status codes (`200` success, `401` a
  missing or wrong credential).
- Confirm a bearer token is accepted and echoed by the server.
- Read a credential from an environment variable so the secret never appears
  inline — the safe pattern you will use with every real key.
- Run an automated test that degrades gracefully offline and exits 0.

## Prerequisites

- The Day 25 lesson (read it first — it explains every scheme this lab sends).
- Day 18 (HTTP status codes) and Day 11 (environment variables) help.
- A terminal with `curl`: Terminal.app (macOS), any terminal (Linux), or
  WSL/Git Bash (Windows).
- No programming experience required; every command is given and explained.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with curl 8.7.1).
- **Linux** — fully supported (any distribution with `curl`).
- **Windows** — run the scripts unchanged in WSL or Git Bash.

## Hardware requirements

Any computer that can run a terminal and reach the internet. The lab only
sends small HTTP requests; it needs no minimum RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- `curl` (preinstalled on macOS and most Linux; `sudo apt install curl` on
  Debian/Ubuntu). Verify with `curl --version`.

## Free and open-source options

Everything in this lab is free: `bash` and `curl` are open-source or ship with
your OS, and `httpbin.org` is a free public test service. No account, API key,
or purchase is needed — the endpoints accept any (fake) credentials on purpose.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-025-api-authentication-keys-tokens-and-oauth
```

## File structure

```text
day-025-api-authentication-keys-tokens-and-oauth/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── auth_demo.sh                ← YOUR working file (4 exercises)
│   └── auth-worksheet.md           ← worksheet for the practice assignment
├── examples/
│   └── auth_demo.sh                ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (skip gracefully offline)
├── expected-output/
│   ├── sample-run.txt              ← real captured run (macOS, online)
│   └── FIELDS.md                   ← required output lines on every platform
├── requirements/
│   └── README.md                   ← dependency statement (curl only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/auth_demo.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/auth_demo.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/auth_demo.sh` — runs the reference script: it checks
  connectivity, then sends Basic auth with correct credentials (expecting
  `200`) and wrong credentials (expecting `401`), a bearer token in the
  `Authorization` header, an `X-API-Key` header the server echoes back, and a
  bearer token read from the `DEMO_TOKEN` environment variable. Offline, it
  announces the skip and exits 0.
- `bash starter/auth_demo.sh` — the same skeleton with four exercises left as
  "NOT DONE YET" placeholder echoes; each comment names the exact `curl`
  command to run. Edit the file in any text editor and replace each placeholder
  line with the command given.
- `bash tests/run_tests.sh` — runs structure checks (files present, the
  example exercises every scheme, the starter names its exercises, both scripts
  parse, no realistic long key-shaped string is present) and, when online,
  network checks: correct Basic auth returns `200`, wrong credentials return
  `401`, and the bearer endpoint returns `200`. Offline or during a transient
  httpbin `503`, the network checks are skipped, not failed. Exits 0 unless a
  structure check fails.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run. The key lines:

```text
--- 1. Basic auth with CORRECT credentials (expect 200) ---
HTTP status: 200

--- 2. Basic auth with WRONG credentials (expect 401) ---
HTTP status: 401

--- 3. Bearer token in the Authorization header ---
{
  "authenticated": true,
  "token": "token-example-123"
}
```

Your `X-Amzn-Trace-Id` value differs on every request — httpbin assigns it.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists exactly which
lines must appear on every platform.

## Validation steps

1. Run `bash examples/auth_demo.sh` — it must reach `=== End of demo ===`
   without errors.
2. Confirm Basic auth printed `200` for correct credentials and `401` for wrong
   ones.
3. Confirm the bearer endpoint returned `"authenticated": true` and echoed your
   token.
4. Complete `starter/auth_demo.sh` (no "NOT DONE YET" placeholder lines left)
   and run it — it must produce the same statuses.
5. Run the tests (next section) — all structure checks must pass and the script
   must exit 0.

## Tests

```bash
bash tests/run_tests.sh
```

The command exits 0 on success (no structure check failed), whether online or
offline, so it can run in CI. Online with httpbin healthy, the final line reads
`16 checks, 0 failure(s), 0 skip(s).`; when httpbin is transiently overloaded,
the three network checks are skipped (`13 checks, 0 failure(s), 3 skip(s).`) and
the script still exits 0 — a server outage is not your bug.

## Cleanup

Nothing to clean up: the scripts only send HTTP requests and write no files. To
reset your work, restore the starter from git:
`git checkout -- starter/auth_demo.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (`000` and `503`
responses, Basic auth `401`, empty `$DEMO_TOKEN`, missing `curl`, Windows).

## Security notes

See [security.md](security.md). Short version: this lab uses **only fake
credentials** against a public test server. Never put a real API key in a
script or commit one — store real keys in an environment variable or a
gitignored `.env`, use least privilege, and rotate any leaked key immediately.

## Extension exercises

1. Prove base64 is not encryption: `printf 'user:pass' | base64` then pipe the
   result to `base64 --decode` and watch `user:pass` come straight back with no
   key.
2. Send the `X-API-Key` in the URL query string instead of a header
   (`https://httpbin.org/get?api_key=demo-key`), see it echoed under `args`,
   and write one sentence on why that placement leaks the key into logs.
3. Verify a missing credential fails: `curl -s -o /dev/null -w '%{http_code}\n'
   https://httpbin.org/bearer` and confirm you get `401` with no token sent.

## Navigation

- **Previous day:** Day 24 — JSON and Data Serialization
  (`labs/sections/computing-foundations/day-024-json-and-data-serialization/`).
- **Next day:** Day 26 — Webhooks and Event-Driven APIs
  (`labs/sections/computing-foundations/day-026-webhooks-and-event-driven-apis/`, to be written).
