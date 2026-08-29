"""Exercise 8 -- .nlargest()/.nsmallest() versus .sort_values().head().

Run: python3 08_nlargest_vs_sort_head.py

`df.nlargest(n, col)` and `df.sort_values(col, ascending=False).head(n)`
answer the same question -- the top n rows by one column -- and when there
are no ties at the cutoff they return byte-for-byte identical rows.
`.nlargest()` is the cheaper way to ask: it never sorts the whole frame,
it maintains a running set of the n largest values seen so far (an
O(n log k) approach for k rows kept, versus sort_values' full O(n log n)
sort of every row), which matters once the frame is large and n is small.
The behaviours diverge exactly at a tie sitting on the cutoff:
`.sort_values().head(n)` always returns exactly n rows, arbitrarily
keeping some tied rows and dropping others; `.nlargest(n, col, keep='all')`
can return MORE than n rows on purpose, returning every row tied at the
boundary rather than picking an arbitrary subset of them.
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


# --- No ties at the cutoff: both approaches agree exactly. -------------
scores = pd.DataFrame(
    {
        "name": ["Ada", "Bo", "Cy", "Dee", "Eli", "Fay", "Gio", "Hu"],
        "score": [72, 45, 20, 91, 50, 15, 88, 33],
    }
)
print("scores (no ties):")
print(scores)

top_nlargest = scores.nlargest(3, "score")
top_sorted_head = scores.sort_values("score", ascending=False).head(3)
print(f"\n.nlargest(3, 'score'):                       {top_nlargest.name.tolist()}")
print(f".sort_values('score', ascending=False).head(3): {top_sorted_head.name.tolist()}")

check("with no ties at the cutoff, nlargest and sort_values().head() give identical rows", top_nlargest.equals(top_sorted_head))
check("the top 3 by score are Dee (91), Gio (88), Ada (72)", top_nlargest.name.tolist() == ["Dee", "Gio", "Ada"])

bottom_nsmallest = scores.nsmallest(2, "score")
bottom_sorted_head = scores.sort_values("score", ascending=True).head(2)
check(
    "nsmallest and sort_values(ascending=True).head() also agree with no ties",
    bottom_nsmallest.equals(bottom_sorted_head),
)

# --- Ties sitting exactly on the cutoff: the two approaches diverge. ----
tied = pd.DataFrame({"name": ["A", "B", "C", "D", "E"], "score": [90, 90, 85, 80, 80]})
print("\nscores with a tie AT the cutoff (D and E both score 80):")
print(tied)

tied_nlargest_default = tied.nlargest(4, "score")
tied_sorted_head = tied.sort_values("score", ascending=False).head(4)
print(f"\n.nlargest(4, 'score') [keep='first' default]: {tied_nlargest_default.name.tolist()}")
print(f".sort_values(ascending=False).head(4):         {tied_sorted_head.name.tolist()}")

check(
    "with keep='first' (the default), nlargest(4) still matches sort_values().head(4) exactly -- both pick D over E",
    tied_nlargest_default.equals(tied_sorted_head),
)
check(".sort_values().head(n) always returns EXACTLY n rows, arbitrarily choosing among ties", len(tied_sorted_head) == 4)

tied_nlargest_all = tied.nlargest(4, "score", keep="all")
print(f"\n.nlargest(4, 'score', keep='all'):             {tied_nlargest_all.name.tolist()}")

check(
    "keep='all' returns MORE than n rows when a tie sits on the cutoff -- every tied row, not an arbitrary subset",
    len(tied_nlargest_all) == 5,
)
check(
    "keep='all' includes BOTH D and E, the tied pair sort_values().head() had to arbitrarily choose between",
    set(tied_nlargest_all.name.tolist()) == {"A", "B", "C", "D", "E"},
)
check(
    "sort_values().head(n) has no equivalent to keep='all' -- .head(4) can never return 5 rows",
    len(tied.sort_values("score", ascending=False).head(4)) == 4,
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("08_nlargest_vs_sort_head.py: every assertion held.")
