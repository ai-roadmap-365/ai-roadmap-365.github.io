"""Day 120 starter -- nine exercises, one function each.

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


def ex01_build_three_ways():
    """Build a Series from a dict {"a": 10, "b": 20, "c": 30}, and read off
    its index as a plain Python list. Return (series, index_list)."""
    s = pd.Series({"a": 10, "b": 20, "c": 30})
    index_list = _FILL_THIS_IN  # convert s.index to a plain list
    return s, index_list


def ex02_alignment():
    """Add x (index a, b, c) to y (index b, c, d) and report which labels
    come back as NaN. Return the set of NaN labels."""
    x = pd.Series([1, 2, 3], index=["a", "b", "c"])
    y = pd.Series([10, 20, 30], index=["b", "c", "d"])
    z = x + y
    nan_labels = _FILL_THIS_IN  # set of index labels where z is NaN -- use z.isna()
    return nan_labels


def ex03_dtype_promotion():
    """Reindex a clean int64 Series onto a 4th label that was never there,
    and report the resulting dtype as a string."""
    ids = pd.Series([1001, 1002, 1003], dtype="int64")
    reindexed = ids.reindex([0, 1, 2, 3])
    dtype_name = _FILL_THIS_IN  # str(reindexed.dtype)
    return dtype_name


def ex04_copy_on_write():
    """Show that chained assignment does nothing, and .loc does. Return the
    'b' column's values (before, after_chained, after_loc) as three lists."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]})
    before = df["b"].tolist()
    df[df["a"] > 1]["b"] = 0  # chained assignment -- do not "fix" this line
    after_chained = df["b"].tolist()
    _FILL_THIS_IN  # write the ONE .loc statement that actually changes df["b"] where a > 1, to 0
    after_loc = df["b"].tolist()
    return before, after_chained, after_loc


def ex05_loc_vs_iloc():
    """On a frame indexed a..e, return (len(.loc['b':'d']), len(.iloc[1:3]))."""
    df = pd.DataFrame({"val": [10, 20, 30, 40, 50]}, index=["a", "b", "c", "d", "e"])
    by_label = df.loc["b":"d"]
    by_position = _FILL_THIS_IN  # the .iloc slice that STOPS BEFORE position 3
    return len(by_label), len(by_position)


def ex06_nan_semantics():
    """Return whether float('nan') == float('nan') (should be False)."""
    result = _FILL_THIS_IN  # the actual comparison, not a hard-coded boolean
    return result


def ex07_vectorized_vs_apply():
    """Compute price * 1.08 vectorised on a Series -- no .apply, no lambda."""
    prices = pd.Series([100.0, 200.0, 300.0])
    result = _FILL_THIS_IN  # one vectorised expression, no .apply
    return result.tolist()


def ex08_string_dtype():
    """Return the dtype of pd.Series(['a', 'b']) as a string."""
    s = pd.Series(["a", "b"])
    dtype_name = _FILL_THIS_IN  # str(s.dtype)
    return dtype_name


def ex09_describe():
    """Return the count, mean, min and max of [2, 4, 4, 4, 5, 5, 7, 9] using
    .describe(), as a 4-tuple of floats."""
    values = [2, 4, 4, 4, 5, 5, 7, 9]
    desc = pd.Series(values).describe()
    result = _FILL_THIS_IN  # (desc["count"], desc["mean"], desc["min"], desc["max"])
    return result
