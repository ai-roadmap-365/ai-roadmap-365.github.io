# Day 001 lab — Inspect Your Own Computer

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** How a Computer Works: From Transistors to Programs
- **Day number:** 1 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-001-how-a-computer-works-from-transistors
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-001-how-a-computer-works-from-transistors` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 1's lesson explains the layers between physics and software. This lab makes it concrete: you interrogate **your own machine** from the terminal and produce a real "machine profile" — the CPU, cores, RAM, disk, and OS you will rely on for the next 364 days.

## Learning objectives

- Run commands in a terminal and read their output confidently.
- Measure your machine's CPU model, core count, RAM, free disk, and OS version.
- Convert bytes to GiB and explain the difference between memory (RAM) and storage (disk).
- Complete a small shell script by filling in five well-specified exercises.
- Run an automated test script and interpret its pass/fail output.

## Prerequisites

- The Day 1 lesson (read it first — it explains every concept this lab measures).
- A terminal: Terminal.app (macOS), any terminal (Linux), or PowerShell/WSL (Windows).
- No programming experience required; every command is given and explained.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution with `lscpu`, `nproc`, `/proc/meminfo`).
- **Windows** — use the PowerShell alternatives in the lesson's hands-on section (`Get-ComputerInfo`), or run the scripts unmodified inside WSL.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only *reads* system information; it needs no minimum RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard OS utilities only: `sysctl`, `sw_vers`, `df` (macOS); `lscpu`, `nproc`, `df` (Linux). All preinstalled.

## Free and open-source options

Everything in this lab is free: bash and every command used are open-source or ship with your OS. No account, API key, or purchase is needed — this is true of every lab in the course wherever possible, and any exception is labelled.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-001-how-a-computer-works-from-transistors
```

## File structure

```text
day-001-how-a-computer-works-from-transistors/
├── README.md                                 ← you are here
├── metadata.yml                              ← machine-readable lab metadata
├── starter/
│   ├── inspect_my_computer.sh                ← YOUR working file (5 exercises)
│   └── machine-profile-template.md           ← worksheet for the practice assignment
├── examples/
│   └── inspect_my_computer_completed.sh      ← completed reference implementation
├── tests/
│   └── run_tests.sh                          ← automated checks
├── expected-output/
│   ├── sample-macos.txt                      ← real captured run (macOS, Apple Silicon)
│   └── FIELDS.md                             ← required fields on every platform
├── requirements/
│   └── README.md                             ← dependency statement (none beyond the OS)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/inspect_my_computer_completed.sh

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/inspect_my_computer.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/inspect_my_computer_completed.sh` — runs the reference script: detects your OS (`uname -s`), then uses `sysctl`/`sw_vers` (macOS) or `lscpu`/`/proc/meminfo`/`/etc/os-release` (Linux) to print your CPU model, core count, RAM (converted from bytes to GiB by dividing by 1073741824), free disk on `/` (`df -h /`), and OS version.
- `bash starter/inspect_my_computer.sh` — the same skeleton with five values set to `unknown`; each exercise comment names the exact command to use. Edit the file in any text editor and replace each `unknown` assignment with the command in `$(...)` form.
- `bash tests/run_tests.sh` — runs both scripts and checks: exit code 0, header/footer lines, all five profile fields present; and (once your starter has no `unknown` left) that every field has a real value and the core count is a positive integer.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) — a real captured run:

```text
=== My Machine Profile ===
Generated on: 2026-07-12
Operating system kernel: Darwin
CPU model: Apple M4 Max
CPU cores: 14
RAM: 36 GiB (38654705664 bytes)
Free disk on /: 436Gi
OS version: macOS 26.5.1
=== End of profile ===
```

Your values will differ — that is the point. On Linux the kernel line reads `Linux` and the OS version comes from `/etc/os-release` (e.g. an Ubuntu or Fedora release name). [`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists exactly which fields must appear on every platform.

## Validation steps

1. Run `bash starter/inspect_my_computer.sh` — it must exit without errors.
2. Confirm **no line contains `unknown`**.
3. Confirm the RAM line shows both GiB and bytes, and the GiB number matches what your OS reports in its own settings UI (About This Mac / System Monitor).
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `18 checks, 0 failure(s).` (10 strict checks against the reference script, and 8 structural checks against your starter — which become 10 strict checks once you have replaced every `unknown`). The command exits 0 on success, non-zero on any failure, so it can run in CI.

## Cleanup

Nothing to clean up: the scripts only read system information and write nothing outside their own console output. To reset your work, restore the starter file from git: `git checkout -- starter/inspect_my_computer.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (command not found, permission messages, byte-conversion confusion, WSL notes).

## Security notes

See [security.md](security.md). Short version: the scripts run no network calls, need no elevated privileges, and expose only local hardware facts — but a machine profile *is* mildly identifying, so think before pasting it publicly.

## Extension exercises

1. Add your CPU cache sizes to the profile (macOS: `sysctl hw.l1dcachesize hw.l2cachesize`; Linux: `lscpu | grep -i cache`) and note how much smaller than RAM they are.
2. Compute how many float32 parameters (4 bytes each) fit in your RAM, and compare that with the parameter counts of AI models you have heard of.
3. Extend the script to print GPU information (macOS: `system_profiler SPDisplaysDataType`; Linux: `lspci | grep -i vga` or `nvidia-smi` if present) and update the tests to check for your new field.

## Navigation

- **Previous day:** none — this is Day 1.
- **Next day:** Day 2 — The CPU: Fetch, Decode, Execute (`labs/sections/computing-foundations/day-002-the-cpu-fetch-decode-execute/`, to be written).
