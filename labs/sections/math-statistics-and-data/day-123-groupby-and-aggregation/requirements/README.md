# What is installed, why, and what it costs

Four packages, all free and open source, installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `pandas` | 3.0.5 | BSD 3-Clause | Every `groupby`, `.agg`, `.transform` and `.filter` call in this lab. |
| `pyarrow` | 25.0.1 | Apache 2.0 | pandas 3.0's default backend for string and several nullable dtypes; installed for parity with Days 120-122 even though this lab's tables use plain numeric and object columns throughout. |
| `numpy` | 2.5.2 | BSD 3-Clause | `np.nan`, `np.average` for exercise 9's weighted mean, and `np.random.default_rng` for exercise 8's synthetic 200,000-row table. |
| `pytest` | 9.1.1 | MIT | The test harness every exercise is written against. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Every script
and test after that runs completely offline.

## What is deliberately *not* installed

**matplotlib**, **scipy** and **polars** are not installed in this
environment. The lesson's Tools section describes polars' `group_by`
from its public documentation as a design contrast to pandas — no output
from polars, scipy or matplotlib is reproduced anywhere in this lab or
its lesson; every place they are mentioned says so plainly.

## If you cannot install anything at all

pandas is not in the Python standard library, and there is no reduced
path through this lab without it. If pandas genuinely cannot be
installed, read the lesson's captured output and `expected-output/`
directory instead; every number there came from a real run and is not
invented.
