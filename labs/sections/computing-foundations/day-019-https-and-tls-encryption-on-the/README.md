# Day 019 lab — Inspect a TLS Certificate

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** HTTPS and TLS: Encryption on the Wire
- **Day number:** 19 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-019-https-and-tls-encryption-on-the
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-019-https-and-tls-encryption-on-the` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 19's lesson explains how HTTPS secures a connection: the handshake, the
mix of symmetric and public-key encryption, and the certificate chain of
trust. This lab makes it concrete. You use `openssl` and `curl` to inspect a
**real** TLS certificate — its subject, issuer, and validity dates — and to
watch the TLS version get negotiated, so the padlock stops being magic and
becomes something you can read for yourself.

## Learning objectives

- Read a certificate's subject, issuer, and not-before / not-after dates from the command line.
- Distinguish the certificate's subject (the domain) from its issuer (the CA that signed it).
- Observe the negotiated TLS version and the "certificate verify ok" result in a real handshake.
- Trace the certificate chain a server sends and explain why a missing intermediate breaks trust.
- Complete a working shell script by filling in four well-specified exercises.

## Prerequisites

- The Day 19 lesson (read it first — it explains every concept this lab inspects).
- Comfort running commands in a terminal (Days 8–14).
- An internet connection (this lab opens a real HTTPS connection).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, OpenSSL 3.x).
- **Linux** — fully supported (any distribution with `openssl` and `curl`).
- **Windows** — use WSL and follow the Linux path, or Git Bash (which bundles `openssl` and `curl`).

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only reads a public
certificate over the network; it needs no special hardware.

## Required software

- `openssl` (LibreSSL on macOS or OpenSSL 3.x — both work; preinstalled).
- `curl` (preinstalled on macOS and Linux).
- Network access to reach the host being inspected.

## Free and open-source options

Everything in this lab is free and open source: `openssl` and `curl` ship
with your OS or install at no cost, and inspecting a public certificate costs
nothing. Getting a certificate for a site *you* run is also free — the lesson
covers Let's Encrypt, a non-profit CA that issues certificates at no charge.

## Installation

None. Both tools are preinstalled. From the repository root:

```bash
cd labs/sections/computing-foundations/day-019-https-and-tls-encryption-on-the
```

## File structure

```text
day-019-https-and-tls-encryption-on-the/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── inspect_tls.sh              ← YOUR working file (4 exercises)
│   └── tls-worksheet.md            ← worksheet for the practice assignment
├── examples/
│   └── inspect_tls.sh              ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (skip gracefully offline)
├── expected-output/
│   ├── sample-example-com.txt      ← real captured run (macOS, example.com)
│   └── FIELDS.md                   ← required fields and platform differences
├── requirements/
│   └── README.md                   ← dependency statement (openssl, curl, network)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first (defaults to example.com)
bash examples/inspect_tls.sh

# 2. Try another host of your choice
bash examples/inspect_tls.sh wikipedia.org

# 3. Your task: complete the four exercises in the starter, then run it
bash starter/inspect_tls.sh

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/inspect_tls.sh [host]` — runs the reference script: it
  checks the host is reachable, then uses `openssl s_client` piped into
  `openssl x509` to print the certificate's subject, issuer, and validity
  dates, and `curl -vI` to show the negotiated TLS version and the
  verification result.
- `bash starter/inspect_tls.sh` — the same skeleton with four `REPLACE ME`
  lines; each exercise comment names the exact command to paste in. Edit the
  file in any text editor and replace each placeholder.
- `bash tests/run_tests.sh` — runs structural checks always, and, when the
  network is available, verifies that `openssl` returns a subject, an issuer,
  and an expiry date and that the reference script completes. Offline, the
  certificate checks are skipped (not failed) and the script still exits 0.

## Expected output

See [`expected-output/sample-example-com.txt`](expected-output/sample-example-com.txt) — a real captured run:

```text
=== TLS inspection for example.com ===
Generated on: 2026-07-12

--- Certificate (openssl) ---
subject=CN=example.com
issuer=C=US, O=SSL Corporation, CN=Cloudflare TLS Issuing ECC CA 3
notBefore=May 31 21:39:12 2026 GMT
notAfter=Aug 29 21:41:26 2026 GMT

--- Handshake summary (curl) ---
* SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
*  subject: CN=example.com
*  expire date: Aug 29 21:41:26 2026 GMT
*  issuer: C=US; O=SSL Corporation; CN=Cloudflare TLS Issuing ECC CA 3
*  SSL certificate verify ok.

=== End of inspection ===
```

Your issuer, dates, and cipher will differ as certificates are renewed — the
*shape* is what stays the same. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists the required fields and describes platform differences.

## Validation steps

1. Run `bash examples/inspect_tls.sh` — it should print a subject, issuer, and dates, then a `SSL certificate verify ok.` line.
2. Confirm you can identify which line is the **domain** (subject) and which is the **CA** (issuer).
3. Confirm you can read the **expiry** date and the negotiated **TLS version**.
4. Complete the four exercises in `starter/inspect_tls.sh` and re-run it — its output should match the reference for the same host.
5. Run the tests (next section) — all checks must pass (or skip cleanly offline).

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line online: `10 checks, 0 failure(s), 0 skipped.` Offline the
certificate checks are skipped and the line reports a non-zero skip count,
but the command still exits 0 as long as nothing genuinely failed, so it is
safe in CI.

## Cleanup

Nothing to clean up: the scripts read a public certificate and print it,
writing nothing outside their own console output. To reset your work, restore
the starter from git: `git checkout -- starter/inspect_tls.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (`s_client`
appearing to hang, OpenSSL/LibreSSL flag differences, offline behavior, and
`curl` verbose formatting).

## Security notes

See [security.md](security.md). Short version: this is read-only inspection
of public certificates. The scripts send no data, need no elevated
privileges, and never disable certificate verification.

## Extension exercises

1. Add `-showcerts` to the `openssl` command and keep the `s:` / `i:` lines to see the full chain the server sends; count the certificates and match each issuer to the next subject up.
2. Inspect a site you run or your school's site and record its issuer and expiry; note whether it uses a free CA (such as Let's Encrypt) or a commercial one.
3. Deliberately find a certificate problem: try `https://expired.badssl.com` or `https://self-signed.badssl.com` and read exactly which check fails and how `curl` reports it.

## Navigation

- **Previous day:** Day 18 — HTTP: Requests, Responses, and Methods (`labs/sections/computing-foundations/day-018-http-requests-responses-and-methods/`).
- **Next day:** Day 20 — How Browsers Render: HTML, CSS, and JavaScript (`labs/sections/computing-foundations/day-020-how-browsers-render-html-css-and/`, to be written).
