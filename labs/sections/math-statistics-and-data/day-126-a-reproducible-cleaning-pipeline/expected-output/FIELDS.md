# Expected output — what is stable and what may differ

Captured from a real run on 2026-08-19: macOS 26.5.2 (Apple Silicon,
arm64), Python 3.14.0, pandas 3.0.5, pyarrow 25.0.1, NumPy 2.5.2,
pytest 9.1.1.

## Stable on any correctly installed copy of this exact pandas version

- **Row counts and the step log.** The raw table has 7 rows; the real
  pipeline's output has 6 (`dedupe_orders` removes exactly 1); every other
  step's `delta` is 0. This is arithmetic on fixed literals, not a
  measurement — it will not differ on any machine.
- **Every numeric value in the pipeline's output**: `amount` values
  (60.0, 75.0, 120.5, 497.1, 900.0, 900.0), `amount_zscore` values, and the
  broken clip step's two results for order 7 (approximately 1236.5, then
  approximately 1223.675). These come from fixed literals and fixed
  arithmetic — no randomness, no timing, no machine-dependent rounding at
  the precision asserted.
- **The properties the manifest hashes are asserted to have**: equal
  across two independent runs on the same input; different when one input
  byte changes; the config hash unchanged when only the data changes.
  These are properties of the hash FUNCTION, not specific hex digests, and
  hold on any machine.
- **The Parquet round-trip dtypes**, including `priority` staying `Int64`
  with its missing value preserved. Parquet's schema is explicit about
  nullability, unlike CSV, so this is a property of the file format, not
  of this machine.
- **`pytest examples` and `pytest starter` reporting `17 passed` /
  `17 skipped` respectively**, and `pytest examples starter` failing to
  collect with `import file mismatch`. Verified directly in this
  repository, not assumed.
- **The harness total, `16 checks, 0 failure(s)`, exit 0.**

## Specific to pandas 3.0.5 (would differ on an older pandas)

- **`region` and `amount`'s input dtype is `str`, not `object`.** pandas
  3.0's default string-inference gives a plain Python string column its
  own dedicated `str` extension dtype. `pipeline.REQUIRED_INPUT_COLUMNS`
  encodes this explicitly, and it is the reason `parse_currency_amount`'s
  idempotence guard checks `is_numeric_dtype` rather than `dtype ==
  object` — the same correction Day 124's lab made for the identical
  reason.

## Machine-dependent — recorded here so it is never mistaken for universal

- **The literal hex strings of `content_hash` and `config_hash`.**
  `content_hash` is built from `DataFrame.to_csv()`'s exact bytes, which
  depend on pandas' float-to-string formatting; that formatting has been
  stable across recent pandas patch releases in this repository's
  experience but is not a documented guarantee of the CSV writer. This
  lab's tests never assert a specific digest for this reason — only that
  two runs on the same input agree, and that a changed input disagrees.
  Do not treat any digest printed by this lab as a value to check your own
  run against; check that YOUR two runs agree with each other instead.
- **`platform darwin`, the Python interpreter path, and `rootdir`** in
  `expected-output/examples-run.txt` and `expected-output/starter-run.txt`
  — captured from the authoring machine and sanitised to `<repo>` in place
  of the local filesystem path; your own run will show your own platform
  and path.
- **Wall-clock timing** in every pytest summary line (`in 0.08s`, and
  similar) — reported by pytest itself, and will differ machine to
  machine and run to run. Nothing in this lab's assertions depends on it.
