# What is installed, why, and what it costs

Three packages, all free and open source, installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `pandas` | 3.0.5 | BSD 3-Clause | Every mask, `.loc` call, `.query()` and `.str.contains()` in this lab. Pinned exactly because two exercises depend on pandas-3.0-specific dtype behaviour — see below. |
| `pyarrow` | 25.0.1 | Apache 2.0 | The storage backend behind the pandas 3.0 default `str` dtype exercised in exercise 5. |
| `numpy` | 2.5.2 | BSD 3-Clause | `np.nan`, boolean-array semantics, and the arrays every mask is ultimately built from. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## Why the versions are pinned exactly, not just floored

`exercise 5` (`.str.contains` on a column with missing values) prints a
genuinely different result depending on the column's dtype, and that dtype
default changed in pandas 3.0:

- On a **pandas-3.0 `str` dtype** column (the default this pandas version
  gives a list of Python strings), `.str.contains()` on a missing entry
  returns a plain `False`, and the resulting mask's own dtype is `bool`
  with no missing values in it at all — the classic trap does not fire.
- On the legacy **`object` dtype** column — still reachable with
  `dtype="object"`, and still what you get from many real-world sources —
  `.str.contains()` on a missing entry returns `None`, the mask's dtype is
  `object`, and filtering a DataFrame with that mask raises
  `ValueError: Cannot mask with non-boolean array containing NA / NaN
  values` rather than silently doing the wrong thing.

Both facts are captured from this exact pandas version and are stated
plainly as version-specific in `expected-output/FIELDS.md`. A different
pandas major version could print a different combination of these two
behaviours.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 6 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/`
to prove that nothing else does.

## What is deliberately *not* installed

**matplotlib**, **scipy** and **polars** are not installed in this
environment. The lesson's Tools section describes polars from its public
documentation as a design contrast to pandas' masks — specifically, that
`pl.col('a') > 1` composes inside one expression rather than through
Python's `&`/`|`/`~` operators, which removes the precedence trap this
lab's exercise 3 demonstrates by construction. **No output from polars,
scipy or matplotlib is reproduced anywhere** in this lab or its lesson;
every place they are mentioned says so plainly.

## If you cannot install anything at all

pandas is not in the Python standard library, and there is no reduced path
through this lab without it — the whole point is pandas' specific masking
and alignment behaviour, which nothing else on your system will reproduce.
If pandas genuinely cannot be installed, read the lesson's captured output
and `expected-output/` directory instead; every number there came from a
real run and is not invented.
