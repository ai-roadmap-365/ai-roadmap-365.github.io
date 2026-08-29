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

## `pd.Series(['a', 'b']).dtype` prints `object`, not `str`

You are running pandas older than 3.0. Check with
`python3 -c "import pandas; print(pandas.__version__)"`. This lab and its
lesson are written against 3.0.5 specifically; `requirements.txt` pins the
exact version because this day's whole point is the 3.0 behaviour change.
Install the pinned version into the lab's `.venv` rather than using a
different pandas already on your system.

## Chained assignment doesn't warn, or it silently updates the frame

If `df[mask]['col'] = value` neither warns nor changes `df`, or if it
*does* change `df`, you are very likely not on pandas 3.0's unconditional
Copy-on-Write. On pandas 2.x with Copy-on-Write opted out of (the 2.x
default), the same statement's effect depends on internal memory layout
that is not a stable contract — sometimes it appears to work, sometimes it
does not, and neither is something you should rely on. Reinstall the
pinned version: `.venv/bin/pip install -r requirements/requirements.txt`.

## `SettingWithCopyWarning` — you were expecting this and didn't see it

That warning class is a pandas < 3.0 artifact of the old, optional
Copy-on-Write mechanism. pandas 3.0 replaced it with a specific
`ChainedAssignmentError` warning that names the exact statement and the
exact fix, shown in `examples/04_copy_on_write.py`. If you see
`SettingWithCopyWarning` instead, you are not running pandas 3.0.5.

## `KeyError` from `.loc[...]` where `.iloc[...]` would have worked

`.loc` looks up **labels** in the index; `.iloc` looks up **positions**.
If your index is not the default `0, 1, 2, ...` RangeIndex — for example,
after filtering or sorting a frame, which does not renumber the index — a
positional number like `.loc[3]` will raise `KeyError` unless `3` also
happens to be a label. Use `.iloc[3]` for "the 4th row regardless of its
label", and `.reset_index(drop=True)` if you want the default numbering
back.

## `.iloc[1:3]` returns one row fewer than you expected

This is exercise 5, and it is not a bug in your code. `.iloc`'s stop value
is a **position to stop before**, not a label to include. If you copied a
`.loc['b':'d']` slice and just swapped in "the same numbers", the row at
the stop label is silently dropped. Write the stop position one past where
you want to stop: `.iloc[1:4]` to include what `.loc['b':'d']` includes.

## An ID column that used to be integers now prints with a trailing `.0`

Something reindexed, joined, or merged a `NaN` into that column, and NumPy
int64 has no bit pattern for "missing" — the whole column silently
promoted to float64, shown in `examples/03_dtype_promotion.py`. If the
column must never lose exact integer precision, declare it `dtype="Int64"`
(capital I, the *nullable* integer type) from the start, or cast to it with
`.astype("Int64")` before the join.

## `pip install` fails or hangs

You are offline, or a corporate proxy is blocking PyPI. This is the only
network-dependent step in the entire lab — everything after installation
runs offline, which `tests/run_tests.sh` section 6 checks by grepping for
any URL in `examples/` or `starter/`. Retry on a connection that can reach
`pypi.org`, or ask whoever manages your network for a mirror.

## `bash tests/run_tests.sh` reports a version mismatch in section 1

The suite checks that the pandas installed in whatever Python it resolves
matches `requirements/requirements.txt` exactly (not just "at least"),
because this lab's captured output is tied to the exact pandas 3.0.5
behaviour. If you intentionally want to see how an older pandas behaves
differently, that is a legitimate thing to explore — just do not expect
this lab's checks to pass while you do it.
