# Troubleshooting

Grouped by the message you actually see.

## `ModuleNotFoundError: No module named 'pandas'`

The lab's dependencies live in its own `.venv`, not on your system Python.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the test suite at a Python that already has pandas 3.0.5 and
pyarrow 25.0.1 installed: `PYTHON=/path/to/python3 bash tests/run_tests.sh`.

## Exercise 1's `code` column doesn't come back as missing for Namibia

You are probably running an older pandas whose `na_values` default list
differs, or you passed `keep_default_na=False` by accident. Check the
column's value directly with `pd.isna(df.loc[0, "code"])` — it should be
`True` on the default read. This lab's captured output on 3.0.5 shows
`NA` becoming `NaN` with no other argument passed.

## Exercise 2's `id` column already looks right without `dtype=`

If your source CSV genuinely has no leading zeros to lose (e.g. you typed
`123` instead of `00123`), the exercise has nothing to demonstrate — check
the exact file contents. The `dtype={"id": "str"}` argument matters
specifically when the column, if read numerically, would drop meaningful
leading characters.

## Exercise 3's precision numbers look "off by more than one"

Confirm you are computing `2**53 + 1` in Python (not in a shell arithmetic
context that silently overflows a fixed-width integer) and that the CSV
you wrote contains the digits of that exact number with no stray newline
or whitespace. `int(pd.read_csv(path)["order_id"].iloc[0])` should equal
`9007199254740993` before any `.astype("float64")` cast.

## Exercise 4 — the "chronological" order looks the same as the "string" order

This happens if every date in your test file happens to already be
zero-padded to the same width — the string sort and the datetime sort only
disagree when a format inconsistency exists. This lab's own example
deliberately writes one date as `2024-1-9` (no leading zero) specifically
to force the disagreement; check your file for the same kind of
inconsistency if you are not seeing one.

## Exercise 5 doesn't raise `UnicodeDecodeError`

Some byte sequences that are valid latin-1 also happen to be valid (but
different) UTF-8 — in that case you get silent mojibake instead of an
exception, which is the OTHER half of the danger this exercise is about.
If you genuinely see clean, correct text with `encoding="utf-8"` on a file
you wrote as latin-1, the specific bytes you chose happened not to trigger
either failure mode; try including an accented character outside the
first 128 code points, as this lab's reference script does.

## `pip install` fails or hangs

You are offline, or a corporate proxy is blocking PyPI. This is the only
network-dependent step in the entire lab — everything after installation
runs offline, writing only into `tempfile.mkdtemp()` directories that each
script removes itself before exiting. Retry on a connection that can reach
`pypi.org`, or ask whoever manages your network for a mirror.

## `bash tests/run_tests.sh` reports a version mismatch in section 1

The suite checks that the pandas installed in whatever Python it resolves
matches `requirements/requirements.txt` exactly (not just "at least"),
because this lab's captured output is tied to the exact pandas 3.0.5
behaviour described in `expected-output/FIELDS.md`. If you intentionally
want to see how an older pandas behaves differently, that is a legitimate
thing to explore — just do not expect this lab's checks to pass while you
do it.

## `.parquet` write fails with a pyarrow-related error

`to_parquet()` needs pyarrow, pinned in `requirements/requirements.txt`
alongside pandas. Reinstall with
`.venv/bin/pip install -r requirements/requirements.txt` and confirm with
`.venv/bin/python3 -c "import pyarrow; print(pyarrow.__version__)"`.

## A `.csv`, `.parquet` or `.db` file is left in the lab directory after a run

Every script in this lab writes into a `tempfile.mkdtemp()` directory and
deletes it in a `finally:` block before exiting, including on a failed
assertion. If a stray file appears, it most likely means a script was
interrupted mid-run (Ctrl-C, a killed process) before its cleanup ran.
Re-run the harness — `tests/run_tests.sh` section 6 checks specifically for
this and will fail loudly rather than pass silently over it.
