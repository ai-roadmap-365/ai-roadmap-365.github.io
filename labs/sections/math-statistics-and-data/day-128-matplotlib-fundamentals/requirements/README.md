# What is installed, why, and what it costs

Three packages, all free and open source, all installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `matplotlib` | 3.11.1 | PSF-derived (matplotlib licence, BSD-compatible) | Every chart in this lab: the object API, `savefig`, subplots, scales, legends, and the Agg backend that lets all of it run headless. |
| `numpy` | 2.5.2 | BSD 3-Clause | Small arrays for exercise 2's exact data round-trip check. Not central to this lab the way it was to earlier days -- matplotlib is the subject here. |
| `pytest` | 9.1.1 | MIT | The reference suite (19 tests) and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 6 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/`
to prove that nothing else does.

## What is deliberately *not* installed

**`seaborn`** builds statistical plots (distributions, categorical
comparisons, regression fits) on top of matplotlib's Axes objects — every
`sns.lineplot(..., ax=ax)` call returns the same kind of Axes this lab's
tests assert on. It is genuinely installed in the authoring environment
and used for real in Day 129, which owns it; this lab's own tests and
scripts do not import it, so no seaborn output is captured here.

**`plotnine`** is a grammar-of-graphics library (the `ggplot2` model,
ported to Python): charts are built by adding layers — `ggplot(df) +
aes(x=..., y=...) + geom_point() + facet_wrap(...)` — rather than by
calling methods on a named Axes. It is not installed here and **no output
from it is reproduced anywhere** in this lab or its lesson; the lesson's
Tools section describes it from its public documentation only.

**`plotly`** builds interactive, browser-rendered charts (`plotly.express`
and `plotly.graph_objects`) with zoom, hover tooltips and export to
static images through a separate `kaleido` dependency. It is not
installed here either, and is described from documentation only, with the
same "not run here" note.

## If you cannot install anything at all

matplotlib is the one package this lab cannot do without — every exercise
is about the Figure/Axes/Artist object model matplotlib defines, and there
is no meaningful stand-in for it using only the standard library. If
matplotlib genuinely cannot be installed, the ideas in this lesson (the
two APIs, `savefig`'s pixel arithmetic, testing a chart by asserting on
its artists rather than its pixels) can still be read and reasoned about,
but this lab's exercises and tests are not written against any other path.
