# Week 18 project — Messy Dataset Rescue

This week was **pandas and Data Wrangling**: Series and DataFrames, loading
and inspecting (and the traps `read_csv` sets for you), selecting and
filtering (and the partition invariant that filtering can silently break),
groupby, merging and reshaping, cleaning messy data, and finally a
reproducible cleaning pipeline built from named, idempotent steps.

Day 126 gave you a dataset the course had already chosen and walked you
through a pipeline for it. This project hands you nothing. You go find a
genuinely messy dataset — one you did not create and cannot quietly patch
from memory — and rescue it. The cleaned file is not the deliverable. The
deliverable is `DAMAGE_REPORT.md`: an account of every change you made to
the data and what it cost. Anyone can hand over a tidy-looking CSV. The
professional act is being able to say, for every column you touched, what it
looked like before, what it looks like after, and what a downstream analyst
would need to know before trusting it. A submission with a spotless dataset
and no damage report has not understood this week, however clean the file
looks.

**Environment:** pandas 3.0.5, pyarrow 25.0.1 and NumPy 2.5.2 are what this
course ran on. scipy, matplotlib, scikit-learn, polars and pandera are not
available — every check in your pipeline is code you wrote yourself, exactly
as on Days 121–126. There is no library that will grade your cleaning for
you.

## What you are building

A pipeline package with no notebook at its center:

```
rescue/
  contracts.py     # input contract, output contract — both actually raise
  steps.py         # named, pure, idempotent cleaning functions
  pipeline.py       # runs the steps in order, keeps the step log
  profile.py        # the Day 121 inspection battery, before and after
  manifest.py        # input hash, config, step log, output hash
run.py               # entry point: profile -> clean -> validate -> write
data/
  raw/<your-file>.csv          # the dataset you found, untouched
  clean/<your-file>.parquet    # the pipeline's output
PROFILE_BEFORE.md
DAMAGE_REPORT.md
manifest.json
```

`run.py` must be runnable twice on the same raw file and produce the same
output hash both times (Day 126's idempotence and determinism). Every step
in `steps.py` is a plain function: it takes a DataFrame (and maybe some
config) and returns a DataFrame, with no hidden state and no step that
reaches back to mutate what an earlier step already touched.

## Requirements

- **A dataset you did not create, with real defects.** A public open-data
  CSV, an export from a tool you use, or a scrape of your own earlier work —
  not a file invented for this project. It must have at least: missing
  values, one column whose type `read_csv` infers wrongly, duplicate rows on
  some key, and inconsistent category labels (case, whitespace, or spelling
  variants of the same value). If your chosen dataset is missing one of
  these defects, say so plainly in `DAMAGE_REPORT.md` rather than
  manufacturing a defect that was not really there — an honest gap is worth
  more than a fabricated one.
- **A profiling pass before any cleaning**, written to `PROFILE_BEFORE.md`
  before a single row is changed. Run the Day 121 inspection battery
  (`.shape`, `.dtypes`, `.info()`, `.describe()`, null counts) and record the
  missingness pattern per column — which columns are missing, how much, and
  whether the missingness looks structured (concentrated in certain rows or
  categories) or scattered. This file is your record of "before," captured
  before "before" is destroyed.
- **A pipeline of named pure functions** (Day 126), not cells in a notebook.
  Each step in `steps.py` must be idempotent — running it twice on its own
  output changes nothing further — and deterministic — the same input always
  produces the same output, with no unseeded randomness and no reliance on
  dict or set iteration order.
- **An input contract and an output contract that both actually fail.**
  Write a function that checks the raw data meets your stated assumptions
  (e.g. required columns present, key column has no nulls) and raises if it
  does not; write a second function that checks the cleaned output meets its
  own stated guarantees (e.g. no duplicate keys, no nulls in columns you
  promised to fill) and raises if it does not. Prove both by feeding each one
  input you know violates it and confirming it raises rather than warns or
  silently passes.
- **A step log that reconciles.** For every step: rows in, rows out, and
  cells changed. Print or write this as a table so a step that quietly drops
  a fifth of the data is visible in the log, not just in a final row count
  that nobody compared against the start.
- **Every cleaning decision paired with its measured cost.** If you imputed
  a column, report the mean, standard deviation and one correlation
  involving that column both before and after (Day 125 — imputation
  preserves the mean while it shrinks the variance; show that you actually
  measured the shrinkage rather than asserting it). If you dropped rows,
  report how many and whether the dropped rows differ systematically from
  the kept ones on at least one other column (a dropped-rows profile, not
  just a count). If you clipped or removed outliers, report what the
  extreme values were and your reasoning for judging them errors rather than
  facts about the world.
- **A `validate=`d join, if your dataset needs one.** If cleaning requires
  merging in a second table (a lookup, a reference file, a second export),
  state the cardinality you expect (`one_to_one`, `one_to_many`, and so on)
  and pass it to `validate=` so pandas raises if your assumption is wrong,
  rather than silently exploding your row count (Day 124). If your dataset
  needs no join, say so in `DAMAGE_REPORT.md` instead of inventing one.
- **A groupby check that reconciles against the whole.** Somewhere in your
  cleaning or profiling, group by at least one categorical column and
  confirm the group totals sum back to the ungrouped total — and confirm
  this explicitly for a version of the groupby with `dropna=False`, since
  the default silently drops rows with a missing group key (Day 123).
- **Type pinning at load, not repair afterwards, wherever it is possible.**
  Pass an explicit `dtype=` (or a post-load `astype` immediately after
  reading, if the CSV needs light coercion first) rather than fixing types
  several steps downstream. In `DAMAGE_REPORT.md`, name which columns needed
  pinning and what pandas' inference would have made them without it (a
  classic case: a leading-zero ID code read as an integer, silently losing
  the leading zeros).
- **A Parquet artifact as the pipeline's output**, written with pyarrow.
  Note in `DAMAGE_REPORT.md` which dtypes the CSV format would have lost or
  weakened (categorical levels collapsing to plain strings, a nullable
  integer column losing its distinction from float, a datetime column
  round-tripping as text) that the Parquet file preserves.
- **A manifest** (`manifest.json`) recording: a hash of the raw input file,
  the pipeline's configuration (which steps ran, in what order, with what
  parameters), the step log, and a hash of the final output file. Running
  `run.py` twice on the same input must produce a manifest with the same
  output hash both times.
- **`DAMAGE_REPORT.md`** — the deliverable that matters most. For every
  cleaning decision: what was changed, how many values, the distribution
  before and after, and what a downstream user must know before trusting the
  column. Close with one explicit, honest section: **what is still wrong
  with this dataset that you could not fix**, and why. Every real dataset
  has one; a report with none is a report that stopped looking too early.

## Steps

1. Find your dataset and read it raw, once, without cleaning anything. Run
   the Day 121 inspection battery by hand in a scratch session before
   writing any pipeline code, so you know what you are dealing with.
2. Write `PROFILE_BEFORE.md` from that raw pass — shape, dtypes, null
   counts per column, and the missingness pattern. This file is locked once
   you start cleaning; do not go back and edit it after the fact.
3. Write the input contract and prove it raises on data you know violates
   it (drop a required column from a copy, or introduce a null in a column
   you plan to require, and confirm the contract catches it).
4. Write the load step with explicit `dtype=` pinning for every column you
   can pin at load time. Note in your working notes which columns you could
   not pin at load and why.
5. Write the remaining cleaning steps one at a time — deduplication, missing
   value handling, category normalisation, outlier judgment — each as its
   own named function. Order matters: normalise category labels **before**
   deduplicating (see Troubleshooting), and decide deliberately whether
   deduplication happens before or after your groupby reconciliation check.
6. Add the step log: wrap each step call so it records rows in, rows out,
   and cells changed, and print the running table as the pipeline executes.
7. Write the output contract and prove it raises on cleaned output you
   deliberately re-break (reintroduce a duplicate key, or leave a null in a
   column your contract promises is complete).
8. Add the groupby reconciliation check and the `validate=`d join if your
   dataset needs one.
9. Write the Parquet output and the manifest (input hash, config, step log,
   output hash).
10. Run the whole pipeline twice on the untouched raw file. Confirm the two
    output hashes match exactly.
11. Write `DAMAGE_REPORT.md` last, once every number in it can be pulled
    from the step log or your before/after measurements — not from memory.

## Expected output

- `PROFILE_BEFORE.md` shows real defects: at least one column with missing
  values, one with a type `read_csv` inferred in a way you did not want, at
  least one duplicated key, and at least one category column with
  inconsistent labels — or an explicit note explaining which of these your
  chosen dataset genuinely lacks.
- The input contract raises (not warns) on deliberately corrupted input, and
  the output contract raises (not warns) on deliberately corrupted output.
  Both must be demonstrated, not just asserted to exist.
- Running `run.py` twice on the same raw file produces two manifests whose
  `output_hash` values are identical, character for character.
- The step log's row counts reconcile: the final row count plus every
  row-drop recorded in the log accounts for the starting row count, with no
  unexplained gap.
- The groupby check's group totals sum to the ungrouped total, checked with
  `dropna=False` as well as the default.
- The Parquet round-trip preserves at least one dtype distinction the raw
  CSV could not hold on its own (state which one — the specific column and
  dtype depend on your dataset, so name yours rather than expecting a fixed
  example here).
- `DAMAGE_REPORT.md` cites, for every cleaning decision, a number that traces
  back to the step log or to a before/after measurement you made — never a
  bare description of an action with no measured effect. Where a result
  depends on which dataset you chose (how much variance an imputed column
  lost, how many rows a dedup step removed, how skewed a dropped-rows
  profile is), report your own measured figure rather than expecting it to
  match any number stated here — this project is graded on the discipline of
  measuring, not on hitting a particular value.

## Validation

- [ ] The raw dataset is genuinely external (not authored for this project)
      and its defects are documented, or its missing defects are named
      honestly in `DAMAGE_REPORT.md`.
- [ ] `PROFILE_BEFORE.md` exists, was written before cleaning began, and
      records the Day 121 inspection battery plus per-column missingness.
- [ ] Every cleaning step is a named, pure function in `steps.py` — no
      notebook cells, no step with hidden state.
- [ ] The input contract raises on data violating it; the output contract
      raises on output violating it. Both demonstrated with a deliberately
      broken input.
- [ ] The step log records rows in, rows out and cells changed per step, and
      the row counts reconcile against the starting count.
- [ ] Every cleaning decision in `DAMAGE_REPORT.md` is paired with a
      measured before/after cost (mean/std/correlation shift for
      imputation, a systematic-difference check for drops, named extremes
      for clipped outliers).
- [ ] A `validate=`d join is used if the dataset needs one, with the
      cardinality assumption stated — or the report says no join was
      needed.
- [ ] A groupby check reconciles group totals against the whole, including
      with `dropna=False`.
- [ ] Types are pinned at load wherever possible, with a note on which
      columns needed pinning and what they would have become without it.
- [ ] The pipeline writes a Parquet artifact and names a dtype the CSV
      format would have lost.
- [ ] `manifest.json` records input hash, config, step log and output hash,
      and running the pipeline twice produces an identical output hash.
- [ ] `DAMAGE_REPORT.md` includes an explicit "what I could not fix"
      section.

## Troubleshooting

- Two runs on the same file produce different output hashes? Something in
  your pipeline is not deterministic — a common cause is iterating over a
  `dict` or `set` whose order is not guaranteed to be stable across runs, or
  a `sort_values()` with tied keys and no tiebreaker column, so equal rows
  land in a different order each time. Sort with an explicit tiebreaker and
  avoid any step whose output depends on hash-based iteration order.
- A step "looks idempotent" but the hash still drifts on a second run?
  Check for a step that appends or re-strips instead of setting — a
  normalisation step that does `.str.strip()` is idempotent, but one that
  appends a suffix (`+ "_cleaned"`) or that re-runs a regex substitution on
  already-substituted text is not, because running it twice compounds the
  change instead of leaving it unchanged.
- You imputed a column and it "looks fine" because the mean matches the
  original? The mean is the one statistic mean-imputation is specifically
  built to preserve — it is not evidence the imputation was safe. Check the
  standard deviation (it will have shrunk) and a correlation the column
  participates in (it will usually have weakened) before calling an
  imputation harmless.
- Your groupby totals do not match the ungrouped total? The default
  `dropna=True` on `groupby` silently removes every row whose group key is
  missing. Re-run with `dropna=False` and compare — the gap is exactly the
  count of rows with a missing key, and it needs to be accounted for
  somewhere in your step log, not quietly absorbed.
- A merge changed your row count in a way you did not expect? The join key
  had duplicates on one or both sides, and the merge produced the cross
  product of matching rows rather than a one-to-one match. Add
  `validate="one_to_one"` (or whichever cardinality you actually intended)
  and let pandas raise instead of finding out from a suspiciously large row
  count downstream.
- Category variants (`"NY"`, `"ny"`, `"New York "`) survived as separate
  rows after deduplication? Normalisation ran after deduplication instead of
  before, so rows that were logically the same value were still literally
  different strings when `drop_duplicates()` ran. Normalise first, dedupe
  second.
- A column you coerced with `pd.to_datetime(..., errors="coerce")` or
  `pd.to_numeric(..., errors="coerce")` turned out mostly missing after
  cleaning? `errors="coerce"` will happily convert an entire column to
  `NaT`/`NaN` if the format assumption is wrong for most of the rows — this
  usually means the real problem is a missing or wrong `format=`/date
  pattern, not that the column is genuinely full of unparseable values.
  Check a handful of the raw strings before trusting a coerced result.
- `DAMAGE_REPORT.md` reads like a changelog — a list of actions with no
  numbers? That is not a damage report. Every entry needs a measured before
  and after: how many values, what the distribution did, what a downstream
  user needs to know. An action with no measured effect is a note to
  yourself, not evidence the cleaning was safe.
