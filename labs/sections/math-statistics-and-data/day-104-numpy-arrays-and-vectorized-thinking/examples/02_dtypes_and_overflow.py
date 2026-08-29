"""The dtype is a promise, and a promise you can break by accident.

Run from inside examples/:

    ../.venv/bin/python3 02_dtypes_and_overflow.py

The claim under test: a Python int grows to whatever size it needs and an int8
does not. 127 + 1 in an int8 array is -128. Nothing raises, nothing warns, and
the wrong number goes on down the pipeline.
"""

import warnings

import numpy as np

import dataset
from vectorize import wrap_int8


def main() -> None:
    print("02_dtypes_and_overflow.py")
    print("=" * 70)

    # -- 1. Python integers do not overflow -----------------------------------
    print()
    print("1. What you are used to")
    print("-" * 70)
    big = 2 ** 200
    print(f"  2 ** 200 = {big}")
    print(f"  that is {big.bit_length()} bits, and Python simply allocated them")
    print("  A Python int is a variable-length object. It grows. It has no")
    print("  maximum. That convenience is exactly what an array gives up.")
    assert big.bit_length() == 201

    # -- 2. The dtype is a fixed-width promise --------------------------------
    print()
    print("2. What an array promises instead")
    print("-" * 70)
    info = np.iinfo(np.int8)
    wide = np.iinfo(np.int64)
    print(f"  np.iinfo(np.int8)   min {info.min}   max {info.max}")
    print(f"  np.iinfo(np.int64)  min {wide.min}")
    print(f"                      max {wide.max}")
    print()
    for dtype in (np.int8, np.int16, np.int32, np.int64, np.float32, np.float64):
        a = np.zeros(3, dtype=dtype)
        print(f"  {str(a.dtype):<10} itemsize {a.itemsize} bytes   3 elements = {a.nbytes:>2} bytes")
    assert info.min == dataset.INT8_MIN
    assert info.max == dataset.INT8_MAX

    # -- 3. The wrap ----------------------------------------------------------
    print()
    print("3. Adding 1 to 127")
    print("-" * 70)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        wrapped = wrap_int8(dataset.INT8_MAX, 1)
        warning_names = [w.category.__name__ for w in caught]
    print(f"  np.array([127], dtype=np.int8) + np.array([1], dtype=np.int8)")
    print(f"  gives                {wrapped}")
    print(f"  warnings raised      {warning_names if warning_names else 'none'}")
    print()
    print("  No exception. No warning. On numpy 2.5.2 the value simply wraps")
    print("  from the top of the range round to the bottom, the way a car")
    print("  odometer rolls from 999999 to 000000, and the next line of your")
    print("  program carries on with -128 as though it were the answer.")
    assert wrapped == dataset.INT8_MIN
    assert warning_names == [], "measured on numpy 2.5.2: no warning is emitted"

    # -- 4. Why -128 and not something arbitrary ------------------------------
    print()
    print("4. Where -128 comes from")
    print("-" * 70)
    print("  An int8 is 8 bits in two's complement. 127 is 0111 1111. Add 1")
    print("  and the carry ripples the whole way:")
    print()
    print("      0111 1111    = 127")
    print("    + 0000 0001    =   1")
    print("      ---------")
    print("      1000 0000    = -128, because the top bit means 'negative'")
    print()
    for value in dataset.INT8_DOUBLING_INPUT:
        doubled = int((np.array([value], dtype=np.int8) * np.int8(2))[0])
        note = "" if doubled == value * 2 else f"   <- wrapped, the true answer is {value * 2}"
        print(f"  int8 {value:>4} doubled -> {doubled:>5}{note}")
    doubled_all = (np.array(dataset.INT8_DOUBLING_INPUT, dtype=np.int8) * np.int8(2)).tolist()
    print(f"  all three at once: {doubled_all}")
    assert doubled_all == [-16, -6, -2]

    # -- 5. A plain Python int does not rescue it -----------------------------
    print()
    print("5. The rule NumPy 2 applies when the types differ")
    print("-" * 70)
    from_python = np.array([127], dtype=np.int8) + 1
    print(f"  np.array([127], dtype=np.int8) + 1  ->  {from_python}  dtype {from_python.dtype}")
    print()
    print("  The plain 1 did not drag the result up to int64. Since NumPy 2 a")
    print("  Python scalar takes the array's dtype rather than the other way")
    print("  round, so the array's promise wins and the result wraps. The")
    print("  array's dtype is the thing to check when a number looks wrong.")
    assert int(from_python[0]) == -128
    assert from_python.dtype == np.int8

    # -- 6. Asking for a wider type on purpose --------------------------------
    print()
    print("6. The fix, which is to say what you meant")
    print("-" * 70)
    widened = np.array([127], dtype=np.int8).astype(np.int16) + 1
    print(f"  .astype(np.int16) + 1  ->  {widened}  dtype {widened.dtype}")
    print("  Two bytes per element instead of one, and 128 fits.")
    print("  This is a decision with a cost. On a million elements it is a")
    print("  megabyte. On a model's weights it can be a gigabyte, which is why")
    print("  half-precision floats exist and why anyone talks about them.")
    assert int(widened[0]) == 128
    assert widened.dtype == np.int16

    # -- 7. Floats lose precision instead of wrapping -------------------------
    print()
    print("7. The float version of the same problem")
    print("-" * 70)
    as32 = np.float32(0.1)
    print(f"  float64 0.1  ->  {0.1!r}")
    print(f"  float32 0.1  ->  {float(as32)!r}")
    print("  Neither is 0.1. One tenth is not representable in binary at all,")
    print("  and float32 has 24 bits of significand where float64 has 53, so")
    print("  it is wrong sooner.")
    print()
    blind = np.float32(dataset.FLOAT32_BLIND_SPOT)
    plus_one = blind + np.float32(1.0)
    print(f"  float32 {dataset.FLOAT32_BLIND_SPOT:.0f} + 1 == {dataset.FLOAT32_BLIND_SPOT:.0f}  ->  {bool(plus_one == blind)}")
    print("  At 2**24 the gap between neighbouring float32 values is exactly")
    print("  1, so adding 1 lands back on the same value. A float does not")
    print("  wrap round like an int8; it stops being able to tell two numbers")
    print("  apart. The failure is quieter and harder to spot.")
    assert bool(plus_one == blind) is True
    assert float(np.float64(dataset.FLOAT32_BLIND_SPOT) + 1.0) == 16777217.0

    print()
    print("=" * 70)
    print("02_dtypes_and_overflow.py: every assertion held.")


if __name__ == "__main__":
    main()
