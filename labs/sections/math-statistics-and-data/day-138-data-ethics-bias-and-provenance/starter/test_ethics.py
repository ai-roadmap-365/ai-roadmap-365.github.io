"""Your exercises for Day 138 — "Bias You Can Measure".

Nine exercises. Every test below currently calls `pytest.skip(...)` —
replace the skip with real assertions and delete the skip line. Read
`00_brief.md` for the exercise-by-exercise explanation, and `ethics.py`
for the measurement functions you are testing. `fixtures.py` holds the
survey counts, the reference population and the two datasheets.

Check yourself at any point:

    pytest starter -v

Never run `pytest examples starter` in one command — both directories
define a module named `test_ethics.py` and pytest aborts collection on
the clash. Run them as two separate commands.

The reference answer key lives in `examples/test_ethics.py` — read it
AFTER you have tried, never before.

Nothing in this lab reads a real dataset about real people. Every table is
constructed in `ethics.py` from a seeded generator, which is deliberate:
a lesson about who is missing from a dataset should not be taught on
people who never agreed to be in it, and a synthetic population has one
property no real one has — its true composition is known exactly, so
"under-represented by a factor of ten" is checkable rather than estimated.
"""

from __future__ import annotations

import pytest

import ethics as et
import fixtures as fx


def test_01_more_data_does_not_fix_a_biased_frame():
    pytest.skip(
        "The centrepiece. Call et.bias_variance_ladder(sizes=(500, 5000, "
        "50000), replicates=40, seed=138). Assert that in_sample_rmse stays "
        "between 1.0 and 1.4 at every n -- the model always looks fine. Then "
        "assert that abs(bias_b) is between 5.85 and 6.00 at every n AND that "
        "the spread (max minus min) across the three sample sizes is under "
        "0.05: a hundredfold more data does not move it. Then assert the "
        "opposite for variance -- each sd_b is more than 2.2 times the next "
        "one down the ladder, and the first is more than 5 times the last. "
        "Finally assert abs(bias_a) < 0.15 at every n, and that sample_share_b "
        "stays near et.FRAME_SHARE_B rather than converging on "
        "et.POPULATION_SHARE_B"
    )


def test_02_coverage_mismatch_is_computable():
    pytest.skip(
        "Call et.coverage_report(fx.SURVEY_COUNTS, fx.REFERENCE_SHARES). "
        "Assert total_variation_distance is approximately 0.0895833333 -- real, "
        "but small enough on its own to be reassuring, which is why it is not "
        "the number that matters. Assert representation_ratio['west'] is "
        "approximately 0.10416666 and below 0.15, that every other region's "
        "ratio sits between 0.9 and 1.2, that flagged == ['west'] and that "
        "worst_group == 'west'. Then prove the check can say 'fine': call it "
        "again with counts {'north': 400, 'south': 350, 'east': 150, 'west': "
        "100} and assert the distance is 0.0 and flagged is empty"
    )


def test_03_optimising_a_proxy_hurts_the_group_it_mismeasures():
    pytest.skip(
        "Call et.proxy_gap_experiment(seed=138). Assert proxy_correlation is "
        "above 0.90 -- the proxy passes the check most people run. Assert "
        "selected_share_b_by_target is about 0.25 (group B's real share, "
        "since both groups are drawn from the same need distribution). Assert "
        "selected_share_b_by_proxy is below half of population_share_b and "
        "below 0.10. Assert b_need_served_by_proxy is under 35% of "
        "b_need_served_by_target. Then assert the part that explains why "
        "nobody notices: need_served_by_proxy divided by need_served_by_target "
        "is between 0.97 and 1.0. Finally, check fx.PROXY_PAIRS contains "
        "('arrests recorded', 'offences committed') and that no pair has the "
        "proxy equal to the target"
    )


def test_04_one_pooled_model_is_worse_for_every_subgroup():
    pytest.skip(
        "Call et.aggregation_bias_experiment(n_per_group=2000, seed=138). "
        "Assert every entry of per_group_fit has a slope between -1.1 and -0.9 "
        "-- both subgroups genuinely trend downward. Then assert pooled_slope "
        "is above 1.5 and sign_flip is True: the single model has the wrong "
        "SIGN for every subgroup. Then compare pooled_rmse_by_group against "
        "per_group_rmse_by_group and assert that for BOTH 'A' and 'B' the "
        "pooled error is larger, that each pooled error is above 4.0 and each "
        "per-group error below 1.2, and that pooled_worse_for_every_group is "
        "True"
    )


def test_05_fairness_criteria_are_in_genuine_tension(fairness_pop):
    pytest.skip(
        "Call et.calibration_by_score_bin(fairness_pop) and assert the maximum "
        "deviation is 0.0 -- the score is perfectly calibrated for both groups "
        "by construction. Call et.base_rates(fairness_pop) and assert A is 0.66 "
        "and B is 0.34. Then evaluate all three policies with "
        "et.evaluate_policy(name, fairness_pop). For 'single_threshold' assert "
        "the selection rates are 0.85 and 0.35, parity_gap is 0.50, "
        "equal_opportunity_gap exceeds 0.30 and precision_gap exceeds 0.10. For "
        "'demographic_parity' assert parity_gap is exactly 0.0 while "
        "equal_opportunity_gap exceeds 0.10 and precision_gap exceeds 0.30. For "
        "'equal_opportunity' assert equal_opportunity_gap is exactly 0.0 with "
        "both true-positive rates at 0.80, while parity_gap exceeds 0.10 and "
        "precision_gap exceeds 0.25. Finally call et.fairness_incompatibility() "
        "and assert any_policy_satisfies_all is False, and that no policy in "
        "its 'satisfied' map has all three flags True. Assert the "
        "INCOMPATIBILITY -- do not assert that one of the three policies is the "
        "right one, because that is a value judgement and not something this "
        "arithmetic can settle"
    )


def test_06_uniqueness_on_a_few_quasi_identifiers(register, generalised):
    pytest.skip(
        "Assert the register has 5000 rows and a 'diagnosis' column. Call "
        "et.unique_row_count(register, et.QUASI_IDS) and assert it equals 2723 "
        "and is more than half the table -- these are rows that are the ONLY "
        "row with their birth year, postcode and sex, in a table carrying no "
        "name and no identifier. Then call et.unique_row_count(generalised, "
        "et.GENERALISED_QUASI_IDS) and assert it equals 13 and is under one "
        "hundredth of the exact count: coarsening ONE field collapses "
        "uniqueness by two orders of magnitude. Assert the generalised frame "
        "still has both birth_year and birth_decade and the same row count"
    )


def test_07_k_anonymity_holds_and_still_discloses(generalised):
    pytest.skip(
        "Assert et.k_anonymity_level(generalised, et.GENERALISED_QUASI_IDS) is "
        "1 -- generalisation alone does not buy k-anonymity. Call "
        "et.suppress_small_classes(generalised, et.GENERALISED_QUASI_IDS, 5), "
        "assert the surviving table's k level is at least 5, that exactly 794 "
        "rows were suppressed, that 4206 remain, and that the suppressed "
        "fraction is between 0.10 and 0.25 -- the cost is paid in rows, and the "
        "rows it costs are the unusual ones. Then the limit: call "
        "et.homogeneous_table(), assert its k level is 4, and call "
        "et.homogeneous_classes(table, et.GENERALISED_QUASI_IDS, 'diagnosis', "
        "4). Assert there is exactly one leaking class, of size 4, with "
        "distinct_sensitive_values == 1, disclosed_value == 'diabetes' and "
        "class == (1970, '1001', 'F'). k-anonymity held and the sensitive "
        "attribute came out anyway"
    )


def test_08_datasheet_contract_names_every_missing_field():
    pytest.skip(
        "Call et.check_datasheet(fx.INCOMPLETE_DATASHEET). Assert complete is "
        "False and that missing equals fx.EXPECTED_MISSING_FROM_INCOMPLETE "
        "exactly, with 8 entries -- named, not counted. Assert 'purpose' (an "
        "empty string) and 'population_definition' (an explicit None) are both "
        "in missing, while 'collector' and 'licence' are not. Then call it on "
        "fx.COMPLETE_DATASHEET and assert complete is True, missing is empty, "
        "the checked list matches et.DATASHEET_REQUIRED_FIELDS and there are 11 "
        "required fields. Finally assert that at least one entry of "
        "fx.COMPLETE_DATASHEET['known_gaps'] mentions 'west' -- exercise 2's "
        "coverage gap, written down where the next reader will find it"
    )


def test_09_version_drift_that_summary_statistics_hide(versions):
    pytest.skip(
        "Unpack v1, v2 = versions and call et.diff_versions(v1, v2). Assert "
        "summary_identical is True and that count, mean, std, min, median and "
        "max are each EQUAL between the two summaries -- not close, equal. Then "
        "assert group_shares_old is {'A': 0.5, 'B': 0.5}, group_shares_new is "
        "{'A': 0.75, 'B': 0.25}, composition_shift is 0.25, material_shift is "
        "True and summary_hides_the_change is True. Then assert the provenance "
        "record is what makes it visible: frame_changed is True, "
        "changelog_explains is True, there is exactly one new changelog entry, "
        "and that entry contains both 'quota' and '50% to 25%'. Finally assert "
        "et.check_datasheet(version.datasheet)['complete'] is True for both "
        "versions -- the comparison was only possible because both releases "
        "were documented"
    )
