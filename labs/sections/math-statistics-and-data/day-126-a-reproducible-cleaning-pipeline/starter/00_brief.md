# Day 126 lab — the brief

Nine exercises, in order. Work top to bottom in `test_pipeline.py`. The
pipeline itself lives in three modules you read but do NOT edit:

- `data.py` — `build_raw_orders()`, the seven-row messy input, and
  `CONFIG`, every threshold and mapping the pipeline reads.
- `steps.py` — seven pure step functions, each frame-to-frame, plus one
  deliberately broken step (`clip_amount_to_recomputed_percentile`) kept
  only so exercise 1 can run it and watch it fail.
- `pipeline.py` — orchestration: `check_input_contract`,
  `check_output_contract`, `apply_steps_logged`, `run_pipeline`,
  `run_pipeline_swapped_order`, `run_pipeline_via_pipe`, `content_hash`,
  `config_hash`, `checkpoint_to_parquet`, `load_checkpoint`,
  `build_manifest`.

Read all three once before you start. Every fixture you need
(`raw_orders`, `config`) comes from `conftest.py`.

Check yourself at any point:

```bash
.venv/bin/pytest starter -v
```

On an untouched checkout that prints `17 skipped`. A **skip** means "not
attempted". Replace a `pytest.skip(...)` line with real assertions and
delete it — when every skip is gone and the suite is green, you are
finished:

```bash
.venv/bin/pytest starter -q
echo $?
```

Assert exact values everywhere. Nothing in this lab depends on timing.

---

## Exercise 1 — idempotence

`pipeline(pipeline(df))` must equal `pipeline(df)` exactly. First reproduce
the failure that makes this worth checking: `steps.clip_amount_to_recomputed_percentile`
computes its clip threshold — the 99th percentile — from whatever data is
CURRENTLY passing through it. Run the real early steps by hand (parse,
normalise, dedupe, impute), then call the broken clip step once and again
on its own output. Assert the two results are NOT equal, and that order 7's
amount differs between the two calls (`approx(1236.5)`, then
`approx(1223.675)`).

Then prove the real pipeline does not share this flaw:
`pipeline.apply_steps_logged` reads every threshold from `config`, never
from the frame passing through it. Call it once, then again on its own
output, and assert the two frames are `.equals()` — exactly, no `approx`.

## Exercise 2 — determinism

Run the real pipeline twice, each time on a **fresh** `build_raw_orders()`
call. Assert the two output frames are `.equals()` and that
`pipeline.content_hash` agrees on both.

Then the tie-break. Orders 2 and 7 both land on `amount == 900.0` after
clipping. Show that sorting by `amount` alone gives a DIFFERENT tie order
depending on whether the rows arrived forward or reversed
(`prepared.iloc[::-1]`), then show that `steps.sort_deterministic` gives
the SAME order either way, because it names `order_id` as an explicit
tie-break.

## Exercise 3 — the step log reconciles

Run the pipeline and read its step log. For every consecutive pair of
steps, assert the earlier one's `rows_out` equals the later one's
`rows_in`. Assert the total change (`last rows_out - first rows_in`)
equals the sum of every step's `delta`, and that this equals `-1` — one row
deduplicated away. Then assert `dedupe_orders` is the ONLY step with a
non-zero delta.

## Exercise 4 — the input contract

Drop the `priority` column from `raw_orders` and assert
`pipeline.run_pipeline` raises `pipeline.ContractError` naming `priority`
in its message. Then cast `order_id` to `float64` and assert it raises
naming `order_id`.

## Exercise 5 — the output contract

Use `monkeypatch.setattr(pipeline, "clip_amount_to_fixed_ceiling", ...)` to
replace the clip step with a function that returns its input unchanged —
sabotage the pipeline's own promise that `amount` never exceeds the
configured ceiling. Assert `run_pipeline` now raises `ContractError`
mentioning "clip ceiling". Then, as a sanity check, run the UNMODIFIED
pipeline and call `pipeline.check_output_contract` on its result directly —
it must raise nothing, confirming the sabotage above, not something else,
was what triggered the failure.

## Exercise 6 — `.pipe()` equivalence

Assert `pipeline.run_pipeline(raw_orders, config)[0]` and
`pipeline.run_pipeline_via_pipe(raw_orders, config)` are `.equals()`.

## Exercise 7 — order dependence

`normalize_region_strings` before `dedupe_orders` is the pipeline's
declared order, and this lab's data makes it matter: order_id 3 is a
resubmission of order_id 1, differing only in region's whitespace and
casing (`" north"` vs `"north"`). Run the real pipeline and assert the
result has 6 rows, order_id 3 is gone, and order_id 1 survives. Then run
`pipeline.run_pipeline_swapped_order` (the same steps, dedupe run first)
and assert it has 7 rows — nothing deduplicated — with BOTH order_id 1 and
order_id 3 present.

## Exercise 8 — the Parquet checkpoint

Parse and normalise `raw_orders` (stop there — do not dedupe yet, so
order_id 4's missing `priority` is still present). Checkpoint it to
`tmp_path / "checkpoint.parquet"` with `pipeline.checkpoint_to_parquet`,
reload it with `pipeline.load_checkpoint`, and assert every dtype matches
exactly, the two frames are `.equals()`, and the reloaded `priority` column
is still `Int64` with order_id 4's value still missing.

## Exercise 9 — the manifest

Build a manifest from two independent `build_raw_orders()` runs through the
pipeline (`pipeline.build_manifest`). Assert `input_hash`, `config_hash`,
`output_hash` and `steps` all agree between the two. Then build a manifest
for `raw_orders`, change order_id 6's amount from `"$60.00"` to `"$60.01"`
(one character), and build a second manifest — assert `input_hash` and
`output_hash` both differ, `config_hash` stays the same (the config did not
change), and the row count is unaffected. Finally, round-trip a manifest
through `json.dumps`/`json.loads` and assert the reloaded `input_hash` and
`steps` match the original.

---

Prove your suite is not vacuous once you are green: re-break one assertion
on purpose (flip a comparison, change an expected number), confirm the run
exits non-zero with a printed `FAIL`, then restore it and confirm green
again.
