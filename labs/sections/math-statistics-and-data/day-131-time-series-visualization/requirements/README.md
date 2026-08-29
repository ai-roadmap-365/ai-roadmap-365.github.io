# What is installed, why, and what it costs

Four packages, all free and open source, installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `pandas` | 3.0.5 | BSD 3-Clause | Every `DatetimeIndex`, `resample`, `rolling`, `melt`-adjacent reshape, and the `tz_convert` calls in exercise 9. |
| `matplotlib` | 3.11.1 | PSF-derived (BSD-style) | Every plot; every assertion reads matplotlib `Line2D`, `Axes` and `Figure` objects directly. |
| `numpy` | 2.5.2 | BSD 3-Clause | The aliasing signal (exercise 3), the log-space arithmetic (exercise 6), and array comparisons throughout. |
| `pytest` | 9.1.1 | MIT | The test harness every exercise is written against. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Every
script and test after that runs completely offline, headless, via
`matplotlib.use("Agg")`.

## Timezone data (exercise 9 only)

Exercise 9 converts UTC timestamps into `"America/New_York"`, which
requires an IANA timezone database. macOS and Linux ship one as part of
the operating system, and pandas (through Python's own `zoneinfo`) finds
it automatically — nothing extra to install on those platforms. If you
are on a system with no system timezone database (this is occasionally
true on a minimal Windows install), install the pure-Python fallback:

```bash
.venv/bin/pip install tzdata
```

That package is not pinned in `requirements.txt` because it was not
needed to produce this lab's own captured run (macOS, arm64) — it is
mentioned here only for the platform where it might be.

## What is deliberately *not* pinned here

`seaborn` is not installed for this lab. Days 129 and 130 already cover
seaborn's statistical plotting layer in depth; this lab's nine exercises
are all either plain pandas (`resample`, `rolling`, `tz_convert`) or the
matplotlib object API Day 128 already established, and nothing here
needs a statistical plotting library on top of that.

Plotly and Bokeh, both discussed in the lesson's Tools section for
interactive zooming on long series, are **not installed**. Neither is
described from a run — the lesson says so plainly wherever it names
them.

## If you cannot install anything at all

pandas is not in the Python standard library, and there is no reduced
path through this lab without it. If pandas genuinely cannot be
installed, read the lesson's captured output and this lab's
`expected-output/` directory instead; every number there came from a
real run and is not invented.
