# What is captured here, and what may legitimately differ

All files in this directory are captured verbatim from real runs on the
authoring machine, on the date recorded in `metadata.yml`. `<repo>` stands
in for the absolute path to this repository on that machine.

## Values that are pandas-3.0-specific — will differ on pandas < 3.0

- **`08-inspection-battery.txt`** — `.dtypes` and `.info()` print `str` for
  the `region` column. On any pandas release before 3.0, the same column
  would print `object` instead, because pandas 3.0 changed the default
  dtype for a column of Python strings.
- **`04-dates.txt`** — the unparsed `date` column's dtype is reported as
  `str`; before pandas 3.0 it would print `object`. The chronological
  comparison itself (string sort disagreeing with datetime sort) does not
  depend on this and would reproduce identically on any pandas version.
- **`10-other-formats.txt`** — `read_json()`'s inferred `name` column dtype
  is `str` for the same reason.

## Values that would legitimately differ on another machine, but not by version

- **`09-category-memory.txt`** — the exact byte counts (`250,204` and
  `20,183` in this run) depend on the specific random values
  `np.random.default_rng(42)` produced for this pandas/NumPy build and on
  the platform's exact string-object overhead. The lab's own test asserts
  the **ratio** clears 5x, not the specific byte counts, precisely because
  of this. The ratio measured on this run was **12.40x**.
- **`06-chunking.txt`** — the specific sum (`24972031` for the 06 example
  script's 50,000-row column, or whatever the harness's independent
  100-row check in section 4 produces) depends on the seeded random
  values, which are themselves stable given the same NumPy version and
  seed, but are not asserted as a fixed literal anywhere except within a
  single run's own two computations of the same file.
- **`platform`** line printed in `test-run.txt`'s section 1 — will read
  differently on Linux or Windows/WSL; only the pandas/pyarrow/NumPy
  version lines are asserted against `requirements.txt`.

## Values that are exact and version-independent

- **`01-the-namibia-trap.txt`**, **`02-leading-zeros.txt`** — the Namibia
  `NA`-as-missing-value behaviour and the leading-zeros-lost-by-default
  behaviour are both driven by `read_csv()`'s type-inference defaults,
  which have been stable across every recent pandas major release. These
  values do not depend on the 3.0 string-dtype change at all.
- **`03-precision-loss.txt`** — `2**53 + 1 = 9007199254740993` surviving
  `int64` inference exactly and losing its last digit through a `float64`
  cast is IEEE 754 floating-point behavior, inherited from the platform's
  double-precision float representation, not from pandas' version.
- **`07-csv-vs-parquet.txt`** — the CSV round-trip promoting a nullable
  `Int64` column with a missing value to `float64`, and the Parquet
  round-trip preserving `Int64` exactly, are both driven by CSV's
  plain-text-with-inference nature versus Parquet's typed columnar
  storage — not by the pandas-3.0 string-dtype change.
- **`05-encoding.txt`** — `UnicodeDecodeError` on a latin-1 file read as
  UTF-8 is Python's standard-library `codecs` behaviour, unrelated to
  pandas' version.

## Absolute paths

No absolute path from the authoring machine appears in any captured file —
every script here writes into a directory created by `tempfile.mkdtemp()`
at run time and reports only relative filenames or values, never the full
temporary path.
