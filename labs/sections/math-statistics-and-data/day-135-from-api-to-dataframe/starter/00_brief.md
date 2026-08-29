# The brief -- One Row Means One Thing

You have been handed access to a small customer-and-orders API
(`examples/api_server.py`, started for you by `conftest.py`). It returns
paginated, nested JSON: each page is a list of customers, and each customer
carries a list of their own orders.

Your job is to build the ingestion pipeline in `ingest.py`, one function at
a time, that turns that nested JSON into a DataFrame you can trust: the
right grain, the right dtypes, a detector for the field that only shows up
from page 3 onward, a raw-before-transform step, an idempotent upsert, a
contract on the assembled frame, and an incremental fetch by watermark.

## Why the grain comes first

Before you write a single line, answer this question out loud: **does one
row in your target frame mean one customer, or one order?**

Both are legitimate. Neither is more "correct" than the other in general.
But they give different row counts and different aggregates from the
*same* JSON, and the difference is not a rounding error -- it is a customer
balance duplicated once per order that customer has. Get the grain wrong
and every downstream number is wrong in a way that looks completely
plausible until someone checks it against the invoice.

## The nine exercises

1. **`flatten_customer_grain` and `flatten_order_grain`** -- the two
   flattenings of the same nested payload, and the numbers that prove they
   disagree.
2. Understand exactly which columns `meta` duplicates, and by how much.
3. **`explode_list_column`** -- and see, on your own machine, what
   pandas 3.0.5 does with an empty list (it is not what `record_path`
   does with one).
4. **`pin_dtypes`** -- everything from JSON arrives as a string, a number,
   or `None`. Fix it, and count what you fixed.
5. **`detect_schema_drift`** -- one field is missing from the first six
   customers and present on the last three. Name it and the page it first
   appeared on.
6. Use the provided `fetch_raw_pages` / `transform_from_raw` to see raw
   storage pay for itself: a full re-run from disk touches no network.
7. **`upsert`** -- ingest the same page twice and prove nothing duplicated.
8. **`check_contract`** -- a frame that passes, and a frame that does not,
   with the exact rule named in the exception.
9. Use the provided `fetch_incremental` and explain, in your own words, why
   it errs toward a possible duplicate rather than a possible loss.

## Run your work at any time

```bash
.venv/bin/pytest starter -q
```

Unfinished exercises are skipped, so this is green from the first minute.
Delete one `raise NotImplementedError` at a time and watch a skip turn into
a pass.
