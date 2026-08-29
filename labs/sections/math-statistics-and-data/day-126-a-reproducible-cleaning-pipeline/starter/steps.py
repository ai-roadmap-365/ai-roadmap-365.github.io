"""Individual pipeline steps.

Each step is a pure function from frame to frame, named for what it does,
and testable on its own against a small fixture -- the cure for the
notebook's defining hazard, out-of-order cell execution. No step mutates
its input in place; every step returns a new frame built with `.copy()`.

Two steps clip `amount` to an upper bound, and only one of them belongs in
the real pipeline:

- `clip_amount_to_fixed_ceiling` reads its threshold from `config` --
  computed once, outside the pipeline, and frozen. Idempotent: clipping
  already-clipped data to the same fixed number changes nothing.
- `clip_amount_to_recomputed_percentile` is kept here ONLY as the lesson's
  worked failure. It recomputes its threshold from whatever data happens to
  be passing through it, which means a second call sees already-clipped
  data and computes a NEW, lower threshold from it -- non-idempotent by
  construction. `pipeline.py` never calls it; `test_pipeline.py` calls it
  directly to prove the failure before the fix.
"""

from __future__ import annotations

import pandas as pd


def parse_currency_amount(df: pd.DataFrame) -> pd.DataFrame:
    """Strip '$' and ',' from `amount` and convert to float64.

    Idempotent by inspection, not just by luck: once `amount` is numeric,
    the "still text" guard below is False and the step is a no-op on a
    second call, rather than re-stripping characters that are no longer
    there. The guard checks for a non-numeric dtype rather than the
    specific `object` dtype, because pandas 3.0's default string inference
    gives a plain Python string column its own `str` extension dtype, not
    `object` -- a version-specific fact this lab's own run confirmed.
    """
    df = df.copy()
    if not pd.api.types.is_numeric_dtype(df["amount"]):
        cleaned = df["amount"].str.replace(r"[$,]", "", regex=True)
        df["amount"] = pd.to_numeric(cleaned, errors="coerce")
    return df


def normalize_region_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and title-case `region` (" north" -> "North").

    Idempotent: an already-normalised string title-cases to itself.
    """
    df = df.copy()
    df["region"] = df["region"].str.strip().str.title()
    return df


def dedupe_orders(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Drop rows that describe the same real-world order, keeping the
    first occurrence after an explicit, deterministic sort by `order_id`.

    The sort matters: `drop_duplicates(keep="first")` depends on row
    order, and pandas does not promise the input arrived in `order_id`
    order. Sorting first makes "first occurrence" mean the same thing on
    every run, not whatever order the source happened to hand rows over
    in.

    Order-dependent by design (exercise 6): comparing `region` before it
    has been normalised treats " north" and "north" as different values,
    so the resubmitted order in this lab's data is NOT recognised as a
    duplicate unless `normalize_region_strings` already ran.
    """
    df = df.sort_values("order_id", kind="stable").reset_index(drop=True)
    df = df.drop_duplicates(subset=config["dedupe_subset"], keep="first")
    return df.reset_index(drop=True)


def impute_missing_amount(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Fill a missing `amount` with the column's own mean.

    Idempotent in the sense this pipeline relies on: once every `amount`
    is filled, `fillna` on a column with no missing values is a no-op, so
    a second call changes nothing -- provided no later step reintroduces a
    missing value, which none of this pipeline's steps do.
    """
    df = df.copy()
    df["amount"] = df["amount"].fillna(df["amount"].mean())
    return df


def clip_amount_to_fixed_ceiling(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Clip `amount` to `config["amount_clip_max"]` -- a fixed number read
    from configuration, never recomputed from the data. This is the
    correct, idempotent version. Compare `clip_amount_to_recomputed_percentile`
    below, which is not.
    """
    df = df.copy()
    df["amount"] = df["amount"].clip(upper=config["amount_clip_max"])
    return df


def clip_amount_to_recomputed_percentile(df: pd.DataFrame) -> pd.DataFrame:
    """DELIBERATELY NON-IDEMPOTENT. Never called by `pipeline.run_pipeline`.

    Computes its own threshold -- the 99th percentile of `amount` -- from
    whatever frame is passed in, every time it runs. The first call clips
    the true outliers down to the raw data's 99th percentile. Because the
    ceiling is now lower than it was, the SECOND call sees a narrower
    column and computes a new, lower 99th percentile from it, clipping
    again. `pipeline(pipeline(df))` therefore does not equal `pipeline(df)`
    when this step is used -- kept here only so
    `test_pipeline.py::test_1` can run it, watch it fail, and then run the
    fixed version and watch it pass.
    """
    df = df.copy()
    ceiling = df["amount"].quantile(0.99)
    df["amount"] = df["amount"].clip(upper=ceiling)
    return df


def add_amount_zscore(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Attach a z-score computed against FIXED reference statistics in
    `config`, never against this frame's own (possibly already-clipped,
    already-deduplicated) mean and standard deviation. Recomputing the
    reference from the current frame would make this step non-idempotent
    for exactly the same reason the broken clip step is.
    """
    df = df.copy()
    mean = config["amount_reference_mean"]
    std = config["amount_reference_std"]
    df["amount_zscore"] = (df["amount"] - mean) / std
    return df


def sort_deterministic(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by `amount` with `order_id` as an explicit tie-break.

    Two rows in this lab's data collide exactly at the clip ceiling
    (900.0), so sorting by `amount` alone leaves their relative order
    unspecified -- a "stable" sort only preserves whatever order the ROWS
    ARRIVED in, which is not the same thing as a deterministic order
    across two independently built frames. Naming `order_id` as the
    tie-break makes the final row order a fact about the values, not
    about arrival order.
    """
    df = df.copy()
    return df.sort_values(["amount", "order_id"], kind="stable").reset_index(drop=True)
