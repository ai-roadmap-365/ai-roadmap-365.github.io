"""Day 121 starter -- nine exercises, one function each.

Each function below is a working skeleton: the setup -- including writing
whatever small file the exercise needs into a temporary directory -- is
written for you, and exactly one line is left for you to write, marked
with the sentinel name `_FILL_THIS_IN`. Replace that name with real code.
Leaving it as-is raises a clear NameError when the function runs, which
`check_progress.py` catches and reports -- it does not crash the whole
script.

Every function cleans up the temporary file(s) it wrote before returning,
so running this file, complete or not, leaves nothing behind.

Read `../examples/` for the fully worked reference AFTER you have tried
each one yourself; that is where every one of these ideas is explained in
comments. Run your progress with:

    python3 check_progress.py

from inside this `starter/` directory (or `python3 starter/check_progress.py`
from the lab root).
"""

import tempfile
from pathlib import Path

import pandas as pd


def _scratch_file(name, content, encoding="utf-8"):
    """Write `content` into a fresh temp directory and return its path."""
    tmpdir = Path(tempfile.mkdtemp(prefix="d121-starter-"))
    path = tmpdir / name
    path.write_text(content, encoding=encoding)
    return path


def _cleanup(path):
    path.unlink()
    path.parent.rmdir()


def ex01_the_namibia_trap():
    """Read a country-code CSV containing "NA" for Namibia. Return
    (default_code, kept_code) -- the value read by default, and the value
    read with keep_default_na=False."""
    path = _scratch_file("countries.csv", "code,country\nNA,Namibia\nUS,United States\n")
    try:
        default_df = pd.read_csv(path)
        kept_df = _FILL_THIS_IN  # pd.read_csv(path, keep_default_na=False)
        return default_df.loc[0, "code"], kept_df.loc[0, "code"]
    finally:
        _cleanup(path)


def ex02_leading_zeros():
    """Read an id column of "00123" two ways. Return (default_id, typed_id)."""
    path = _scratch_file("customers.csv", "id,name\n00123,Alice\n")
    try:
        default_df = pd.read_csv(path)
        typed_df = pd.read_csv(path, dtype=_FILL_THIS_IN)  # {'id': 'str'}
        return int(default_df.loc[0, "id"]), typed_df.loc[0, "id"]
    finally:
        _cleanup(path)


def ex03_precision_loss():
    """Read an integer above 2**53 and round-trip it through float64.
    Return (as_int64, as_float64) as plain Python ints."""
    big_id = 2**53 + 1
    path = _scratch_file("orders.csv", f"order_id\n{big_id}\n")
    try:
        df = pd.read_csv(path)
        as_int64 = int(df.loc[0, "order_id"])
        promoted = df.astype({"order_id": _FILL_THIS_IN})  # 'float64'
        as_float64 = int(promoted.loc[0, "order_id"])
        return as_int64, as_float64
    finally:
        _cleanup(path)


def ex04_dates():
    """Read a date column with and without parse_dates. Return
    (unparsed_dtype, parsed_dtype) as strings."""
    path = _scratch_file("events.csv", "event,date\nfirst,2024-01-05\n")
    try:
        unparsed = pd.read_csv(path)
        parsed = pd.read_csv(path, parse_dates=_FILL_THIS_IN)  # ['date']
        return str(unparsed["date"].dtype), str(parsed["date"].dtype)
    finally:
        _cleanup(path)


def ex05_encoding():
    """Write a latin-1 file and read it back with the WRONG encoding.
    Return the name of the exception class raised (a string), or None if
    nothing was raised."""
    path = _scratch_file("name.csv", "name\nJosé\n", encoding="latin-1")
    try:
        try:
            pd.read_csv(path, encoding=_FILL_THIS_IN)  # 'utf-8'
            return None
        except UnicodeDecodeError as exc:
            return type(exc).__name__
    finally:
        _cleanup(path)


def ex06_chunking():
    """Sum a column two ways: all at once, and via chunksize=3. Return
    (whole_sum, chunked_sum) as plain ints."""
    path = _scratch_file("readings.csv", "value\n1\n2\n3\n4\n5\n6\n7\n")
    try:
        whole_sum = int(pd.read_csv(path)["value"].sum())
        chunked_sum = 0
        for chunk in pd.read_csv(path, chunksize=_FILL_THIS_IN):  # 3
            chunked_sum += int(chunk["value"].sum())
        return whole_sum, chunked_sum
    finally:
        _cleanup(path)


def ex07_csv_vs_parquet():
    """Round-trip a nullable-Int64 column through CSV and through Parquet.
    Return (csv_dtype, parquet_dtype) as strings."""
    tmpdir = Path(tempfile.mkdtemp(prefix="d121-starter-"))
    df = pd.DataFrame({"order_id": pd.array([1001, 1002, pd.NA], dtype="Int64")})
    csv_path = tmpdir / "orders.csv"
    pq_path = tmpdir / "orders.parquet"
    try:
        df.to_csv(csv_path, index=False)
        df.to_parquet(pq_path)
        csv_dtype = str(pd.read_csv(csv_path)["order_id"].dtype)
        parquet_dtype = str(_FILL_THIS_IN["order_id"].dtype)  # pd.read_parquet(pq_path)
        return csv_dtype, parquet_dtype
    finally:
        csv_path.unlink()
        pq_path.unlink()
        tmpdir.rmdir()


def ex08_inspection_battery():
    """On a frame with a known missing value and a known most-common
    region, return (na_count_for_region, top_region) using .isna().sum()
    and .value_counts()."""
    df = pd.DataFrame({"region": ["north", "north", "south", None, "north"]})
    na_count = df["region"].isna().sum()
    top_region = _FILL_THIS_IN  # df["region"].value_counts().index[0]
    return int(na_count), top_region


def ex09_category_memory():
    """Convert a string column to category and return (str_bytes,
    category_bytes) from memory_usage(deep=True), as plain ints."""
    df = pd.DataFrame({"region": ["north", "south"] * 500})
    str_bytes = int(df["region"].memory_usage(deep=True))
    cat_bytes = int(df["region"].astype(_FILL_THIS_IN).memory_usage(deep=True))  # "category"
    return str_bytes, cat_bytes
