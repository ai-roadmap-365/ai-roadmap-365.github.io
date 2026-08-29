"""Day 122 starter -- nine exercises, one function each.

Each function below is a working skeleton: the setup is written for you, and
exactly one line is left for you to write, marked with the sentinel name
`_FILL_THIS_IN`. Replace that name with real code. Leaving it as-is raises a
clear NameError when the function runs, which `check_progress.py` catches
and reports -- it does not crash the whole script.

Read `../examples/` for the fully worked reference AFTER you have tried each
one yourself; that is where every one of these ideas is explained in
comments. Run your progress with:

    python3 check_progress.py

from inside this `starter/` directory (or `python3 starter/check_progress.py`
from the lab root).
"""

import numpy as np
import pandas as pd


def ex01_partition_invariant():
    """On a score column with two NaN entries, high = score > 50 and
    low = score <= 50 do not sum to the total. Return
    (len(high), len(low), len(scores), missing_count)."""
    scores = pd.DataFrame(
        {
            "name": ["Ada", "Bo", "Cy", "Dee", "Eli", "Fay", "Gio", "Hu"],
            "score": [72, 45, np.nan, 91, 50, np.nan, 88, 33],
        }
    )
    high = scores[scores.score > 50]
    low = scores[scores.score <= 50]
    missing_count = _FILL_THIS_IN  # count of rows where score is NaN -- use .isna().sum()
    return len(high), len(low), len(scores), missing_count


def ex02_and_or_raise():
    """mask1 and mask2 should raise ValueError; mask1 & mask2 should not.
    Return (raised_bool, and_mask_as_list)."""
    scores = pd.Series([72, 45, np.nan, 91], name="score")
    mask1 = scores > 60
    mask2 = scores < 90
    try:
        mask1 and mask2
        raised = False
    except ValueError:
        raised = True
    and_mask = _FILL_THIS_IN  # the elementwise-AND version, using & not `and`
    return raised, and_mask.tolist()


def ex03_precedence():
    """table.a > 1 & table.b < 2 does not mean what it looks like. Return
    the CORRECT mask (as a list) for 'a > 1 AND b < 2', properly
    parenthesised."""
    table = pd.DataFrame({"a": [0, 1, 2, 3, 4], "b": [5, 3, 1, 0, -1]})
    correct_mask = _FILL_THIS_IN  # (table.a > 1) & (table.b < 2), correctly parenthesised
    return correct_mask.tolist()


def ex04_mask_alignment():
    """Build a mask from scores sorted by score descending, then apply it
    to the ORIGINAL (unsorted) scores. Return the resulting index as a
    list -- it should come back in the ORIGINAL frame's row order."""
    scores = pd.DataFrame(
        {"name": ["Ada", "Bo", "Cy", "Dee"], "score": [72, 45, 91, 33]},
        index=[10, 11, 12, 13],
    )
    reordered = scores.sort_values("score", ascending=False)
    mask = reordered["score"] > 50
    result = _FILL_THIS_IN  # apply `mask` to the ORIGINAL `scores`, not `reordered`
    return result.index.tolist()


def ex05_str_contains_na():
    """On an object-dtype Series with a missing entry, .str.contains(...)
    without na= raises when used to filter. Fix it with na=False. Return
    the filtered list of names."""
    names = pd.Series(["Alice Smith", "bob jones", None, "dave"], dtype="object")
    mask = _FILL_THIS_IN  # names.str.contains("a", case=False, na=False)
    return names[mask].tolist()


def ex06_query_equivalence():
    """Select rows where amount > threshold using .query() with an
    @variable. Return the customer list."""
    orders = pd.DataFrame(
        {"customer": ["Ada", "Bo", "Cy"], "amount": [42.5, 108.0, 15.75]}
    )
    threshold = 50
    result = _FILL_THIS_IN  # orders.query("amount > @threshold")
    return result.customer.tolist()


def ex07_isin_empty():
    """isin() with an empty list of wanted values returns zero rows, not
    the whole frame. Return the row count."""
    staff = pd.DataFrame({"dept": ["eng", "sales", "hr"]})
    empty_wanted: list[str] = []
    result = _FILL_THIS_IN  # staff[staff.dept.isin(empty_wanted)]
    return len(result)


def ex08_nlargest_ties():
    """Three rows (A, B, C) all tie for the top score, but n=2 asks for
    only the top 2. nlargest(2, 'score', keep='all') should return ALL
    THREE tied rows -- more than n. Return the row count."""
    tied = pd.DataFrame({"name": ["A", "B", "C", "D"], "score": [80, 80, 80, 60]})
    result = _FILL_THIS_IN  # tied.nlargest(2, "score", keep="all")
    return len(result)


def ex09_drop_duplicates_subset():
    """Two rows share the same customer even though they ordered
    different items. Drop duplicates by customer alone, keeping the
    first occurrence. Return the surviving customer list, in order."""
    orders = pd.DataFrame(
        {"customer": ["Ada", "Bo", "Ada"], "item": ["pen", "cup", "mug"]}
    )
    result = _FILL_THIS_IN  # orders.drop_duplicates(subset=["customer"], keep="first")
    return result.customer.tolist()
