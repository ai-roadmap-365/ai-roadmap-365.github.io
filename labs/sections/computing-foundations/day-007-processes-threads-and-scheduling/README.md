# Day 007 lab — Processes in the Wild: Spawn, Watch, Signal

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Processes, Threads, and Scheduling
- **Day number:** 7 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-007-processes-threads-and-scheduling
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-007-processes-threads-and-scheduling` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 7's lesson explains processes, threads, and the scheduler. This lab puts your hands on the controls: you count the process population on **your own machine**, trace your shell's ancestry through the process tree, spawn a background process, watch it through both the shell's eyes (`jobs`) and the system's (`ps`), terminate it politely with a signal, and verify its death by exit code — the exact spawn-observe-signal-verify cycle you will use on real training jobs later in the course.

## Learning objectives

- Start a background process with `&` and capture its PID from `$!` immediately.
- Observe a process with `jobs -l` and `ps -o pid,ppid,stat,command`, and read its state.
- Trace a parent chain: your script's PID, its parent shell, and upward toward PID 1.
- Terminate a process politely with SIGTERM, collect its exit status with `wait`, and explain why it is 143.
- Observe the difference between `kill` (SIGTERM) and `kill -9` (SIGKILL) on processes you started.
- Complete a working shell script by filling in five well-specified exercises and pass an automated test suite.

## Prerequisites

- The Day 7 lesson (read it first — it explains every concept this lab exercises).
- The Day 1 lab (comfort running commands in a terminal).
- A terminal: Terminal.app (macOS), any terminal (Linux), or WSL (Windows).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution; only standard `ps`, `kill`, `sleep` are used).
- **Windows** — run the scripts unmodified inside WSL; native PowerShell equivalents (`Get-Process`, `Stop-Process`) exist but are not covered by the tests.

## Hardware requirements

Any computer that runs a shell. The lab spawns nothing heavier than a `sleep`, which uses effectively zero CPU and memory.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard OS utilities only: `ps`, `kill`, `sleep`, `wc`, `tail`, `tr`, `sed`, `date`, plus the shell built-ins `jobs`, `wait`, and `trap`. All preinstalled.

## Free and open-source options

Everything in this lab is free: bash and every command used ship with your operating system. No account, API key, or purchase is needed — this is true of every lab in the course wherever possible, and any exception is labelled.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-007-processes-threads-and-scheduling
```

## File structure

```text
day-007-processes-threads-and-scheduling/
├── README.md                          ← you are here
├── metadata.yml                       ← machine-readable lab metadata
├── starter/
│   ├── process_playground.sh          ← YOUR working file (5 exercises)
│   └── process-worksheet.md           ← worksheet for the practice assignment
├── examples/
│   └── process_playground.sh          ← completed reference implementation
├── tests/
│   └── run_tests.sh                   ← automated checks
├── expected-output/
│   ├── sample-run-macos.txt           ← real captured run (macOS, Apple Silicon)
│   └── FIELDS.md                      ← required fields; why your PIDs will differ
├── requirements/
│   └── README.md                      ← dependency statement (none beyond the OS)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/process_playground.sh

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/process_playground.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/process_playground.sh` — runs the reference script: counts every process (`ps -e | tail -n +2 | wc -l`), prints its own PID (`$$`) and walks its parent chain with `ps -o pid,ppid,command`, starts `sleep 300 &`, captures the worker's PID from `$!`, shows the worker via `jobs -l` and `ps -o pid,ppid,stat,command`, sends SIGTERM with `kill`, collects exit status 143 with `wait`, and proves the PID is gone with `ps -p`.
- `bash starter/process_playground.sh` — the same skeleton with five exercises left for you; each exercise comment names the exact command to use. The script runs safely even before you start (the spawn/kill steps activate once Exercise 3 is done).
- `bash tests/run_tests.sh` — runs both scripts and checks: exit code 0, header/footer, a real numeric process count, that the script spawned **its own** worker and captured its PID, that the worker died to SIGTERM (exit status 143), that the script verified the death, and — independently — that the worker's PID no longer exists afterward (no orphaned sleeps). The tests only read the process table; they never signal anything themselves.

## Expected output

See [`expected-output/sample-run-macos.txt`](expected-output/sample-run-macos.txt) — a real captured run:

```text
=== Process Playground ===
Generated on: 2026-07-12
Processes running right now: 912
This script's PID: 25751
Parent chain (this script and up to 5 ancestors):
  25751     1 bash examples/process_playground.sh
      1     0 /sbin/launchd
Started background worker: sleep 300 (PID 25776)
The worker as seen by jobs:
  [1]+ 25776 Running                 sleep 300 &
The worker as seen by ps:
    PID  PPID STAT COMMAND
  25776 25751 SN   sleep 300
Sent SIGTERM to 25776; wait reported exit status 143 (143 = 128 + 15, death by SIGTERM)
Verified: PID 25776 is gone
=== End of playground ===
```

**Every PID (and the process count) will differ on your run** — the kernel assigns PIDs at spawn time. What must match is the shape: the worker's PPID equals the script's PID, the exit status is exactly 143, and the verified-gone line names the spawned PID. Run from an interactive terminal, your parent chain will be longer than the sample's (your shell, your terminal app, up toward PID 1); the sample was captured from a detached run, so its chain ends at `/sbin/launchd`. [`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists exactly which fields must appear.

## Validation steps

1. Run `bash starter/process_playground.sh` — it must exit without errors.
2. Confirm **no line contains `unknown`**.
3. Confirm the worker's PPID in the `ps` output equals the script's own PID — parent and child.
4. Confirm the exit status line reports 143, and the final line reads `Verified: PID <yours> is gone`.
5. Run `pgrep -l sleep` — no sleeper of yours should remain.
6. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `17 checks, 0 failure(s).` (12 strict checks against the reference script, and 5 structural checks against your starter — which become 12 strict checks once you have replaced every `unknown`, for `24 checks, 0 failure(s).` in total). The command exits 0 on success, non-zero on any failure, so it can run in CI.

## Cleanup

The scripts clean up after themselves: each sets a `trap` so its own worker is terminated even if the script fails midway, and the tests verify no sleeper survives. If you experimented manually and lost track of a sleeper, see the orphaned-sleeps entry in [troubleshooting.md](troubleshooting.md) — or simply wait: a `sleep 300` exits by itself within five minutes. To reset your work: `git checkout -- starter/process_playground.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (stale PIDs, `wait` refusing foreign children, per-shell `jobs`, orphaned sleeps and cleanup, 137-versus-143 confusion, WSL notes).

## Security notes

See [security.md](security.md). Short version: the scripts only ever signal the one process they started themselves, captured from `$!` — **never signal a process you did not start**, never `sudo kill`, and treat `kill -9` as a last resort because it forbids cleanup.

## Extension exercises

1. Add a second worker to your completed script (`sleep 300 &` again, capturing a second PID), terminate one with `kill` and the other with `kill -9`, and print both exit statuses (143 versus 137) with a line explaining the 128 + signal-number arithmetic.
2. Freeze and thaw: send your worker `kill -STOP <PID>`, show its `T` state in `ps -o stat`, resume it with `kill -CONT <PID>`, then terminate it politely.
3. Make the scheduler visible: run `yes > /dev/null &` (a pure CPU burner), watch it with `top`, add more burners than you have cores, observe the sharing, then terminate every burner you started — politely, by the PIDs you captured.

## Navigation

- **Previous day:** Day 6 — Operating Systems: What They Do and Why (`labs/sections/computing-foundations/day-006-operating-systems-what-they-do-and/`).
- **Next day:** Day 8 — the first day of Week 2, The Command Line (`labs/sections/computing-foundations/command-line/week-02/`, to be written).
- **Weekly project:** Annotated Machine Teardown (`labs/sections/computing-foundations/project/`).
