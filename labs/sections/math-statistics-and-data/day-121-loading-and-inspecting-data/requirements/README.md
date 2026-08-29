# What is installed, why, and what it costs

Three packages, all free and open source, installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `pandas` | 3.0.5 | BSD 3-Clause | Every `read_csv`, `read_json`, `read_sql`, `read_parquet`, `to_csv` and `to_parquet` call in this lab. Pinned exactly because this day's captured output — dtypes, error messages, the `str` default — is version-specific. |
| `pyarrow` | 25.0.1 | Apache 2.0 | The engine behind `to_parquet()` / `read_parquet()` (exercise 7) and the storage backing pandas 3.0's default `str` dtype and `Int64` nullable arrays. |
| `numpy` | 2.5.2 | BSD 3-Clause | The random number generator behind the synthetic columns in exercises 6 and 9. |

`sqlite3`, `csv`, `json` and `io`, used in exercise 10 and the inspection
battery, are all standard library — nothing extra to install for them.

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## Why the versions are pinned exactly, not just floored

This lab's central claims are pandas-3.0-specific and would print
different, equally-correct values on pandas 2.x:

- A plain integer column of digits like `"00123"` is inferred as `int64`
  here; the exact inference rules for `dtype=` overrides have not changed
  across recent pandas majors, but the default string dtype it prints when
  you check `.dtypes` elsewhere in this lab (`str` versus `object`) has.
- The CSV-versus-Parquet dtype comparison in exercise 7 depends on the
  nullable `Int64` dtype's exact round-trip behaviour through
  `to_csv()`/`read_csv()`, which is consistent across recent pandas
  releases but is asserted here against the specific 3.0.5 install this
  lab was authored and captured on.
- `pd.Series(["a", "b"]).dtype` prints `str` on 3.0.5 (used throughout the
  inspection battery in exercise 8); it prints `object` on any pandas
  release before 3.0.

Running this lab's suite against a different pandas major version may
produce differences that are not bugs — `expected-output/FIELDS.md` states
precisely which values are version-specific and which are not.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Every script
this lab runs writes its own tiny CSV, JSON, SQLite database or Parquet
file into a temporary directory it created itself and deletes before
returning — nothing is downloaded, and no external dataset is fetched.

## What is deliberately *not* installed

**openpyxl**, **matplotlib**, **scipy** and **polars** are not installed in
this environment. The lesson's Tools section describes Excel support via
`openpyxl` from pandas' own documentation, since it is not installed here
— it says so plainly, and no output attributed to `read_excel()` is
reproduced anywhere in this lab or its lesson. polars' lazy `scan_csv` is
covered the same way, from its public documentation, as a design contrast.

## If you cannot install anything at all

pandas is not in the Python standard library, and there is no reduced path
through most of this lab without it. Exercise 10's stdlib-`csv` half is the
one part that would still run on a bare Python installation; everything
else genuinely needs pandas 3.0.5's specific behaviour, which nothing else
on your system will reproduce. If pandas cannot be installed, read the
lesson's captured output and this lab's `expected-output/` directory
instead; every number there came from a real run and is not invented.
