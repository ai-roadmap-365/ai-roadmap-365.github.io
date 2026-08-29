# Expected output -- Day 135 lab

Real captured runs from the authoring machine (macOS, Python 3.14.0, pandas
3.0.5, pytest 9.1.1, 2026-08-20). Every byte below came out of a command
that really ran, against the mock API this lab starts on 127.0.0.1. **No
capture in this directory involved the internet.**

## Files

- `sample-run.txt` -- the grain trap, the meta duplication, untyped
  arrival and pinning, and `explode` on an empty list, run directly against
  `examples/ingest.py`.
- `pytest-runs.txt` -- `pytest examples -q` and `pytest starter -q`
  (exercises unfinished).
- `test-run.txt` -- a full run of `bash tests/run_tests.sh`.

## What is deterministic and what is not

| Varies | Where | Why |
| --- | --- | --- |
| The port, e.g. `127.0.0.1:54321` | every capture that starts the server | The lab binds port `0`, so the operating system picks a free port each run. A hard-coded port would collide with whatever you already have running. |
| pytest's reported duration, e.g. `2.99s` | `pytest-runs.txt`, `test-run.txt` | Wall-clock timing on the machine that ran it. |

Everything else -- every row count, every dtype, every dollar figure, every
exit code, every message from `ContractViolation` -- is identical on every
run and on every machine, because the API is a fixture with a fixed,
in-memory dataset rather than a live service.

## Required behaviour -- the mock API (`examples/api_server.py`)

| Endpoint | Result |
| --- | --- |
| `GET /api/customers?page=1&page_size=2` | `{"page":1,"page_size":2,"total_pages":4,"customers":[C1,C2]}` |
| `GET /api/customers?page=3&page_size=2` | C5 and C6 -- the first page carrying `loyalty_tier` |
| `GET /api/customers?page=4&page_size=2` | one customer, C7 -- 7 customers total, ceiling-divided into 4 pages of size 2 |
| `GET /api/customers/incremental?since=1970-01-01T00:00:00Z` | all 7 customers, `watermark` = `2026-01-11T10:00:00Z` (C7's `updated_at`) |
| `GET /api/customers/incremental?since=<that watermark>` | 1 customer back: C7 again (inclusive boundary, by design) |
| `GET /control/stats` after 4 page requests | `{"requests": 4}` |

## Required behaviour -- the grain trap (exercises 1-2)

| Flattening | Rows | `sum(total_amount_due)` |
| --- | --- | --- |
| `flatten_customer_grain` (`json_normalize`, no `record_path`) | 3 | 1550.0 -- the true total |
| `flatten_order_grain` (`record_path="orders"`, `meta=[...]`) | 6 | 2650.0 -- inflated by **1100.0** |

C1 contributes 2 order rows and its `total_amount_due` (500.0) is
duplicated across both; C3 contributes 3 order rows and its 300.0 is
duplicated across all three. That is the entire source of the 1100.0
inflation: `500*2 + 750*1 + 300*3 = 2650`, against a true total of
`500 + 750 + 300 = 1550`.

## Required behaviour -- explode vs. record_path (exercise 3)

| Input | Method | Rows out | Empty-list row |
| --- | --- | --- | --- |
| a customer with `tags: []` | `DataFrame.explode("tags")` | kept, 1 row | `NaN` in the exploded column |
| a customer with `orders: []` | `json_normalize(..., record_path="orders")` | **dropped**, 0 rows | the customer disappears entirely |

Measured directly on pandas 3.0.5: `explode` on an all-empty-list column
produces one row per original row with `NaN`, never zero rows. This is the
opposite of what `record_path` does with the same shape of data, and the
lab's tests assert both behaviours side by side so the contrast is a fact,
not a claim.

## Required behaviour -- untyped arrival and pinning (exercise 4)

| Column | Before `pin_dtypes` | After | Coerced count |
| --- | --- | --- | --- |
| `amount` (order-grain, 6 rows) | `str`, e.g. `"200.00"` | `float64` | 6 |
| `updated_at` | `str`, ISO 8601 | `datetime64[ns, UTC]` | n/a (parsed, not counted) |

## Required behaviour -- schema drift (exercise 5)

`detect_schema_drift` on the 4 pages (`page_size=2`) returns exactly
`{"loyalty_tier": 3}` -- `loyalty_tier` first appears on page 3 (customers
C5 and C6) and is present on every page from there on. After assembly, the
column exists for all 7 rows: 4 `NaN` (C1-C4), 3 populated (C5-C7).

## Required behaviour -- raw then transform (exercise 6)

Fetching all 7 customers at `page_size=2` costs **4** HTTP requests, which
the server's own `/control/stats` counter confirms independently of the
client's count. `transform_from_raw` rebuilds all 7 rows from the stored
JSONL with the server stopped -- zero further requests are possible because
there is nothing listening.

## Required behaviour -- idempotent ingestion (exercise 7)

Running `upsert` twice with the same incoming frame leaves the row count
and the frame's contents unchanged (`pandas.testing.assert_frame_equal`
passes on the two results). Upserting a changed row (same key, new value)
replaces it in place rather than adding a second row for that key.

## Required behaviour -- the contract (exercise 8)

| Input | Result |
| --- | --- |
| the healthy 7-row assembled, pinned frame | `check_contract` returns, no exception |
| the same frame with one row duplicated (same `customer_id`) | `ContractViolation("duplicate customer_id: [...]")` |
| the same frame with `total_amount_due` dropped | `ContractViolation("missing required columns: ['total_amount_due']")` |
| the same frame with one balance set to -1.0 | `ContractViolation("total_amount_due contains a negative balance")` |

## Required behaviour -- the incremental watermark (exercise 9)

A first call with `since` far in the past returns all 7 customers and a
`watermark` equal to the latest `updated_at` seen (C7's). A second call
using that exact watermark as `since` returns **1** record: C7, again. This
lab chose the inclusive (`>=`) boundary on purpose -- see `ingest.py`'s
`fetch_incremental` docstring and the lesson's "Implications" section for
why a harmless duplicate beats a silently dropped record.

## Test counts

| Command | Result |
| --- | --- |
| `pytest examples -q` | `12 passed`, exit 0, about 3 s |
| `pytest starter -q` (exercises unfinished) | `8 skipped`, exit 0 |
| `pytest starter -q` (reference `ingest.py` copied in) | `8 passed`, exit 0 |
| `bash tests/run_tests.sh` | `39 checks, 0 failure(s).`, exit 0 |

## Platform notes

- **macOS and Linux** -- identical. `python3`, `bash` and `mktemp -d`
  behave the same, and `http.server` is the same code on both.
- **Windows** -- use WSL and follow the Linux path.
- **Python version** -- verified on 3.14.0. Python 3.10 or newer is
  required for the `X | None` annotation style used throughout.
- **pandas version** -- verified on 3.0.5. The `explode`-keeps /
  `record_path`-drops contrast in exercise 3 was measured directly on this
  version; earlier pandas releases have made small changes to
  `json_normalize`'s handling of empty lists in the past, so re-verify on
  another major version before relying on the exact row counts.
