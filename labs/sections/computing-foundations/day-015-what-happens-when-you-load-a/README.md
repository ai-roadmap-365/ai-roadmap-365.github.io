# Day 015 lab — Trace a Real Page Load

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** What Happens When You Load a Web Page
- **Day number:** 15 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-015-what-happens-when-you-load-a
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-015-what-happens-when-you-load-a` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 15's lesson maps the journey a web request takes — URL, DNS, TCP, TLS,
HTTP, server, response, render. This lab makes the first stops concrete: you
point three standard command-line tools at a real website and watch its name
resolve to an address, measure the round-trip time, and read the per-stage
connection timings. By the end you can say, with real numbers, where the time
goes when a page starts to load.

## Learning objectives

- Resolve a host name to an IP address with `dig` (the DNS stop).
- Measure round-trip time to a host with `ping`, and recognise when ping is blocked.
- Read `curl`'s `-w` timing fields as a timeline of DNS, TCP, and TLS stages.
- Compute each stop's cost by subtracting consecutive `curl` timestamps.
- Complete a four-exercise shell script and run an automated test that degrades gracefully offline.

## Prerequisites

- The Day 15 lesson (read it first — it explains every stop this lab measures).
- Days 1–14 of this course (the terminal and running commands).
- An internet connection for live values; the lab and its tests still run and pass offline (network checks are skipped).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (`dig`, `ping`, `curl`; on minimal images `dig` may need the `dnsutils`/`bind-utils` package).
- **Windows** — run the scripts unmodified inside WSL, or use the PowerShell equivalents noted in `troubleshooting.md`.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only sends tiny
network probes and reads their timings; it needs no minimum RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- `dig`, `ping`, and `curl` — preinstalled on macOS and most Linux systems. See `requirements/README.md`.

## Free and open-source options

Everything here is free: `bash`, `dig`, `ping`, and `curl` are open-source or
ship with your OS. No account, API key, or purchase is needed. The lab only
queries public hosts over ordinary web traffic.

## Installation

None. Copy this directory (or clone the repository) and you are ready:

```bash
cd labs/sections/computing-foundations/day-015-what-happens-when-you-load-a
```

## File structure

```text
day-015-what-happens-when-you-load-a/
├── README.md                         ← you are here
├── metadata.yml                      ← machine-readable lab metadata
├── starter/
│   ├── trace_page_load.sh            ← YOUR working file (4 exercises)
│   └── journey-worksheet.md          ← worksheet for the practice assignment
├── examples/
│   └── trace_page_load.sh            ← completed reference implementation
├── tests/
│   └── run_tests.sh                  ← automated checks (skip network checks offline)
├── expected-output/
│   └── sample-macos.txt              ← real captured run (macOS, example.com)
├── requirements/
│   └── README.md                     ← dependency statement
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first (defaults to example.com)
bash examples/trace_page_load.sh

# 2. Trace a site of your choice
bash examples/trace_page_load.sh en.wikipedia.org

# 3. Your task: complete the four exercises in the starter, then run it
bash starter/trace_page_load.sh

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/trace_page_load.sh [host]` — runs the reference script. It performs `dig +short` on the host (DNS: name → IP), `ping -c 2` (round-trip time), and `curl -sS -o /dev/null -w "..."` with the fields `time_namelookup`, `time_connect`, `time_appconnect`, and `time_total` (the DNS, TCP, TLS, and total timings), printing a labelled journey report. If a tool is missing or the network is down, it prints a clear note and continues.
- `bash starter/trace_page_load.sh [host]` — the same report skeleton with four `PENDING-exercise-N` lines; each exercise comment names the exact command to substitute in.
- `bash tests/run_tests.sh` — runs the reference script and checks the report's structure (header, footer, the three stops). If the network is reachable it also checks that a real IP and real `curl` timings appear; if not, it skips those checks with a message and still exits 0.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) — a
real captured run (macOS, `example.com`, 2026-07-12):

```text
=== Request Journey Report ===
Host: example.com
Generated on: 2026-07-12

--- Stop 1: DNS lookup (name -> IP) ---
Resolved IP address(es):
  104.20.23.154
  172.66.147.243

--- Stop 2: Round-trip time (ping -c 2) ---
  PING example.com (104.20.23.154): 56 data bytes
  64 bytes from 104.20.23.154: icmp_seq=0 ttl=58 time=16.488 ms
  ...

--- Stop 3: Connection stages (curl -w timings) ---
  dns=0.003654s connect=0.021513s tls=0.046752s total=0.073891s
  ...
=== End of report ===
```

Your numbers will differ with distance and network — that is the point. Read
the `curl` line as a timeline: DNS finished at 3.7 ms, TCP connect at 21.5 ms,
TLS at 46.8 ms, and the full response at 73.9 ms.

## Validation steps

1. Run `bash examples/trace_page_load.sh` — it must print the report and exit without errors.
2. Confirm Stop 1 shows a resolved IP, Stop 2 shows `time=` values (or a clear "blocked" note), and Stop 3 shows a `dns=... total=...` line.
3. Complete the four exercises in `starter/trace_page_load.sh` and run it; no `PENDING-exercise` line should remain.
4. Run the tests (next section) — all checks must pass (or be skipped offline).

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line online: `12 checks, 0 failure(s), 0 skipped.` Offline it
reads `7 checks, 0 failure(s), 3 skipped.` The command exits 0 on success and
non-zero on any structural failure, so it can run in CI with or without a
network.

## Cleanup

Nothing to clean up: the scripts make only tiny outbound probes and write no
files outside their own console output. To reset your work, restore the
starter from version control: `git checkout -- starter/trace_page_load.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (`dig` missing,
ping blocked, `could not resolve host`, all-zero timings, WSL notes).

## Security notes

See [security.md](security.md). Short version: the scripts query only the
public host you name, over ordinary DNS and HTTPS traffic, send no data beyond
a normal GET, need no elevated privileges, and write nothing to disk.

## Extension exercises

1. Run `traceroute <host>` (Windows: `tracert`) and count the network hops; note where the round-trip time jumps.
2. Trace two sites — one hosted near you and one on another continent — and compare their DNS, TLS, and total `curl` times.
3. Extend the reference script to also print `time_starttransfer` (when the first response byte arrived) and update the tests to check for it.

## Navigation

- **Previous day:** Day 14 — the last lesson of the tools-and-terminal week (`labs/sections/computing-foundations/day-014-.../`).
- **Next day:** Day 16 — IP Addresses, DNS, and Routing (`labs/sections/computing-foundations/day-016-ip-addresses-dns-and-routing/`, to be written).
