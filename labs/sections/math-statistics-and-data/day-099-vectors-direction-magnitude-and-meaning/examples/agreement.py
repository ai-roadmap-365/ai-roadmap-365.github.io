"""The same nine operations, twice: your loops, then NumPy — and they agree.

This is the only file in the lab that imports NumPy. Read it after you have
written the loops in `vectors.py`, not before. The order matters: once you have
written `sum(a * a for a in v)` yourself, `np.linalg.norm(v)` is not magic, it
is your loop with a shorter name and a faster inner loop.

Every comparison uses `numpy.allclose` or `math.isclose` with a stated
tolerance. Nothing here is compared with `==`, and the reason is in
`normalise.py`.

Run from the examples directory:

    python3 agreement.py
"""

from __future__ import annotations

import math

import numpy as np

import vectors as pure

RTOL = 1e-9
ATOL = 1e-12

U = [3, 4, 12]
V = [1, -2, 5]
K = 2.5

CASES = [
    ("add(u, v)", lambda: pure.add(U, V), lambda: np.array(U) + np.array(V)),
    ("subtract(u, v)", lambda: pure.subtract(U, V), lambda: np.array(U) - np.array(V)),
    ("scale(k, u)", lambda: pure.scale(K, U), lambda: K * np.array(U)),
    ("negate(u)", lambda: pure.negate(U), lambda: -np.array(U)),
    ("zero(3)", lambda: pure.zero(3), lambda: np.zeros(3)),
    ("normalise(u)", lambda: pure.normalise(U), lambda: np.array(U) / np.linalg.norm(U)),
]

SCALAR_CASES = [
    ("dot(u, v)", lambda: pure.dot(U, V), lambda: float(np.dot(U, V))),
    ("l2_norm(u)", lambda: pure.l2_norm(U), lambda: float(np.linalg.norm(U))),
    ("l1_norm(u)", lambda: pure.l1_norm(U), lambda: float(np.linalg.norm(U, ord=1))),
    (
        "distance(u, v)",
        lambda: pure.distance(U, V),
        lambda: float(np.linalg.norm(np.array(U) - np.array(V))),
    ),
    (
        "l1_distance(u, v)",
        lambda: pure.l1_distance(U, V),
        lambda: float(np.linalg.norm(np.array(U) - np.array(V), ord=1)),
    ),
]


def main() -> int:
    print("Pure Python against NumPy, on the same inputs")
    print(f"numpy {np.__version__}")
    print(f"u = {U}    v = {V}    k = {K}")
    print(f"tolerance: rtol={RTOL}, atol={ATOL} — never ==")
    print()

    all_agree = True

    header = f"{'operation':<22}{'pure Python':<34}{'NumPy':<34}agree"
    print(header)
    print("-" * len(header))

    for name, py_fn, np_fn in CASES:
        py_out = py_fn()
        np_out = np_fn()
        agree = bool(np.allclose(py_out, np_out, rtol=RTOL, atol=ATOL))
        all_agree = all_agree and agree
        py_text = str([round(float(x), 6) for x in py_out])
        np_text = str([round(float(x), 6) for x in np_out])
        print(f"{name:<22}{py_text:<34}{np_text:<34}{agree}")

    for name, py_fn, np_fn in SCALAR_CASES:
        py_out = py_fn()
        np_out = np_fn()
        agree = math.isclose(py_out, np_out, rel_tol=RTOL, abs_tol=ATOL)
        all_agree = all_agree and agree
        print(f"{name:<22}{py_out!r:<34}{np_out!r:<34}{agree}")

    print()
    print("every operation agrees:", all_agree)
    print()

    # ---------------------------------------------------------------------
    print("Three things NumPy gives you that the loops do not")
    print()

    stacked = np.array(
        [
            [9, 0, 1, 0],
            [8, 0, 2, 0],
            [0, 9, 1, 2],
        ]
    )
    print("1. A whole table of vectors is one object, and one call measures")
    print("   every row at once:")
    print(f"     matrix shape        = {stacked.shape}")
    print(f"     norms of all rows   = {np.linalg.norm(stacked, axis=1).round(4)}")
    row_by_row = [pure.l2_norm(list(row)) for row in stacked]
    print(f"     the same, by loop   = {[round(x, 4) for x in row_by_row]}")
    print(
        "     agree               = "
        f"{bool(np.allclose(np.linalg.norm(stacked, axis=1), row_by_row, rtol=RTOL, atol=ATOL))}"
    )
    print()

    print("2. Every distance from one query to every row, in one expression:")
    query = np.array([1, 0, 0, 0])
    diffs = stacked - query
    dists = np.linalg.norm(diffs, axis=1)
    loop_dists = [pure.distance([1, 0, 0, 0], list(row)) for row in stacked]
    print(f"     query               = {query.tolist()}")
    print(f"     distances (NumPy)   = {dists.round(4)}")
    print(f"     distances (loop)    = {[round(x, 4) for x in loop_dists]}")
    print(
        "     agree               = "
        f"{bool(np.allclose(dists, loop_dists, rtol=RTOL, atol=ATOL))}"
    )
    print()
    print("   `stacked - query` subtracted a 4-component vector from every row")
    print("   of a 3-by-4 table without a loop. That is broadcasting, and it is")
    print("   the reason a search over a million embeddings is a few lines.")
    print()

    print("3. The dimension check is still there — NumPy just phrases it in")
    print("   terms of shapes:")
    try:
        np.array([1, 2]) + np.array([1, 2, 3])
    except ValueError as exc:
        print(f"     numpy : ValueError: {exc}")
    try:
        pure.add([1, 2], [1, 2, 3])
    except ValueError as exc:
        print(f"     ours  : ValueError: {exc}")

    return 0 if all_agree else 1


if __name__ == "__main__":
    raise SystemExit(main())
