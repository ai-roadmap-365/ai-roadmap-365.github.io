"""The tables every exercise in this lab is built from.

Nothing here is randomised or loaded from a file -- every table is a small
literal so a reader can check every asserted number by eye against the
source.

`left_dup` / `right_dup` -- exercises 1 and 2. Each has a duplicated key,
so a merge between them is many-to-many by construction.

`left_keys` / `right_keys` -- exercises 3 and 5. Each key is unique on
both sides, so the four join types differ only in which rows survive, not
in how many copies of a row a duplicated key would produce.

`int_keyed` / `str_keyed` -- exercise 4. Same digits, different dtypes.

`price_left` / `price_right` -- exercise 6. Both have a `price` column,
so a plain merge collides on the name.

`wide` -- exercise 8's melt/pivot round trip.

`dup_index_col` -- exercise 9's pivot-versus-pivot_table contrast.
"""

from __future__ import annotations

import pandas as pd

# --------------------------------------------------------------------------
# `left_dup` / `right_dup` -- exercises 1 and 2. Duplicated keys on both
# sides, so an inner merge is a per-key Cartesian product.
#
# Key 'A': 3 rows on the left, 2 on the right -> 3*2 = 6 matched rows.
# Key 'B': 2 rows on the left, 4 on the right -> 2*4 = 8 matched rows.
# Key 'C': 1 row on the left, 0 on the right  -> 0 matched rows.
# Key 'D': 0 rows on the left, 1 on the right -> 0 matched rows.
# Total inner rows: 6 + 8 = 14.
# --------------------------------------------------------------------------


def build_left_dup() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cust_id": ["A", "A", "A", "B", "B", "C"],
            "order_id": [1, 2, 3, 4, 5, 6],
            "amount": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
        }
    )


def build_right_dup() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cust_id": ["A", "A", "B", "B", "B", "B", "D"],
            "contact_id": [101, 102, 103, 104, 105, 106, 107],
            "channel": ["email", "phone", "email", "phone", "sms", "email", "phone"],
        }
    )


# --------------------------------------------------------------------------
# `left_keys` / `right_keys` -- exercises 3 and 5. Every key is unique on
# both sides: left has A, B, C, D; right has B, C, D, E. Overlap is
# exactly {B, C, D}.
# --------------------------------------------------------------------------


def build_left_keys() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cust_id": ["A", "B", "C", "D"],
            "region": ["North", "South", "East", "West"],
        }
    )


def build_right_keys() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cust_id": ["B", "C", "D", "E"],
            "plan": ["basic", "pro", "pro", "basic"],
        }
    )


# --------------------------------------------------------------------------
# `int_keyed` / `str_keyed` -- exercise 4. Same three ids, one column
# int64, the other the same digits stored as a pandas Categorical -- the
# read-one-way, read-another-way trap from Day 121 arriving as a join.
#
# A plain str/object key against an int64 key is caught by pandas 3.0.5's
# own dtype check and RAISES a ValueError -- verified separately below and
# documented as an honest correction to the classic "silent zero rows"
# story. A CATEGORICAL key of the same digits (exactly what you get from
# reading a column with dtype="category", a common CSV-loading choice)
# slips past that check and reproduces the classic silent failure: an
# inner join that matches nothing and raises nothing.
# --------------------------------------------------------------------------


def build_int_keyed() -> pd.DataFrame:
    return pd.DataFrame({"id": pd.array([1001, 1002, 1003], dtype="int64"), "name": ["Ann", "Bo", "Cy"]})


def build_str_keyed() -> pd.DataFrame:
    return pd.DataFrame({"id": pd.Categorical(["1001", "1002", "1003"]), "score": [88, 91, 77]})


# --------------------------------------------------------------------------
# `price_left` / `price_right` -- exercise 6. Both carry a `price` column,
# which collides under a plain merge and needs `suffixes=`.
# --------------------------------------------------------------------------


def build_price_left() -> pd.DataFrame:
    return pd.DataFrame({"sku": ["X1", "X2", "X3"], "price": [9.99, 14.50, 3.25]})


def build_price_right() -> pd.DataFrame:
    return pd.DataFrame({"sku": ["X1", "X2", "X3"], "price": [10.99, 13.00, 3.75]})


# --------------------------------------------------------------------------
# `wide` -- exercise 8. Three measurement columns beside an id column, the
# shape aggregation and plotting want turned into long form and back.
# --------------------------------------------------------------------------


def build_wide() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "student_id": [1, 2, 3],
            "math": [88, 72, 95],
            "reading": [91, 85, 79],
            "science": [76, 90, 83],
        }
    )


# --------------------------------------------------------------------------
# `dup_index_col` -- exercise 9. Two rows share the same (student, subject)
# pair with different scores, so a plain `pivot` cannot place them both --
# `pivot_table` averages them instead.
# --------------------------------------------------------------------------


def build_dup_index_col() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "student": ["Ann", "Ann", "Bo", "Ann"],
            "subject": ["math", "reading", "math", "math"],
            "score": [80.0, 91.0, 70.0, 90.0],
        }
    )
