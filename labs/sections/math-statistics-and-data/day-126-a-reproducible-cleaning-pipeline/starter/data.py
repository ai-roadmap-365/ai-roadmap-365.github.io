"""Raw messy orders data and pipeline configuration for Day 126's lab.

`build_raw_orders()` returns a small, deliberately messy DataFrame built to
exercise every property this lab tests:

- `amount` arrives as currency-formatted strings ("$120.50"), including one
  genuinely missing value -- the input a real intake system would hand you.
- `region` carries whitespace and inconsistent casing (" north", "South").
- Two rows (order_id 1 and 3) are the SAME real-world order resubmitted
  under a new order_id, differing only in region's whitespace/casing --
  they become visible as duplicates only after normalisation. This is
  exercise 6's order-dependence case, built into the data on purpose.
- `priority` is a nullable pandas Int64 column with one missing value
  (order_id 4), carried through the whole pipeline untouched, so exercise 8
  can prove a Parquet checkpoint preserves it exactly (Day 121's result,
  used in anger).

CONFIG carries every threshold, mapping and column list the pipeline reads,
so re-running with different parameters never means editing steps.py or
pipeline.py -- only this dict.
"""

from __future__ import annotations

import pandas as pd

CONFIG: dict = {
    # Fixed ceiling for outlier clipping. NEVER recomputed from the data at
    # run time -- that is exactly the mistake exercise 1's broken step
    # demonstrates. Chosen so two rows collide exactly at the ceiling,
    # which is what makes exercise 2's explicit tie-break necessary.
    "amount_clip_max": 900.0,
    # Columns compared when deciding whether two rows describe the same
    # real-world order. Deliberately excludes order_id, because a
    # resubmitted order is assigned a NEW order_id by the intake system.
    "dedupe_subset": ["region", "amount", "priority"],
    # Fixed reference statistics for the z-score step, computed once from
    # this lab's known-good raw data and frozen here -- never recomputed
    # from whatever frame happens to be passing through the pipeline.
    "amount_reference_mean": 300.0,
    "amount_reference_std": 150.0,
}


def build_raw_orders() -> pd.DataFrame:
    """Seven rows, one duplicate pair, one missing amount, one missing
    priority. Every value below is a literal -- nothing here is randomised,
    so every hash and every assertion in this lab is exactly reproducible.
    """
    return pd.DataFrame(
        {
            "order_id": pd.array([1, 2, 3, 4, 5, 6, 7], dtype="int64"),
            "region": [
                " north",
                "South",
                "north",
                "EAST ",
                "South",
                "west",
                "East",
            ],
            "amount": [
                "$120.50",
                "$980.00",
                "$120.50",
                "$75.00",
                None,
                "$60.00",
                "$1,250.00",
            ],
            "priority": pd.array([1, 2, 1, None, 3, 2, 1], dtype="Int64"),
        }
    )
