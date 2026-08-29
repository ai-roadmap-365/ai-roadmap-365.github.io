"""Exercise 5 -- .str.contains and missing values: a trap that depends on
dtype, and pandas 3.0 changed which dtype you get by default.

Run: python3 05_str_contains_na.py

On the legacy `object` dtype, `.str.contains()` applied to a missing entry
returns `None` rather than `False`, because there is no text to search.
The resulting mask is not a clean boolean array -- its own dtype becomes
`object` -- and filtering a DataFrame with a mask that contains missing
values raises `ValueError: Cannot mask with non-boolean array containing
NA / NaN values` rather than silently doing the wrong thing. `na=False`
tells `.str.contains()` to treat a missing entry as "did not match" up
front, producing a clean boolean mask.

Pandas 3.0's new default `str` dtype (backed by PyArrow) behaves
differently, and this script measures that difference rather than
asserting the old story blindly: on a `str`-dtype column, `.str.contains()`
already returns a plain `False` for a missing entry, with no `NaN` in the
mask at all. The trap has NOT disappeared -- it still fires on `object`
dtype, which is still common (an explicit dtype="object" column, or a
column that arrived that way from elsewhere) -- but it no longer fires by
default on a plain list of Python strings under pandas 3.0.
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


raw_names = ["Alice Smith", "bob jones", None, "CAROL", "dave"]

# --- The pandas-3.0 default: str dtype -------------------------------
names_str = pd.Series(raw_names, dtype="str")
print(f"names_str.dtype: {names_str.dtype}")
mask_str = names_str.str.contains("a", case=False)
print(f"mask (str dtype):    {mask_str.tolist()}  dtype={mask_str.dtype}")

check("on pandas 3.0's default str dtype, the mask dtype is a clean bool", mask_str.dtype == bool)
check(
    "on str dtype, the missing entry (index 2) already comes back False, not NaN",
    bool(mask_str.iloc[2]) is False and not mask_str.isna().any(),
)
filtered_str = names_str[mask_str]
print(f"names_str[mask_str]: {filtered_str.tolist()}")
check(
    "filtering with the str-dtype mask works directly, no na= needed",
    filtered_str.tolist() == ["Alice Smith", "CAROL", "dave"],
)

# --- The trap: object dtype, still common in practice -----------------
names_obj = pd.Series(raw_names, dtype="object")
print(f"\nnames_obj.dtype: {names_obj.dtype}")
mask_obj = names_obj.str.contains("a", case=False)
print(f"mask (object dtype): {mask_obj.tolist()}  dtype={mask_obj.dtype}")

check("on object dtype, the missing entry's mask value is None, not False", mask_obj.iloc[2] is None)
check("on object dtype, the mask's own dtype is object, not bool", mask_obj.dtype == object)

try:
    _ = names_obj[mask_obj]
    contains_trap_raised = False
    trap_message = ""
except ValueError as exc:
    contains_trap_raised = True
    trap_message = str(exc)
print(f"names_obj[mask_obj] -> {'ValueError: ' + trap_message if contains_trap_raised else 'no error'}")

check("filtering with an object-dtype mask containing None raises ValueError", contains_trap_raised)
check(
    "the error names the real cause: masking with non-boolean / NA values",
    "non-boolean" in trap_message or "NA" in trap_message,
)

# The fix: na=False.
mask_obj_fixed = names_obj.str.contains("a", case=False, na=False)
print(f"\nmask (object dtype, na=False): {mask_obj_fixed.tolist()}  dtype={mask_obj_fixed.dtype}")
filtered_obj = names_obj[mask_obj_fixed]
print(f"names_obj[mask_obj_fixed]: {filtered_obj.tolist()}")

check("na=False produces a clean boolean mask on object dtype", mask_obj_fixed.dtype == bool)
check(
    "na=False filters correctly, matching the str-dtype result exactly",
    filtered_obj.tolist() == ["Alice Smith", "CAROL", "dave"],
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("05_str_contains_na.py: every assertion held.")
