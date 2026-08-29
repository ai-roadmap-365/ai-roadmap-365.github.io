# Day 005 lab — X-Ray Your Files: Seeing Bytes with hexdump

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Text, Images, and Sound as Data
- **Day number:** 5 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-005-text-images-and-sound-as-data
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-005-text-images-and-sound-as-data` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 5's lesson claims that text, images, and sound are nothing but bytes
under agreed conventions. This lab lets you verify that claim with your
own eyes: you point `xxd` and `file` at three small committed sample
files — pure ASCII text, UTF-8 text with accents and an emoji, and a
real 145-byte PNG image — and read the actual bytes: ASCII codes,
multi-byte UTF-8 sequences, and the PNG magic bytes `89 50 4E 47`.

## Learning objectives

- Read a hex dump: offsets on the left, bytes in the middle, the ASCII
  interpretation on the right.
- Locate 1-, 2-, 3-, and 4-byte UTF-8 sequences in a real file and explain
  why byte count and character count differ.
- Identify a file format from its magic bytes and verify it with `file`.
- Demonstrate that a file's extension is a naming convention while its
  content determines its true type.
- Complete a small shell script by filling in four well-specified
  exercises, and answer a worksheet from observed bytes only.

## Prerequisites

- The Day 5 lesson (read it first — it explains every byte you will see).
- Comfort running commands in a terminal (Day 1 lab).
- No programming experience required; every command is given and explained.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution with `xxd` and `file`;
  install `xxd` from your package manager if a minimal image lacks it).
- **Windows** — run the scripts unmodified inside WSL; PowerShell users
  can explore manually with `Format-Hex`, but the tests assume a
  Unix-style shell.

## Hardware requirements

Any computer. The samples total 191 bytes; the lab only reads them and
writes to a throwaway temp directory.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- `xxd` (preinstalled on macOS; ships with vim on Linux) and `file`
  (preinstalled everywhere). `hexdump -C` works as a stand-in for `xxd`.

## Free and open-source options

Everything in this lab is free: bash, `xxd`, `hexdump`, and `file` are
open-source or ship with your OS. No account, API key, or download is
needed — the sample files are committed to the repository, and
`examples/make_samples.sh` can rebuild them offline at any time.

## Installation

None. From the repository root:

```bash
cd labs/sections/computing-foundations/day-005-text-images-and-sound-as-data
```

## File structure

```text
day-005-text-images-and-sound-as-data/
├── README.md                        ← you are here
├── metadata.yml                     ← machine-readable lab metadata
├── starter/
│   ├── inspect_bytes.sh             ← YOUR working file (4 exercises)
│   └── byte-detective-worksheet.md  ← 10 questions answered from real bytes
├── examples/
│   ├── inspect_bytes.sh             ← completed reference walkthrough
│   ├── make_samples.sh              ← rebuilds the samples byte by byte
│   └── samples/
│       ├── hello.txt                ← 14 bytes of pure ASCII
│       ├── unicode.txt              ← UTF-8: é (2 bytes), € (3), emoji (4)
│       └── tiny.png                 ← real 145-byte PNG, 2×2 pixels
├── tests/
│   └── run_tests.sh                 ← automated checks
├── expected-output/
│   ├── inspect-bytes-macos.txt      ← real captured walkthrough run
│   ├── test-run-macos.txt           ← real captured test run
│   └── NOTES.md                     ← what must match vs. may differ
├── requirements/
│   └── README.md                    ← dependency statement
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. Watch the finished walkthrough first
bash examples/inspect_bytes.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/inspect_bytes.sh

# 3. Fill in starter/byte-detective-worksheet.md from what you observed

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/inspect_bytes.sh` — for each sample file, runs `file`
  (identify by content), `wc -c`/`wc -m` (bytes vs. characters), and
  `xxd` (hex dump), with printed notes pointing at the interesting bytes:
  ASCII codes in `hello.txt`, the sequences `c3 a9`, `e2 82 ac`, and
  `f0 9f 8e 89` in `unicode.txt`, and the PNG signature plus readable
  chunk names in `tiny.png`. Section 4 copies the samples under swapped
  extensions into a temp directory and shows `file` judging content, not
  names.
- `bash starter/inspect_bytes.sh` — the same investigation as a skeleton:
  four placeholder lines, each preceded by a comment naming the exact
  command to put there (`xxd`, `xxd -l 8`, and a `cp … && file …` line).
- `bash examples/make_samples.sh` — optional; rebuilds the three samples
  deterministically (`printf` byte escapes for the text files, base64
  decoding for the PNG) and prints `file`'s verdict on each.
- `bash tests/run_tests.sh` — checks that the samples exist and are
  identified correctly by `file`, that `xxd` shows the exact expected
  byte sequences (PNG signature `89504e470d0a1a0a`, the UTF-8 sequences,
  the exact 14 bytes of `hello.txt`), that content beats extension, and
  that both scripts run cleanly.

## Expected output

See [`expected-output/inspect-bytes-macos.txt`](expected-output/inspect-bytes-macos.txt)
for the full real captured run. The heart of it:

```text
00000000: 4865 6c6c 6f2c 2077 6f72 6c64 210a       Hello, world!.

00000000: 6361 66c3 a920 636f 7374 7320 3320 e282  caf.. costs 3 ..
00000010: ac0a 72c3 a973 756d c3a9 0af0 9f8e 890a  ..r..sum........

00000000: 8950 4e47 0d0a 1a0a                      .PNG....
```

Your output must show the same bytes — bytes do not vary by machine.
Only `file`'s phrasing and locale-dependent character counts may differ
slightly (see [`expected-output/NOTES.md`](expected-output/NOTES.md)).

## Validation steps

1. Run `bash starter/inspect_bytes.sh` — it must exit without errors and
   no longer print any `not completed yet` line.
2. In your own output, point at: the byte `48` (H), the pair `c3 a9` (é),
   and the four bytes `89 50 4e 47` (PNG signature).
3. Confirm the worksheet has all 10 answers filled in, each backed by a
   command you actually ran.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `18 checks, 0 failure(s).` while the starter still
has placeholders (structure-only check), rising to `20 checks, 0
failure(s).` once you have completed all four exercises. The command
exits 0 on success and non-zero on any failure, so it can run in CI.

## Cleanup

Nothing to clean up: the scripts write only inside `mktemp -d` scratch
directories, which they remove themselves. To reset your work:
`git checkout -- starter/inspect_bytes.sh starter/byte-detective-worksheet.md`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (missing
`xxd`, locale-dependent `wc -m`, emoji rendering, `file` wording
differences, corrupted PNG after line-ending translation, BOM bytes).

## Security notes

See [security.md](security.md). Short version: read-only inspection, no
network, no privileges — and the rename experiment is itself a security
lesson: extensions are claims, magic bytes are evidence.

## Extension exercises

1. Hex-dump other real files on your machine with `xxd file | head` — a
   JPEG photo (starts `ff d8 ff`), a PDF (`25 50 44 46`, which spells
   `%PDF`), a ZIP archive (`50 4b`, "PK"). Keep a small table of the
   magic bytes you find.
2. Use `xxd -b examples/samples/hello.txt | head -3` to see the same
   bytes as raw binary, and check that `H` is `01001000` (72).
3. Save the same short sentence from your editor as UTF-8 and as UTF-16,
   dump both, and explain the size difference and the `ff fe`
   byte-order mark you will find.
4. Run `strings examples/samples/tiny.png` and compare with the full hex
   dump: which parts of a binary file does `strings` surface, and why is
   it a favorite first tool for inspecting unknown binaries?

## Navigation

- **Previous day:** Day 4 — Binary and Data Representation: Bits, Bytes, and Numbers (`../day-004-binary-and-data-representation-bits-bytes/`)
- **Next day:** Day 6 — Operating Systems: What They Do and Why (`../day-006-operating-systems-what-they-do-and/`)
