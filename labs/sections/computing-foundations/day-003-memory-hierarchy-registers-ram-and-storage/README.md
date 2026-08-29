# Day 003 lab — Feel the Hierarchy: Measuring Your Machine's Memory Levels

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Memory Hierarchy: Registers, RAM, and Storage
- **Day number:** 3 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-003-memory-hierarchy-registers-ram-and-storage
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-003-memory-hierarchy-registers-ram-and-storage` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 3's lesson explained the memory hierarchy — registers, caches, RAM,
storage — and the speed/size/cost trade-off that creates it. This lab makes
two of those levels measurable on your own machine: it reads your CPU's L1
and L2 cache sizes and your RAM, then times a cold versus warm read of a
large file so you can *watch* the operating system's page cache at work.

## Learning objectives

- Read your machine's L1 data cache, L2 cache, and RAM sizes from the OS.
- Explain, in bytes and in KiB/MiB/GiB, how far apart those levels are.
- Measure a cold read versus a warm (cached) read and interpret the result.
- Connect the page-cache effect you observe to why "loading" something the
  second time is faster.

## Prerequisites

- The Day 3 lesson (it explains every level this lab measures).
- The Day 1 lab's machine profile (you extend it here).
- A terminal. No programming experience required.

## Supported operating systems

- **macOS** — fully supported (Apple Silicon and Intel).
- **Linux** — fully supported where the kernel exposes cache descriptors
  (most bare-metal and full VMs; minimal containers may not — handled
  gracefully).
- **Windows** — run under WSL, or read cache sizes with PowerShell (see
  `troubleshooting.md`) and fill the worksheet by hand.

## Hardware requirements

Any computer with at least ~500 MB of free disk (for the temporary test
file, which is deleted afterwards). No GPU or minimum RAM needed.

## Required software

`bash` plus standard OS utilities (`sysctl`/`sw_vers` on macOS; `/proc` and
`/sys` on Linux; `dd`, `date`, `df`). All preinstalled — see
`requirements/README.md`.

## Free and open-source options

Everything here is free and ships with your OS. No accounts, keys, or
purchases.

## Installation

None. Change into this directory:

```bash
cd labs/sections/computing-foundations/day-003-memory-hierarchy-registers-ram-and-storage
```

## File structure

```text
day-003-.../
├── README.md
├── metadata.yml
├── starter/
│   ├── measure_read_speed.sh     ← YOUR working file (numbered exercises)
│   └── hierarchy-worksheet.md    ← record your machine's real numbers
├── examples/
│   └── measure_read_speed.sh     ← completed reference implementation
├── tests/
│   └── run_tests.sh
├── expected-output/
│   ├── sample-macos.txt          ← real captured run
│   ├── sample-test-run.txt       ← real captured test run
│   └── FIELDS.md                 ← required fields on every platform
├── requirements/README.md
├── troubleshooting.md
└── security.md
```

## How to run

```bash
# 1. See the finished result first
bash examples/measure_read_speed.sh

# 2. Complete the exercises in the starter, then run it
bash starter/measure_read_speed.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/measure_read_speed.sh` — reads your L1/L2 cache and RAM
  sizes (via `sysctl` on macOS or `/sys` and `/proc/meminfo` on Linux),
  then creates a ~200 MB file inside the lab directory with `dd`, times a
  first (cold) read and a second (warm) read of it, prints both speeds and
  their ratio, and deletes the file on exit.
- `bash starter/measure_read_speed.sh` — the same skeleton with numbered
  exercises for you to complete; each names the exact command to use.
- `bash tests/run_tests.sh` — runs the reference (and your starter) and
  checks the report has every required field and exits cleanly.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt)
for a real captured run and [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
for the exact fields required on every platform. Your cache sizes, RAM, and
timings will differ — that is the point.

## Validation steps

1. `bash starter/measure_read_speed.sh` exits with no error.
2. No field reads `unknown` or is left blank (except a level your OS genuinely
   does not expose, which prints `not exposed by this environment`).
3. The RAM figure matches your Day 1 profile.
4. The tests pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `19 checks, 0 failure(s).` (exit 0 on success, non-zero
on any failure — CI-ready).

## Cleanup

The scripts delete their temporary file automatically. To reset your edited
starter: `git checkout -- starter/measure_read_speed.sh`. If a hard kill left
`read-speed-testfile.bin` behind, delete it manually.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) — cache names per platform,
empty cache values on minimal Linux, warm-vs-cold ratios, disk space, WSL.

## Security notes

See [security.md](security.md). The scripts read hardware facts and write
one temporary file inside the lab directory (auto-deleted); no network, no
sudo.

## Extension exercises

1. Raise `size_mb` toward (but below) your free RAM and observe how the
   cold/warm gap changes.
2. Add L3 cache to the report (macOS: `sysctl -a | grep -i l3`; Linux: the
   `index3` cache descriptor) and note how much larger it is than L2.
3. Estimate how many float32 model weights (4 bytes each) fit in your L2
   cache versus your RAM, and relate that to why AI models stream weights
   from RAM rather than holding them all in cache.

## Navigation

- **Previous day:** Day 2 — The CPU: Fetch, Decode, Execute.
- **Next day:** Day 4 — Binary and Data Representation: Bits, Bytes, and Numbers.
