"""Boolean masking: the idea that replaces `if` inside a loop.

Run from inside examples/:

    ../.venv/bin/python3 05_masks_and_selection.py

The claim under test: a comparison on an array is an array, one True or False
per element, and that array can be used to count, to select, to choose between
two values and to assign. Almost every filtering loop you would have written
becomes one line.

And the one that trips everyone: combining two masks needs `&` and `|`, not
`and` and `or`, and the reason is a ValueError you can read.
"""

import numpy as np

import dataset
from vectorize import count_above, mask_between, select


def main() -> None:
    print("05_masks_and_selection.py")
    print("=" * 70)

    readings = dataset.small_readings()

    # -- 1. The data, small enough to check by eye ----------------------------
    print()
    print("1. Twenty readings from the seeded generator")
    print("-" * 70)
    print(f"  {readings.tolist()}")
    print(f"  dtype {readings.dtype}   shape {readings.shape}")
    print()
    print("  Written out in dataset.py as SMALL_READINGS_EXPECTED so you can")
    print("  check any answer below without running anything.")
    assert readings.tolist() == dataset.SMALL_READINGS_EXPECTED

    # -- 2. A comparison returns an array -------------------------------------
    print()
    print("2. `readings > 50` is not a yes or a no")
    print("-" * 70)
    mask = readings > 50
    print(f"  readings > 50  ->  {mask}")
    print(f"  dtype {mask.dtype}   shape {mask.shape}   size {mask.size}")
    print()
    print("  Twenty answers, one per element. That single fact is what every")
    print("  other line in this script is built on.")
    assert mask.dtype == np.bool_
    assert mask.shape == (dataset.N_SMALL,)
    assert mask.tolist()[:4] == [True, True, False, True]

    # -- 3. Counting, without a counter ---------------------------------------
    print()
    print("3. Counting")
    print("-" * 70)
    how_many = count_above(readings, 50)
    print(f"  mask.sum()          {int(mask.sum())}")
    print(f"  count_above(a, 50)  {how_many}")
    print("  True is 1 and False is 0 when summed, so a count is a sum. The")
    print("  loop with a `total += 1` inside it does not need writing again.")
    print()
    print(f"  mask.any()   {bool(mask.any())}    is anything above 50?")
    print(f"  mask.all()   {bool(mask.all())}   is EVERYTHING above 50?")
    print(f"  mask.mean()  {float(mask.mean())}    what fraction? (a sum divided by n)")
    assert how_many == 9
    assert bool(mask.any()) is True
    assert bool(mask.all()) is False
    assert float(mask.mean()) == 0.45

    # -- 4. Selecting ---------------------------------------------------------
    print()
    print("4. Selecting the elements the mask marks")
    print("-" * 70)
    chosen = select(readings, mask)
    print(f"  readings[readings > 50]  ->  {chosen.tolist()}")
    print(f"  shape {chosen.shape}, which is the count from section 3")
    print()
    print(f"  np.nonzero(mask)[0]      ->  {np.nonzero(mask)[0].tolist()}")
    print("  ...if it is the POSITIONS you want rather than the values.")
    assert chosen.tolist() == [70, 83, 69, 65, 75, 73, 97, 64, 82]
    assert chosen.shape == (9,)
    assert np.nonzero(mask)[0].tolist() == [0, 1, 3, 8, 11, 13, 16, 17, 19]

    # -- 5. Combining masks, and the error everybody meets --------------------
    print()
    print("5. Two conditions at once")
    print("-" * 70)
    between = mask_between(readings, 30, 70)
    print(f"  (readings > 30) & (readings < 70)")
    print(f"  count {int(between.sum())}   values {readings[between].tolist()}")
    outer = (readings < 10) | (readings > 90)
    print(f"  (readings < 10) | (readings > 90)")
    print(f"  count {int(outer.sum())}   values {readings[outer].tolist()}")
    print(f"  ~between  (the negation)  count {int((~between).sum())}")
    assert int(between.sum()) == 7
    assert readings[between].tolist() == [34, 69, 65, 37, 37, 41, 64]
    assert int(outer.sum()) == 1
    assert readings[outer].tolist() == [97]
    assert int((~between).sum()) == 13

    print()
    print("  Now the same thing with `and`:")
    try:
        (readings > 30) and (readings < 70)
    except ValueError as exc:
        print(f"    ValueError: {exc}")
        message = str(exc)
    else:  # pragma: no cover - documents an outcome that would falsify the claim
        raise AssertionError("`and` on two arrays must raise")
    assert "truth value of an array" in message
    print()
    print("  `and` is not an operator NumPy can define. It is a control-flow")
    print("  keyword: Python asks the left operand 'are you true?' and an")
    print("  array of twenty answers cannot say. `&` IS an operator, so NumPy")
    print("  defines it to mean elementwise-and, which is what you wanted.")
    print()
    print("  The same refusal, more directly:")
    try:
        bool(readings > 30)
    except ValueError as exc:
        print(f"    bool(readings > 30) -> ValueError: {exc}")
    else:  # pragma: no cover - documents an outcome that would falsify the claim
        raise AssertionError("bool() on a multi-element array must raise")
    print()
    print("  It even tells you the two ways out, .any() and .all(), which are")
    print("  the two questions that DO have a single answer.")

    # -- 6. The parentheses are not optional ----------------------------------
    print()
    print("6. Why those brackets are load-bearing")
    print("-" * 70)
    print("  `&` binds TIGHTER than `>` in Python, so")
    print("      readings > 30 & readings < 70")
    print("  parses as")
    print("      readings > (30 & readings) < 70")
    print("  which is a bitwise-and of 30 with every reading, then a chained")
    print("  comparison. Here is what that actually raises -- the expression")
    print("  below is written out literally, brackets and all left off:")
    try:
        readings > 30 & readings < 70  # noqa: B015 - the point is the exception
    except ValueError as exc:
        print(f"    ValueError: {exc}")
    else:  # pragma: no cover - documents an outcome that would falsify the claim
        raise AssertionError("the unbracketed form must raise")
    print()
    print("  Not a syntax error, which would be kinder. It is a chained")
    print("  comparison, and chaining calls bool() on the first half.")
    print(f"  And 30 & readings really is a bitwise-and, element by element:")
    print(f"    {(30 & readings).tolist()[:6]} ...")

    # -- 7. Choosing between two values ---------------------------------------
    print()
    print("7. np.where: the vectorised if-else")
    print("-" * 70)
    labels = np.where(readings > 50, 1, 0)
    print(f"  np.where(readings > 50, 1, 0)")
    print(f"    {labels.tolist()}")
    capped = np.where(readings > 50, 50, readings)
    print(f"  np.where(readings > 50, 50, readings)   <- cap at 50")
    print(f"    {capped.tolist()}")
    print()
    print("  Three arguments: the mask, the value where True, the value where")
    print("  False. Either of the last two may be an array, and then it is")
    print("  read elementwise. This is `x if cond else y` for a whole array.")
    assert labels.sum() == 9
    assert int(capped.max()) == 50
    assert capped.tolist()[:4] == [50, 50, 34, 50]

    # -- 8. Assigning through a mask ------------------------------------------
    print()
    print("8. Writing through a mask")
    print("-" * 70)
    working = readings.copy()
    working[working > 90] = 90
    print(f"  a[a > 90] = 90   ->  max is now {int(working.max())}")
    print(f"  and the original is untouched: max {int(readings.max())}")
    print("  (untouched only because .copy() was called first -- script 06)")
    assert int(working.max()) == 90
    assert int(readings.max()) == 97

    # -- 9. Fancy indexing ----------------------------------------------------
    print()
    print("9. Fancy indexing: an array of positions")
    print("-" * 70)
    wanted = np.array([0, 5, 19, 5])
    print(f"  readings[[0, 5, 19, 5]]  ->  {readings[wanted].tolist()}")
    print()
    print("  Three differences from a boolean mask, all of them useful:")
    print("    * the result has the shape of the INDEX array, not the source")
    print("    * you choose the order")
    print("    * you may ask for the same element twice, as 5 is here")
    print("  This is how a batch of rows is pulled out of a dataset, and it is")
    print("  what the next script's top-k does with the argsort result.")
    assert readings[wanted].tolist() == [70, 21, 82, 21]
    assert readings[wanted].shape == (4,)

    print()
    print("=" * 70)
    print("05_masks_and_selection.py: every assertion held.")


if __name__ == "__main__":
    main()
