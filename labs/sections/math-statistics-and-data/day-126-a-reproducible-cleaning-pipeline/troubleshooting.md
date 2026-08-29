# Troubleshooting

Grouped by the message you actually see.

## `ModuleNotFoundError: No module named 'pandas'`

The lab's dependencies live in its own `.venv`, not on your system Python.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the test suite at a Python that already has pandas 3.0.5
installed: `PYTHON=/path/to/python3 bash tests/run_tests.sh`.

## `pytest examples starter` fails with `import file mismatch`

This is expected, not a bug — do not try to work around it by renaming
files or adding `__init__.py`. `starter/` and `examples/` both define
modules named `data`, `steps`, `pipeline`, `conftest` and `test_pipeline`;
pytest imports test modules by their dotted name, and when the second
directory's `data.py` (for example) tries to import under a name pytest
already bound to the first directory's `data.py`, collection aborts
outright rather than silently running one directory's code under the
other's name. Run the two directories as two separate commands, always:

```bash
.venv/bin/pytest examples
.venv/bin/pytest starter
```

## `pipeline.ContractError: input contract violated: column 'amount' has dtype 'float64', expected 'str'`

You passed a pipeline's OUTPUT back into `pipeline.run_pipeline` (which
checks the INPUT contract) instead of `pipeline.apply_steps_logged` (which
does not). This is not a bug in the pipeline — the input contract exists
to catch freshly-ingested data with the wrong shape, and a pipeline's own
output is supposed to have `amount` as a float, exactly as the contract
would then correctly reject if it were re-checked. Idempotence is checked
with `apply_steps_logged`, never `run_pipeline`, for exactly this reason
— see exercise 1 and the docstring on `apply_steps_logged` in
`pipeline.py`.

## Exercise 1's "broken" step does not look non-idempotent to you

Print `once["amount"]` and `twice["amount"]` for order_id 7 side by side.
The first call clips to the 99th percentile of the ORIGINAL data (roughly
1236.5); by the time the second call runs, the top value has already been
pulled down, so the second call's 99th percentile is computed from a
narrower column and produces a lower ceiling (roughly 1223.675). If your
numbers do not match, confirm you ran `parse_currency_amount`,
`normalize_region_strings`, `dedupe_orders` and `impute_missing_amount`
first, in that order, before calling the broken clip step.

## Exercise 2's tie-break test shows the same order both ways

Confirm you actually reversed the row order before the second sort
(`prepared.iloc[::-1]`), not just re-sorted the same frame twice. A stable
sort's tie-break IS the arrival order — you have to change the arrival
order to see it matter.

## `pipeline.ContractError` is never raised in exercise 5

Confirm `monkeypatch.setattr` targets the `pipeline` module's own name for
the function (`pipeline.clip_amount_to_fixed_ceiling`), not
`steps.clip_amount_to_fixed_ceiling`. `pipeline.py` imported the function
by name into its own module namespace at import time; patching the copy
inside `steps` does not affect the name `pipeline.apply_steps_logged`
actually looks up when it calls it.

## Exercise 7's swapped-order result does not have 7 rows

Confirm you called `pipeline.run_pipeline_swapped_order`, not
`pipeline.run_pipeline`. The declared, correct order lives in
`run_pipeline`; the deliberately reversed order (used only to demonstrate
order-dependence) lives in the separate function `run_pipeline_swapped_order`.

## Exercise 8's reloaded `priority` column is not `Int64`

Confirm you checkpointed BEFORE calling `dedupe_orders` — the missing
`priority` value belongs to order_id 4, which survives deduplication
either way, but checkpointing straight after `parse_currency_amount` and
`normalize_region_strings` keeps the exercise closest to what the lesson
demonstrates. If you see `float64` with `NaN` instead of `Int64` with a
proper missing value, you likely wrote the frame through CSV at some
point instead of Parquet — CSV round-trips everything through text and
cannot represent a nullable integer's missing value without losing the
integer dtype (Day 121).

## `pip install` fails or hangs

You are offline, or a corporate proxy is blocking PyPI. This is the only
network-dependent step in the entire lab. Retry on a connection that can
reach `pypi.org`, or ask whoever manages your network for a mirror.
