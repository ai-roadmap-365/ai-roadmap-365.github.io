# Day 016 lab — Explore DNS and Routing

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** IP Addresses, DNS, and Routing
- **Day number:** 16 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-016-ip-addresses-dns-and-routing
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-016-ip-addresses-dns-and-routing` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 16's lesson explains how a name becomes an address and how packets reach
it. This lab makes it concrete: you query the real Domain Name System and
trace the real route to a host from your own machine, using the same
command-line tools professionals reach for first. You resolve `example.com`
to its IPv4 and IPv6 addresses, read its mail record, and trace the path
across routers to it — then classify each address as public or private.

## Learning objectives

- Resolve a name to its A (IPv4) and AAAA (IPv6) addresses with `dig`.
- Read a domain's MX (mail-exchange) record and interpret a null MX.
- Trace the route to a host and count the hops with `traceroute`.
- Classify an IPv4 address as public, private, or loopback by its range.
- Complete a shell script by filling in four well-specified exercises.
- Run an automated test that degrades gracefully when offline.

## Prerequisites

- The Day 16 lesson (read it first — it explains every concept this lab uses).
- A terminal and comfort running commands (Days 8–14).
- A working network connection for the live queries. Offline, the scripts and
  tests still run and report clearly — see "How to run".

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon; `dig`,
  `traceroute`, `whois`, and `ping` ship with the system or via one package).
- **Linux** — fully supported (`dig` from `dnsutils`/`bind-utils`,
  `traceroute` from its own package; installation covered in `requirements/`).
- **Windows** — use `nslookup` for lookups and `tracert` for the path (both
  built in), or run the scripts unmodified inside WSL.

## Hardware requirements

Any computer able to reach the network. The lab only reads DNS answers and
sends small trace probes; it needs no particular RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- `dig` (from BIND/`dnsutils`) — or `nslookup` as a fallback.
- `traceroute` (or `tracert` on Windows).
- Optional: `whois` and `ping` for the extension exercises.

See [`requirements/README.md`](requirements/README.md) for install commands.

## Free and open-source options

Everything here is free and open source or ships with your OS: `bash`, `dig`,
`nslookup`, `traceroute`, `whois`, and `ping`. No account, API key, or
purchase is needed. Commercial DNS-monitoring and IP-intelligence services
exist, but they are built on exactly these queries, which you run yourself
here for free.

## Installation

Usually nothing to install on macOS. On minimal Linux images you may need the
DNS and traceroute tools:

```bash
# Debian / Ubuntu
sudo apt install dnsutils traceroute
# Fedora
sudo dnf install bind-utils traceroute
```

## File structure

```text
day-016-ip-addresses-dns-and-routing/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── explore_dns.sh              ← YOUR working file (4 exercises)
│   └── dns-worksheet.md            ← worksheet for the practice assignment
├── examples/
│   └── explore_dns.sh              ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (online and offline)
├── expected-output/
│   └── sample-macos.txt            ← a real captured run (macOS, online)
├── requirements/
│   └── README.md                   ← dependency and install notes
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/explore_dns.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/explore_dns.sh

# 3. Check your work
bash tests/run_tests.sh
```

You may pass a different domain as an argument, e.g.
`bash examples/explore_dns.sh wikipedia.org`.

## What the commands do

- `bash examples/explore_dns.sh` — the reference script: resolves the A and
  AAAA records with `dig +short`, reads the MX record, notes how to run
  `dig +trace` to watch the hierarchy walk, then runs a short, timeout-bounded
  `traceroute` and classifies each IPv4 address as public, private, or
  loopback. If the machine is offline (or `dig` is missing) it says so on each
  line and still exits 0.
- `bash starter/explore_dns.sh` — the same report skeleton with four values
  set to `REPLACE_ME`; each exercise comment names the exact command to use.
  Edit the file and replace each assignment with the command in `$(...)` form.
- `bash tests/run_tests.sh` — checks that the reference script exits cleanly
  and prints a well-formed report; when online, that `dig` returns a real
  IPv4; when offline, it SKIPS the network checks with a message and still
  passes. Exit code is 0 on success, non-zero on any structural failure.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) — a
real captured run (macOS, online, 2026-07-12). Your addresses and hops will
differ; that is the point. The traceroute middle hops depend on your ISP and
location, and some routers answer with `* * *` (silence) — both are normal.
When offline, every live line is replaced by a plain "(offline / no dig …)"
note and the script still completes.

## Validation steps

1. Run `bash examples/explore_dns.sh` — it must complete and exit without
   errors, online or offline.
2. Complete the four exercises in `starter/explore_dns.sh` and run it; confirm
   the A, AAAA, and MX sections show real values (when online).
3. Confirm you can say, for each IPv4 address shown, whether it is public or
   private (does it start with `10.`, `192.168.`, `172.16`–`172.31`, or `127.`?).
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line online: `12 checks, 0 failure(s), 0 skipped.` (Offline it
reads `10 checks, 0 failure(s), 2 skipped.` — the two network checks are
skipped, not failed.) The command exits 0 on success and non-zero on any
structural failure, so it is safe to run in CI.

## Cleanup

Nothing to clean up: the scripts make DNS queries and short trace probes and
write nothing outside their own console output. To reset your work, restore
the starter from git: `git checkout -- starter/explore_dns.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (missing `dig`
or `traceroute`, silent `* * *` hops, empty MX answers, caching surprises,
Windows notes).

## Security notes

See [security.md](security.md). Short version: the scripts query public DNS
and trace a route to a public test domain; they make no other connections,
need no elevated privileges, and collect nothing sensitive — but a traceroute
does reveal your ISP and rough location, so think before pasting one publicly.

## Extension exercises

1. Run `dig +trace example.com` and find the line where a root server hands
   off to the `.com` servers and where a `.com` server hands off to the
   authoritative servers.
2. Run `dig NS example.com` (authoritative name servers) and
   `whois example.com` (who is registered as responsible for the name).
3. Pick any address you saw and classify it fully — IPv4 or IPv6, public or
   private — and run `whois <address>` to see which organization's block it
   belongs to.

## Navigation

- **Previous day:** Day 15 — What Happens When You Load a Web Page.
- **Next day:** Day 17 — TCP, UDP, and Ports.
