"""The worked reference suite for Day 126 -- "A Pipeline You Can Re-run".

Nine exercises, each proving one real property of a reproducible pandas
3.0.5 cleaning pipeline by running code and reading real values -- never by
reading source. Run it:

    pytest examples

Every table and every configuration value these tests use comes from
`data.py`. `steps.py` holds the seven pure step functions plus the one
deliberately broken step. `pipeline.py` composes them, checks contracts,
logs steps, hashes content, checkpoints to Parquet, and builds the
manifest. Read `starter/00_brief.md` for the exercise-by-exercise
explanation; this file is the answer key.
"""

from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

import pipeline as P
import steps as S
from data import CONFIG, build_raw_orders

# --------------------------------------------------------------------------
# Exercise 1 -- idempotence. pipeline(pipeline(df)) must equal pipeline(df)
# exactly. First, the worked failure: a step that recomputes its threshold
# from whatever data is currently passing through it is NOT idempotent.
# --------------------------------------------------------------------------


def test_1_broken_clip_step_is_not_idempotent(raw_orders, config):
    # Get to the point in the pipeline right before clipping, using the
    # real, correct earlier steps.
    prepared = S.parse_currency_amount(raw_orders)
    prepared = S.normalize_region_strings(prepared)
    prepared = S.dedupe_orders(prepared, config)
    prepared = S.impute_missing_amount(prepared, config)

    once = S.clip_amount_to_recomputed_percentile(prepared)
    twice = S.clip_amount_to_recomputed_percentile(once)

    # The two calls do NOT agree: the second call sees already-clipped
    # data, computes a new (lower) 99th percentile from it, and clips
    # again. This is exactly the failure the lesson opens with.
    assert not once.equals(twice), "the recomputing-percentile step is expected to NOT be idempotent"

    # Order 7's amount was clipped twice, to two different values.
    order_7_once = once.loc[once["order_id"] == 7, "amount"].iloc[0]
    order_7_twice = twice.loc[twice["order_id"] == 7, "amount"].iloc[0]
    assert order_7_once == pytest.approx(1236.5)
    assert order_7_twice == pytest.approx(1223.675)
    assert order_7_once != order_7_twice


def test_1_real_pipeline_is_idempotent(raw_orders, config):
    once, _ = P.apply_steps_logged(raw_orders, config)
    twice, _ = P.apply_steps_logged(once, config)

    # Every step in the real pipeline reads its thresholds from `config`,
    # never from the frame passing through it -- applying the whole
    # pipeline to its own output changes nothing.
    assert once.equals(twice)


# --------------------------------------------------------------------------
# Exercise 2 -- determinism. Two independent runs on the same input must
# produce an identical content hash, including after an explicit
# tie-breaking sort.
# --------------------------------------------------------------------------


def test_2_two_independent_runs_produce_an_identical_hash(config):
    df_a, _ = P.run_pipeline(build_raw_orders(), config)
    df_b, _ = P.run_pipeline(build_raw_orders(), config)

    assert df_a.equals(df_b)
    assert P.content_hash(df_a) == P.content_hash(df_b)


def test_2_tie_break_makes_the_final_order_deterministic_regardless_of_arrival_order(raw_orders, config):
    prepared, _ = P.apply_steps_logged(raw_orders, config)
    # Two rows -- order_id 2 and order_id 7 -- collide exactly at the clip
    # ceiling (900.0), so their relative order after a sort by `amount`
    # alone is not determined by the VALUES.
    tied = prepared.loc[prepared["amount"] == 900.0, "order_id"].tolist()
    assert sorted(tied) == [2, 7]

    # A stable sort by amount ALONE merely preserves whatever order the
    # rows happened to arrive in -- shuffle the arrival order and the tie
    # is broken differently.
    forward = prepared.sort_values("amount", kind="stable").reset_index(drop=True)
    reversed_input = prepared.iloc[::-1].reset_index(drop=True)
    backward = reversed_input.sort_values("amount", kind="stable").reset_index(drop=True)
    forward_tied_order = forward.loc[forward["amount"] == 900.0, "order_id"].tolist()
    backward_tied_order = backward.loc[backward["amount"] == 900.0, "order_id"].tolist()
    assert forward_tied_order != backward_tied_order, (
        "a sort with no tie-break is expected to depend on arrival order among tied rows"
    )

    # sort_deterministic names order_id as an explicit tie-break, so the
    # SAME two arrival orders now agree with each other.
    forward_final = S.sort_deterministic(prepared)
    backward_final = S.sort_deterministic(reversed_input)
    assert forward_final.equals(backward_final)
    assert forward_final.loc[forward_final["amount"] == 900.0, "order_id"].tolist() == [2, 7]


# --------------------------------------------------------------------------
# Exercise 3 -- the step log reconciles: every step's rows-out equals the
# next step's rows-in, and the total change equals the sum of the
# per-step changes.
# --------------------------------------------------------------------------


def test_3_step_log_reconciles_between_consecutive_steps(raw_orders, config):
    _, log = P.run_pipeline(raw_orders, config)

    for earlier, later in zip(log, log[1:]):
        assert earlier["rows_out"] == later["rows_in"], (
            f"{earlier['step']}'s rows_out must equal {later['step']}'s rows_in"
        )

    total_change = log[-1]["rows_out"] - log[0]["rows_in"]
    sum_of_deltas = sum(step["delta"] for step in log)
    assert total_change == sum_of_deltas == -1  # exactly one row deduplicated away


def test_3_step_log_shows_exactly_where_the_row_count_changed(raw_orders, config):
    _, log = P.run_pipeline(raw_orders, config)
    by_name = {step["step"]: step for step in log}

    assert by_name["dedupe_orders"]["delta"] == -1
    for name, step in by_name.items():
        if name != "dedupe_orders":
            assert step["delta"] == 0, f"{name} was expected to change no rows, delta was {step['delta']}"


# --------------------------------------------------------------------------
# Exercise 4 -- the input contract raises on a frame with a missing column
# or a wrong dtype, naming the offending column.
# --------------------------------------------------------------------------


def test_4_input_contract_raises_on_a_missing_column(raw_orders, config):
    broken = raw_orders.drop(columns=["priority"])
    with pytest.raises(P.ContractError, match="priority"):
        P.run_pipeline(broken, config)


def test_4_input_contract_raises_on_a_wrong_dtype(raw_orders, config):
    broken = raw_orders.copy()
    broken["order_id"] = broken["order_id"].astype("float64")
    with pytest.raises(P.ContractError, match="order_id"):
        P.run_pipeline(broken, config)


# --------------------------------------------------------------------------
# Exercise 5 -- the output contract raises when a step is sabotaged so its
# post-condition fails -- proving the contract can genuinely fail, not
# just pass.
# --------------------------------------------------------------------------


def test_5_output_contract_raises_when_the_clip_step_is_sabotaged(raw_orders, config, monkeypatch):
    def no_op_clip(df, config):  # a "clip" step that clips nothing
        return df

    monkeypatch.setattr(P, "clip_amount_to_fixed_ceiling", no_op_clip)

    with pytest.raises(P.ContractError, match="clip ceiling"):
        P.run_pipeline(raw_orders, config)


def test_5_output_contract_passes_once_the_step_is_restored(raw_orders, config):
    # Sanity check that the sabotage above is what triggers the failure,
    # not something else -- the unmodified pipeline must still pass.
    df, _ = P.run_pipeline(raw_orders, config)
    P.check_output_contract(df, config)  # raises nothing


# --------------------------------------------------------------------------
# Exercise 6 -- a .pipe() chain gives exactly the same frame as sequential
# application.
# --------------------------------------------------------------------------


def test_6_pipe_chain_equals_sequential_application(raw_orders, config):
    sequential, _ = P.run_pipeline(raw_orders, config)
    via_pipe = P.run_pipeline_via_pipe(raw_orders, config)
    assert sequential.equals(via_pipe)


# --------------------------------------------------------------------------
# Exercise 7 -- order dependence. Swapping normalize_region_strings and
# dedupe_orders changes the result: the declared order (normalise, then
# dedupe) catches a resubmitted order that arrives with different region
# casing; the reversed order misses it.
# --------------------------------------------------------------------------


def test_7_declared_order_catches_the_resubmitted_order(raw_orders, config):
    df, _ = P.run_pipeline(raw_orders, config)
    assert len(df) == 6
    assert 3 not in df["order_id"].tolist()  # the resubmission, order_id 3, is gone
    assert 1 in df["order_id"].tolist()  # the original, order_id 1, survives


def test_7_reversed_order_misses_the_resubmitted_order(raw_orders, config):
    swapped = P.run_pipeline_swapped_order(raw_orders, config)
    assert len(swapped) == 7  # nothing was deduplicated
    assert {1, 3}.issubset(set(swapped["order_id"].tolist()))  # BOTH survive


# --------------------------------------------------------------------------
# Exercise 8 -- a Parquet checkpoint round-trip preserves every dtype
# exactly, including a nullable Int64 column with a missing value.
# --------------------------------------------------------------------------


def test_8_parquet_checkpoint_preserves_every_dtype_exactly(raw_orders, tmp_path):
    before = S.normalize_region_strings(S.parse_currency_amount(raw_orders))
    checkpoint_path = tmp_path / "checkpoint.parquet"

    P.checkpoint_to_parquet(before, checkpoint_path)
    after = P.load_checkpoint(checkpoint_path)

    assert list(before.dtypes.astype(str)) == list(after.dtypes.astype(str))
    assert before.equals(after)

    # The nullable Int64 column, missing value included, round-trips exactly.
    assert str(before["priority"].dtype) == "Int64"
    assert str(after["priority"].dtype) == "Int64"
    assert before["priority"].isna().tolist() == after["priority"].isna().tolist()
    assert after.loc[after["order_id"] == 4, "priority"].isna().iloc[0]


# --------------------------------------------------------------------------
# Exercise 9 -- the manifest's hashes are stable across runs, and changing
# one input byte changes the input hash AND the output hash.
# --------------------------------------------------------------------------


def test_9_manifest_hashes_are_stable_across_independent_runs(config):
    df_a, log_a = P.run_pipeline(build_raw_orders(), config)
    manifest_a = P.build_manifest(build_raw_orders(), config, log_a, df_a)

    df_b, log_b = P.run_pipeline(build_raw_orders(), config)
    manifest_b = P.build_manifest(build_raw_orders(), config, log_b, df_b)

    assert manifest_a["input_hash"] == manifest_b["input_hash"]
    assert manifest_a["config_hash"] == manifest_b["config_hash"]
    assert manifest_a["output_hash"] == manifest_b["output_hash"]
    assert manifest_a["steps"] == manifest_b["steps"]


def test_9_changing_one_input_byte_changes_both_input_and_output_hash(raw_orders, config):
    original_df, original_log = P.run_pipeline(raw_orders, config)
    original_manifest = P.build_manifest(raw_orders, config, original_log, original_df)

    changed = raw_orders.copy()
    changed.loc[5, "amount"] = "$60.01"  # was "$60.00" -- one character different
    changed_df, changed_log = P.run_pipeline(changed, config)
    changed_manifest = P.build_manifest(changed, config, changed_log, changed_df)

    assert original_manifest["input_hash"] != changed_manifest["input_hash"]
    assert original_manifest["output_hash"] != changed_manifest["output_hash"]
    # The config did not change, so its hash must not change either.
    assert original_manifest["config_hash"] == changed_manifest["config_hash"]
    # Row count is unaffected -- only the one value changed.
    assert len(original_df) == len(changed_df) == 6


def test_9_manifest_is_json_serialisable(raw_orders, config):
    df, log = P.run_pipeline(raw_orders, config)
    manifest = P.build_manifest(raw_orders, config, log, df)
    # A manifest that cannot round-trip through JSON is not much of a
    # provenance record -- prove it actually can.
    serialised = json.dumps(manifest, sort_keys=True)
    reloaded = json.loads(serialised)
    assert reloaded["input_hash"] == manifest["input_hash"]
    assert reloaded["steps"] == manifest["steps"]
