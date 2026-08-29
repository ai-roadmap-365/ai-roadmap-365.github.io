# Day 135 lab -- One Row Means One Thing

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** From API to DataFrame
- **Day number:** 135 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-135-from-api-to-dataframe
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-135-from-api-to-dataframe` when the site is running.
<!-- generated-links:end -->

## Purpose

JSON is a tree and a DataFrame is a rectangle, so every ingestion is a
lossy flattening -- and the loss is silent. This lab builds a small,
complete ingestion pipeline against a mock customer-and-orders API
(`examples/api_server.py`, standard library only, bound to `127.0.0.1` on
an ephemeral port) that makes that loss visible and then closes it, in nine
numbered steps: the grain trap, `json_normalize`'s `meta` duplication,
`DataFrame.explode`, untyped arrival, schema drift across pages, raw-before-
transform, idempotent upsert, a contract on the assembled frame, and an
incremental fetch by watermark.

Every number this lab asserts is real: the two row counts and the exact
dollar figure a wrong flattening inflates a customer's balance by, the
count of string values `pin_dtypes` actually coerced, the page a drifting
field first appears on, the number of HTTP requests a raw-then-replay
round trip costs versus a plain re-fetch.

## Learning objectives

- Flatten a nested JSON payload two different ways with
  `pandas.json_normalize` -- customer grain and order grain -- and state,
  in one sentence, which question each grain answers correctly.
- Use `record_path` and `meta` together, and explain exactly which columns
  `meta` duplicates and by how much.
- Use `DataFrame.explode` on a nested list column, and state precisely how
  it treats an empty list differently from `json_normalize`'s `record_path`.
- Pin dtypes on a frame that arrived from JSON, where numbers are strings,
  dates are strings, and a field absent from some records becomes an
  all-NaN column rather than an error.
- Detect schema drift across paginated API responses: a field introduced
  partway through a run, named along with the page it first appeared on.
- Persist raw API responses before transforming them, and prove a replay
  from that raw copy touches the network zero times.
- Build an idempotent ingestion step with a natural key and an upsert, and
  prove that running it twice leaves the frame unchanged.
- Write a contract on an assembled frame -- columns, dtypes, key
  uniqueness, row-count bounds -- that raises and names the exact rule a
  corrupted payload breaks.
- Fetch incrementally by a watermark, and explain which side of the
  boundary off-by-one to choose and why.

## Prerequisites

- Day 134 -- finding data, open datasets and APIs, pagination, rate limits
  and licences. This lab assumes a page and a cursor already exist; it does
  not re-derive where they came from.
- Day 121 -- loading and inspecting data, and its dtype-pinning discipline,
  applied here to JSON's extra wrinkle: a field missing from some records.
- Day 126 -- the reproducible cleaning pipeline: contracts, a manifest, and
  the raw-then-transform discipline this lab applies to ingestion.
- Course01 Days 22-28 -- HTTP fundamentals: status codes, `urllib.request`,
  and reading a response body as JSON.
- A working `python3` on your PATH; the lab needs the standard library plus
  pandas and pytest.

## Supported operating systems

macOS and Linux, tested directly. Windows: use WSL and follow the Linux
path below -- `bash`, `mktemp -d` and Python's `http.server` all behave
identically there.

## Hardware requirements

None beyond a normal laptop. The dataset is seven customers; nothing here
is memory- or CPU-bound.

## Required software

- Python 3.10 or newer (verified on 3.14.0 -- the code uses the `X | None`
  annotation style).
- pandas 3.0.5 and pytest 9.1.1, pinned in `requirements/requirements.txt`.
- `bash` to run `tests/run_tests.sh`.

## Free and open-source options

Every tool this lab uses -- pandas, pytest, and the standard library's
`http.server`, `urllib.request` and `json` -- is free and open source, with
no account, no API key and no paid tier. See
`requirements/README.md` for licences and exactly why each dependency is
needed.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-135-from-api-to-dataframe
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
.venv/bin/python3 -c "import pandas; print(pandas.__version__)"
```

## File structure

```
day-135-from-api-to-dataframe/
  README.md
  metadata.yml
  security.md
  troubleshooting.md
  requirements/
    requirements.txt
    README.md
  starter/
    00_brief.md
    conftest.py
    ingest.py           # 7 exercises: delete `raise NotImplementedError`
    test_ingest.py       # grades all 9 exercises; skips the unfinished ones
  examples/
    api_server.py         # the mock API, standard library only
    ingest.py              # the complete reference pipeline
    test_ingest.py          # the reference suite, 12 tests
  tests/
    run_tests.sh
  expected-output/
    sample-run.txt
    pytest-runs.txt
    test-run.txt
    FIELDS.md
```

## How to run

```bash
# The reference pipeline, complete and passing:
.venv/bin/pytest examples -q

# Your work, one exercise at a time (green from minute one):
.venv/bin/pytest starter -q

# Everything, with the numbers spelled out:
bash tests/run_tests.sh
```

Run `pytest examples` and `pytest starter` as two **separate** commands,
never combined (`pytest examples starter`). Both directories define
identically-named test modules, and pytest's collection of the combined
form is unreliable in both directions.

## What the commands do

- `pytest examples -q` runs the complete reference pipeline in
  `examples/ingest.py` against the mock API in `examples/api_server.py`,
  starting and stopping the server inside each test that needs it.
- `pytest starter -q` runs the same nine exercises against your
  `starter/ingest.py`. Any exercise whose function still contains
  `raise NotImplementedError` is skipped rather than failed, so the suite
  is green before you write a line and turns exercises green one at a time
  as you finish them.
- `bash tests/run_tests.sh` runs both suites, spells out the grain-trap
  numbers directly, proves idempotence and the contract by running them
  outside pytest as well, checks that copying the reference `ingest.py`
  into `starter/` turns every exercise green, and runs a hygiene pass
  (no real hostnames, no `sudo`, nothing left behind).

## Expected output

See `expected-output/FIELDS.md` for the full table of what is deterministic
and what varies by machine, and the three captured `.txt` files for real
runs. The one number worth knowing before you start: the order-grain
flattening of this lab's opening example inflates a true customer total of
**1550.0** to **2650.0** -- a **1100.0** overcount from duplicating two
customers' balances across their orders.

## Validation steps

1. `.venv/bin/pytest examples -q` reports `12 passed`.
2. `.venv/bin/pytest starter -q` reports `8 skipped` before you start, and
   `8 passed` once every exercise is finished.
3. `bash tests/run_tests.sh` ends with `39 checks, 0 failure(s).` and exits 0.

## Tests

`tests/run_tests.sh` is a bash assert harness. It resolves `pytest` from
`$PYTEST`, then `.venv/bin/`, then `PATH`; runs the example and starter
suites separately; spells out the grain-trap, idempotence and contract
numbers directly; proves the reference solution turns the starter suite
fully green; and runs a hygiene pass. It prints `N checks, M failure(s).`
and exits non-zero on any failure.

## Cleanup

```bash
rm -rf .venv
git checkout -- starter/   # optional: discard your work and start over
```

The test suite starts and stops the mock server inside each test, deletes
every temporary file it creates, and leaves no `__pycache__`, `.pytest_cache`
or generated JSONL behind. `tests/run_tests.sh`'s hygiene section checks
this directly.

## Troubleshooting

See `troubleshooting.md` for the full list. The most common one: if
`pytest` cannot import `api_server` or `ingest`, you are not running it
from this lab's directory, or a starter test is missing `conftest.py`.

## Security notes

See `security.md`. Short version: everything binds `127.0.0.1` on an
operating-system-assigned port, the mock API has no authentication and
must never be deployed, and validate a response body's shape before
anything downstream reads it -- that is what `check_contract` is for.

## Extension exercises

- Add a `source_url` and `fetched_at` column to the raw JSONL, so the raw
  store records provenance as well as content -- Day 126's manifest idea,
  applied one level earlier.
- Change `page_size` and confirm `detect_schema_drift` still reports page 3
  for `loyalty_tier` regardless of how the same 7 customers are paginated.
- Extend `check_contract` with a rule of your own -- for example, that
  `updated_at` is never in the future relative to when the frame was
  assembled -- and write a test that a corrupted payload trips it.
- Rewrite `fetch_incremental` to use the exclusive (`>`) boundary instead,
  and write a test that demonstrates the record it silently drops.

## Navigation

- Lesson: see the generated link above.
- Previous lab: `labs/sections/math-statistics-and-data/day-134-finding-data-open-datasets-and-apis/`
- Next lab: `labs/sections/math-statistics-and-data/day-136-the-exploratory-data-analysis-process/`
