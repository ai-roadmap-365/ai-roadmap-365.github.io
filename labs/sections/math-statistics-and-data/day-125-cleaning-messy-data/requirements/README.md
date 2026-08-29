# What is installed, why, and what it costs

Four packages, all free and open source, installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `pandas` | 3.0.5 | BSD 3-Clause | Every `fillna`, `dropna`, `ffill`, `to_numeric`, `.str`, `duplicated` and `groupby` call in this lab. |
| `pyarrow` | 25.0.1 | Apache 2.0 | pandas 3.0's default backend for the `str` dtype; installed for parity with Days 120-124 even though this lab's own assertions do not inspect it directly. |
| `numpy` | 2.5.2 | BSD 3-Clause | `np.nan`, and the seeded `np.random.default_rng` that builds `income_spending` and shuffles the sensor time series. |
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

**matplotlib**, **scipy** and **scikit-learn** are not installed in this
environment. The lesson's Tools section describes scikit-learn's
`SimpleImputer` and Great Expectations / pandera from their public
documentation as design contrasts to the hand-rolled contract this lab
builds — no output from any of them is reproduced anywhere in this lab or
its lesson; every place they are mentioned says so plainly.

## If you cannot install anything at all

pandas is not in the Python standard library, and there is no reduced
path through this lab without it. If pandas genuinely cannot be
installed, read the lesson's captured output and `expected-output/`
directory instead; every number there came from a real run and is not
invented.
