"""From API to DataFrame -- the nine ideas this lab tests, as real code.

Every function here works on plain Python objects (dicts and lists decoded
from JSON) and pandas DataFrames. Nothing here is specific to the mock
server in `api_server.py`; the fetch helpers just happen to talk to it with
`urllib.request`, which is the one stdlib HTTP client this lesson exercises
end to end.

Read this top to bottom in the order the lesson's nine exercises use it:

  1-2. flatten_customer_grain / flatten_order_grain -- the grain trap
  3.   explode_list_column                          -- nested lists
  4.   pin_dtypes                                    -- untyped arrival
  5.   detect_schema_drift / assemble_pages          -- drift across pages
  6.   fetch_raw_pages / transform_from_raw           -- raw before transform
  7.   upsert                                         -- idempotent ingestion
  8.   ContractViolation / check_contract              -- the boundary contract
  9.   fetch_incremental                               -- the watermark
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd

# --------------------------------------------------------------------------
# 1-2. The grain trap: two flattenings of the same nested payload.
# --------------------------------------------------------------------------


def flatten_customer_grain(customers: list[dict[str, Any]]) -> pd.DataFrame:
    """One row per customer. `orders` stays a Python list inside each cell.

    This is what you get from `pandas.json_normalize(customers)` with no
    `record_path`: it flattens each customer's own fields into columns but
    leaves any nested list exactly where it was. Every customer-level number
    -- `total_amount_due` here -- appears exactly once, which is what makes
    this the correct grain for a "how much is each customer's balance"
    question.
    """
    return pd.json_normalize(customers)


def flatten_order_grain(customers: list[dict[str, Any]]) -> pd.DataFrame:
    """One row per order. Every customer-level field is repeated by design.

    `record_path="orders"` tells `json_normalize` which nested list becomes
    the grain of the output; `meta` names the parent fields to carry down
    onto every child row. That carrying-down is not a bug -- it is exactly
    what `meta` is for -- but it means `total_amount_due` is now duplicated
    once per order, and `.sum()` on it no longer means what it meant a
    moment ago. A customer with no orders contributes zero rows here: an
    empty list under `record_path` produces zero rows for that customer
    (contrast this with `DataFrame.explode`, exercise 3, which keeps a row).
    """
    return pd.json_normalize(
        customers,
        record_path="orders",
        meta=["customer_id", "name", "total_amount_due"],
    )


def duplicated_meta_columns(customers: list[dict[str, Any]]) -> dict[str, int]:
    """For each `meta` column, how many times does each customer's value repeat?

    Returns {customer_id: number of order rows that customer contributed},
    which is exactly the duplication factor for every meta column on that
    customer's rows.
    """
    return {str(c["customer_id"]): len(c.get("orders", [])) for c in customers}


# --------------------------------------------------------------------------
# 3. Nested lists and explode.
# --------------------------------------------------------------------------


def explode_list_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Turn one row holding a list into one row per list element.

    Unlike `json_normalize(..., record_path=...)`, `DataFrame.explode`
    KEEPS a row for an empty list -- it produces a single row with NaN in
    the exploded column, rather than dropping the parent entirely. That
    difference is the point of running both this and the grain-trap
    functions above side by side.
    """
    return df.explode(column, ignore_index=True)


# --------------------------------------------------------------------------
# 4. Untyped arrival: everything from JSON is a string, a number, or None.
# --------------------------------------------------------------------------


def pin_dtypes(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Coerce the known numeric and datetime columns; report how many values moved.

    Returns the pinned frame and the count of cells that were successfully
    converted from a string to a number across every column pinned here.
    Day 121's dtype-pinning discipline, applied to a frame that arrived as
    JSON rather than CSV -- the wrinkle here is that a column absent from
    some records (like `loyalty_tier`) is silently all-NaN for those rows
    rather than raising, so pinning has to tolerate missing columns too.
    """
    out = df.copy()
    coerced = 0

    for column in ("total_amount_due", "amount"):
        if column not in out.columns:
            continue
        before_numeric = pd.to_numeric(out[column], errors="coerce")
        was_string = out[column].apply(lambda v: isinstance(v, str))
        now_numeric = before_numeric.notna()
        coerced += int((was_string & now_numeric).sum())
        out[column] = before_numeric

    if "updated_at" in out.columns:
        out["updated_at"] = pd.to_datetime(out["updated_at"], utc=True, format="ISO8601")

    return out, coerced


# --------------------------------------------------------------------------
# 5. Schema drift across pages.
# --------------------------------------------------------------------------


def detect_schema_drift(pages: list[list[dict[str, Any]]]) -> dict[str, int]:
    """For each field that is NOT present on every page's first record set,
    report the 1-indexed page it first appears on.

    A field is "drift" here if it is missing from at least one earlier page
    and present on a later one. Fields present everywhere, or absent
    everywhere, are not drift.
    """
    seen_from: dict[str, int] = {}
    seen_by_page: list[set[str]] = []
    for page_records in pages:
        fields: set[str] = set()
        for record in page_records:
            fields |= set(record.keys())
        seen_by_page.append(fields)

    all_fields: set[str] = set()
    for fields in seen_by_page:
        all_fields |= fields

    drift: dict[str, int] = {}
    for field in sorted(all_fields):
        first_page = next(
            (i + 1 for i, fields in enumerate(seen_by_page) if field in fields), None
        )
        absent_from_an_earlier_page = any(field not in fields for fields in seen_by_page)
        if first_page is not None and absent_from_an_earlier_page and first_page > 1:
            drift[field] = first_page
        seen_from[field] = first_page or 0

    return drift


def assemble_pages(pages: list[list[dict[str, Any]]]) -> pd.DataFrame:
    """Concatenate every page's customer-grain flattening into one frame.

    A field that appears only from page 3 onward becomes a column that is
    NaN for every row from pages 1 and 2 -- pandas does this silently, which
    is exactly why `detect_schema_drift` exists as a separate, deliberate
    check rather than relying on someone noticing the NaNs.
    """
    frames = [flatten_customer_grain(page) for page in pages if page]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# --------------------------------------------------------------------------
# 6. Raw-then-transform.
# --------------------------------------------------------------------------


def fetch_raw_pages(base_url: str, page_size: int, raw_path: Path) -> int:
    """Fetch every page from the API and persist each raw response as one
    JSONL line, before any transformation happens. Returns the number of
    HTTP requests made.
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
    """Rebuild the assembled, dtype-pinned frame from the stored raw JSONL,
    touching no network at all.
    """
    pages: list[list[dict[str, Any]]] = []
    with raw_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            payload = json.loads(line)
            pages.append(payload["customers"])
    df = assemble_pages(pages)
    pinned, _ = pin_dtypes(df)
    return pinned


# --------------------------------------------------------------------------
# 7. Idempotent ingestion.
# --------------------------------------------------------------------------


def upsert(existing: pd.DataFrame, incoming: pd.DataFrame, key: str) -> pd.DataFrame:
    """Merge `incoming` into `existing`, keyed on `key`.

    Running this twice with the same `incoming` must leave the row count
    and the frame unchanged -- that is what "idempotent" means here. The
    incoming rows win a conflict, since they represent the most recently
    fetched state of that key.
    """
    if existing.empty:
        merged = incoming.copy()
    else:
        stays = existing[~existing[key].isin(incoming[key])]
        merged = pd.concat([stays, incoming], ignore_index=True)
    return merged.sort_values(key, ignore_index=True)


# --------------------------------------------------------------------------
# 8. The contract on the assembled frame.
# --------------------------------------------------------------------------


class ContractViolation(ValueError):
    """Raised by `check_contract` with the name of the rule that failed."""


REQUIRED_COLUMNS = {"customer_id", "name", "updated_at", "total_amount_due"}
MIN_ROWS, MAX_ROWS = 1, 10_000


def check_contract(df: pd.DataFrame) -> None:
    """Raise `ContractViolation` naming the first rule the frame breaks.

    Checked in order: required columns present, `customer_id` unique,
    `total_amount_due` numeric and non-negative, row count within bounds.
    """
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ContractViolation(f"missing required columns: {sorted(missing)}")

    if df["customer_id"].duplicated().any():
        dupes = sorted(df.loc[df["customer_id"].duplicated(), "customer_id"].unique())
        raise ContractViolation(f"duplicate customer_id: {dupes}")

    if not pd.api.types.is_numeric_dtype(df["total_amount_due"]):
        raise ContractViolation("total_amount_due is not numeric -- pin_dtypes must run first")

    if (df["total_amount_due"] < 0).any():
        raise ContractViolation("total_amount_due contains a negative balance")

    if not (MIN_ROWS <= len(df) <= MAX_ROWS):
        raise ContractViolation(f"row count {len(df)} is outside [{MIN_ROWS}, {MAX_ROWS}]")


# --------------------------------------------------------------------------
# 9. Incremental fetch by watermark.
# --------------------------------------------------------------------------


def fetch_incremental(base_url: str, since: str) -> tuple[pd.DataFrame, str]:
    """Fetch every customer updated at or after `since`.

    The boundary convention is INCLUSIVE (`>=`, not `>`): the server may
    hand back the same boundary record twice across two consecutive calls,
    but `upsert`'s natural-key merge absorbs that duplicate for free. The
    exclusive convention (`>`) would avoid the duplicate but risks silently
    DROPPING a record that shares its `updated_at` with the watermark record
    -- a customer updated in the same second the last page was fetched simply
    never appears in any later call. A harmless duplicate beats permanent
    data loss, so this lab errs on the side of `>=`.
    """
    url = f"{base_url}/api/customers/incremental?since={since}"
    with urllib.request.urlopen(url, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
    df = flatten_customer_grain(payload["customers"]) if payload["customers"] else pd.DataFrame(
        columns=["customer_id", "name", "updated_at", "total_amount_due"]
    )
    return df, payload["watermark"]
