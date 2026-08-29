"""The tables every exercise in this lab is built from.

Nothing here downloads anything. Two tables use a seeded NumPy generator so
a re-run always produces the same rows (`build_income_spending`,
`build_large_income_spending`); everything else is a small hand-written
literal table, chosen so every exercise's expected values can be checked
exactly rather than approximately.

`build_income_spending` carries the day's opening failure on purpose: some
rows have no recorded income at all, and `spending` is genuinely, linearly
related to `income` plus noise -- so a real correlation exists to distort.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Exercises 1 and 2 -- mean imputation and fillna(0), and the correlation
# claim in exercise 1. Seeded so the numbers are reproducible exactly.
# --------------------------------------------------------------------------


def build_income_spending(seed: int = 20250825, n: int = 40, n_missing: int = 10) -> pd.DataFrame:
    """`income` and `spending`, genuinely correlated, with `income` missing
    at `n_missing` rows chosen completely at random (MCAR)."""
    rng = np.random.default_rng(seed)
    income = rng.normal(52_000, 11_000, n)
    spending = 0.42 * income + rng.normal(0, 3_500, n)
    df = pd.DataFrame(
        {
            "customer_id": np.arange(1001, 1001 + n),
            "income": income,
            "spending": spending,
        }
    )
    missing_idx = rng.choice(n, size=n_missing, replace=False)
    df.loc[missing_idx, "income"] = np.nan
    return df


def build_temperature_readings() -> pd.DataFrame:
    """A sensor log where a missing reading and a genuine 0.0C reading must
    stay distinguishable -- exercise 2's fillna(0) trap."""
    return pd.DataFrame(
        {
            "station": ["A", "A", "A", "B", "B", "B", "C", "C", "C", "C"],
            "reading_c": [18.2, np.nan, 17.5, 22.0, 21.4, np.nan, -3.0, np.nan, -1.5, 0.0],
        }
    )


# --------------------------------------------------------------------------
# Exercise 3 -- dropna with how, thresh, subset. Eight rows, three columns,
# a deliberately mixed missingness pattern.
# --------------------------------------------------------------------------


def build_dropna_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "email": ["a@x.com", None, "c@x.com", None, "e@x.com", None, "g@x.com", None],
            "phone": ["555-1", "555-2", None, None, "555-5", None, None, None],
            "signup_date": [
                "2026-01-02",
                "2026-01-03",
                "2026-01-04",
                None,
                "2026-01-06",
                None,
                "2026-01-08",
                None,
            ],
        }
    )


# --------------------------------------------------------------------------
# Exercise 4 -- ffill on unsorted data. A daily reading with two gaps,
# written here in TRUE chronological order; the exercise shuffles it.
# --------------------------------------------------------------------------


def build_sensor_timeseries() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "day": [1, 2, 3, 4, 5, 6, 7, 8],
            "reading": [10.0, np.nan, np.nan, 13.0, 14.0, np.nan, 16.0, 17.0],
        }
    )


def shuffle_rows(df: pd.DataFrame, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(df))
    return df.iloc[order].reset_index(drop=True)


# --------------------------------------------------------------------------
# Exercise 5 -- the missing indicator. Reuses build_temperature_readings.
# --------------------------------------------------------------------------

# (no separate builder needed -- exercise 5 works directly on
# build_temperature_readings())


# --------------------------------------------------------------------------
# Exercise 6 -- to_numeric(errors="coerce"). A column that is mostly clean
# numbers with a KNOWN number of unparseable strings planted in it.
# --------------------------------------------------------------------------


def build_coerce_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "quantity_raw": ["12", "7", "N/A", "3", "unknown", "9", "5", "--", "20", "4"],
        }
    )


# --------------------------------------------------------------------------
# Exercise 7 -- string normalisation. One true country, four spellings.
# --------------------------------------------------------------------------


def build_country_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": list(range(1, 13)),
            "country_raw": [
                "USA",
                "U.S.A.",
                " usa ",
                "Usa",
                "USA",
                "U.S.A.",
                "Canada",
                "canada ",
                " Canada",
                "USA",
                "CANADA",
                "U.S.A.",
            ],
            "amount": [
                120.0,
                85.0,
                60.0,
                200.0,
                75.0,
                150.0,
                40.0,
                90.0,
                30.0,
                110.0,
                55.0,
                65.0,
            ],
        }
    )


# --------------------------------------------------------------------------
# Exercise 8 -- duplicates. Row 5 is an exact duplicate of row 1. Row 6
# shares (customer_id, item) with row 2 but has a different price -- a
# subset duplicate that is not an exact duplicate.
# --------------------------------------------------------------------------


def build_duplicates_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 1, 2, 5],
            "item": ["pen", "mug", "pen", "bag", "pen", "mug", "hat"],
            "price": [1.5, 8.0, 1.5, 20.0, 1.5, 8.0, 12.0],
            "order_ts": [
                "2026-01-01T09:00",
                "2026-01-01T09:05",
                "2026-01-01T09:10",
                "2026-01-01T09:15",
                "2026-01-01T09:00",
                "2026-01-02T14:30",
                "2026-01-01T09:20",
            ],
        }
    )


# --------------------------------------------------------------------------
# Exercise 9 -- the cleaning contract. A frame that passes, and one that
# is built to fail each post-condition in turn.
# --------------------------------------------------------------------------


def build_clean_customers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 5],
            "country": ["USA", "Canada", "USA", "Canada", "USA"],
            "income": [52_000.0, 61_000.0, 48_500.0, 73_200.0, 55_000.0],
        }
    )


def build_contract_violating_customers() -> pd.DataFrame:
    """Violates the contract three ways: a null in a key column, the wrong
    dtype on `income` (object, because one entry is a stray string), and a
    row count far outside the expected range."""
    return pd.DataFrame(
        {
            "customer_id": [1, 2, None],
            "country": ["USA", "Canada", "USA"],
            "income": [52_000.0, "unknown", 48_500.0],
        }
    )
