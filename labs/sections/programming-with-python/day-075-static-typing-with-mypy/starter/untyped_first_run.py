"""Exercise 0 — what mypy says about code that carries no annotations at all.

This module is correct, ordinary, working Python. It has no type hints. Run
mypy over it twice and compare:

    python3 -m mypy starter/untyped_first_run.py
    python3 -m mypy --strict starter/untyped_first_run.py

The first run reports success. That is not praise. A function with no
annotations is a function mypy declines to check — it has nothing to compare
anything against, so it checks nothing and says so by saying nothing. This is
gradual typing working exactly as designed, and it is the single most
misleading result a newcomer can get: "mypy passes" on an unannotated
codebase means "mypy did not look".

The second run refuses to be quiet about it. Under --strict, an unannotated
function is itself an error, and so is calling one from typed code.

That contrast is the whole argument for turning strictness up: without it,
the checker's silence tells you nothing about your code and everything about
your annotations.
"""


def load_prices(rows):
    prices = {}
    for row in rows:
        name, value = row.split("=")
        prices[name] = float(value)
    return prices


def total(prices, names):
    return sum(prices[name] for name in names)


def main():
    prices = load_prices(["small=0.25", "large=15.0"])
    print(f"total: {total(prices, ['small', 'large'])}")


if __name__ == "__main__":
    main()
