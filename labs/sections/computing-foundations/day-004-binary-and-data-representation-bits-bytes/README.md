# Day 004 lab — Binary by Hand and by Shell

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Binary and Data Representation: Bits, Bytes, and Numbers
- **Day number:** 4 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-004-binary-and-data-representation-bits-bytes
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-004-binary-and-data-representation-bits-bytes` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 4's lesson teaches binary, hexadecimal, two's complement, and the byte arithmetic behind model sizes. This lab makes it muscle memory in two passes: first **by hand** — twelve conversion drills on paper, carries and all — and then **by shell**, where you build a base-conversion toolkit from the two number tools every macOS and Linux machine already ships: `printf` and `bc`.

## Learning objectives

- Convert between decimal, binary, and hexadecimal by hand, quickly and correctly.
- Add 8-bit binary numbers with carries and negate a number in two's complement.
- Drive `printf` (decimal ↔ hex, character → code) and `bc` (`ibase`/`obase`) as base converters.
- Complete a working shell toolkit by filling in four well-specified exercises.
- Verify your own hand arithmetic mechanically, and run an automated test suite.

## Prerequisites

- The Day 4 lesson (read it first — every drill uses a method worked there).
- The Day 1 lab (comfort running commands in a terminal).
- Paper and a pencil for the drill sheet. This is deliberate: the hand pass comes first.

## Supported operating systems

- **macOS** — fully supported; `printf` and `bc` are preinstalled (tested on Apple Silicon).
- **Linux** — fully supported; most desktop distributions preinstall `bc` (minimal/container images may not — see [requirements/README.md](requirements/README.md)).
- **Windows** — run everything unmodified inside WSL; native PowerShell lacks `bc` and printf's character trick.

## Hardware requirements

Any computer that can open a terminal. The lab computes with numbers no larger than a few hundred; there are no meaningful CPU, RAM, or disk demands.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- `printf` (a shell builtin) and `bc` (the POSIX arbitrary-precision calculator).

## Free and open-source options

Everything in this lab is free: bash, `printf`, and `bc` are open-source and ship with (or install from the standard package manager of) every supported OS. No account, API key, or purchase is needed.

## Installation

Usually none. If `bc` is missing (some minimal Linux images), install it with your package manager — one line, covered in [requirements/README.md](requirements/README.md). Then change into this directory:

```bash
cd labs/sections/computing-foundations/day-004-binary-and-data-representation-bits-bytes
```

## File structure

```text
day-004-binary-and-data-representation-bits-bytes/
├── README.md                     ← you are here
├── metadata.yml                  ← machine-readable lab metadata
├── starter/
│   ├── conversion-drills.md      ← 12 hand drills with working space (do these first)
│   └── binary_toolkit.sh         ← YOUR working file (4 exercises in a running skeleton)
├── examples/
│   └── binary_toolkit.sh         ← completed reference toolkit
├── tests/
│   └── run_tests.sh              ← automated checks
├── expected-output/
│   ├── toolkit-demo.txt          ← real captured demo run of the reference toolkit
│   └── tests-run.txt             ← real captured test run (14 checks)
├── requirements/
│   └── README.md                 ← dependency statement (bash + bc)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. Do the twelve drills on paper
open starter/conversion-drills.md   # or any text editor / pager

# 2. See the finished toolkit work, and use it to check your drill answers
bash examples/binary_toolkit.sh
bash examples/binary_toolkit.sh d2b 42

# 3. Your task: complete the four exercises in the starter, then run it
bash starter/binary_toolkit.sh

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/binary_toolkit.sh` — runs the demo: every converter once, with labeled output. With arguments it converts one value: `d2b`/`b2d` go decimal↔binary via `bc` (`obase=2`/`ibase=2`), `d2h`/`h2d` go decimal↔hex via `printf '%X'`/`printf '%d' 0x…`, `h2b` goes hex→binary via `bc` with both bases set (obase first), and `byte` prints a character's ASCII code, hex form, and 8-bit pattern using printf's `"'A"` trick.
- `bash starter/binary_toolkit.sh` — the same skeleton with the four conversion functions returning `unknown`; each exercise comment names the exact incantation. Edit the file and replace each `echo "unknown"` line.
- `bash tests/run_tests.sh` — verifies the reference toolkit against known values (42→101010, 255→11111111, 0xFF→255, 'A'→65/01000001, a round trip), and tests your starter: structure only while any `unknown` remains, full strictness once you have completed all four exercises.

## Expected output

See [`expected-output/toolkit-demo.txt`](expected-output/toolkit-demo.txt) — a real captured run:

```text
=== Binary toolkit demo ===
dec2bin 42        -> 101010
bin2dec 101010    -> 42
dec2hex 255       -> FF
hex2dec 0xFF      -> 255
hex2bin 2F        -> 00101111
byte inspector    -> character 'A'  ->  decimal 65  =  hex 0x41  =  bits 01000001
=== End of demo ===
```

Your completed starter must produce exactly the same demo. The captured test run is in [`expected-output/tests-run.txt`](expected-output/tests-run.txt).

## Validation steps

1. All twelve drills on the sheet have an answer **and** shown working — no answer without steps.
2. Each drill answer matches the toolkit's output for the listed check command.
3. `bash starter/binary_toolkit.sh` prints the demo with **no `unknown` anywhere**.
4. `bash tests/run_tests.sh` passes (next section) — with the starter finished, it runs the full 20 strict checks.

## Tests

```bash
bash tests/run_tests.sh
```

As shipped (starter untouched) the suite runs 10 strict checks against the reference and 4 structural checks against the starter, ending `14 checks, 0 failure(s).` Once your starter has no `unknown` left, it is held to the same standard as the reference, ending `20 checks, 0 failure(s).` The command exits 0 on success and non-zero on any failure, so it can run in CI.

## Cleanup

Nothing to clean up: the scripts read no files and write nothing outside their console output. To reset your work, restore the starter from version control: `git checkout -- starter/binary_toolkit.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (`bc` missing, hex case sensitivity, `ibase`/`obase` ordering, leading zeros, PowerShell notes).

## Security notes

See [security.md](security.md). Short version: pure local arithmetic — no network, no privileges, no files written, nothing sensitive read.

## Extension exercises

1. Add a `b2h` (binary → hexadecimal) command to your toolkit — `bc` can do it directly, or you can chain your existing `b2d` and `d2h`. Extend the tests to cover it.
2. Add a `neg` command that prints the 8-bit two's complement of a small positive number. `bc` has no bit-flip, but the lesson gives you the arithmetic shortcut: the pattern for −n reads, as an unsigned byte, 256 − n.
3. Add a `word` command that walks a whole word (e.g. `word Hi`) and prints one byte-inspector line per character; compare the bit patterns of `A` and `a` and explain the single differing bit.

## Navigation

- **Previous day:** Day 3 — Memory and Storage (`../day-003-memory-and-storage-ram-disks-and`, if present in your checkout).
- **Next day:** Day 5 — Text, Images, and Sound as Data (`../day-005-text-images-and-sound-as-data`, where these bytes become media).
- **Week overview:** [`../README.md`](../README.md)
