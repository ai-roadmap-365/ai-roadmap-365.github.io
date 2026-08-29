"""Exercise 6 -- .query() versus the equivalent mask.

Run: python3 06_query_equivalence.py

`.query()` takes a string of Python-like expression syntax and evaluates
it against the DataFrame's own columns as if they were local variables,
returning exactly the same rows a hand-built boolean mask would. Its real
advantage is readability once several conditions stack up -- no repeated
`df.` prefix, no risk of the `&`/`<` precedence trap from exercise 3,
because `.query()` parses comparison and boolean-combination the way plain
Python reads. A value from outside the frame is referenced with an `@`
prefix. The honest cost: `.query()` builds and parses a small string at
every call, which is measurably slower than a mask for a single simple
condition, and it turns what used to be a static-analysis-friendly Python
expression into a string your editor cannot type-check. For one condition
on a small frame, a mask is simpler; once you are combining four or five
conditions with named thresholds, `.query()` usually reads better.
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
        "customer": ["Ada", "Bo", "Cy", "Dee", "Eli", "Fay"],
        "amount": [42.50, 108.00, 15.75, 220.10, 60.00, 9.99],
        "region": ["east", "west", "east", "west", "east", "west"],
    }
)
print("orders:")
print(orders)

# A single condition: mask and query give identical rows.
threshold = 50
mask_single = orders[orders.amount > threshold]
query_single = orders.query("amount > @threshold")
print(f"\nmask (amount > {threshold}):  {mask_single.customer.tolist()}")
print(f"query (amount > @threshold): {query_single.customer.tolist()}")

check("mask and .query() select the identical rows for a single condition", mask_single.equals(query_single))
check(
    "the @threshold syntax correctly reaches the Python variable, not a column named 'threshold'",
    query_single.customer.tolist() == ["Bo", "Dee", "Eli"],
)

# A compound condition: the case .query() is genuinely nicer for, and the
# case exercise 3's precedence trap would bite on if written unparenthesised.
mask_compound = orders[(orders.amount > threshold) & (orders.region == "east")]
query_compound = orders.query("amount > @threshold and region == 'east'")
print(f"\nmask (amount > {threshold} & region == east):  {mask_compound.customer.tolist()}")
print(f"query (amount > @threshold and region == 'east'): {query_compound.customer.tolist()}")

check(
    "mask and .query() select the identical rows for a compound condition",
    mask_compound.equals(query_compound),
)
check("the compound condition selects exactly Eli", query_compound.customer.tolist() == ["Eli"])

# .query() parses `and`/`or` in the query string the way plain Python reads
# them, with none of exercise 3's `&`-binds-tighter surprise -- because the
# string is parsed by pandas' own expression engine, not by Python's own
# operator-precedence table applied to Series objects.
query_no_parens_needed = orders.query("amount > @threshold and region == 'east'")
check(
    "inside a .query() string, 'and' works directly -- no precedence trap, unlike exercise 3's `&`",
    query_no_parens_needed.equals(query_compound),
)

# A second @variable, referencing a Python list, combined with isin.
wanted_regions = ["west"]
query_isin = orders.query("region in @wanted_regions")
mask_isin = orders[orders.region.isin(wanted_regions)]
print(f"\nquery (region in @wanted_regions): {query_isin.customer.tolist()}")
check("`in @variable` inside .query() matches .isin() exactly", query_isin.equals(mask_isin))

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("06_query_equivalence.py: every assertion held.")
