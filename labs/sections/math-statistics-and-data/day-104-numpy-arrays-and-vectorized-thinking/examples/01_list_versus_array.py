"""What an ndarray is, and what it costs, measured rather than asserted.

Run from inside examples/:

    ../.venv/bin/python3 01_list_versus_array.py

The claim under test: a list of a million integers and an array of a million
integers hold the same numbers and do not cost the same memory, because one is
a million separate objects with a million pointers to them and the other is one
typed block.

This script also refuses to make the measurement the easy way, and says why.
"""

import sys

import numpy as np

import dataset
from vectorize import array_bytes, describe, list_bytes


def main() -> None:
    print("01_list_versus_array.py")
    print("=" * 70)

    N = dataset.N_BIG

    # -- 1. The same numbers, two ways ----------------------------------------
    print()
    print("1. A million integers, held two ways")
    print("-" * 70)
    values = list(range(N))
    array = np.arange(N, dtype=np.int64)
    print(f"  list  : {values[:5]} ... {values[-3:]}   len {len(values):,}")
    print(f"  array : {array[:5]} ... {array[-3:]}   size {array.size:,}")
    print(f"  same numbers: {values[:1000] == array[:1000].tolist()} (first thousand)")
    assert values[:1000] == array[:1000].tolist()

    # -- 2. The naive measurement, and why it lies ----------------------------
    print()
    print("2. The measurement almost everyone makes first")
    print("-" * 70)
    naive_list = sys.getsizeof(values)
    print(f"  sys.getsizeof(list)   {naive_list:>12,} bytes")
    print(f"  array.nbytes          {array.nbytes:>12,} bytes")
    print(f"  ratio                 {naive_list / array.nbytes:>12.4f}")
    print()
    print("  Read that ratio again. It says the list costs the SAME as the")
    print("  array, which is the opposite of what every NumPy tutorial")
    print("  promises -- including this one. The measurement is wrong, not the")
    print("  promise.")
    print()
    print("  sys.getsizeof measures the LIST OBJECT: a header plus one 8-byte")
    print("  pointer per element. It does not measure the integers, because")
    print("  the list does not own them. They are a million separate objects")
    print("  sitting elsewhere in memory, and they are where the cost is.")
    assert abs(naive_list / array.nbytes - 1.0) < 0.01, (
        "on this build the pointer array and the int64 block are the same size"
    )

    # -- 3. The honest measurement --------------------------------------------
    print()
    print("3. Counting what the list actually costs")
    print("-" * 70)
    one_int = sys.getsizeof(values[999])
    print(f"  sys.getsizeof(one Python int)     {one_int:>12,} bytes")
    print(f"  one int64 element in the array    {array.itemsize:>12,} bytes")
    print()
    honest_list = list_bytes(values)
    honest_array = array_bytes(array)
    payload = honest_list - naive_list
    print(f"  the list's pointers               {naive_list:>12,} bytes")
    print(f"  the integers they point at        {payload:>12,} bytes")
    print(f"  list total                        {honest_list:>12,} bytes")
    print(f"  array total                       {honest_array:>12,} bytes")
    print(f"  the array is                      {honest_list / honest_array:>12.2f}x smaller")
    assert honest_list == 36_000_056, honest_list
    assert honest_array == 8_000_000, honest_array
    assert honest_list / honest_array > 4.0

    print()
    print("  A Python int is 28 bytes because it is a full object: a reference")
    print("  count, a pointer to its type, a length, and only then the digits.")
    print("  An int64 in an array is 8 bytes because it is 8 bytes.")

    # -- 4. Why the small integers are counted once ---------------------------
    print()
    print("4. A detail that would otherwise overcount")
    print("-" * 70)
    a, b = int("100"), int("100")
    c, d = int("1000"), int("1000")
    print(f'  int("100")  is int("100")   -> {a is b}   (cached: -5 to 256)')
    print(f'  int("1000") is int("1000")  -> {c is d}   (built fresh each time)')
    print()
    print("  The values are built from strings on purpose. Writing the literal")
    print("  1000 twice in one function gives you the same object both times,")
    print("  because the compiler folds equal constants in a code object into")
    print("  one -- which would have made the cache look far bigger than it is.")
    print()
    print("  list_bytes counts each DISTINCT integer object once, so the")
    print("  cached ones are not charged a million times over.")
    assert a is b, "small integers are cached"
    assert c is not d, "1000 is above the cache, so these are two objects"
    distinct = len({id(x) for x in values})
    print(f"  distinct integer objects in the list: {distinct:,} of {N:,}")
    assert distinct == N, "range() builds a new object for every value above 256"

    # -- 5. The three things that make an ndarray different -------------------
    print()
    print("5. dtype, shape, strides -- the three facts a list does not have")
    print("-" * 70)
    grid = np.arange(12).reshape(3, 4)
    print("  a 3 by 4 array of the numbers 0 to 11:")
    for row in grid:
        print(f"    {row}")
    print()
    print(f"  {describe(grid)}")
    print()
    print("  dtype   int64: every element is the same type, decided once,")
    print("          which is what lets the loop live in C.")
    print("  shape   (3, 4): 3 rows of 4, laid out end to end in ONE block.")
    print("  strides (32, 8): to step one row, skip 32 bytes; one column, 8.")
    print("          Four int64 is 32 bytes, so a row IS four elements along.")
    print("  A list of lists has none of these. It has pointers to lists of")
    print("  pointers to integers, scattered wherever the allocator put them.")
    assert grid.dtype == np.int64
    assert grid.shape == (3, 4)
    assert grid.strides == (32, 8)
    assert grid.flags["C_CONTIGUOUS"]

    # -- 6. What contiguity buys ----------------------------------------------
    print()
    print("6. One block, so a transpose costs nothing")
    print("-" * 70)
    transposed = grid.T
    print(f"  grid.T shape      {transposed.shape}")
    print(f"  grid.T strides    {transposed.strides}   <- the two swapped over")
    print(f"  shares memory     {np.shares_memory(grid, transposed)}")
    print(f"  C contiguous      {transposed.flags['C_CONTIGUOUS']}")
    print(f"  F contiguous      {transposed.flags['F_CONTIGUOUS']}")
    print()
    print("  Nothing was copied. NumPy swapped two numbers in the strides and")
    print("  handed back a new way of reading the same bytes. That is what a")
    print("  view is, and section 6 of script 06 is about the bug it causes.")
    assert np.shares_memory(grid, transposed)
    assert transposed.strides == (8, 32)

    print()
    print("=" * 70)
    print("01_list_versus_array.py: every assertion held.")


if __name__ == "__main__":
    main()
