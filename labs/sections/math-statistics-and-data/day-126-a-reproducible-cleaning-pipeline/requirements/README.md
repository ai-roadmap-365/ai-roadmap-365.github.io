# What is installed, why, and what it costs

Four packages, all free and open source, installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `pandas` | 3.0.5 | BSD 3-Clause | Every step function, `.pipe()` chain, `to_csv` (content hashing), `to_parquet`/`read_parquet` (checkpointing). |
| `pyarrow` | 25.0.1 | Apache 2.0 | pandas 3.0's Parquet engine — exercise 8's checkpoint round-trip goes through it. |
| `numpy` | 2.5.2 | BSD 3-Clause | Pulled in as a pandas dependency; nothing in this lab calls NumPy directly. |
| `pytest` | 9.1.1 | MIT | The test harness every exercise is written against, plus `monkeypatch` and `tmp_path` for exercises 5 and 8. |

`hashlib`, `json`, `logging` and `pathlib` — all standard library, no
install, no cost — do the rest: `hashlib` builds every hash in
`pipeline.py`, `json` serialises the manifest and the config for hashing,
and `pathlib.Path` is the type every checkpoint path uses.

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Every script
and test after that runs completely offline.

## What is deliberately *not* installed

**matplotlib**, **scipy**, **scikit-learn**, **polars**, **pandera** and
**Great Expectations** are not installed in this environment. The lesson's
Tools section describes `pandera`, Great Expectations, and a workflow
runner such as Prefect or Dagster from their public documentation as
design contrasts to this lab's hand-written contracts — no output from any
of them is reproduced anywhere in this lab or its lesson; every place they
are mentioned says so plainly.

## If you cannot install anything at all

pandas is not in the Python standard library, and there is no reduced path
through this lab without it. If pandas genuinely cannot be installed, read
the lesson's captured output and `expected-output/` directory instead;
every number there came from a real run and is not invented.
