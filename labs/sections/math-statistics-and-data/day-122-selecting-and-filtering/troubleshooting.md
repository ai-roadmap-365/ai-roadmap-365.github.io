# Troubleshooting

Grouped by the message you actually see.

## `ModuleNotFoundError: No module named 'pandas'`

The lab's dependencies live in its own `.venv`, not on your system Python.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the test suite at a Python that already has pandas 3.0.5 and
pyarrow 25.0.1 installed: `PYTHON=/path/to/python3 bash tests/run_tests.sh`.

## `mask1 and mask2` doesn't raise for you — it silently gives a `bool`

If `mask1` or `mask2` is a single-element Series, `bool(series)` succeeds
(pandas allows it only for length-1 Series) and `and`/`or` will run without
complaint, masking the exact problem this lab's exercise 2 demonstrates.
Use a mask of length 2 or more to see the real `ValueError: The truth value
of a Series is ambiguous` — every example script in this lab is built that
way on purpose.

## `df[df.a > 1 & df.b < 2]` gives a confusing error, or a suspiciously
## empty result, and you don't see why

This is exercise 3's precedence trap. `&` binds tighter than `>` and `<`
in Python, so the expression does not group the way it reads — it groups
as `df.a > (1 & df.b) < 2`, a chained comparison that ends up calling the
same ambiguous-truth-value machinery `and` does. Parenthesise every single
comparison before combining it with `&`, `|` or `~`:
`(df.a > 1) & (df.b < 2)`. The same trap applies to `~`, which also binds
tighter than `==`: `~df.a == 2` computes the bitwise-NOT of `df.a` first,
then compares THAT to 2 — write `~(df.a == 2)` instead.

## A mask built from a differently-sorted copy of a frame gives a
## `UserWarning: Boolean Series key will be reindexed to match DataFrame
## index`

This is expected, not a bug — pandas is telling you exactly what exercise
4 demonstrates: it is reindexing the mask by label to match the frame you
are filtering, rather than walking it position by position. The warning is
informational; the result is correct as long as every label the mask
carries actually exists in the frame you are applying it to. If you meant
to filter positionally instead, that is `.to_numpy()` territory, and
exercise 4 also shows why that usually gives the wrong answer instead.

## `.str.contains(...)` filtering raises `ValueError: Cannot mask with
## non-boolean array containing NA / NaN values`

You are filtering with a mask built from an **`object`**-dtype string
column that has a missing entry, and you left off `na=`. `.str.contains()`
on a missing entry in an object-dtype column returns `None`, not `False`,
and pandas correctly refuses to use a mask with `None` in it as a boolean
selector. Add `na=False`: `series.str.contains(pattern, na=False)`. Note
that on pandas 3.0's default `str`-dtype column (as opposed to `object`),
`.str.contains()` already returns a clean `False` for missing entries with
no `na=` needed — see `expected-output/FIELDS.md` for exactly which dtype
this affects.

## `.query("amount > @threshold")` raises `UndefinedVariableError`

The `@` prefix looks up a name in the **calling scope**, not inside the
DataFrame. If `threshold` is defined inside a function and you call
`.query()` from a different scope (for example, passing the query string
around and evaluating it later), the variable will not be visible. Keep
the `@variable` reference in the same function that defines the variable,
or pass it explicitly with `.query("amount > @threshold", local_dict={"threshold": threshold})`.

## `isin([])` returns everything, or nothing, and you're not sure which
## you wanted

`series.isin([])` always returns an all-`False` mask — "is this value one
of these zero values" can only ever be false — so filtering with it gives
an **empty** result, never the untouched original. If you wanted "no
filter applied when the list is empty," that is a decision you have to
make explicitly, for example
`df if not wanted else df[df.col.isin(wanted)]`; pandas will not infer it
for you.

## `nlargest(n, col)` returns more than `n` rows

That is `keep='all'`, and it is working as designed: it returns every row
tied for the value that would otherwise sit right at the cutoff, rather
than picking an arbitrary subset of them the way
`.sort_values().head(n)` is forced to. If you need exactly `n` rows even
when there is a tie at the boundary, use the default `keep='first'` (or
`'last'`), which behaves identically to `.sort_values().head(n)`.

## `drop_duplicates()` isn't dropping the rows you expected

Check what `subset` you passed, or didn't. With no `subset`, a row only
counts as a duplicate if **every column** matches exactly. If two rows
agree on the columns you care about but differ in some other column
(a timestamp, an ID, a quantity), they will both survive unless you name
the columns that should define "duplicate" explicitly:
`df.drop_duplicates(subset=["customer", "item"])`.

## `pip install` fails or hangs

You are offline, or a corporate proxy is blocking PyPI. This is the only
network-dependent step in the entire lab — everything after installation
runs offline, which `tests/run_tests.sh` section 6 checks by grepping for
any URL in `examples/` or `starter/`. Retry on a connection that can reach
`pypi.org`, or ask whoever manages your network for a mirror.
