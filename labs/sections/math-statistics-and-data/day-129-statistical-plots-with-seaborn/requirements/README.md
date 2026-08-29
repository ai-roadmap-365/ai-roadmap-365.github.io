# What is installed, why, and what it costs

Five packages, all free and open source, installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `seaborn` | 0.13.2 | BSD 3-Clause | Every plotting call in this lab — `barplot`, `stripplot`, `boxplot`, `lineplot`, `catplot`, `relplot`, `set_theme`. |
| `matplotlib` | 3.11.1 | PSF-derived (BSD-style) | seaborn's drawing engine; every assertion reads matplotlib `Axes`, `Figure`, `Patch` and `Line2D` objects directly. |
| `pandas` | 3.0.5 | BSD 3-Clause | `team_scores`, `wide_revenue` and `long_revenue`; the `melt` call in exercise 5, continuing directly from Day 124. |
| `numpy` | 2.5.2 | BSD 3-Clause | Pulled in transitively by pandas and matplotlib; not called directly by this lab's own code. |
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

## What is deliberately *not* pinned here

`pyarrow` is not installed for this lab. Day 124's merge/reshape lab
pinned it for parity with the pandas-dtype days it built on; this lab's
three tables are plain `int64`/`object` columns with no Arrow-backed
dtype anywhere, and a `pip install --dry-run` of `seaborn==0.13.2`
against this lab's other pins does not pull `pyarrow` in as a
dependency, so it is left out rather than added for no reason.

`plotnine` and the Vega-Lite/Altair ecosystem, both discussed in the
lesson's Tools section, are **not installed**. Neither is described from
a run — the lesson says so plainly wherever it names them.

## If you cannot install anything at all

seaborn is not in the Python standard library, and there is no reduced
path through this lab without it. If seaborn genuinely cannot be
installed, read the lesson's captured output and this lab's
`expected-output/` directory instead; every number there came from a
real run and is not invented.
