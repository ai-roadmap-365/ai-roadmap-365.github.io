# What is installed, why, and what it costs

Five packages, all free and open source, installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `seaborn` | 0.13.2 | BSD 3-Clause | `kdeplot` (exercises 3 and 4) and `ecdfplot` (exercise 6). |
| `matplotlib` | 3.11.1 | PSF-derived (BSD-style) | `hist`, `scatter`, `hexbin`, and every `Axes`/`Figure` object this lab's assertions read directly, including seaborn's own drawing engine underneath `kdeplot` and `ecdfplot`. |
| `pandas` | 3.0.5 | BSD 3-Clause | `.corr()` for Pearson (exercise 8) and `.rank()` for a hand-rolled Spearman. |
| `numpy` | 2.5.2 | BSD 3-Clause | Every sample in `data.py`, `histogram_bin_edges`, `percentile`, `polyfit`, `trapezoid`. Does almost all of the real work in this lab. |
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

## What is deliberately *not* installed here

`scipy` is **not** installed in this authoring environment. Two
consequences, both handled honestly rather than worked around silently:

- `scipy.stats.gaussian_kde` is described in the lesson from its public
  documentation only, and no output attributed to it is reproduced
  anywhere in this lab. The lab's own KDE work (exercises 3 and 4) uses
  `seaborn.kdeplot`, which ships its own bandwidth-estimation code and
  does **not** require `scipy` to run — confirmed directly in this
  environment.
- pandas' `Series.corr(method="spearman")` calls `scipy.stats.spearmanr`
  internally and raises `ModuleNotFoundError` here. Exercise 8 computes
  Spearman's correlation by its exact mathematical definition instead —
  the Pearson correlation of the two columns' `.rank()`-ed values — which
  needs no `scipy` at all.

`plotnine` and the Vega-Lite/Altair ecosystem, mentioned briefly in the
lesson's Tools section for a different reason, are **not installed**
either. Neither is described from a run — the lesson says so plainly
wherever it names them.

## If you cannot install anything at all

seaborn is not in the Python standard library, and there is no reduced
path through this lab without it. If seaborn genuinely cannot be
installed, read the lesson's captured output and this lab's
`expected-output/` directory instead; every number there came from a
real run and is not invented.
