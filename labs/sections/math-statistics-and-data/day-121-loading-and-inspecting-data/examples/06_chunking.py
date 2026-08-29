"""Exercise 6 -- reading in chunks: a file larger than memory, one piece at a time.

Run: python3 06_chunking.py

`chunksize` turns read_csv() into an iterator of DataFrames instead of one
big DataFrame, so you can process a file far larger than available memory
by never holding more than one chunk of it at once. The claim this exercise
proves: an aggregate computed chunk-by-chunk must equal the whole-file
answer EXACTLY -- chunking changes how the data arrives, never what it
adds up to.
"""

import tempfile
from pathlib import Path

import numpy as np
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


tmpdir = Path(tempfile.mkdtemp(prefix="d121-ex06-"))
try:
    csv_path = tmpdir / "readings.csv"
    rng = np.random.default_rng(42)
    n_rows = 50_000
    values = rng.integers(1, 1000, size=n_rows)
    pd.DataFrame({"value": values}).to_csv(csv_path, index=False)
    print(f"wrote {n_rows} rows to a temporary CSV")

    whole_sum = int(pd.read_csv(csv_path)["value"].sum())
    print("whole-file sum:", whole_sum)

    chunk_sum = 0
    n_chunks = 0
    n_rows_seen = 0
    for chunk in pd.read_csv(csv_path, chunksize=1_000):
        chunk_sum += int(chunk["value"].sum())
        n_rows_seen += len(chunk)
        n_chunks += 1
    print(f"chunked sum ({n_chunks} chunks of up to 1,000 rows): {chunk_sum}")

    check("chunking visits every row exactly once", n_rows_seen == n_rows)
    check("chunking produces the expected number of chunks", n_chunks == 50)
    check(
        "the chunk-by-chunk sum equals the whole-file sum exactly",
        chunk_sum == whole_sum,
    )

    # A second aggregate, to show it's not a coincidence of sum() specifically:
    # the row count is also exact when accumulated chunk by chunk.
    counted = 0
    for chunk in pd.read_csv(csv_path, chunksize=777):  # a chunk size that does not divide evenly
        counted += len(chunk)
    check(
        "row count accumulated over odd-sized chunks (777) still matches exactly",
        counted == n_rows,
    )
finally:
    for f in tmpdir.iterdir():
        f.unlink()
    tmpdir.rmdir()

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("06_chunking.py: every assertion held.")
