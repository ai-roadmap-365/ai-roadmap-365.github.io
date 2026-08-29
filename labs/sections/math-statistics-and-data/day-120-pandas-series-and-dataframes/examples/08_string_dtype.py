"""Exercise 8 -- the pandas 3.0 string dtype default.

Run: python3 08_string_dtype.py

Every pre-3.0 pandas tutorial says a Series of strings has dtype `object`
-- a column of pointers to arbitrary Python objects, no faster and no more
memory-efficient than a Python list. As of pandas 3.0, built on PyArrow,
the DEFAULT dtype for string data is `str`, a dedicated string dtype backed
by PyArrow's contiguous string arrays. `object` still exists and is still
what you get for genuinely mixed-type columns, but a column that is
actually just text no longer pays the `object` tax by default.
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


print(f"pandas {pd.__version__}")

s = pd.Series(["a", "b"])
print(f"\npd.Series(['a', 'b']).dtype  ->  {s.dtype}")
print("(pandas < 2.x and most tutorials say this is `object` -- it is not, here)")

check("the default dtype for a plain string Series is 'str' on pandas 3.0.5", str(s.dtype) == "str")
check("it is explicitly NOT the old object dtype", str(s.dtype) != "object")

# object is still available -- and still what mixed-type data gets.
mixed = pd.Series(["a", 1, 3.5])
print(f"\npd.Series(['a', 1, 3.5]).dtype  ->  {mixed.dtype}  (genuinely mixed types)")
check("a genuinely mixed-type column still falls back to object", mixed.dtype == "object")

# You can still ask for object explicitly if you need the old behaviour.
forced_object = pd.Series(["a", "b"], dtype="object")
print(f"pd.Series(['a', 'b'], dtype='object').dtype  ->  {forced_object.dtype}")
check("object remains available on request, it is just no longer the default", forced_object.dtype == "object")

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("08_string_dtype.py: every assertion held.")
