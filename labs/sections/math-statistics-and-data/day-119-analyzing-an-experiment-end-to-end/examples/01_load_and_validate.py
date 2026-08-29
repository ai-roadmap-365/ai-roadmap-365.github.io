"""Exercise 1 -- load and validate.

Load both shipped experiments and confirm the columns, the row counts and
the group labels are exactly what the CSVs promise, with no missing values
in dataset A. This step says nothing about whether the experiment is
TRUSTWORTHY -- only that the file is well-formed. That question starts at
exercise 2.
"""

from pathlib import Path

from experiment import load_experiment

DATA_DIR = Path(__file__).parent.parent / "data"

rows_a = load_experiment(DATA_DIR / "exp_a.csv")
rows_b = load_experiment(DATA_DIR / "exp_b.csv")

print(f"exp_a.csv: {len(rows_a)} rows")
print(f"exp_b.csv: {len(rows_b)} rows")

assert len(rows_a) == 16000, f"expected 16000 rows in A, got {len(rows_a)}"
assert len(rows_b) == 20000, f"expected 20000 rows in B, got {len(rows_b)}"

groups_a = {r["group"] for r in rows_a}
groups_b = {r["group"] for r in rows_b}
print(f"groups in A: {sorted(groups_a)}")
print(f"groups in B: {sorted(groups_b)}")
assert groups_a == {"control", "treatment"}
assert groups_b == {"control", "treatment"}

# No missing values: every row loaded successfully means every required
# column had a non-empty value for every row (load_experiment raises
# ValueError otherwise), and every numeric column actually parsed.
for row in rows_a:
    for key in ("user_id", "converted"):
        assert isinstance(row[key], int)
    for key in ("latency_ms", "time_on_page_sec"):
        assert isinstance(row[key], float)

# A missing value should be rejected, not silently skipped. Prove it on a
# hand-built broken row set written to a temporary file.
import csv
import tempfile

with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as fh:
    writer = csv.writer(fh)
    writer.writerow(["user_id", "group", "segment", "converted", "latency_ms", "time_on_page_sec"])
    writer.writerow(["1", "control", "desktop", "", "200.0", "40.0"])  # missing converted
    broken_path = fh.name

raised = False
try:
    load_experiment(broken_path)
except ValueError as exc:
    raised = True
    print(f"load_experiment correctly rejected a missing value: {exc}")
finally:
    Path(broken_path).unlink()

assert raised, "load_experiment must reject a row with a missing value"

print("01_load_and_validate.py: every assertion held.")
