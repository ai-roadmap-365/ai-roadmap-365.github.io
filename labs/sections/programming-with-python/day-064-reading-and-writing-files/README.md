# Day 064 lab — Safe File I/O Toolkit

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Reading and Writing Files
- **Day number:** 64 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-064-reading-and-writing-files
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-064-reading-and-writing-files` when the site is running.
<!-- generated-links:end -->

## Purpose

Build a small toolkit of six functions that cover everything file handling
asks of you in practice, and prove each one by running it against real files.
You write text with an explicit encoding and read it back unchanged; you
measure — not guess — what a whole-file read costs against a streaming read
on a generated 8.2 MB log; you meet a genuine `UnicodeDecodeError` and
recover from it deliberately; you implement the atomic write and catch it
mid-operation to see that a reader always gets a complete file; and you walk
a directory tree with `pathlib`. These are the habits every later lab
depends on, because from here on your programs read and write data that
matters.

## Learning objectives

By the end of this lab you can:

- Round-trip text through an explicit `encoding="utf-8"` and explain why the
  byte count exceeds the character count.
- Measure peak memory with `tracemalloc` and show that streaming reads do not
  scale with file size while whole-file reads do.
- Trigger a `UnicodeDecodeError` on purpose and recover with
  `errors="replace"`, returning a flag so the recovery can be logged rather
  than hidden.
- Implement `atomic_write_text` with a same-directory temp file, `flush`,
  `os.fsync`, and `os.replace`, and demonstrate that the target file is
  never observed in a partial state.
- Contrast that with a naive `mode="w"` write caught holding a fragment.
- Walk a directory tree with `Path.rglob` and return sorted relative paths.

## Prerequisites

- Day 64's lesson, "Reading and Writing Files" (read it first — this lab is
  its exercise).
- Days 57-63: functions, modules and imports, the standard library, and
  designing a small program well.
- Comfort running `python3` from a terminal and editing a text file.

## Supported operating systems

macOS and Linux run every command as written. On Windows, use WSL — the
Python is portable, but the test runner is a bash script.

## Hardware requirements

Any machine that runs Python 3. The lab generates an 8.2 MB log file, so
allow about 10 MB of free disk space. Peak memory during the deliberately
wasteful whole-file read is roughly 25 MB.

## Required software

- `python3` 3.8 or newer (tested on 3.14.0)
- `bash` for the test runner

Nothing else. No pip install, no network access, no privileges. See
`requirements/README.md` for details.

## Free and open-source options

Everything here is free and open source. Python is released under the PSF
License; the only modules used — `os`, `pathlib`, `tracemalloc`, `sys` — are
part of the standard library. There is no paid tier for reading a file, and
no account to create.

## Installation

```bash
cd labs/sections/programming-with-python/day-064-reading-and-writing-files
python3 --version
```

If that prints `Python 3.8` or higher, you are ready. There is nothing to
install.

## File structure

```
day-064-reading-and-writing-files/
  README.md                     this file
  metadata.yml                  lab metadata and the recorded execution evidence
  examples/
    fileio_toolkit.py           the reference implementation of all six functions
    demo.py                     the five-part driver that proves each one
  starter/
    fileio_toolkit.py           your copy, with five numbered exercises to complete
    demo.py                     the same driver, importing your version
  tests/
    run_tests.sh                assert-based suite; 28 checks against real files
  expected-output/
    sample-run.txt              captured output of examples/demo.py
    test-run.txt                captured output of the test suite
  requirements/README.md        dependencies and platform notes
  troubleshooting.md            symptom-by-symptom fixes
  security.md                   path traversal, safe parsing, and why atomicity matters
```

## How to run

First drive the finished reference so you know the target:

```bash
python3 examples/demo.py
```

Inspect the evidence it left behind:

```bash
ls -1 workspace workspace/config workspace/tree
head -2 workspace/big.log
wc -l < workspace/big.log
rm -rf workspace
```

Now open `starter/fileio_toolkit.py`, complete its five numbered exercises,
and run the same driver against your version:

```bash
python3 starter/demo.py
```

Finally run the suite:

```bash
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/demo.py` — runs all five parts in a `workspace/`
  directory it creates beside the lab: the text round trip, the memory
  comparison (which generates the 200,000-line log), the decoding failure and
  recovery, the atomic write with a mid-operation inspection, and the
  `pathlib` tree walk.
- `head -2 workspace/big.log` / `wc -l < workspace/big.log` — confirm the
  generated log is real: two sample lines, and 200,000 of them.
- `rm -rf workspace` — removes everything the demo created. The lab writes
  nowhere else.
- `python3 starter/demo.py` — the identical driver, importing
  `starter/fileio_toolkit.py`, so your implementation is held to the same
  output as the reference.
- `bash tests/run_tests.sh` — 28 assertions against real files in a
  throwaway directory created with `mktemp -d` and removed on exit.

## Expected output

`python3 examples/demo.py` produces (captured on the authoring machine; byte
counts are deterministic, memory peaks vary by a few kilobytes between runs):

```text
Safe File I/O Toolkit — workspace: workspace

[1] text round-trip with an explicit encoding
    wrote notes.txt: 70 bytes on disk, 62 characters in memory
    lines read back: 3
    round-trip identical: True

[2] whole-file read vs line-by-line streaming
    generated big.log: 200000 lines, 8200020 bytes (7.82 MiB)
    read() + splitlines()  -> longest line 60 chars, peak memory 24.82 MiB
    for line in handle     -> longest line 60 chars, peak memory 0.14 MiB
    same answer: True
    streaming used 175x less memory

[3] decoding trouble and how to survive it
    strict utf-8 read raised UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 3: invalid continuation byte
    errors='replace' read: 'caf� was logged by a latin-1 program'
    recovered: True; U+FFFD present: True

[4] atomic write — proved by looking at the directory mid-operation
    before: ['config.txt'] content='version = 1'
    during: ['config.txt', 'config.txt.tmp'] content='version = 1'
    after : ['config.txt'] content='version = 2'

[5] walking a directory tree with pathlib
    a.txt
    sub/b.txt
    sub/deeper/c.txt
    3 file(s) found by Path.rglob
```

The full capture, including the explanatory notes the driver prints, is in
`expected-output/sample-run.txt`; the suite's output is in
`expected-output/test-run.txt`.

## Validation steps

You are done when every box is checked:

- [ ] `python3 examples/demo.py` runs all five parts and exits 0.
- [ ] Part 1 reports `round-trip identical: True`, with 70 bytes for 62
      characters.
- [ ] Part 2 reports the same longest-line length from both strategies, with
      the streaming peak far below the whole-file peak.
- [ ] Part 3 raises a real `UnicodeDecodeError` and then reports
      `recovered: True`.
- [ ] Part 4's `during:` line shows both `config.txt` and `config.txt.tmp`,
      with `config.txt` still holding `version = 1`.
- [ ] Part 5 lists exactly three relative paths.
- [ ] All five exercises in `starter/fileio_toolkit.py` are complete and
      `python3 starter/demo.py` matches the reference.
- [ ] `bash tests/run_tests.sh` prints `0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

The suite checks real behaviour, not file existence: that mode `w` replaces
while mode `a` appends, that `write()` adds no newline of its own, that both
reading strategies return the same answer while only one stays flat in
memory, that a strict read really raises and the fallback really recovers,
that during an atomic write the target still holds the *old* content while
the temp file sits in the *same directory*, that the naive writer is caught
holding a fragment, and that `list_tree` returns sorted relative paths for
files only. It exits 0 on success and non-zero on any failure.

Recorded evidence: on the authoring machine (macOS, Apple Silicon, Python
3.14.0) the suite reports `28 checks, 0 failure(s).` and exits 0.

## Cleanup

```bash
rm -rf workspace
git checkout -- starter/fileio_toolkit.py   # optional: reset your work
```

The test suite cleans up after itself automatically — its scratch directory
is created with `mktemp -d` and removed by an `EXIT` trap.

## Troubleshooting

See `troubleshooting.md` for symptom-by-symptom fixes, including
`FileNotFoundError` from relative paths, memory figures that differ from the
capture, `UnicodeDecodeError` on unexpected files, `Invalid cross-device
link` from `os.replace`, and stray `.tmp` files.

## Security notes

See `security.md`. The essentials: never build a path from untrusted input
by concatenation (path traversal), never `eval()` file contents, use mode
`x` when a file must not be overwritten, keep the atomic-write temp file in
the target's own directory, and remember that anything you write outlives
the program that wrote it.

## Extension exercises

1. **Add an index to the record store.** Record `handle.tell()` before each
   append into a companion file, then implement `get(path, key)` that
   `seek()`s straight to the offset and reads one line. Time it against a
   full scan on 100,000 records — you will have built, in miniature, the
   reason databases have indexes.
2. **Prove crash-safety under compaction.** Kill the process between writing
   the temp file and `os.replace`, then show every record is still present
   and the only trace is a stray `.tmp`. Add a startup step that cleans such
   strays safely.
3. **Rotate the store.** Past a size threshold, atomically rename it to
   `store.1` and start fresh, then make the reader read across rotated files
   oldest-first with `Path.glob`.
4. **Measure the cost of durability.** Time 10,000 appends with `fsync` on
   every record against `fsync` once at the end. The gap is why databases
   group commits, and why you reserve `fsync` for the moments that matter.

## Navigation

- Previous day: Day 063 — Designing a Small Program Well
- Next day: Day 065 — CSV and JSON in the Real World
