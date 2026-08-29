"""Axes, shapes, views, and the ranking that Day 103 needed.

Run from inside examples/:

    ../.venv/bin/python3 06_axes_views_and_ranking.py

Four claims under test:

  * the axis you name is the one that DISAPPEARS;
  * `np.newaxis` turns a row into a column so broadcasting can pair everything
    with everything;
  * a slice is a VIEW, so writing to it writes to the original, and this is
    where a beginner's hardest bug lives;
  * `argsort` and not `sort` is what a search needs, because the indices are
    the answer and the scores are only how you got there.
"""

import numpy as np

import dataset
from vectorize import cosine_similarities, top_k_indices


def main() -> None:
    print("06_axes_views_and_ranking.py")
    print("=" * 70)

    # -- 1. The axis rule -----------------------------------------------------
    print()
    print("1. Aggregating, and the one rule that makes axis make sense")
    print("-" * 70)
    grid = np.arange(12).reshape(3, 4)
    print("  a 3 by 4 array:")
    for row in grid:
        print(f"    {row}")
    print()
    print(f"  grid.sum()          {grid.sum():<20} shape {np.shape(grid.sum())}")
    print(f"  grid.sum(axis=0)    {str(grid.sum(axis=0)):<20} shape {grid.sum(axis=0).shape}")
    print(f"  grid.sum(axis=1)    {str(grid.sum(axis=1)):<20} shape {grid.sum(axis=1).shape}")
    print()
    print("  THE RULE: the axis you name is the one that disappears.")
    print("    shape (3, 4), axis=0 -> shape (4,)   the 3 went")
    print("    shape (3, 4), axis=1 -> shape (3,)   the 4 went")
    print()
    print("  So axis=0 collapses DOWN the rows and gives one number per")
    print("  column; axis=1 collapses ACROSS the columns and gives one number")
    print("  per row. Reading it as 'which axis do I want to keep' is the")
    print("  mistake, and it is off by exactly one every time.")
    assert int(grid.sum()) == 66
    assert grid.sum(axis=0).tolist() == [12, 15, 18, 21]
    assert grid.sum(axis=1).tolist() == [6, 22, 38]
    assert grid.sum(axis=0).shape == (4,)
    assert grid.sum(axis=1).shape == (3,)

    print()
    print("  The same rule for every aggregation:")
    for name, fn in (("min", np.min), ("max", np.max), ("mean", np.mean)):
        print(
            f"    {name:<5} whole {str(fn(grid)):<8} axis=0 {str(fn(grid, axis=0)):<22}"
            f" axis=1 {fn(grid, axis=1)}"
        )
    assert np.max(grid, axis=1).tolist() == [3, 7, 11]

    print()
    print(f"  keepdims=True holds the shape open: {grid.sum(axis=1, keepdims=True).shape}")
    print("  which is what you want when the result has to broadcast back")
    print("  against the array it came from -- normalising every row, say.")
    assert grid.sum(axis=1, keepdims=True).shape == (3, 1)

    # -- 2. newaxis -----------------------------------------------------------
    print()
    print("2. np.newaxis: making a row into a column")
    print("-" * 70)
    v = np.array([1.0, 2.0, 3.0])
    print(f"  v                shape {v.shape}")
    print(f"  v[:, np.newaxis] shape {v[:, np.newaxis].shape}   a column")
    print(f"  v[np.newaxis, :] shape {v[np.newaxis, :].shape}   a row")
    print()
    print("  A column against a row broadcasts to a full table, every pairing")
    print("  at once, with no loop over pairs:")
    table = v[:, np.newaxis] - v[np.newaxis, :]
    for row in table:
        print(f"    {row}")
    print(f"  shape {table.shape}: every difference of every pair.")
    print("  This is how a whole distance matrix gets built in one line, and")
    print("  section 7 of script 07 is about when that line is a bad idea.")
    assert v[:, np.newaxis].shape == (3, 1)
    assert table.shape == (3, 3)
    assert table.tolist() == [[0.0, -1.0, -2.0], [1.0, 0.0, -1.0], [2.0, 1.0, 0.0]]
    print()
    print(f"  reshape does the same job explicitly: {v.reshape(3, 1).shape}")
    print(f"  and -1 means 'work it out': v.reshape(-1, 1) -> {v.reshape(-1, 1).shape}")
    assert v.reshape(-1, 1).shape == (3, 1)

    # -- 3. A view is not a copy ----------------------------------------------
    print()
    print("3. A slice is a VIEW, and this is where the bug lives")
    print("-" * 70)
    original = np.arange(12).reshape(3, 4)
    print("  original:")
    for row in original:
        print(f"    {row}")
    row_one = original[1]
    print()
    print(f"  row_one = original[1]  ->  {row_one}")
    print(f"  shares memory with the original: {np.shares_memory(original, row_one)}")
    print(f"  row_one.base is None: {row_one.base is None}   (a view knows its owner)")
    row_one[0] = 999
    print()
    print("  row_one[0] = 999")
    print("  the ORIGINAL now reads:")
    for row in original:
        print(f"    {row}")
    print()
    print("  Nothing was copied, so nothing was protected. In a list, `b =")
    print("  a[1:3]` hands you a new list and you can do what you like to it.")
    print("  In NumPy it hands you a different way of reading the same bytes.")
    assert np.shares_memory(original, row_one)
    assert int(original[1, 0]) == 999
    assert row_one.base is not None

    print()
    print("  .copy() breaks the link:")
    detached = original[2].copy()
    detached[0] = -1
    print(f"    detached = original[2].copy(); detached[0] = -1")
    print(f"    detached      {detached}")
    print(f"    original[2]   {original[2]}   <- untouched")
    print(f"    shares memory {np.shares_memory(original, detached)}")
    assert int(original[2, 0]) == 8
    assert not np.shares_memory(original, detached)

    # -- 4. Which operations give a view --------------------------------------
    print()
    print("4. Which of them hand back a view, and which a copy")
    print("-" * 70)
    base = np.arange(12).reshape(3, 4)
    cases = [
        ("base[1]           row slice", base[1]),
        ("base[:, 1]        column slice", base[:, 1]),
        ("base[0:2, 1:3]    block slice", base[0:2, 1:3]),
        ("base.T            transpose", base.T),
        ("base.reshape(4,3) reshape", base.reshape(4, 3)),
        ("base.ravel()      flatten (view when it can)", base.ravel()),
        ("base[base > 5]    boolean mask", base[base > 5]),
        ("base[[0, 2]]      fancy index", base[[0, 2]]),
        ("base.copy()       explicit copy", base.copy()),
        ("base + 0          arithmetic", base + 0),
    ]
    print(f"  {'expression':<44} {'view?':<6}")
    for label, result in cases:
        is_view = np.shares_memory(base, result)
        print(f"  {label:<44} {'VIEW' if is_view else 'copy'}")
    print()
    print("  The pattern: if the elements you asked for are evenly spaced,")
    print("  NumPy can describe them with a stride and gives you a view. If")
    print("  they are not -- a mask, a list of positions -- it has no choice")
    print("  but to copy. So the cheap operations are the dangerous ones.")
    assert np.shares_memory(base, base[:, 1])
    assert np.shares_memory(base, base.T)
    assert not np.shares_memory(base, base[base > 5])
    assert not np.shares_memory(base, base[[0, 2]])
    assert not np.shares_memory(base, base + 0)

    # -- 5. sort, and why it is the wrong tool --------------------------------
    print()
    print("5. sort loses the thing you were looking for")
    print("-" * 70)
    scores = np.array([5.0, 1.0, 9.0, 3.0])
    print(f"  scores          {scores}")
    print(f"  np.sort(scores) {np.sort(scores)}   <- the values, in order")
    print(f"  scores after    {scores}   <- np.sort returns a NEW array")
    print(f"  np.argsort      {np.argsort(scores)}   <- the POSITIONS, in order")
    print()
    print("  argsort answers 'which element would come first, then which'.")
    print("  scores[np.argsort(scores)] rebuilds the sorted values:")
    print(f"    {scores[np.argsort(scores)]}")
    print()
    print("  When the rows mean something -- an article, a customer, a token --")
    print("  the sorted values are useless on their own and the indices are")
    print("  the entire answer. That is why argsort is the one to reach for.")
    assert np.sort(scores).tolist() == [1.0, 3.0, 5.0, 9.0]
    assert np.argsort(scores).tolist() == [1, 3, 0, 2]
    assert scores.tolist() == [5.0, 1.0, 9.0, 3.0]
    assert scores[np.argsort(scores)].tolist() == [1.0, 3.0, 5.0, 9.0]
    print()
    print("  a.sort() -- the method, no np. -- sorts IN PLACE and returns None:")
    in_place = scores.copy()
    returned = in_place.sort()
    print(f"    returned {returned}, array now {in_place}")
    assert returned is None
    assert in_place.tolist() == [1.0, 3.0, 5.0, 9.0]

    # -- 6. Day 103's search, done with argsort -------------------------------
    print()
    print("6. Day 103's search, ranked with argsort")
    print("-" * 70)
    sims = cosine_similarities(dataset.CATALOGUE, dataset.QUERY)
    print(f"  catalogue shape {dataset.CATALOGUE.shape}   query shape {dataset.QUERY.shape}")
    print(f"  query: 'training for a race and what to eat' = {dataset.QUERY}")
    print()
    print("  all six similarities, from one matrix-vector product and one")
    print("  norm along axis=1 -- no loop over articles:")
    for name, score in zip(dataset.ARTICLE_NAMES, sims):
        print(f"    {name:<20} {score:.6f}")
    assert sims.shape == (6,)

    print()
    ordering = np.argsort(sims)
    top = top_k_indices(sims, dataset.TOP_K)
    print(f"  np.argsort(sims)          {ordering.tolist()}   <- worst first")
    print(f"  reversed, first {dataset.TOP_K}         {top.tolist()}   <- best first")
    print()
    print(f"  top {dataset.TOP_K}:")
    for rank, index in enumerate(top, start=1):
        print(f"    {rank}. {dataset.ARTICLE_NAMES[index]:<20} {sims[index]:.6f}")
    assert ordering.tolist() == [4, 5, 1, 0, 2, 3]
    assert top.tolist() == [3, 2, 0]
    assert [dataset.ARTICLE_NAMES[i] for i in top] == [
        "race-day-nutrition",
        "marathon-plan",
        "roast-chicken",
    ]

    print()
    margin = float(sims[top[0]] - sims[top[1]])
    print(f"  margin between first and second: {margin:.6f}")
    print("  Day 103 called this a close call and it still is. The ranking is")
    print("  reported with its margin rather than as a verdict, because a gap")
    print("  of two thousandths is not evidence of much.")
    assert 0.0 < margin < 0.01

    print()
    print("  One more way to say the same thing, and the one you will meet in")
    print("  model code, where only the top few matter out of a hundred")
    print("  thousand:")
    partitioned = np.argpartition(-sims, dataset.TOP_K)[: dataset.TOP_K]
    ordered = partitioned[np.argsort(-sims[partitioned])]
    print(f"    np.argpartition(-sims, {dataset.TOP_K})[:{dataset.TOP_K}] then sorted -> {ordered.tolist()}")
    print("  argpartition does not sort everything; it only guarantees that")
    print("  the k best are in the first k places, in no particular order. On")
    print("  six articles that saves nothing. On a hundred thousand it is the")
    print("  difference between sorting them all and not.")
    assert ordered.tolist() == top.tolist()

    print()
    print("=" * 70)
    print("06_axes_views_and_ranking.py: every assertion held.")


if __name__ == "__main__":
    main()
