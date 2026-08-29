# Day 040 lab — Build a Mini Observability Pipeline

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Observability: Logs, Metrics, Traces, and Dashboards
- **Day number:** 40 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-040-observability-logs-metrics-traces-and-dashboards
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-040-observability-logs-metrics-traces-and-dashboards` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 40's lesson explains the three pillars of observability — logs, metrics,
and traces — and how they feed dashboards and alerts. This lab makes them
concrete by building the whole pipeline **from nothing but plain log lines**: a
tiny "app" emits structured JSON logs, you derive real metrics from them (total
requests, error rate, and a p95 percentile), print a text dashboard, and
reconstruct a trace of nested spans. By the end you have seen that there is no
magic in any pillar — each is just events, counting, and arithmetic.

## Learning objectives

- Emit **structured JSON logs** with a timestamp, level, event, and latency.
- Derive **metrics** from raw logs: a total (counter), an error rate, and a p95
  latency computed as a real nearest-rank percentile.
- Print a small text **dashboard** of those metrics.
- Reconstruct a **trace** of nested spans from span start/end log lines.
- Run an automated test script and interpret its pass/fail output.

## Prerequisites

- The Day 40 lesson (read it first — it explains every concept this lab builds).
- A terminal: Terminal.app (macOS), any terminal (Linux), or WSL (Windows).
- `bash` and `python3` (both preinstalled on macOS and Linux; see Required software).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution with bash and python3).
- **Windows** — run the scripts unmodified inside WSL (Windows Subsystem for Linux).

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only generates a few
kilobytes of synthetic logs in a temporary file; it needs no minimum RAM, disk,
or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- `python3` (used for the percentile and JSON span parsing — preinstalled on
  macOS and nearly every Linux distribution; check with `python3 --version`).
- Standard text utilities: `grep`, `sed`, `awk`, `head`, `seq`, `mktemp` — all
  part of the base system.

## Free and open-source options

Everything in this lab is free and open source: bash, python3, and every
utility used ship with your OS or are open-source. No account, API key, network
access, or purchase is needed. The lesson's tool survey (Prometheus, Grafana,
OpenTelemetry, the ELK and Loki stacks) is likewise free and open source — this
lab teaches the ideas underneath those tools by hand.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-040-observability-logs-metrics-traces-and-dashboards
```

## File structure

```text
day-040-observability-logs-metrics-traces-and-dashboards/
├── README.md                          ← you are here
├── metadata.yml                       ← machine-readable lab metadata
├── starter/
│   ├── observe.sh                     ← YOUR working file (4 exercises)
│   └── observability-worksheet.md     ← worksheet for the practice assignment
├── examples/
│   └── observe.sh                     ← completed reference pipeline
├── tests/
│   └── run_tests.sh                   ← automated checks
├── expected-output/
│   ├── sample-run.txt                 ← real captured run (macOS, Apple Silicon)
│   ├── test-run.txt                   ← real captured test result
│   └── FIELDS.md                      ← the fixed metrics a correct run produces
├── requirements/
│   └── README.md                      ← dependency statement (bash + python3)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished pipeline first
bash examples/observe.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/observe.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/observe.sh` — runs the complete reference: an "app" writes 50
  structured JSON log lines to a temporary file (6 of them at `ERROR` level),
  then the script counts the requests (a counter), counts the errors and
  computes the error rate, computes the p95 and p50 latency as real nearest-rank
  percentiles with `python3`, prints a text dashboard, and reconstructs a trace
  of nested spans from span start/end lines. The temporary log file is removed
  automatically on exit.
- `bash starter/observe.sh` — the same pipeline with four values left as
  `FILL_ME`; each exercise comment names the exact command to use. Edit the file
  and replace each `FILL_ME` with the real command.
- `bash tests/run_tests.sh` — runs the reference strictly (structured logs
  emitted, error count is 6, error rate is 12.00%, p95 is a number, trace
  reconstructed) and checks the starter's structure until you finish it.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run. Because the workload is deterministic, a correct run produces the
same metrics on any platform:

```text
=== Observability Dashboard ===
Total requests:   50
Errors:           6
Error rate:       12.00%
p95 latency (ms): 2900
p50 latency (ms): 180
=== Trace: request trace-7f3a9c ===
  span total_request     812 ms
    span validate_input     12 ms
    span db_query          540 ms
    span call_service      248 ms
=== End of dashboard ===
```

[`expected-output/FIELDS.md`](expected-output/FIELDS.md) explains why each
number is what it is.

## Validation steps

1. Run `bash examples/observe.sh` — it prints the dashboard and trace above.
2. Complete the four exercises in `starter/observe.sh` and run it; confirm **no
   `FILL_ME` remains** and the dashboard shows an error rate of `12.00%` and a
   numeric p95.
3. Confirm the p95 latency is at or above the p50 (the slow tail is higher than
   the median).
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `22 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. It reaches no network.

## Cleanup

Nothing to clean up: the scripts write only to a temporary file that is deleted
automatically when they exit, and they change no settings and reach no network.
To reset your work, restore the starter from git:
`git checkout -- starter/observe.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (missing
`python3`, empty p95, error rate stuck at zero, permission messages, octal
arithmetic, and WSL notes).

## Security notes

See [security.md](security.md). Short version: the scripts run no network calls,
need no elevated privileges, and log **only synthetic data**. The lesson the
lab reinforces is that real logs can leak secrets and personal data — so you
never log credentials, tokens, or full request bodies without scrubbing them.

## Extension exercises

1. Add the **p99** latency to your dashboard alongside the p95, and note how far
   apart they are — a large gap means a few requests are dramatically slower than
   the rest.
2. Add a `region` field (such as `"us"` or `"eu"`) to each structured log line,
   then compute the **error rate per region** — a question the dashboard was not
   built to answer, which structured logging lets you ask after the fact.
3. Change the alerting threshold: decide the error rate at which you would page
   an on-call engineer, and write one sentence justifying it as a user-facing
   symptom rather than an internal cause.

## Navigation

- **Previous day:** Day 39 — Data Storage: Files, Databases, Object Storage, and Caches (`labs/sections/computing-foundations/day-039-data-storage-files-databases-object-storage/`).
- **Next day:** Day 41 — Thinking in Automation: Scripts, Hooks, and Pipelines (`labs/sections/computing-foundations/day-041-thinking-in-automation-scripts-hooks-and/`, to be written).
