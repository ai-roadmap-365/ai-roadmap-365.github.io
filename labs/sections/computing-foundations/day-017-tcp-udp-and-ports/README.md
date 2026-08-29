# Day 017 lab — See Ports and Connections

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** TCP, UDP, and Ports
- **Day number:** 17 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-017-tcp-udp-and-ports
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-017-tcp-udp-and-ports` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 17's lesson explains the transport layer: TCP, UDP, and the port numbers
that let one machine run many services at once. This lab makes it concrete.
You interrogate **your own machine** to see which TCP ports it is *listening*
on, classify each port number into its IANA range, and then prove — with a
loopback connection test — the difference between a port that is **open**
(something is listening) and one that is **closed** (the "connection refused"
error you will meet constantly). Everything is read-only and local: the only
network action is `127.0.0.1` talking to itself.

## Learning objectives

- List the listening TCP ports on your machine with `lsof` (macOS) or `ss` /
  `netstat` (Linux).
- Classify a port number as well-known (0–1023), registered (1024–49151), or
  ephemeral (49152–65535), and name the service behind common well-known ports.
- Use `nc -z` to probe a port on the loopback and read its exit status to tell
  open from closed.
- Explain what "connection refused" means in terms of a listening socket.
- Run an automated test script and interpret its pass/fail output.

## Prerequisites

- The Day 17 lesson (read it first — it explains ports, TCP, UDP, and sockets).
- Day 16 (IP addresses, DNS, and routing) for the idea of an IP address that a
  port number rides on top of.
- A terminal: Terminal.app (macOS), any terminal (Linux), or PowerShell/WSL
  (Windows).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon), uses `lsof`.
- **Linux** — fully supported (uses `ss` from `iproute2`, or `netstat` as a
  fallback).
- **Windows** — use WSL and follow the Linux path, or the PowerShell
  equivalents noted in `troubleshooting.md`.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only reads local
system state and probes the loopback; it needs no minimum RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- A listening-socket viewer: `lsof` (macOS, preinstalled) or `ss` / `netstat`
  (Linux).
- `nc` (netcat) for the loopback probe — preinstalled on macOS; a one-line
  install on Linux (see `requirements/README.md`).

## Free and open-source options

Everything here is free and ships with your OS or installs from your package
manager at no cost. No account, API key, or purchase is needed.

## Installation

None. Copy this directory (or clone the repository) and change into it:

```bash
cd labs/sections/computing-foundations/day-017-tcp-udp-and-ports
```

If `nc` or `ss` is missing on Linux, see `requirements/README.md` for the
one-line install.

## File structure

```text
day-017-tcp-udp-and-ports/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── inspect_ports.sh            ← YOUR working file (4 exercises)
│   └── ports-worksheet.md          ← worksheet to fill in for your machine
├── examples/
│   └── inspect_ports.sh            ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (read-only, loopback-only)
├── expected-output/
│   ├── sample-macos.txt            ← real captured run (macOS, Apple Silicon)
│   └── FIELDS.md                   ← required sections + platform differences
├── requirements/
│   └── README.md                   ← dependency statement
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/inspect_ports.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/inspect_ports.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/inspect_ports.sh` — the reference script. It detects your OS
  (`uname -s`), lists listening TCP ports (`lsof -nP -iTCP -sTCP:LISTEN` on
  macOS; `ss -tlnp` / `netstat -tln` on Linux), classifies each port into its
  IANA range and guesses the service, then runs two `nc -z -w 1 127.0.0.1
  <port>` probes to demonstrate one OPEN port and one closed port.
- `bash starter/inspect_ports.sh` — the same skeleton with four numbered
  exercises. Each comment names the exact command to run; you replace the
  `EXERCISE N` placeholder lines with real commands.
- `bash tests/run_tests.sh` — runs the reference script and checks: exit code
  0, all four required section headers present, the loopback test targets
  `127.0.0.1`, and the script contains no `sudo`/`curl`/`wget` and no `nc`
  probe against any non-loopback address.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) —
a real captured run:

```text
=== Ports and Connections ===
Generated on: 2026-07-12
Operating system kernel: Darwin

--- Listening TCP ports ---
A 'listening' port is a service waiting for incoming connections.
PORT    CLASS        LIKELY SERVICE                   PROCESS
4321    registered   -                                node
5000    registered   common dev server / AirPlay on macOS ControlCe
7000    registered   AirPlay receiver (macOS)         ControlCe
...

--- Loopback connection test ---
127.0.0.1 is 'localhost' — this machine talking to itself, no network.
Testing 127.0.0.1:5000 ... OPEN (something is listening here)
Testing 127.0.0.1:1 ... closed (connection refused — nothing listening)
=== End of report ===
```

Your ports will differ — that is the point. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists the required sections and describes Linux and Windows differences.

## Validation steps

1. Run `bash examples/inspect_ports.sh` — it must exit without errors.
2. Confirm all four sections print: `Listening TCP ports`, `Well-known vs
   ephemeral`, `Loopback connection test`, and the header/footer.
3. Confirm the loopback test prints one OPEN line and one closed line, both
   against `127.0.0.1`.
4. Fill in `starter/ports-worksheet.md` for your own machine.
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `9 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. The tests confirm the script
is read-only and probes only the loopback.

## Cleanup

Nothing to clean up: the scripts only read local state and probe `127.0.0.1`;
they write no files and change no settings. To reset your work, restore the
starter from git: `git checkout -- starter/inspect_ports.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (`lsof` shows
fewer ports without `sudo` — that is fine and expected; missing `nc`/`ss`;
IPv6-only listeners; the port-1 "connection refused" demonstration; Windows
notes).

## Security notes

See [security.md](security.md). Short version: read-only, loopback-only, no
`sudo`, and it never scans or contacts an external host — scanning machines
you do not own can be illegal, so this lab hard-codes `127.0.0.1`.

## Extension exercises

1. Probe the **IPv6** loopback for a service bound to `[::1]`:
   `nc -z -w 1 ::1 <port>`. Which of your services answer on IPv6 but not
   IPv4?
2. Add a UDP listing to the report. On macOS: `lsof -nP -iUDP`; on Linux:
   `ss -ulnp`. Notice UDP sockets have no "LISTEN" state — a clue to how UDP
   differs from TCP.
3. Extend the well-known-port lookup table in the script with three more
   ports you care about (for example `3306` MySQL, `27017` MongoDB, `11434`
   for a local model server) and re-run it.

## Navigation

- **Previous day:** Day 16 — IP Addresses, DNS, and Routing
  (`labs/sections/computing-foundations/day-016-ip-addresses-dns-and-routing/`).
- **Next day:** Day 18 — HTTP: Requests, Responses, and Methods
  (`labs/sections/computing-foundations/day-018-http-requests-responses-and-methods/`, to be written).
