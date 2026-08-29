"""Exercise 7 -- the day's headline claim: CSV loses dtypes, Parquet keeps them.

Run: python3 07_csv_vs_parquet.py

CSV is plain text. Every value that goes into a CSV file becomes a
character string on disk, and every value that comes back out is
RE-INFERRED from scratch by read_csv()'s type-inference engine -- the same
engine exercises 1-4 spent proving is not infallible. Parquet is a typed,
columnar binary format: the dtype of every column is written into the file
itself, so reading it back is a lookup, not a guess. This exercise writes
the same DataFrame -- including a nullable Int64 column with a genuine
missing value -- through both formats and compares the dtypes side by side.
"""

import tempfile
from pathlib import Path

import pandas as pd

checks = 0
failures = 0


def check(label, condition):
    global checks, failures
    checks += 1
    if condition:
        print(f"  ok: {label}")
    else:
        print(f"  FAIL: {label}")
        failures += 1


original = pd.DataFrame(
    {
        "order_id": pd.array([1001, 1002, pd.NA], dtype="Int64"),
        "price": pd.array([19.99, 44.50, 7.25], dtype="float64"),
        "in_stock": pd.array([True, False, True], dtype="bool"),
        "category": pd.array(["books", "tools", "books"], dtype="str"),
    }
)
print("original dtypes:")
print(original.dtypes)

tmpdir = Path(tempfile.mkdtemp(prefix="d121-ex07-"))
try:
    csv_path = tmpdir / "orders.csv"
    original.to_csv(csv_path, index=False)
    round_tripped_csv = pd.read_csv(csv_path)
    print("\ndtypes after a CSV round-trip:")
    print(round_tripped_csv.dtypes)
    print(round_tripped_csv)

    pq_path = tmpdir / "orders.parquet"
    original.to_parquet(pq_path)
    round_tripped_parquet = pd.read_parquet(pq_path)
    print("\ndtypes after a Parquet round-trip:")
    print(round_tripped_parquet.dtypes)
    print(round_tripped_parquet)

    csv_changed = [
        col for col in original.columns
        if str(original[col].dtype) != str(round_tripped_csv[col].dtype)
    ]
    parquet_changed = [
        col for col in original.columns
        if str(original[col].dtype) != str(round_tripped_parquet[col].dtype)
    ]
    print("\ncolumns whose dtype changed via CSV:    ", csv_changed)
    print("columns whose dtype changed via Parquet:", parquet_changed)

    check(
        "the CSV round-trip changes at least one column's dtype",
        len(csv_changed) >= 1,
    )
    check(
        "specifically, the nullable Int64 order_id column is not what it started as after CSV",
        str(round_tripped_csv["order_id"].dtype) != "Int64",
    )
    check(
        "the missing order_id survives the CSV round-trip only as a float NaN, not pd.NA",
        round_tripped_csv["order_id"].isna().sum() == 1
        and str(round_tripped_csv["order_id"].dtype) == "float64",
    )
    check(
        "the Parquet round-trip preserves every column's dtype EXACTLY",
        parquet_changed == [],
    )
    check(
        "the Parquet round-trip keeps order_id as the nullable Int64 dtype, missing value and all",
        str(round_tripped_parquet["order_id"].dtype) == "Int64"
        and round_tripped_parquet["order_id"].isna().sum() == 1,
    )
    check(
        "the Parquet round-trip's actual values equal the originals exactly, not just the dtypes",
        round_tripped_parquet.equals(original),
    )
finally:
    for f in tmpdir.iterdir():
        f.unlink()
    tmpdir.rmdir()

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("07_csv_vs_parquet.py: every assertion held.")
