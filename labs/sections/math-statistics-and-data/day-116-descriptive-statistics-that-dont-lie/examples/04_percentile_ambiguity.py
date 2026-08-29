"""Exercise 4: the 75th percentile of one small array, under several of
NumPy's `method=` conventions. The assertion is that "the percentile" is
not a well-defined number: at least two conventions disagree."""

import dataset as D
import descriptive as F


def main() -> None:
    print(f"array   : {D.PERCENTILE_ARRAY}")
    print(f"target  : {D.PERCENTILE_TARGET}th percentile")

    results: dict[str, float] = {}
    for method in D.PERCENTILE_METHODS:
        value = F.percentile_under(D.PERCENTILE_ARRAY, D.PERCENTILE_TARGET, method)
        results[method] = value
        print(f"  method={method:<16} -> {value}")

    distinct = sorted(set(results.values()))
    print(f"distinct values across {len(D.PERCENTILE_METHODS)} conventions: {distinct}")
    assert len(distinct) >= 2, "expected at least two conventions to disagree"

    # The default ('linear') is the convention pandas' DataFrame.describe()
    # also uses -- worth naming explicitly, since it is the one most people
    # get without ever choosing it.
    print(f"default ('linear') result: {results['linear']}")
    assert results["linear"] == 8.25

    # 'lower' and 'higher' are not just close -- they land on two different
    # ACTUAL DATA POINTS, one full step apart.
    assert results["lower"] != results["higher"]
    print(f"'lower' picks an actual data point: {results['lower']}")
    print(f"'higher' picks a DIFFERENT actual data point: {results['higher']}")

    print("04_percentile_ambiguity.py: every assertion held.")


if __name__ == "__main__":
    main()
