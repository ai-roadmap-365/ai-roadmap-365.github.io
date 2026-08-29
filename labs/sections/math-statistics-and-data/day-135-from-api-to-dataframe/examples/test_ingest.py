"""The nine exercises, asserted against real behaviour.

Run with: pytest examples -q  (from the lab directory)

Every test in this file names the number of the exercise it belongs to in
its docstring, matching the lesson's "One Row Means One Thing" lab brief.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from api_server import CUSTOMERS, base_url, running_server
from ingest import (
    ContractViolation,
    assemble_pages,
    check_contract,
    detect_schema_drift,
    duplicated_meta_columns,
    explode_list_column,
    fetch_incremental,
    fetch_raw_pages,
    flatten_customer_grain,
    flatten_order_grain,
    pin_dtypes,
    transform_from_raw,
    upsert,
)

# A small standalone nested payload for exercises 1-3, independent of the
# server's dataset -- these exercises only need recorded JSON, not HTTP.
GRAIN_PAYLOAD = [
    {
        "customer_id": "C1",
        "name": "Ada Lovelace",
        "total_amount_due": 500.00,
        "orders": [
            {"order_id": "O1", "amount": "200.00"},
            {"order_id": "O2", "amount": "300.00"},
        ],
    },
    {
        "customer_id": "C2",
        "name": "Grace Hopper",
        "total_amount_due": 750.00,
        "orders": [{"order_id": "O3", "amount": "750.00"}],
    },
    {
        "customer_id": "C3",
        "name": "Alan Turing",
        "total_amount_due": 300.00,
        "orders": [
            {"order_id": "O4", "amount": "100.00"},
            {"order_id": "O5", "amount": "100.00"},
            {"order_id": "O6", "amount": "100.00"},
        ],
    },
]

TAGGED_PAYLOAD = pd.DataFrame(
    {
        "customer_id": ["C1", "C2", "C3"],
        "tags": [["vip", "early-adopter"], ["vip"], []],
    }
)


# --------------------------------------------------------------------------
# 1. The grain trap.
# --------------------------------------------------------------------------


def test_exercise1_the_two_flattenings_give_different_row_counts():
    customer_grain = flatten_customer_grain(GRAIN_PAYLOAD)
    order_grain = flatten_order_grain(GRAIN_PAYLOAD)

    assert len(customer_grain) == 3
    assert len(order_grain) == 6

    true_total = customer_grain["total_amount_due"].sum()
    inflated_total = order_grain["total_amount_due"].sum()

    assert true_total == 1550.0
    assert inflated_total == 2650.0
    assert inflated_total - true_total == 1100.0


# --------------------------------------------------------------------------
# 2. json_normalize with meta -- the duplication, understood not discovered.
# --------------------------------------------------------------------------


def test_exercise2_meta_columns_duplicate_by_the_order_count():
    order_grain = flatten_order_grain(GRAIN_PAYLOAD)
    duplication = duplicated_meta_columns(GRAIN_PAYLOAD)

    assert duplication == {"C1": 2, "C2": 1, "C3": 3}

    for customer_id, expected_repeats in duplication.items():
        rows = order_grain[order_grain["customer_id"] == customer_id]
        assert len(rows) == expected_repeats
        assert rows["total_amount_due"].nunique() == 1  # one value, repeated

    # Every meta column carries the duplication, not just total_amount_due.
    for column in ("customer_id", "name", "total_amount_due"):
        assert column in order_grain.columns


# --------------------------------------------------------------------------
# 3. explode: exact multiplication, empty list survives as NaN.
# --------------------------------------------------------------------------


def test_exercise3_explode_multiplies_rows_by_list_length():
    exploded = explode_list_column(TAGGED_PAYLOAD, "tags")

    # 2 tags + 1 tag + 1 (empty list keeps one row) = 4.
    assert len(exploded) == 4

    c3_rows = exploded[exploded["customer_id"] == "C3"]
    assert len(c3_rows) == 1
    assert pd.isna(c3_rows["tags"].iloc[0])

    c1_rows = exploded[exploded["customer_id"] == "C1"]
    assert len(c1_rows) == 2
    assert set(c1_rows["tags"]) == {"vip", "early-adopter"}


def test_exercise3_record_path_drops_what_explode_keeps():
    # Contrast: json_normalize(record_path=...) on the same shape of data
    # DROPS a record with an empty list entirely, rather than keeping a row.
    no_orders = [{"customer_id": "C4", "orders": []}]
    order_grain = pd.json_normalize(no_orders, record_path="orders", meta=["customer_id"])
    assert len(order_grain) == 0

    as_frame = pd.DataFrame(no_orders)
    exploded = explode_list_column(as_frame, "orders")
    assert len(exploded) == 1
    assert pd.isna(exploded["orders"].iloc[0])


# --------------------------------------------------------------------------
# 4. Untyped arrival.
# --------------------------------------------------------------------------


def test_exercise4_numeric_fields_arrive_as_strings_and_pinning_fixes_them():
    order_grain = flatten_order_grain(GRAIN_PAYLOAD)
    assert order_grain["amount"].apply(lambda v: isinstance(v, str)).all()

    pinned, coerced = pin_dtypes(order_grain)
    assert pd.api.types.is_numeric_dtype(pinned["amount"])
    assert coerced == 6  # every one of the 6 order-grain amount values
    assert pinned["amount"].sum() == pytest.approx(1550.0)


# --------------------------------------------------------------------------
# 5. Schema drift across pages.
# --------------------------------------------------------------------------


def _pages_from_server(page_size: int = 2) -> list[list[dict]]:
    with running_server() as server:
        url = base_url(server)
        pages: list[list[dict]] = []
        import urllib.request

        page = 1
        total_pages = 1
        while page <= total_pages:
            with urllib.request.urlopen(
                f"{url}/api/customers?page={page}&page_size={page_size}", timeout=5
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
            pages.append(payload["customers"])
            total_pages = payload["total_pages"]
            page += 1
        return pages


def test_exercise5_drift_detector_names_the_field_and_first_page():
    pages = _pages_from_server(page_size=2)
    assert len(pages) == 4  # 7 customers, page_size 2 -> pages of 2,2,2,1

    drift = detect_schema_drift(pages)
    assert drift == {"loyalty_tier": 3}

    assembled = assemble_pages(pages)
    assert len(assembled) == 7
    assert assembled["loyalty_tier"].isna().sum() == 4  # C1-C4 have none
    assert assembled["loyalty_tier"].notna().sum() == 3  # C5-C7 have it


# --------------------------------------------------------------------------
# 6. Raw then transform.
# --------------------------------------------------------------------------


def test_exercise6_raw_is_written_before_transform_and_replay_touches_no_server(tmp_path: Path):
    raw_path = tmp_path / "raw_customers.jsonl"

    with running_server() as server:
        url = base_url(server)
        requests_made = fetch_raw_pages(url, page_size=2, raw_path=raw_path)

    assert requests_made == 4  # one request per page, 4 pages
    assert raw_path.exists()
    lines = raw_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 4  # one raw line per page, written before any transform

    # Replaying from the stored raw copy must not touch the server at all --
    # there is no server running here, so any attempted call would raise.
    replayed = transform_from_raw(raw_path)
    assert len(replayed) == 7
    assert pd.api.types.is_numeric_dtype(replayed["total_amount_due"])


# --------------------------------------------------------------------------
# 7. Idempotent ingestion.
# --------------------------------------------------------------------------


def test_exercise7_ingesting_the_same_page_twice_does_not_duplicate():
    page = CUSTOMERS[0:2]
    frame = flatten_customer_grain(page)
    pinned, _ = pin_dtypes(frame)

    once = upsert(pd.DataFrame(), pinned, key="customer_id")
    twice = upsert(once, pinned, key="customer_id")

    assert len(once) == 2
    assert len(twice) == 2
    pd.testing.assert_frame_equal(
        once.reset_index(drop=True), twice.reset_index(drop=True)
    )


def test_exercise7_upsert_replaces_a_changed_row_rather_than_adding_one():
    original = flatten_customer_grain([CUSTOMERS[0]])
    changed = flatten_customer_grain([CUSTOMERS[0]]).copy()
    changed.loc[0, "total_amount_due"] = "999.00"

    merged = upsert(original, changed, key="customer_id")
    assert len(merged) == 1
    assert merged.loc[0, "total_amount_due"] == "999.00"


# --------------------------------------------------------------------------
# 8. The contract.
# --------------------------------------------------------------------------


def test_exercise8_a_healthy_frame_passes_the_contract():
    pages = _pages_from_server(page_size=3)
    assembled = assemble_pages(pages)
    pinned, _ = pin_dtypes(assembled)
    check_contract(pinned)  # must not raise


def test_exercise8_a_corrupted_payload_is_named_and_refused():
    pages = _pages_from_server(page_size=3)
    assembled = assemble_pages(pages)
    pinned, _ = pin_dtypes(assembled)

    corrupted = pd.concat([pinned, pinned.iloc[[0]]], ignore_index=True)  # duplicate key
    with pytest.raises(ContractViolation, match="duplicate customer_id"):
        check_contract(corrupted)

    missing_column = pinned.drop(columns=["total_amount_due"])
    with pytest.raises(ContractViolation, match="missing required columns"):
        check_contract(missing_column)

    negative_balance = pinned.copy()
    negative_balance.loc[0, "total_amount_due"] = -5.0
    with pytest.raises(ContractViolation, match="negative balance"):
        check_contract(negative_balance)


# --------------------------------------------------------------------------
# 9. Incremental watermark.
# --------------------------------------------------------------------------


def test_exercise9_incremental_fetch_returns_only_records_after_the_watermark():
    with running_server() as server:
        url = base_url(server)
        first_batch, watermark = fetch_incremental(url, since="1970-01-01T00:00:00Z")
        assert len(first_batch) == 7
        assert watermark == "2026-01-11T10:00:00Z"

        second_batch, watermark2 = fetch_incremental(url, since=watermark)
        # Inclusive boundary: the watermark record (C7) comes back again.
        assert len(second_batch) == 1
        assert set(second_batch["customer_id"]) == {"C7"}
        assert watermark2 == watermark

        after_c7, _ = fetch_incremental(url, since="2026-01-11T10:00:01Z")
        assert len(after_c7) == 0
