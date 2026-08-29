# Day 006 lab — Meet Your Operating System

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Operating Systems: What They Do and Why
- **Day number:** 6 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-006-operating-systems-what-they-do-and
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-006-operating-systems-what-they-do-and` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 6's lesson explained what an operating system does — managing processes,
memory, files, devices, and permissions behind a system-call boundary. This
lab makes that concrete: you interrogate your own OS from the terminal —
kernel, uptime, identity, shell, filesystems, and the processes it is
juggling right now — and add an OS layer to the machine profile you started
on Day 1.

## Learning objectives

- Read your kernel name and version and explain what the kernel is.
- Identify your login shell and your user identity.
- List your mounted filesystems and your top memory-consuming processes.
- Explain how the OS sits between your programs and the hardware.

## Prerequisites

- The Day 6 lesson.
- The Day 1 machine profile (you extend it with OS-layer facts).
- A terminal; no programming experience required.

## Supported operating systems

- **macOS** — fully supported (Darwin).
- **Linux** — fully supported, including WSL.
- **Windows** — run inside WSL (the script works unchanged), or read the
  equivalent facts with PowerShell `Get-ComputerInfo` and fill the worksheet
  by hand.

## Hardware requirements

Any computer. The lab only reads system information; it writes nothing and
needs no special hardware.

## Required software

`bash` plus standard OS utilities (`uname`, `uptime`, `whoami`, `ps`, `df`).
All preinstalled — see `requirements/README.md`.

## Free and open-source options

Everything here is free and ships with your OS. No accounts, keys, or
purchases.

## Installation

None. Change into this directory:

```bash
cd labs/sections/computing-foundations/day-006-operating-systems-what-they-do-and
```

## File structure

```text
day-006-.../
├── README.md
├── metadata.yml
├── starter/
│   ├── explore_os.sh             ← YOUR working file (numbered exercises)
│   └── os-profile-worksheet.md   ← record your machine's OS-layer facts
├── examples/
│   └── explore_os.sh             ← completed reference implementation
├── tests/
│   └── run_tests.sh
├── expected-output/
│   ├── sample-macos.txt          ← real captured run
│   └── FIELDS.md                 ← required fields on every platform
├── requirements/README.md
├── troubleshooting.md
└── security.md
```

## How to run

```bash
# 1. See the finished tour first
bash examples/explore_os.sh

# 2. Complete the exercises in the starter, then run it
bash starter/explore_os.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/explore_os.sh` — prints your kernel line (`uname -a`),
  uptime, user identity, login shell, a filesystem summary (`df -h`), your
  top five memory-consuming processes (`ps`), and where the kernel lives on
  disk — labelled per OS.
- `bash starter/explore_os.sh` — the same tour with numbered exercises for
  you to complete; each names the exact command.
- `bash tests/run_tests.sh` — runs the reference (and your starter) and
  checks every required section prints and the script exits cleanly.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt)
for a real captured run and [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
for the fields required on every platform. Your kernel version, shell, and
process list will differ.

## Validation steps

1. `bash starter/explore_os.sh` exits with no error.
2. Every section header prints (Kernel, Uptime, Identity, Shell,
   Filesystems, Top processes).
3. Your kernel name matches your OS (Darwin on macOS, Linux on Linux/WSL).
4. The tests pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `29 checks, 0 failure(s).` (exit 0 on success,
non-zero on any failure).

## Cleanup

Nothing to clean up — the scripts only read system information. Reset your
edited starter with `git checkout -- starter/explore_os.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) — `ps` column differences,
WSL notes, and reading the kernel path per platform.

## Security notes

See [security.md](security.md). The scripts are read-only, need no sudo,
and make no network calls; note that `ps` can show other users' process
names, so avoid sharing full output from shared machines.

## Extension exercises

1. Add the number of running processes (`ps -ax | wc -l`) to your worksheet
   and compare it with your CPU core count from Day 1.
2. Look up one unfamiliar process from the top-memory list and record what
   it is.
3. On Linux, print your distribution's `PRETTY_NAME` from
   `/etc/os-release`; on macOS, print the Darwin version and map it to the
   marketing macOS version.

## Navigation

- **Previous day:** Day 5 — Text, Images, and Sound as Data.
- **Next day:** Day 7 — Processes, Threads, and Scheduling.
