# What is installed, why, and what it costs

Four packages, all free and open source, all installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | `numpy.random.default_rng` for the seeded dataset and the seeded exploration/confirmation split; array maths for the difference of means. |
| `pandas` | 3.0.5 | BSD 3-Clause | The frame the worked study ingests, asserts a grain on, cleans, splits and measures. |
| `matplotlib` | 3.11.1 | matplotlib licence (BSD-style, PSF-derived) | The worked study's two figures, rendered headless through the `Agg` backend and saved as byte-deterministic PNGs. |
| `pytest` | 9.1.1 | MIT | The reference suite (54 tests) and your running score in `starter/` (33 tests once every exercise is solved). |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially. Everything else the lab needs is standard
library: `hashlib` for the checksums and the manifest, `json` for the study's
machine-readable records, `re` for the four Markdown parsers, `math.erf` for
the normal distribution behind the confidence interval, and `textwrap` for the
deterministic report layout.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Everything after
it runs entirely offline against a CSV file committed inside the lab.

## Why the study directory uses JSON and not YAML

`SOURCE.json`, `INGEST.json`, `FIGURES.json` and `MANIFEST.json` would be YAML
in most real studies. They are JSON here because `json` is in the standard
library and no YAML parser is, so the harness carries no dependency the study
does not already need. Every one of the eight gates works unchanged against a
YAML study directory if you swap `json.loads` for `yaml.safe_load`.

## What is deliberately *not* installed

**`seaborn`** is not in this lab's `requirements.txt`, so it is not installed
into the lab's virtual environment. Day 129 used it for statistical plots and
it would draw this lab's box plot in one line; the worked study uses plain
matplotlib because a box plot and an overlapping histogram need nothing more,
and because one fewer dependency is one fewer version to pin for a figure that
has to hash identically on two runs. Seaborn's own documentation describes its
figure-level versus axes-level split; no seaborn output is reproduced anywhere
in this lab.

**`scipy`, `statsmodels` and `scikit-learn`** are not installed. The interval
in the worked study is built from `math.erf` alone, the Day 118 construction,
which is exact for the normal case and needs no package. No output from any of
those three is reproduced anywhere in this lab or its lesson.

**Jupyter / `nbconvert`** is not installed. Day 139 covers the notebook that
restarts and runs clean; this lab's study runs as a plain module so that
"rebuild it and compare the bytes" is a one-line assertion.

## If you cannot install anything at all

You need pandas, NumPy and matplotlib for the worked study: the frame, the
seeded split and the two figures are all built on them. The **harness** is a
different matter — `acceptance.py` imports only `hashlib`, `json`, `re`,
`dataclasses` and `pathlib`, all standard library. If you can run Python at
all, you can run `check_study` against a study directory somebody else built.
