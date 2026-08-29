"""Pipeline orchestration: contracts at both ends, a step log that
reconciles, two equivalent ways to compose the steps, content hashing,
a Parquet checkpoint, and a manifest tying an output back to the input
and configuration that produced it.

The declared, required order is:

    parse_currency_amount
    normalize_region_strings
    dedupe_orders
    impute_missing_amount
    clip_amount_to_fixed_ceiling
    add_amount_zscore
    sort_deterministic

`normalize_region_strings` before `dedupe_orders` is not arbitrary: this
lab's data contains a resubmitted order whose region string is only
recognisable as a duplicate of an earlier order once whitespace and casing
are normalised (see `data.py` and exercise 6). Swapping those two steps
changes which rows survive.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from steps import (
    add_amount_zscore,
    clip_amount_to_fixed_ceiling,
    dedupe_orders,
    impute_missing_amount,
    normalize_region_strings,
    parse_currency_amount,
    sort_deterministic,
)

# --------------------------------------------------------------------------
# Contracts at both ends. A step that cannot meet its contract fails loudly
# -- ContractError, naming the offending column -- rather than passing a
# subtly wrong frame further down the pipeline.
# --------------------------------------------------------------------------

REQUIRED_INPUT_COLUMNS: dict[str, str] = {
    "order_id": "int64",
    # pandas 3.0's default string-inference gives plain Python string
    # columns pandas' own dedicated "str" extension dtype, not "object" --
    # a real, version-specific fact confirmed in this lab's own run, and
    # recorded again in expected-output/FIELDS.md.
    "region": "str",
    "amount": "str",
    "priority": "Int64",
}


class ContractError(ValueError):
    """Raised when a frame fails an input or output contract."""


def check_input_contract(df: pd.DataFrame) -> None:
    for column, expected_dtype in REQUIRED_INPUT_COLUMNS.items():
        if column not in df.columns:
            raise ContractError(f"input contract violated: missing required column '{column}'")
        actual_dtype = str(df[column].dtype)
        if actual_dtype != expected_dtype:
            raise ContractError(
                f"input contract violated: column '{column}' has dtype "
                f"'{actual_dtype}', expected '{expected_dtype}'"
            )


def check_output_contract(df: pd.DataFrame, config: dict) -> None:
    if df["amount"].isna().any():
        raise ContractError("output contract violated: 'amount' still has missing values")
    if not pd.api.types.is_float_dtype(df["amount"]):
        raise ContractError(f"output contract violated: 'amount' has dtype '{df['amount'].dtype}', expected float")
    ceiling = config["amount_clip_max"]
    if df["amount"].max() > ceiling:
        raise ContractError(
            f"output contract violated: 'amount' has a value above the clip ceiling "
            f"{ceiling} (max seen: {df['amount'].max()})"
        )
    if "amount_zscore" not in df.columns:
        raise ContractError("output contract violated: missing required output column 'amount_zscore'")


# --------------------------------------------------------------------------
# The step log. Every step records rows in, rows out, and the resulting
# net change -- read after the fact, it is how you discover that a step is
# quietly discarding rows nobody meant to discard.
# --------------------------------------------------------------------------


def _run_logged(name: str, func, df: pd.DataFrame, log: list[dict]) -> pd.DataFrame:
    rows_in = len(df)
    result = func(df)
    rows_out = len(result)
    log.append({"step": name, "rows_in": rows_in, "rows_out": rows_out, "delta": rows_out - rows_in})
    return result


def apply_steps_logged(df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, list[dict]]:
    """The pipeline itself: the seven steps, in the declared order, with NO
    contract checks. This is deliberately the function idempotence is
    checked against (exercise 1), because the input contract below is a
    check on raw, freshly-ingested data specifically (`amount` still a
    string) -- feeding a pipeline's OWN output back into that same contract
    would fail for a reason that has nothing to do with idempotence
    (`amount` is now float64, exactly as the pipeline is supposed to leave
    it). Idempotence is a property of the TRANSFORMATION, checked by
    applying it twice in a row; the input contract is a property of
    external data arriving from outside the pipeline for the first time.
    Both matter; they are not the same check.
    """
    log: list[dict] = []
    out = df
    out = _run_logged("parse_currency_amount", parse_currency_amount, out, log)
    out = _run_logged("normalize_region_strings", normalize_region_strings, out, log)
    out = _run_logged("dedupe_orders", lambda d: dedupe_orders(d, config), out, log)
    out = _run_logged("impute_missing_amount", lambda d: impute_missing_amount(d, config), out, log)
    out = _run_logged("clip_amount_to_fixed_ceiling", lambda d: clip_amount_to_fixed_ceiling(d, config), out, log)
    out = _run_logged("add_amount_zscore", lambda d: add_amount_zscore(d, config), out, log)
    out = _run_logged("sort_deterministic", sort_deterministic, out, log)
    return out, log


def run_pipeline(raw_df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, list[dict]]:
    """The pipeline's real entry point for freshly-ingested data: checks
    the input contract, runs `apply_steps_logged`, checks the output
    contract, and returns the result and its step log.
    """
    check_input_contract(raw_df)
    df, log = apply_steps_logged(raw_df, config)
    check_output_contract(df, config)
    return df, log


def run_pipeline_swapped_order(raw_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """The SAME seven steps, with `dedupe_orders` run BEFORE
    `normalize_region_strings` instead of after -- the declared order,
    reversed. Used only to demonstrate order-dependence (exercise 6); never
    called from `run_pipeline`.
    """
    check_input_contract(raw_df)
    df = parse_currency_amount(raw_df)
    df = dedupe_orders(df, config)  # swapped: dedupe before normalising
    df = normalize_region_strings(df)
    df = impute_missing_amount(df, config)
    df = clip_amount_to_fixed_ceiling(df, config)
    df = add_amount_zscore(df, config)
    df = sort_deterministic(df)
    return df


def run_pipeline_via_pipe(raw_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """The same seven steps, in the same declared order, composed with
    `DataFrame.pipe` instead of sequential assignment. Must produce a
    frame identical to `run_pipeline`'s -- exercise 4 proves it.

    `.pipe()` chaining reads well top to bottom, but it comes at a real
    cost: there is nowhere to put a breakpoint or a `print(df.shape)`
    between two links in the chain without breaking the chain apart again,
    which `run_pipeline`'s sequential form gives you for free. That
    tradeoff -- readability against inspectability -- is real, not
    cosmetic, and this lab ran both forms to show it rather than asserting
    it.
    """
    check_input_contract(raw_df)
    df = (
        raw_df.pipe(parse_currency_amount)
        .pipe(normalize_region_strings)
        .pipe(dedupe_orders, config)
        .pipe(impute_missing_amount, config)
        .pipe(clip_amount_to_fixed_ceiling, config)
        .pipe(add_amount_zscore, config)
        .pipe(sort_deterministic)
    )
    check_output_contract(df, config)
    return df


# --------------------------------------------------------------------------
# Determinism: content hashing, a Parquet checkpoint, and the manifest that
# ties an output back to the input and configuration that produced it.
# --------------------------------------------------------------------------


def content_hash(df: pd.DataFrame) -> str:
    """A SHA-256 hex digest of the frame's exact CSV bytes.

    Deterministic for a given pandas/NumPy version and a given frame's
    values, column order and dtypes -- change any one value, one column's
    dtype, or the column or row order, and the digest changes. See this
    lab's `expected-output/FIELDS.md` for exactly what is and is not
    guaranteed to be identical on a different machine.
    """
    payload = df.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def config_hash(config: dict) -> str:
    """A SHA-256 hex digest of the config, serialised with sorted keys so
    the digest does not depend on the dict's insertion order.
    """
    payload = json.dumps(config, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def checkpoint_to_parquet(df: pd.DataFrame, path: Path) -> None:
    """Write a checkpoint. Parquet, not CSV, because Parquet preserves
    dtypes exactly -- including a nullable Int64 column's missing values
    -- where CSV round-trips everything through text and loses them
    (Day 121).
    """
    df.to_parquet(path, index=False)


def load_checkpoint(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def build_manifest(raw_df: pd.DataFrame, config: dict, step_log: list[dict], output_df: pd.DataFrame) -> dict:
    """The provenance record: which input, which configuration, which
    steps ran and what each one did to the row count, and what came out --
    everything needed, months later, to answer "which data produced this
    number?" without guessing.
    """
    return {
        "input_hash": content_hash(raw_df),
        "config_hash": config_hash(config),
        "steps": step_log,
        "output_hash": content_hash(output_df),
    }
