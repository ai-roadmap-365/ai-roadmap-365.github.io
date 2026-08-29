"""Exercise 9 -- .drop_duplicates() with subset and keep, and a note on
.filter(), which selects LABELS, not rows -- one of the library's more
confusingly named methods.

Run: python3 09_drop_duplicates_and_filter.py

"Duplicate" is not a fixed property of a row; it means whatever columns you
name in `subset`. The same table has 4 whole-row-unique rows, 4 rows unique
by (customer, item), and only 3 rows unique by customer alone -- three
different, all-correct answers to "how many duplicates", because they
answer three different questions. `keep='first'`/`'last'` decide which of a
duplicate group survives; the row count is identical either way, only WHICH
row differs.

`.filter()` looks like a row filter and is not one: it selects COLUMN (or
row, with axis=0) LABELS by exact name, a `like=` substring, or a `regex=`
pattern -- never by a condition on the data inside them. Passing it
row-shaped arguments does not raise; it silently matches nothing and
returns an empty selection on that axis, which is exactly the trap.
"""

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


orders = pd.DataFrame(
    {
        "customer": ["Ada", "Bo", "Ada", "Cy", "Bo", "Ada"],
        "item": ["pen", "cup", "pen", "pen", "cup", "mug"],
        "qty": [1, 2, 1, 5, 2, 3],
    }
)
print("orders:")
print(orders)

# Whole-row duplicates: rows 0 and 2 are byte-for-byte identical.
whole_row = orders.drop_duplicates()
print(f"\ndrop_duplicates() [whole row]: kept {len(whole_row)} of {len(orders)} rows -> index {whole_row.index.tolist()}")
check("dropping whole-row duplicates keeps exactly 4 rows (row 2 is identical to row 0)", len(whole_row) == 4)
check("the surviving rows are 0, 1, 3, 5", whole_row.index.tolist() == [0, 1, 3, 5])

# Duplicate by (customer, item): rows 0/2 collide (Ada, pen) and rows 1/4
# collide (Bo, cup) -- two collisions this time, not one.
subset_ci_first = orders.drop_duplicates(subset=["customer", "item"], keep="first")
subset_ci_last = orders.drop_duplicates(subset=["customer", "item"], keep="last")
print(f"\ndrop_duplicates(subset=['customer','item'], keep='first'): index {subset_ci_first.index.tolist()}")
print(f"drop_duplicates(subset=['customer','item'], keep='last'):  index {subset_ci_last.index.tolist()}")

check("by (customer, item), 4 rows survive either way -- the COUNT does not depend on keep", len(subset_ci_first) == 4 and len(subset_ci_last) == 4)
check("keep='first' keeps the FIRST occurrence of each (customer, item) pair: rows 0, 1, 3, 5", subset_ci_first.index.tolist() == [0, 1, 3, 5])
check("keep='last' keeps the LAST occurrence instead: rows 2, 3, 4, 5", subset_ci_last.index.tolist() == [2, 3, 4, 5])
check(
    "first and last keep DIFFERENT rows for the same duplicate group -- (Ada, pen) keeps qty=1 either way here by coincidence, but the surviving ROW differs",
    subset_ci_first.index.tolist() != subset_ci_last.index.tolist(),
)

# Duplicate by customer alone: a stricter subset finds MORE duplicates,
# because it ignores what the customer actually ordered.
subset_customer = orders.drop_duplicates(subset=["customer"], keep="first")
print(f"\ndrop_duplicates(subset=['customer'], keep='first'): index {subset_customer.index.tolist()}")
check("by customer alone, only 3 rows survive -- one per distinct customer", len(subset_customer) == 3)
check("'duplicate' is not fixed: the SAME table gives 4, 4, and 3 depending on subset chosen", len(whole_row) != len(subset_customer))

# --- .filter(): selects LABELS, never a condition on the data. ---------
print("\n--- .filter() is not a row filter ---")
by_items = orders.filter(items=["customer", "qty"])
print(f"orders.filter(items=['customer', 'qty']).columns: {by_items.columns.tolist()}")
check(".filter(items=...) selects COLUMNS by exact name, unrelated to any row condition", by_items.columns.tolist() == ["customer", "qty"])
check(".filter() does not drop any rows -- same row count as the original", len(by_items) == len(orders))

by_like = orders.filter(like="qty")
print(f"orders.filter(like='qty').columns:            {by_like.columns.tolist()}")
check(".filter(like=...) matches columns by substring, still label-based", by_like.columns.tolist() == ["qty"])

# The trap: passing row-shaped intentions to .filter() does not raise --
# it silently matches nothing on the columns axis, keeping every row.
looks_like_a_row_filter = orders.filter(items=[0, 1, 2])
print(f"orders.filter(items=[0, 1, 2]) -- looks like 'keep rows 0,1,2', is NOT: columns={looks_like_a_row_filter.columns.tolist()}, rows kept={len(looks_like_a_row_filter)}")
check(
    "filter(items=[0,1,2]) does NOT keep rows 0-2 -- it looks for COLUMNS named 0, 1, 2, finds none, and keeps every row with zero columns",
    looks_like_a_row_filter.shape == (len(orders), 0),
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("09_drop_duplicates_and_filter.py: every assertion held.")
