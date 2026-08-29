# What is installed, why, and what it costs

Three packages, all free and open source, installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `pandas` | 3.0.5 | BSD 3-Clause | Every Series and DataFrame in this lab. Pinned exactly because this day's captured output is version-specific — see below. |
| `pyarrow` | 25.0.1 | Apache 2.0 | The storage backend behind pandas 3.0's default `str` dtype (exercise 8) and the `Int64` nullable-integer arrays (exercise 3). |
| `numpy` | 2.5.2 | BSD 3-Clause | `np.nan`, `np.dtype`, and the underlying arrays a Series wraps — Day 104's ndarray, one layer down. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## Why the versions are pinned exactly, not just floored

Every other lab in this course pins a *minimum* version. This one pins the
exact version, because **the lesson's central claims are pandas-3.0-specific
and would print different, equally-correct values on pandas 2.x**:

- `pd.Series(['a', 'b']).dtype` is `str` here; it is `object` on every
  pandas release before 3.0.
- Chained assignment (`df[mask]['col'] = value`) leaves the frame
  completely unchanged here, with a `ChainedAssignmentError` warning
  explaining why, because Copy-on-Write is unconditional starting in 3.0.
  On earlier pandas the same statement's behaviour depends on internal
  memory layout that is not part of any stable API contract.
- `pd.options.mode.copy_on_write = False` is a no-op with a deprecation
  warning here; on 2.x it actually did something.

Running this lab's suite against a different pandas major version will
produce test failures that are not bugs — they are the exact behavioural
difference the lesson exists to teach. `expected-output/FIELDS.md` states
precisely which values are version-specific.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Step 6 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/`
to prove that nothing else does.

## What is deliberately *not* installed

**matplotlib**, **scipy** and **polars** are not installed in this
environment. The lesson's Tools section describes polars from its public
documentation as a design contrast to pandas — specifically, that polars
has no implicit row index at all, which is the single fact that sharpens
what this whole day is about: an index is not free, and it is not
decorative. **No output from polars, scipy or matplotlib is reproduced
anywhere** in this lab or its lesson; every place they are mentioned says
so plainly.

**scikit-learn** is not installed either. The lesson's AI-thread paragraph
references how a DataFrame index feeds into a training pipeline, but does
not run one.

## If you cannot install anything at all

pandas is not in the Python standard library, and there is no reduced path
through this lab without it — the whole point is pandas 3.0's specific
behaviour, which nothing else on your system will reproduce. If pandas
genuinely cannot be installed, read the lesson's captured output and
`expected-output/` directory instead; every number there came from a real
run and is not invented.
