"""YOUR test suite for Day 126 -- "A Pipeline You Can Re-run". Nine exercises.

Run it from the lab directory, not from here:

    pytest starter -v

Every exercise below ends in a `pytest.skip(...)` line. pytest reports a
skip as `s` in the dot line and moves on, so an unfinished suite still
exits 0. Replace each skip with real assertions -- deleting the skip line
is part of the exercise. `starter/00_brief.md` explains each exercise in
full; `data.py`, `steps.py` and `pipeline.py` are the pipeline itself, not
exercises -- read them before you start.

Assert exact values everywhere; nothing in this lab depends on timing.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

import pipeline as P
import steps as S
from data import CONFIG, build_raw_orders

# --------------------------------------------------------------------------
# EXERCISE 1 -- idempotence. pipeline(pipeline(df)) must equal pipeline(df)
# exactly. First reproduce the worked failure, then prove the real
# pipeline does not share it. See starter/00_brief.md exercise 1.
#
# Check with:   pytest starter -v -k test_1
# --------------------------------------------------------------------------


def test_1_broken_clip_step_is_not_idempotent(raw_orders, config):
    pytest.skip(
        "exercise 1a: run parse_currency_amount, normalize_region_strings, dedupe_orders "
        "and impute_missing_amount, then call clip_amount_to_recomputed_percentile once and "
        "again on its own output. Assert the two results are NOT equal, and that order_id 7's "
        "amount differs between the two calls (approx 1236.5, then approx 1223.675)."
    )


def test_1_real_pipeline_is_idempotent(raw_orders, config):
    pytest.skip(
        "exercise 1b: call pipeline.apply_steps_logged on raw_orders, then call it again on "
        "that result. Assert the two frames are equal exactly (.equals(), no approx)."
    )


# --------------------------------------------------------------------------
# EXERCISE 2 -- determinism. Two independent runs on the same input must
# hash identically, and an explicit tie-break must make the final row
# order independent of arrival order.
#
# Check with:   pytest starter -v -k test_2
# --------------------------------------------------------------------------


def test_2_two_independent_runs_produce_an_identical_hash(config):
    pytest.skip(
        "exercise 2a: run the pipeline twice, each time on a FRESH build_raw_orders() call. "
        "Assert the two output frames are .equals() and that pipeline.content_hash agrees on both."
    )


def test_2_tie_break_makes_the_final_order_deterministic_regardless_of_arrival_order(raw_orders, config):
    pytest.skip(
        "exercise 2b: order_id 2 and order_id 7 both land on amount 900.0 after clipping. "
        "Show that sorting by 'amount' ALONE gives a different tie order depending on whether "
        "the rows arrived forward or reversed (prepared.iloc[::-1]), then show that "
        "steps.sort_deterministic gives the SAME order either way, because it names order_id "
        "as an explicit tie-break."
    )


# --------------------------------------------------------------------------
# EXERCISE 3 -- the step log reconciles: every step's rows-out equals the
# next step's rows-in, and the total change equals the sum of the
# per-step changes.
#
# Check with:   pytest starter -v -k test_3
# --------------------------------------------------------------------------


def test_3_step_log_reconciles_between_consecutive_steps(raw_orders, config):
    pytest.skip(
        "exercise 3a: run the pipeline and get its step log. For every consecutive pair of "
        "steps, assert the earlier one's rows_out equals the later one's rows_in. Assert the "
        "total change (last rows_out minus first rows_in) equals the sum of every step's delta, "
        "and that this equals -1."
    )


def test_3_step_log_shows_exactly_where_the_row_count_changed(raw_orders, config):
    pytest.skip(
        "exercise 3b: from the same step log, assert 'dedupe_orders' has delta -1 and every "
        "other step has delta 0."
    )


# --------------------------------------------------------------------------
# EXERCISE 4 -- the input contract raises on a frame with a missing column
# or a wrong dtype, naming the offending column.
#
# Check with:   pytest starter -v -k test_4
# --------------------------------------------------------------------------


def test_4_input_contract_raises_on_a_missing_column(raw_orders, config):
    pytest.skip(
        "exercise 4a: drop the 'priority' column from raw_orders and assert pipeline.run_pipeline "
        "raises pipeline.ContractError with 'priority' in the message (pytest.raises(..., match=...))."
    )


def test_4_input_contract_raises_on_a_wrong_dtype(raw_orders, config):
    pytest.skip(
        "exercise 4b: cast 'order_id' to float64 and assert run_pipeline raises ContractError "
        "with 'order_id' in the message."
    )


# --------------------------------------------------------------------------
# EXERCISE 5 -- the output contract raises when a step is sabotaged so its
# post-condition fails -- proving the contract can genuinely fail.
#
# Check with:   pytest starter -v -k test_5
# --------------------------------------------------------------------------


def test_5_output_contract_raises_when_the_clip_step_is_sabotaged(raw_orders, config, monkeypatch):
    pytest.skip(
        "exercise 5a: use monkeypatch.setattr(pipeline, 'clip_amount_to_fixed_ceiling', a function "
        "that returns its input unchanged), then assert run_pipeline raises ContractError "
        "mentioning 'clip ceiling'."
    )


def test_5_output_contract_passes_once_the_step_is_restored(raw_orders, config):
    pytest.skip(
        "exercise 5b: run the UNMODIFIED pipeline and call pipeline.check_output_contract on "
        "its result directly -- it must raise nothing, confirming the sabotage above, not "
        "something else, was what triggered exercise 5a's failure."
    )


# --------------------------------------------------------------------------
# EXERCISE 6 -- a .pipe() chain gives exactly the same frame as sequential
# application.
#
# Check with:   pytest starter -v -k test_6
# --------------------------------------------------------------------------


def test_6_pipe_chain_equals_sequential_application(raw_orders, config):
    pytest.skip(
        "exercise 6: assert pipeline.run_pipeline(raw_orders, config)[0] and "
        "pipeline.run_pipeline_via_pipe(raw_orders, config) are .equals()."
    )


# --------------------------------------------------------------------------
# EXERCISE 7 -- order dependence. normalize_region_strings before
# dedupe_orders is the declared order, and it is not arbitrary.
#
# Check with:   pytest starter -v -k test_7
# --------------------------------------------------------------------------


def test_7_declared_order_catches_the_resubmitted_order(raw_orders, config):
    pytest.skip(
        "exercise 7a: run the real pipeline. Assert the result has 6 rows, order_id 3 (the "
        "resubmission) is gone, and order_id 1 (the original) survives."
    )


def test_7_reversed_order_misses_the_resubmitted_order(raw_orders, config):
    pytest.skip(
        "exercise 7b: run pipeline.run_pipeline_swapped_order. Assert it has 7 rows -- nothing "
        "was deduplicated -- and that BOTH order_id 1 and order_id 3 survive."
    )


# --------------------------------------------------------------------------
# EXERCISE 8 -- a Parquet checkpoint round-trip preserves every dtype
# exactly, including a nullable Int64 column with a missing value.
#
# Check with:   pytest starter -v -k test_8
# --------------------------------------------------------------------------


def test_8_parquet_checkpoint_preserves_every_dtype_exactly(raw_orders, tmp_path):
    pytest.skip(
        "exercise 8: parse and normalise raw_orders (do not dedupe yet, so order_id 4's missing "
        "priority is still present), checkpoint it to tmp_path / 'checkpoint.parquet' with "
        "pipeline.checkpoint_to_parquet, reload it with pipeline.load_checkpoint, and assert "
        "every dtype matches exactly, the frames are .equals(), and the reloaded 'priority' "
        "column is still Int64 with order_id 4's value still missing."
    )


# --------------------------------------------------------------------------
# EXERCISE 9 -- the manifest's hashes are stable across runs, and changing
# one input byte changes the input hash AND the output hash.
#
# Check with:   pytest starter -v -k test_9
# --------------------------------------------------------------------------


def test_9_manifest_hashes_are_stable_across_independent_runs(config):
    pytest.skip(
        "exercise 9a: build a manifest from two independent build_raw_orders() runs through the "
        "pipeline. Assert input_hash, config_hash, output_hash and steps all agree between the two."
    )


def test_9_changing_one_input_byte_changes_both_input_and_output_hash(raw_orders, config):
    pytest.skip(
        "exercise 9b: build a manifest for raw_orders, then change order_id 6's amount from "
        "'$60.00' to '$60.01' (one character) and build a second manifest. Assert input_hash and "
        "output_hash both differ, config_hash stays the same, and the row count is unaffected."
    )


def test_9_manifest_is_json_serialisable(raw_orders, config):
    pytest.skip(
        "exercise 9c: build a manifest, round-trip it through json.dumps/json.loads, and assert "
        "the reloaded input_hash and steps match the original manifest's."
    )
