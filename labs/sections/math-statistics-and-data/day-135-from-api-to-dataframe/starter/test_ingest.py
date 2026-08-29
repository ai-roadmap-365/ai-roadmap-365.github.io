"""YOUR FILE -- checks that grade exercises 1 to 9.

Run it at any time:

    .venv/bin/pytest starter -q

Every test for an unfinished exercise is SKIPPED, so this file exits 0 from
the first minute and turns green one exercise at a time as you delete each
`raise NotImplementedError` in `ingest.py`.
"""

from __future__ import annotations

import inspect
import json
import urllib.request

import pandas as pd
import pytest

import ingest
from ingest import ContractViolation
from api_server import CUSTOMERS


def unfinished(fn) -> bool:
    try:
        return "raise NotImplementedError" in inspect.getsource(fn)
    except OSError:  # pragma: no cover
        return False


def needs(*fns):
    reason = ", ".join(fn.__name__ for fn in fns if unfinished(fn))
    return pytest.mark.skipif(bool(reason), reason=f"not written yet: {reason}")


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


@needs(ingest.flatten_customer_grain, ingest.flatten_order_grain)
def test_exercises1_and_2_the_grain_trap_and_meta_duplication():
    customer_grain = ingest.flatten_customer_grain(GRAIN_PAYLOAD)
    order_grain = ingest.flatten_order_grain(GRAIN_PAYLOAD)

    assert len(customer_grain) == 3
    assert len(order_grain) == 6
    assert customer_grain["total_amount_due"].sum() == 1550.0
    assert order_grain["total_amount_due"].sum() == 2650.0


@needs(ingest.explode_list_column)
def test_exercise3_explode_multiplies_and_keeps_the_empty_list():
    exploded = ingest.explode_list_column(TAGGED_PAYLOAD, "tags")
    assert len(exploded) == 4
    c3 = exploded[exploded["customer_id"] == "C3"]
    assert len(c3) == 1
    assert pd.isna(c3["tags"].iloc[0])


@needs(ingest.flatten_order_grain, ingest.pin_dtypes)
def test_exercise4_pinning_coerces_the_string_amounts():
    order_grain = ingest.flatten_order_grain(GRAIN_PAYLOAD)
    assert order_grain["amount"].apply(lambda v: isinstance(v, str)).all()
    pinned, coerced = ingest.pin_dtypes(order_grain)
    assert pd.api.types.is_numeric_dtype(pinned["amount"])
    assert coerced == 6


@needs(ingest.flatten_customer_grain, ingest.detect_schema_drift)
def test_exercise5_drift_detector_finds_loyalty_tier_on_page_3(base):
    pages: list[list[dict]] = []
    page, total_pages = 1, 1
    while page <= total_pages:
        with urllib.request.urlopen(
            f"{base}/api/customers?page={page}&page_size=2", timeout=5
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
        pages.append(payload["customers"])
        total_pages = payload["total_pages"]
        page += 1

    drift = ingest.detect_schema_drift(pages)
    assert drift == {"loyalty_tier": 3}

    assembled = ingest.assemble_pages(pages)
    assert len(assembled) == 7
    assert assembled["loyalty_tier"].isna().sum() == 4


def test_exercise6_raw_then_transform_and_replay_hits_no_server(base, tmp_path):
    raw_path = tmp_path / "raw.jsonl"
    requests_made = ingest.fetch_raw_pages(base, page_size=2, raw_path=raw_path)
    assert requests_made == 4
    lines = raw_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 4

    if unfinished(ingest.flatten_customer_grain) or unfinished(ingest.pin_dtypes):
        pytest.skip("needs flatten_customer_grain and pin_dtypes finished first")
    replayed = ingest.transform_from_raw(raw_path)
    assert len(replayed) == 7


@needs(ingest.flatten_customer_grain, ingest.pin_dtypes, ingest.upsert)
def test_exercise7_upsert_is_idempotent():
    page = CUSTOMERS[0:2]
    frame = ingest.flatten_customer_grain(page)
    pinned, _ = ingest.pin_dtypes(frame)

    once = ingest.upsert(pd.DataFrame(), pinned, key="customer_id")
    twice = ingest.upsert(once, pinned, key="customer_id")
    assert len(once) == 2
    assert len(twice) == 2
    pd.testing.assert_frame_equal(once.reset_index(drop=True), twice.reset_index(drop=True))


@needs(ingest.flatten_customer_grain, ingest.pin_dtypes, ingest.check_contract)
def test_exercise8_contract_names_the_broken_rule():
    frame = ingest.flatten_customer_grain(CUSTOMERS)
    pinned, _ = ingest.pin_dtypes(frame)
    ingest.check_contract(pinned)  # a healthy frame must not raise

    corrupted = pd.concat([pinned, pinned.iloc[[0]]], ignore_index=True)
    with pytest.raises(ContractViolation, match="duplicate customer_id"):
        ingest.check_contract(corrupted)


def test_exercise9_incremental_fetch_respects_the_watermark(base):
    if unfinished(ingest.flatten_customer_grain):
        pytest.skip("needs flatten_customer_grain finished first")
    first_batch, watermark = ingest.fetch_incremental(base, since="1970-01-01T00:00:00Z")
    assert len(first_batch) == 7
    second_batch, _ = ingest.fetch_incremental(base, since=watermark)
    assert set(second_batch["customer_id"]) == {"C7"}  # inclusive boundary
