"""A tiny cleaning contract: name the post-conditions cleaning is supposed
to guarantee, and check them mechanically instead of trusting that the
cleaning steps above did what they were meant to do.

This is deliberately small -- three checks, one function -- because the
point of exercise 9 is the SHAPE of the idea (assert what you intend, fail
loudly when it does not hold), not a general-purpose validation framework.
Day 126 builds a real reusable pipeline around this idea; this is the
one-function version that proves the shape works.
"""

from __future__ import annotations

import pandas as pd


class ContractViolation(AssertionError):
    """Raised when cleaned data fails one of the contract's post-conditions."""


def assert_cleaning_contract(
    df: pd.DataFrame,
    *,
    key_columns: list[str],
    dtypes: dict[str, str],
    min_rows: int,
    max_rows: int,
) -> None:
    """Check three post-conditions a cleaning step is supposed to guarantee.

    Raises `ContractViolation` naming the FIRST check that fails, so a
    caller sees exactly what broke rather than a generic assertion error.
    """
    for column in key_columns:
        n_null = df[column].isna().sum()
        if n_null > 0:
            raise ContractViolation(
                f"key column {column!r} has {n_null} null value(s); "
                "key columns must be fully populated after cleaning"
            )

    for column, expected_dtype in dtypes.items():
        actual_dtype = str(df[column].dtype)
        if actual_dtype != expected_dtype:
            raise ContractViolation(
                f"column {column!r} has dtype {actual_dtype!r}, expected {expected_dtype!r}"
            )

    n_rows = len(df)
    if not (min_rows <= n_rows <= max_rows):
        raise ContractViolation(
            f"row count {n_rows} is outside the expected range [{min_rows}, {max_rows}]"
        )
