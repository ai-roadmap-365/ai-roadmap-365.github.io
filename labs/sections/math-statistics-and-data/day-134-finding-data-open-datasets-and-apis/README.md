# Day 134 lab — Judge the Source Before the Data

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Finding Data: Open Datasets and APIs
- **Day number:** 134 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-134-finding-data-open-datasets-and-apis
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-134-finding-data-open-datasets-and-apis` when the site is running.
<!-- generated-links:end -->

## Purpose

You build the judgement functions and the client behaviours that decide
whether a real source deserves your time, before you ever build a
DataFrame from it.

`datasource.py` implements a small HTTP client on the standard library's
`urllib.request` — pagination that follows the source's own `has_more`
flag, bounded backoff on a `429`, a conditional `ETag` fetch that costs
zero bytes on a re-run — plus five judgement functions that never touch
the network at all: a five-minute source assessment, a licence gate that
returns a reason rather than a boolean, a coverage check that catches a
missing region by comparing key sets, a checksum pin, and a provenance
record.

The centrepiece is Exercise 1. Two fixture columns are both called
`unemployment_rate`, both `float64`, with overlapping ranges — the check
most people actually run passes on both. Only reading the two sources'
data dictionaries, which say the columns count different things, catches
what the numbers cannot.

Nine numbered exercises, all running against a mock API on `127.0.0.1`
and an ephemeral port that implements real pagination, a real rate limit,
and a real `ETag` — never against the internet.

## Learning objectives

By the end of this lab you will be able to:

- Detect a join between two same-named columns that are defined
  differently, and explain why a dtype-and-range check cannot catch it.
- Fetch a paginated collection by following the source's own stopping
  signal, and prove the assembled row count against the advertised total.
- Handle a `429` with bounded exponential backoff, and give up loudly with
  a named attempt count rather than retrying a source forever.
- Make a conditional request with `ETag`/`If-None-Match` and measure, in
  bytes, what a cache hit actually saves.
- Pin a downloaded file to its SHA-256 and prove a single changed byte
  changes the digest.
- Run a five-minute source assessment that returns a structured verdict —
  granularity, coverage, licence, dictionary presence — for both a
  well-documented and a deficient source.
- Gate redistribution on a licence, returning a reason rather than a bare
  boolean, and distinguish "you may analyse this" from "you may
  republish this".
- Detect a documented coverage gap by comparing a dataset's actual keys
  against a data dictionary's expected list.
- Build a provenance record — URL, retrieval timestamp, checksum — that
  is stable when regenerated from the same fixture with the same pinned
  clock.

## Prerequisites

- Days 22-28 — REST fundamentals, JSON, authentication, rate limits and
  pagination as HTTP mechanics. This lab does not re-teach any of that;
  it assumes it and builds the judgement layer on top.
- Days 87-98 (or equivalent pandas comfort) — reading a `Series`'s dtype
  and range, which Exercise 1's naive check relies on.
- Comfort with `pytest`, and a working `python3` on your PATH.

## Supported operating systems

- **macOS** (Intel or Apple Silicon) — the machine this lab was written
  and run on: macOS 26.5.2, arm64.
- **Linux** — any distribution with Python 3.11 or newer. Every command
  below is identical.
- **Windows** — use WSL2 and follow the Linux path. Native PowerShell
  works too if you substitute `.venv\Scripts\python.exe` for
  `.venv/bin/python3`, but `tests/run_tests.sh` is a bash script and needs
  Git Bash or WSL.

## Hardware requirements

Nothing special. The mock dataset is 25 rows, the full harness runs in
well under a second, and nothing here needs a GPU, a display, or a
network connection after the one-time install.

## Required software

- Python 3.11 or newer (3.14.0 here).
- The pins in `requirements/requirements.txt`: pandas 3.0.5, pytest 9.1.1.
- `bash` for the test harness (3.2 or newer; macOS's system bash is fine).

Everything else this lab uses — `http.server`, `urllib.request`,
`hashlib`, `json`, `threading`, `dataclasses`, `datetime` — is standard
library. No third-party HTTP client is a dependency of this lab.

## Free and open-source options

Every tool in this lab is free. `urllib.request` ships with Python under
the PSF licence and needs no installation at all; pandas (BSD-3-Clause)
and pytest (MIT) are the only two pins. `requests` (Apache-2.0) is
described in the lesson as the ergonomic alternative to `urllib.request`
— it was not installed for this lab's own runs, and the lesson says so
plainly. All of the open-data portals, statistical agencies and research
repositories the lesson maps are free to query; several (Kaggle,
Hugging Face) also offer paid compute tiers for training, which is a
separate thing from the free data access this lesson covers.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-134-finding-data-open-datasets-and-apis
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import pandas, pytest; print(pandas.__version__, pytest.__version__)"
```

That last line should print `3.0.5 9.1.1`. The `pip install` is the only
step that touches the network; everything after runs offline against the
lab's own mock server.

## File structure

```
day-134-finding-data-open-datasets-and-apis/
├── README.md                 this file
├── metadata.yml               lab metadata and the literal result of the real run
├── security.md                what this lab does to your machine
├── troubleshooting.md         the failures you are most likely to hit
├── requirements/
│   ├── README.md               why pandas and pytest are the only pins
│   └── requirements.txt        pandas, pytest
├── starter/                    your work
│   ├── 00_brief.md             the nine exercises, explained
│   ├── conftest.py             mock_api and stubborn_mock_api fixtures
│   ├── mock_server.py          pagination, rate limiting, ETag — on 127.0.0.1
│   ├── datasource.py           the client and judgement functions
│   ├── fixtures.py             the two unemployment_rate dictionaries and series
│   └── test_datasource.py      nine exercises, each currently a pytest.skip
├── examples/                    the reference answers — read after you try
│   ├── conftest.py              identical to starter/conftest.py
│   ├── mock_server.py           identical to starter/mock_server.py
│   ├── datasource.py            identical to starter/datasource.py
│   ├── fixtures.py              identical to starter/fixtures.py
│   └── test_datasource.py       the nine exercises, solved
├── tests/
│   └── run_tests.sh             the bash harness: 38 checks
└── expected-output/
    ├── FIELDS.md                what is exact, what may differ, and why
    ├── examples-run.txt         pytest examples -q
    ├── starter-run.txt          pytest starter -q
    └── test-run.txt             bash tests/run_tests.sh
```

## How to run

Read `starter/00_brief.md` first, then `starter/datasource.py`. Then:

```bash
# your work, from the lab directory
.venv/bin/pytest starter -v

# the reference answers, once you have tried
.venv/bin/pytest examples -q

# everything, including the proof that the suite can fail
bash tests/run_tests.sh
```

**Run `pytest starter` and `pytest examples` as two separate commands.**
Both directories contain a module named `test_datasource.py`, and pytest
collects test modules by dotted name; a single `pytest examples starter`
aborts collection with an `import file mismatch`. Section 5 of the
harness runs that combined form on purpose and asserts it fails, so this
is checked, not merely stated.

## What the commands do

| Command | What happens |
| --- | --- |
| `.venv/bin/pytest starter -v` | Runs your nine exercises. On an untouched checkout all nine skip, and each skip message tells you exactly what to assert |
| `.venv/bin/pytest examples -q` | Runs the reference answers. Should print `9 passed` |
| `bash tests/run_tests.sh` | The full harness: version pins, every claim driven directly from Python against a real mock server, both suites, the collision check, the fail-then-restore proof, and the cleanliness checks |

Section 2 of the harness is the interesting one. It starts real mock
servers, makes real HTTP requests against them, and prints the attempt
counts and byte counts it measured — never a value nobody computed.

## Expected output

The final section of a green run:

```
7. Offline, and nothing left behind
  ok: no literal 'localhost:port' string anywhere -- 127.0.0.1 only
  ok: no __pycache__ or .pytest_cache left behind
  ok: no d134 temporary directory left in the system temp directory

-------------------------------------------------------------
38 checks, 0 failure(s)
```

The full capture is in `expected-output/test-run.txt`.
`expected-output/FIELDS.md` records which captured numbers are exact
everywhere (every checksum, every row and attempt count) and which are
environment-dependent (package versions, wall-clock timings, the specific
ephemeral port).

## Validation steps

1. `bash tests/run_tests.sh` prints `38 checks, 0 failure(s)` and exits 0
   (`echo $?` immediately after, with no pipe in between — a pipeline
   reports the *last* command's status and will hide a real failure).
2. `.venv/bin/pytest examples -q` prints `9 passed`.
3. `.venv/bin/pytest starter -q` prints `9 skipped` before you start, and
   `9 passed` when you are done.
4. Confirm no process is left listening: `lsof -i -P | grep python` should
   show nothing from this lab once the harness finishes.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints `N checks,
M failure(s)`, exits 0 only when `M` is zero, and covers:

1. the installed versions against `requirements/requirements.txt`;
2. every exercise's real behaviour, driven directly against a real mock
   server: the definition trap, pagination to exhaustion, bounded backoff
   against both a relenting and a stubborn source, the conditional
   request's byte counts, checksum pinning, the five-minute assessment,
   the licence gate, the coverage check, and the provenance record;
3. `examples/` passing in full;
4. `starter/` skipping in full on an untouched checkout;
5. the `pytest examples starter` collision, run and asserted;
6. **the proof that the suite can fail** — the harness copies the solved
   suite into a scratch directory, confirms 9 passed, breaks Exercise 8's
   exact missing-region assertion on purpose, confirms a non-zero exit and
   a printed failure, restores the file, and confirms 9 passed again;
7. no literal `localhost:port` anywhere, and no `__pycache__`,
   `.pytest_cache` or stray temporary directory left behind.

## Cleanup

The harness cleans up after itself, before and after every run. To reset
completely:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: throws away your work and restores the skips
```

Every mock server this lab starts is shut down inside the fixture that
started it, including on a failing test, so no port stays bound and no
process is left running.

## Troubleshooting

`troubleshooting.md` covers the failures in detail. The three most common:

- **`pytest: command not found`** — you have not created the `.venv`, or
  you are calling bare `pytest` instead of `.venv/bin/pytest`. The harness
  also accepts `PYTEST=/path/to/pytest bash tests/run_tests.sh`.
- **`import file mismatch`** — you ran `pytest examples starter` in one
  command. Run them as two.
- **`RateLimitExceeded` was not raised when expected** — check which
  server fixture you used. `mock_api` relents after 2 rejections;
  `stubborn_mock_api` relents after 10, which is what makes a small
  `max_attempts` budget genuinely exhaust against it.

## Security notes

`security.md` has the full account. In short: one network connection ever
(the `pip install`), every mock server bound to `127.0.0.1` on an
ephemeral port and shut down in a `finally` block, no `sudo`, no
credential, no API key, nothing written outside this lab's own directory
and the temporary directories pytest deletes itself.

## Extension exercises

1. **Point `assess_source` at a real dataset's documentation page.** Fill
   in a metadata dict from what you can actually find on the page, and see
   how many of the six fields are genuinely stated versus assumed.
2. **Add a second rate-limit header.** Real APIs often send
   `X-RateLimit-Remaining` alongside `Retry-After` — extend
   `fetch_with_backoff` to stop proactively when remaining hits zero,
   rather than waiting for the first 429.
3. **Persist the ETag cache.** `fetch_with_etag`'s cache is a plain dict
   that dies with the process. Write a version that reads and writes a
   small JSON file, so a re-run tomorrow still costs nothing.
4. **Widen the licence table.** Add `CC-BY-SA` and `CC-BY-NC` to
   `check_licence`, with reasons that state their extra conditions
   (share-alike, non-commercial) rather than just marking them allowed.
5. **Make the coverage check granular.** Extend `check_coverage` to
   report which dictionary-listed *fields*, not just which values, a
   dataset's actual columns are missing.
6. **Break the naive check on purpose, worse.** Construct a third
   `unemployment_rate` fixture whose values are shifted by exactly the
   amount that would make `naive_join_check` pass even more convincingly
   — then write the dictionary entry that would still catch it.

## Navigation

- **Previous day:** Day 133 — Building an EDA Report
  (`labs/sections/math-statistics-and-data/day-133-building-an-eda-report/`).
- **Next day:** Day 135 — From API to DataFrame
  (`labs/sections/math-statistics-and-data/`), which picks up exactly
  where `fetch_all_pages` leaves off: turning assembled JSON rows into a
  tidy DataFrame.
- **Week 20 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/`), a full exploratory study
  built on a source you chose and judged using this lab's checklist.
