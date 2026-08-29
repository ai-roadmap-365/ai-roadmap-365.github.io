"""The three tables every exercise in this lab is built from.

Nothing here is randomised except the two performance-comparison tables,
which are seeded so a re-run always produces the same row counts (the
*timing* still varies machine to machine, which is why exercise 8 asserts a
ratio rather than a millisecond figure).

`orders` carries the day's opening failure on purpose: two rows have no
`region` at all, and two more have no `amount`. `sales` and `cat_sales` are
deliberately clean, so exercises 3, 4, 6 and 7 are not fighting missing data
while they teach a different point.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# `orders` -- exercises 1, 2 and 5. Twelve rows. Two have no region at all
# (order_id 5 and 8); two have no amount at all (order_id 2 and 11).
# --------------------------------------------------------------------------


def build_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "region": [
                "North",
                "South",
                "North",
                "East",
                None,
                "South",
                "North",
                None,
                "East",
                "South",
                "West",
                "East",
            ],
            "rep": [
                "Ann",
                "Bo",
                "Ann",
                "Cy",
                "Bo",
                "Ann",
                "Cy",
                "Bo",
                "Ann",
                "Cy",
                "Deb",
                "Deb",
            ],
            "amount": [
                100.0,
                np.nan,
                150.0,
                300.0,
                80.0,
                200.0,
                120.0,
                90.0,
                400.0,
                175.0,
                np.nan,
                500.0,
            ],
        }
    )


# --------------------------------------------------------------------------
# `sales` -- exercises 3, 4 and 6. Twelve rows, four regions of three rows
# each, no missing values anywhere.
# --------------------------------------------------------------------------


def build_sales() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112],
            "region": [
                "North",
                "North",
                "North",
                "South",
                "South",
                "South",
                "East",
                "East",
                "East",
                "West",
                "West",
                "West",
            ],
            "rep": ["Ann", "Bo", "Ann", "Bo", "Cy", "Bo", "Cy", "Ann", "Cy", "Ann", "Bo", "Cy"],
            "amount": [
                120.0,
                80.0,
                160.0,
                200.0,
                150.0,
                250.0,
                300.0,
                420.0,
                360.0,
                60.0,
                90.0,
                45.0,
            ],
        }
    )


# --------------------------------------------------------------------------
# `cat_sales` -- exercise 7. Same rows as `sales`, but `region` and `rep`
# are declared as categoricals with categories that are never observed in
# the data ("Central" and "Deb"), so grouping by both keys can either
# manufacture every combination or only the ones actually seen.
# --------------------------------------------------------------------------


def build_cat_sales() -> pd.DataFrame:
    df = build_sales()
    df["region"] = pd.Categorical(df["region"], categories=["North", "South", "East", "West", "Central"])
    df["rep"] = pd.Categorical(df["rep"], categories=["Ann", "Bo", "Cy", "Deb"])
    return df


# --------------------------------------------------------------------------
# `weighted` -- exercise 9. Three groups of unequal size and unequal
# weights, so a weighted mean genuinely differs from a plain mean.
# --------------------------------------------------------------------------


def build_weighted() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region": ["North", "North", "South", "South", "South", "East", "East"],
            "value": [10.0, 20.0, 5.0, 15.0, 25.0, 100.0, 50.0],
            "weight": [1.0, 3.0, 2.0, 2.0, 1.0, 1.0, 4.0],
        }
    )


# --------------------------------------------------------------------------
# `build_large` -- exercise 8. A frame big enough that the gap between a
# built-in aggregation and a Python-level `.apply` is not measurement noise.
# --------------------------------------------------------------------------


def build_large(n: int = 200_000, n_keys: int = 2000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "key": rng.integers(0, n_keys, size=n),
            "value": rng.normal(size=n),
        }
    )
