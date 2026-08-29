# Day 039 lab — Store Data Four Ways

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Data Storage: Files, Databases, Object Storage, and Caches
- **Day number:** 39 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-039-data-storage-files-databases-object-storage
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-039-data-storage-files-databases-object-storage` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 39's lesson maps the four main ways software stores data. This lab makes
them concrete: you store the **same small dataset four ways** — as a file, in
a SQLite database, in a simulated object-storage bucket, and behind a cache —
and feel exactly what each is good for. The centerpiece is watching a SQL
query answer a precise question that a plain file could only grep at.

## Learning objectives

- Write structured data to a file and read it back.
- Create a real SQLite database, insert rows, and run a `SELECT` with a
  `WHERE` clause and an aggregate.
- Store a blob under a content key (its hash) in a bucket directory and
  retrieve it by that key — the object-storage model.
- Implement a tiny key→value cache that shows a hit versus a recompute.
- Explain, for a given workload, which of the four stores fits and why.

## Prerequisites

- The Day 39 lesson (read it first — it explains every store this lab builds).
- Days 3 and 5 (the memory hierarchy; data as bytes).
- A terminal with `bash` and `sqlite3` (both preinstalled on macOS and most
  Linux). No programming experience required; every command is given.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, sqlite3 3.51.0).
- **Linux** — fully supported (any distribution with `bash`, `sqlite3`, and
  `shasum` or `sha256sum`).
- **Windows** — run the scripts unmodified inside WSL (Windows Subsystem for
  Linux); native PowerShell is not supported here.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab writes only a few
kilobytes to a temporary directory and needs no special hardware.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- `sqlite3` — the embedded database used in step 2. Preinstalled on macOS;
  on Debian/Ubuntu install with `apt install sqlite3`.
- `shasum` or `sha256sum` (one is always present on macOS/Linux) for the
  content-key step.

## Free and open-source options

Everything here is free. `sqlite3` is public-domain software, `bash` and the
hashing tools are open source or ship with your OS, and the object-storage and
cache steps are simulated with plain directories and files. No account, API
key, cloud service, or purchase is needed.

## Installation

None beyond `sqlite3`, which is almost always already present:

```bash
cd labs/sections/computing-foundations/day-039-data-storage-files-databases-object-storage
sqlite3 --version   # confirm sqlite3 is installed
```

If that prints a version, you are ready. If not, install it (see Required
software above).

## File structure

```text
day-039-data-storage-files-databases-object-storage/
├── README.md                     ← you are here
├── metadata.yml                  ← machine-readable lab metadata
├── starter/
│   ├── storage_demo.sh           ← YOUR working file (4 exercises)
│   └── storage-worksheet.md      ← record your query, key, and store choices
├── examples/
│   └── storage_demo.sh           ← completed reference implementation
├── tests/
│   └── run_tests.sh              ← automated checks (exits 0/non-zero)
├── expected-output/
│   ├── sample-macos.txt          ← real captured demo run (macOS)
│   ├── sample-tests.txt          ← real captured test run (macOS)
│   └── FIELDS.md                 ← required fields and platform notes
├── requirements/
│   └── README.md                 ← dependency statement
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/storage_demo.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/storage_demo.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/storage_demo.sh` — runs the reference demo end to end: writes
  a CSV **file**; creates a SQLite **database**, inserts rows, and runs a
  `SELECT ... WHERE state='OH' GROUP BY customer` aggregate; stores a blob in a
  bucket directory under its SHA-256 **content key** and reads it back; and
  runs a key→value **cache** that prints `MISS` then `HIT`. It works in a
  temporary directory and cleans up on exit.
- `bash starter/storage_demo.sh` — the same skeleton with four exercises left
  for you: create the table and insert rows, run the query, store and fetch a
  blob by key, and implement the cache's hit/miss logic. Each exercise comment
  names the exact command.
- `bash tests/run_tests.sh` — drives the reference demo into an inspectable
  temp directory and verifies real behavior: the database file exists, the
  query returns `ada|180.0` and `grace|90.0`, the blob is retrievable by a key
  equal to its content hash, and the cache prints `MISS` then `HIT`. Exits 0
  on success, non-zero on failure, so it runs in CI.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) — a
real captured run. The load-bearing lines:

```text
[2/4] DATABASE (SQLite)
  Query: total revenue per customer in state 'OH'
  ada|180.0
  grace|90.0

[4/4] CACHE (key -> value with timestamp)
  First call:  MISS -> computed and stored: 270.0 (at 23:22:13)
  Second call: HIT  -> served from cache (no recompute): 270.0
```

Your object key is identical for identical bytes; the cache timestamp and the
temp-dir path will differ. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists exactly which lines must appear and which values legitimately vary.

## Validation steps

1. Run `bash examples/storage_demo.sh` — it must exit without errors and print
   all four `[n/4]` sections.
2. Confirm the database section prints `ada|180.0` and `grace|90.0`.
3. Confirm the cache section prints `MISS` then `HIT`.
4. Complete the four exercises in `starter/storage_demo.sh` and run it — its
   output should match the example's.
5. Run the tests (next section) — all checks must pass and the exit code must
   be 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `7 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure. A real captured run is in
[`expected-output/sample-tests.txt`](expected-output/sample-tests.txt).

## Cleanup

Nothing to clean up manually: every script does its work inside a temporary
directory created with `mktemp` and removes it on exit (the test harness does
the same). To reset your starter file, restore it from git:
`git checkout -- starter/storage_demo.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (`sqlite3` not
found, empty query results, the cache always missing, `database is locked`).

## Security notes

See [security.md](security.md). Short version: the scripts make no network
calls, need no elevated privileges, and write only to a private temp
directory — but treat SQL built from untrusted input, and any real secrets,
with the care the file describes.

## Extension exercises

1. Turn the object step into real content-addressed storage: store the same
   bytes twice and confirm the second store reuses the same key (free
   deduplication); then store slightly different bytes and confirm a new key.
2. Add a second table and a `JOIN`: a `customers` table plus the `orders`
   table, then one query listing each customer's name and total.
3. Give the cache a time-to-live: stamp each cache file with a creation time
   and treat entries older than N seconds as a miss, so stale values expire.

## Navigation

- **Previous day:** Day 38 — Regular Expressions
  (`labs/sections/computing-foundations/day-038-regular-expressions/`, to be written).
- **Next day:** Day 40 — Observability: Logs, Metrics, Traces, and Dashboards
  (`labs/sections/computing-foundations/day-040-observability-logs-metrics-traces-and-dashboards/`, to be written).
