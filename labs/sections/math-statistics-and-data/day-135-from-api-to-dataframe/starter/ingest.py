"""YOUR FILE -- exercises 1, 2, 3, 4, 5, 7 and 8.

Seven functions below have a docstring saying exactly what they must do, a
signature that is already right, and a `raise NotImplementedError` you
delete. `examples/ingest.py` contains a complete reference implementation:
use it when you are stuck, but write yours first.

`fetch_raw_pages`, `transform_from_raw` and `fetch_incremental` (exercises 6
and 9) are provided complete below -- they are mostly HTTP and file
plumbing, not the pandas ideas this lab is about, and you will use them
as-is while writing the rest.

Run your work at any time:

    .venv/bin/pytest starter -q

Unfinished exercises are skipped, so the suite exits 0 from the first
minute. Check everything at the end with:

    bash tests/run_tests.sh
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd


def flatten_customer_grain(customers: list[dict[str, Any]]) -> pd.DataFrame:
    """Exercise 1a. One row per customer, using `pandas.json_normalize`.

    Call `pandas.json_normalize` with NO `record_path` -- that is what keeps
    each customer's nested `orders` list inside a single cell instead of
    exploding it, which is what makes this the customer grain.
    """
    raise NotImplementedError


def flatten_order_grain(customers: list[dict[str, Any]]) -> pd.DataFrame:
    """Exercise 1b. One row per order, using `record_path` and `meta`.

    Call `pandas.json_normalize` with `record_path="orders"` and
    `meta=["customer_id", "name", "total_amount_due"]`. Every meta field
    will repeat once per order that customer has.
    """
    raise NotImplementedError


def explode_list_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Exercise 3. One row per list element, using `DataFrame.explode`.

    Use `df.explode(column, ignore_index=True)`. Unlike `record_path`
    above, exploding an empty list KEEPS one row with NaN rather than
    dropping the parent record.
    """
    raise NotImplementedError


def pin_dtypes(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Exercise 4. Coerce `total_amount_due` and `amount` to numeric, and
    `updated_at` to a UTC datetime, wherever those columns are present.

    Return `(pinned_df, coerced_count)` where `coerced_count` is the number
    of string cells across those numeric columns that successfully became
    numbers. Use `pandas.to_numeric(..., errors="coerce")` and
    `pandas.to_datetime(..., utc=True, format="ISO8601")`.
    """
    raise NotImplementedError


def detect_schema_drift(pages: list[list[dict[str, Any]]]) -> dict[str, int]:
    """Exercise 5. For each field missing from at least one EARLIER page but
    present on a LATER one, report the 1-indexed page it first appears on.

    A field present on every page, or on none, is not drift and must not
    appear in the returned dict.
    """
    raise NotImplementedError


def upsert(existing: pd.DataFrame, incoming: pd.DataFrame, key: str) -> pd.DataFrame:
    """Exercise 7. Merge `incoming` into `existing`, keyed on `key`.

    Rows in `existing` whose key also appears in `incoming` must be
    replaced, not duplicated. Running this twice with the same `incoming`
    must produce the same result both times -- that is the idempotence this
    exercise proves.
    """
    raise NotImplementedError


class ContractViolation(ValueError):
    """Raised by `check_contract` with the name of the rule that failed."""


REQUIRED_COLUMNS = {"customer_id", "name", "updated_at", "total_amount_due"}
MIN_ROWS, MAX_ROWS = 1, 10_000


def check_contract(df: pd.DataFrame) -> None:
    """Exercise 8. Raise `ContractViolation` naming the FIRST rule broken.

    Check, in this order: (1) every column in `REQUIRED_COLUMNS` is
    present, (2) `customer_id` has no duplicates, (3) `total_amount_due` is
    numeric, (4) `total_amount_due` has no negative values, (5) the row
    count is within `[MIN_ROWS, MAX_ROWS]`. Put the offending value(s) in
    the message, e.g. "duplicate customer_id: [...]".
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Provided, complete -- exercises 6 and 9 build on these directly.
# --------------------------------------------------------------------------


def assemble_pages(pages: list[list[dict[str, Any]]]) -> pd.DataFrame:
    frames = [flatten_customer_grain(page) for page in pages if page]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def fetch_raw_pages(base_url: str, page_size: int, raw_path: Path) -> int:
    """Exercise 6. Fetch every page and persist each raw response as one
    JSONL line BEFORE any transformation. Returns the number of requests made.
    Provided complete -- read it, then use it.
    """
    requests_made = 0
    page = 1
    total_pages = 1
    with raw_path.open("w", encoding="utf-8") as fh:
        while page <= total_pages:
            url = f"{base_url}/api/customers?page={page}&page_size={page_size}"
            with urllib.request.urlopen(url, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
            requests_made += 1
            total_pages = payload["total_pages"]
            fh.write(json.dumps(payload) + "\n")
            page += 1
    return requests_made


def transform_from_raw(raw_path: Path) -> pd.DataFrame:
    """Exercise 6. Rebuild the frame from stored raw JSONL, touching no
    network. Provided complete -- it calls your `assemble_pages` and
    `pin_dtypes` once those are written.
    """
    pages: list[list[dict[str, Any]]] = []
    with raw_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            payload = json.loads(line)
            pages.append(payload["customers"])
    df = assemble_pages(pages)
    pinned, _ = pin_dtypes(df)
    return pinned


def fetch_incremental(base_url: str, since: str) -> tuple[pd.DataFrame, str]:
    """Exercise 9. Fetch every customer updated at or after `since`
    (inclusive boundary -- see the lesson for why). Provided complete.
    """
    url = f"{base_url}/api/customers/incremental?since={since}"
    with urllib.request.urlopen(url, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload["customers"]:
        df = flatten_customer_grain(payload["customers"])
    else:
        df = pd.DataFrame(columns=["customer_id", "name", "updated_at", "total_amount_due"])
    return df, payload["watermark"]
