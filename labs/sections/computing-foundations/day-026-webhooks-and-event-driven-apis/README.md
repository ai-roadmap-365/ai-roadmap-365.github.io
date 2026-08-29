# Day 026 lab — Simulate a Webhook Delivery

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Webhooks and Event-Driven APIs
- **Day number:** 26 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-026-webhooks-and-event-driven-apis
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-026-webhooks-and-event-driven-apis` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 26's lesson explained the shift from pull to push — how a server calls
*your* URL when an event happens. This lab makes it concrete without needing a
public server: you play **both** sides of a webhook on your own machine. You
compute the HMAC signature a sender attaches, deliver a sample payload to a
free echo service so you can see exactly what a receiver receives, verify a
genuine signature and reject a forged one, and watch a retry loop back off on a
simulated failure.

## Learning objectives

- Compute an HMAC-SHA-256 signature over a raw payload with a shared secret.
- Deliver a JSON payload as an HTTP `POST` and read what the receiver sees.
- Verify a delivery by recomputing and comparing the signature, and detect a
  tampered payload.
- Explain, from a working retry loop, why at-least-once delivery requires
  idempotent handling.

## Prerequisites

- The Day 26 lesson, and days 18–25 (HTTP, HTTPS/TLS, JSON, API authentication).
- A terminal with `curl` and `openssl` (both preinstalled). Network access for
  the live delivery step only.

## Supported operating systems

- **macOS** and **Linux** — fully supported (`curl` and `openssl` preinstalled).
- **Windows** — use WSL, or run the individual `curl`/`openssl` commands in a
  shell that provides them.

## Hardware requirements

Any computer with a terminal. The live delivery step needs an internet
connection; every other step is local.

## Required software

`curl` and `openssl` only — preinstalled almost everywhere. See
`requirements/README.md`.

## Free and open-source options

Everything here is free: `curl` and `openssl` are open source, and the echo
service (`httpbin.org`) is a free public endpoint. No accounts or API keys.

## Installation

None. Change into this directory:

```bash
cd labs/sections/computing-foundations/day-026-webhooks-and-event-driven-apis
```

## File structure

```text
day-026-webhooks-and-event-driven-apis/
├── README.md                    ← you are here
├── metadata.yml                 ← machine-readable lab metadata
├── starter/
│   ├── webhook_demo.sh          ← YOUR working file (4 exercises)
│   └── webhook-worksheet.md     ← record your signature, echo, and notes
├── examples/
│   └── webhook_demo.sh          ← completed reference implementation
├── tests/
│   └── run_tests.sh             ← structure + local HMAC + (online) echo checks
├── expected-output/
│   └── sample-run.txt           ← real captured run (online)
├── requirements/README.md
├── troubleshooting.md
└── security.md
```

## How to run

```bash
# 1. See the finished flow first (delivery step needs network)
bash examples/webhook_demo.sh

# 2. Complete the four exercises in the starter, then run it
bash starter/webhook_demo.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/webhook_demo.sh` — runs the full simulation in three sections:
  (1) computes the HMAC signature a sender attaches; (2) `POST`s the sample
  payload to `httpbin.org/post` and prints the body and signature header the
  receiver echoes back; (3) verifies a genuine signature (MATCH), rejects a
  tampered one (MISMATCH), and runs a retry loop that stops on a `200`. It
  degrades gracefully offline.
- `bash starter/webhook_demo.sh` — the same skeleton with four numbered
  exercises; each names the exact `openssl`/`curl` command to use.
- `bash tests/run_tests.sh` — always runs structure and **local HMAC** checks
  (both scripts parse, the example exercises each step, the signature is a
  64-hex string equal to the known value, a tampered body differs). When
  online it also confirms the echo endpoint returns your payload and
  signature; offline (or when httpbin is transiently down) that one check is
  **skipped**, never failed. Exits 0 on success.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) for a
real captured run. The signature is deterministic
(`sha256=cadd3bf8...e3c0`); your trace ID and the exact echo formatting will
differ.

## Validation steps

1. `bash examples/webhook_demo.sh` prints all three sections without errors.
2. The signature is 64 hexadecimal characters and equals
   `cadd3bf8973d72aec386c06d46c8803f68aa1f6936e9ee4a334adedace74e3c0`.
3. The echo section shows your exact payload body and `X-Webhook-Signature`.
4. The verify section shows MATCH for the genuine payload and MISMATCH for the
   tampered one, and the retry loop stops on the `200`.
5. The tests pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line online: `15 checks, 0 failure(s), 0 skip(s).` Offline the
live delivery check is skipped: `14 checks, 0 failure(s), 1 skip(s).` Either
way the command exits 0 on success, so it can run in CI.

## Cleanup

Nothing to clean up — the scripts write no files and make one ordinary web
request. Reset your edited starter with `git checkout -- starter/webhook_demo.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) — signature mismatches (trailing
newline), `openssl` formatting, httpbin transient failures, the skip on the
network check, and offline behavior.

## Security notes

See [security.md](security.md). Short version: the demo secret is fake — never
use a real one in code; verifying signatures is what stops forged webhooks;
always use HTTPS for a real receiver; never send real secrets to an echo
service.

## Extension exercises

1. Add **idempotency**: record each delivery's ID and make a repeated ID
   acknowledge with `200` but act only once; send the same delivery twice and
   prove the action happened once.
2. Add a **timestamp** inside the signed payload and reject deliveries older
   than five minutes, defending against replay of a captured message.
3. Send a **tampered** payload with the *original* signature header to the echo
   service, recompute on receipt, and confirm your verify step would reject it.

## Navigation

- **Previous day:** Day 25 — API Authentication: Keys, Tokens, and OAuth.
- **Next day:** Day 27 — Rate Limits, Pagination, and Error Handling.
