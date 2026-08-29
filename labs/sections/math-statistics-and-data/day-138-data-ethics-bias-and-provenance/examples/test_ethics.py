"""Reference answers for Day 138 — "Bias You Can Measure".

Nine exercises, all solved. Read `starter/test_ethics.py` and try them
first; this file is the answer key, and reading it early costs you the
only part of the day that is actually difficult.

Every assertion here is a claim about a synthetic table constructed in
`ethics.py` with known properties. No real dataset about real people is
read anywhere in this lab.
"""

from __future__ import annotations

import pytest

import ethics as et
import fixtures as fx


# ---------------------------------------------------------------------------
# 1. More data does not fix a biased frame
# ---------------------------------------------------------------------------


def test_01_more_data_does_not_fix_a_biased_frame():
    ladder = et.bias_variance_ladder(sizes=(500, 5_000, 50_000), replicates=40, seed=138)

    assert list(ladder["n"]) == [500, 5_000, 50_000]

    # The model looks fine. In-sample RMSE is about the size of the noise the
    # data was generated with, at every sample size -- nothing here says
    # "something is wrong".
    for rmse in ladder["in_sample_rmse"]:
        assert 1.0 < rmse < 1.4

    # The BIAS for the under-represented group does not move. It sits at the
    # intercept gap scaled by how little of group B the frame lets through:
    # 6.0 * (1 - 0.01) = 5.94, and it is still 5.94 after a hundredfold more
    # data.
    biases = [abs(b) for b in ladder["bias_b"]]
    for bias in biases:
        assert 5.85 < bias < 6.00
    assert max(biases) - min(biases) < 0.05, (
        "the bias must be flat across a hundredfold increase in n"
    )

    # The VARIANCE does move, and it moves the way sampling theory says it
    # should: roughly a factor of sqrt(10) per tenfold increase in n.
    sds = list(ladder["sd_b"])
    for smaller_n_sd, larger_n_sd in zip(sds, sds[1:]):
        assert smaller_n_sd / larger_n_sd > 2.2
    assert sds[0] / sds[-1] > 5.0

    # Meanwhile group A -- the group the frame does reach -- is fine. The
    # pooled model is wrong for exactly the group nobody measured.
    for bias_a in ladder["bias_a"]:
        assert abs(bias_a) < 0.15

    # And the sample's own composition never converges on the population's:
    # the frame is 1% group B whatever n is, against a true 10%.
    for share in ladder["sample_share_b"]:
        assert abs(share - et.FRAME_SHARE_B) < 0.005
        assert share < et.POPULATION_SHARE_B / 5


# ---------------------------------------------------------------------------
# 2. Coverage mismatch, computed
# ---------------------------------------------------------------------------


def test_02_coverage_mismatch_is_computable():
    report = et.coverage_report(fx.SURVEY_COUNTS, fx.REFERENCE_SHARES)

    # The single summary number is real but small, which is exactly why it is
    # not enough on its own: one region can be almost absent while the
    # distance between the two distributions still reads as "0.09".
    assert report["total_variation_distance"] == pytest.approx(0.0895833333, abs=1e-6)

    # The per-group ratio names the problem and quantifies it. The west
    # appears at roughly a tenth of its population share.
    ratios = report["representation_ratio"]
    assert ratios["west"] == pytest.approx(0.10416666, abs=1e-6)
    assert ratios["west"] < 0.15

    # Every other region is close to where it should be.
    for region in ("north", "south", "east"):
        assert 0.9 < ratios[region] < 1.2

    assert report["flagged"] == ["west"]
    assert report["worst_group"] == "west"

    # A sample that mirrors the reference produces a distance of exactly zero
    # and flags nobody -- the check is capable of saying "fine".
    matching = {"north": 400, "south": 350, "east": 150, "west": 100}
    clean = et.coverage_report(matching, fx.REFERENCE_SHARES)
    assert clean["total_variation_distance"] == pytest.approx(0.0, abs=1e-12)
    assert clean["flagged"] == []


# ---------------------------------------------------------------------------
# 3. The proxy gap
# ---------------------------------------------------------------------------


def test_03_optimising_a_proxy_hurts_the_group_it_mismeasures():
    result = et.proxy_gap_experiment(seed=138)

    # The proxy looks excellent by the check most people run.
    assert result["proxy_correlation"] > 0.90

    # Both groups are drawn from the same true-need distribution, so a fair
    # selection would take group B at roughly its population share of 0.25.
    # Ranking by the target does exactly that.
    assert result["selected_share_b_by_target"] == pytest.approx(0.25, abs=0.05)

    # Ranking by the proxy does not. Group B is selected at a small fraction
    # of its share, because the proxy records its need at 85% of the true
    # level and that is enough to push it below the cut.
    assert result["selected_share_b_by_proxy"] < 0.5 * result["population_share_b"]
    assert result["selected_share_b_by_proxy"] < 0.10

    # The true outcome is worse for group B, and by a lot.
    assert result["b_need_served_by_proxy"] < 0.35 * result["b_need_served_by_target"]

    # And the aggregate barely moves, which is why nobody notices: total need
    # served falls by under 3% while group B's share of it collapses.
    total_ratio = result["need_served_by_proxy"] / result["need_served_by_target"]
    assert 0.97 < total_ratio < 1.0

    # A named proxy and the thing it stands in for are two different things,
    # and the fixture list says so out loud.
    assert ("arrests recorded", "offences committed") in fx.PROXY_PAIRS
    for proxy, target in fx.PROXY_PAIRS:
        assert proxy != target


# ---------------------------------------------------------------------------
# 4. Aggregation bias
# ---------------------------------------------------------------------------


def test_04_one_pooled_model_is_worse_for_every_subgroup():
    result = et.aggregation_bias_experiment(n_per_group=2_000, seed=138)

    # Both subgroups genuinely trend downward.
    for fit in result["per_group_fit"].values():
        assert fit["slope"] < -0.9
        assert fit["slope"] > -1.1

    # The pooled fit trends upward. It is not merely imprecise; it has the
    # wrong sign for every subgroup in the data.
    assert result["pooled_slope"] > 1.5
    assert result["sign_flip"] is True

    pooled = result["pooled_rmse_by_group"]
    own = result["per_group_rmse_by_group"]
    assert set(pooled) == {"A", "B"}

    # Worse for EVERY subgroup, not worse on average.
    for group in ("A", "B"):
        assert pooled[group] > own[group]
        assert pooled[group] > 4.0
        assert own[group] < 1.2
    assert result["pooled_worse_for_every_group"] is True


# ---------------------------------------------------------------------------
# 5. The fairness tension, demonstrated
# ---------------------------------------------------------------------------


def test_05_fairness_criteria_are_in_genuine_tension(fairness_pop):
    # The score is perfectly calibrated for both groups: in every score bin,
    # the observed positive rate IS the score.
    calibration = et.calibration_by_score_bin(fairness_pop)
    assert float(calibration["deviation"].max()) == pytest.approx(0.0, abs=1e-12)

    # The two groups have different base rates. That single fact is the whole
    # engine of what follows.
    rates = et.base_rates(fairness_pop)
    assert rates["A"] == pytest.approx(0.66, abs=1e-9)
    assert rates["B"] == pytest.approx(0.34, abs=1e-9)
    assert rates["A"] != rates["B"]

    single = et.evaluate_policy("single_threshold", fairness_pop)
    parity = et.evaluate_policy("demographic_parity", fairness_pop)
    opportunity = et.evaluate_policy("equal_opportunity", fairness_pop)

    # One threshold for everyone leaves the calibrated score untouched and
    # violates both of the other two criteria.
    assert single["per_group"]["A"]["selection_rate"] == pytest.approx(0.85, abs=1e-9)
    assert single["per_group"]["B"]["selection_rate"] == pytest.approx(0.35, abs=1e-9)
    assert single["parity_gap"] == pytest.approx(0.50, abs=1e-9)
    assert single["equal_opportunity_gap"] > 0.30
    assert single["precision_gap"] > 0.10

    # Enforcing demographic parity closes the selection-rate gap EXACTLY and
    # opens the other two.
    assert parity["parity_gap"] == pytest.approx(0.0, abs=1e-9)
    assert parity["equal_opportunity_gap"] > 0.10
    assert parity["precision_gap"] > 0.30

    # Enforcing equal opportunity closes the true-positive-rate gap EXACTLY
    # and reopens the selection-rate gap.
    assert opportunity["equal_opportunity_gap"] == pytest.approx(0.0, abs=1e-9)
    assert opportunity["per_group"]["A"]["true_positive_rate"] == pytest.approx(
        0.80, abs=1e-9
    )
    assert opportunity["per_group"]["B"]["true_positive_rate"] == pytest.approx(
        0.80, abs=1e-9
    )
    assert opportunity["parity_gap"] > 0.10
    assert opportunity["precision_gap"] > 0.25

    # The assertion this exercise exists for: NO policy satisfies all three.
    # This is the incompatibility, not a preference between the policies.
    summary = et.fairness_incompatibility()
    assert summary["any_policy_satisfies_all"] is False
    for policy, flags in summary["satisfied"].items():
        assert not all(flags.values()), f"{policy} cannot satisfy all three"


# ---------------------------------------------------------------------------
# 6. Re-identification risk
# ---------------------------------------------------------------------------


def test_06_uniqueness_on_a_few_quasi_identifiers(register, generalised):
    assert len(register) == 5_000
    assert "diagnosis" in register.columns

    exact = et.unique_row_count(register, et.QUASI_IDS)
    coarse = et.unique_row_count(generalised, et.GENERALISED_QUASI_IDS)

    # Over half the rows are the only row with their birth year, postcode and
    # sex -- in a table that carries no name, no address and no identifier.
    assert exact == 2_723
    assert exact / len(register) > 0.50

    # Coarsening ONE field -- exact birth year to a ten-year band -- collapses
    # that by two orders of magnitude.
    assert coarse == 13
    assert coarse < exact / 100

    # The register itself is unchanged; generalisation added a column rather
    # than editing anyone's record in place.
    assert "birth_year" in generalised.columns
    assert "birth_decade" in generalised.columns
    assert len(generalised) == len(register)


# ---------------------------------------------------------------------------
# 7. k-anonymity as a check with limits
# ---------------------------------------------------------------------------


def test_07_k_anonymity_holds_and_still_discloses(generalised):
    # Generalisation alone does not buy k-anonymity: some bands still hold a
    # single person.
    assert et.k_anonymity_level(generalised, et.GENERALISED_QUASI_IDS) == 1

    kept, suppressed = et.suppress_small_classes(generalised, et.GENERALISED_QUASI_IDS, 5)

    # After suppression the table really is 5-anonymous.
    assert et.k_anonymity_level(kept, et.GENERALISED_QUASI_IDS) >= 5
    assert suppressed == 794
    assert len(kept) == 4_206
    # And it cost 794 rows -- roughly one in six people, all of them the
    # people in unusual combinations.
    assert 0.10 < suppressed / 5_000 < 0.25

    # Now the limit. This table is 4-anonymous by construction.
    table = et.homogeneous_table()
    assert et.k_anonymity_level(table, et.GENERALISED_QUASI_IDS) == 4

    # And it still discloses, because one of its classes is homogeneous in the
    # sensitive attribute: every member of it shares the same diagnosis, so
    # membership alone reveals it. No re-identification was required.
    leaks = et.homogeneous_classes(table, et.GENERALISED_QUASI_IDS, "diagnosis", 4)
    assert len(leaks) == 1
    leak = leaks[0]
    assert leak["size"] == 4
    assert leak["distinct_sensitive_values"] == 1
    assert leak["disclosed_value"] == "diabetes"
    assert leak["class"] == (1970, "1001", "F")


# ---------------------------------------------------------------------------
# 8. A datasheet contract
# ---------------------------------------------------------------------------


def test_08_datasheet_contract_names_every_missing_field():
    bad = et.check_datasheet(fx.INCOMPLETE_DATASHEET)

    assert bad["complete"] is False
    # Named, not counted: "documentation incomplete" is not actionable and
    # "no exclusion_criteria recorded" is.
    assert bad["missing"] == fx.EXPECTED_MISSING_FROM_INCOMPLETE
    assert len(bad["missing"]) == 8

    # An empty string and an explicit None both count as unanswered, because
    # a field that is present but blank tells a reader nothing.
    assert "purpose" in bad["missing"]
    assert "population_definition" in bad["missing"]
    # A field that IS answered is not reported.
    assert "collector" not in bad["missing"]
    assert "licence" not in bad["missing"]

    good = et.check_datasheet(fx.COMPLETE_DATASHEET)
    assert good["complete"] is True
    assert good["missing"] == []
    assert set(good["checked"]) == set(et.DATASHEET_REQUIRED_FIELDS)
    assert len(et.DATASHEET_REQUIRED_FIELDS) == 11

    # The complete datasheet documents the coverage gap from exercise 2 in
    # prose, which is the whole point: the gap is a known property of the
    # sampling frame, written down where the next reader will find it.
    assert any("west" in gap for gap in fx.COMPLETE_DATASHEET["known_gaps"])


# ---------------------------------------------------------------------------
# 9. Version drift
# ---------------------------------------------------------------------------


def test_09_version_drift_that_summary_statistics_hide(versions):
    v1, v2 = versions
    diff = et.diff_versions(v1, v2)

    # Every summary statistic of the measured column is IDENTICAL between the
    # two releases -- not close, identical. A reader diffing describe() output
    # sees nothing at all.
    assert diff["summary_identical"] is True
    for key in ("count", "mean", "std", "min", "median", "max"):
        assert diff["summary_old"][key] == diff["summary_new"][key]

    # And yet a quarter of the sample changed group.
    assert diff["group_shares_old"] == {"A": 0.5, "B": 0.5}
    assert diff["group_shares_new"] == {"A": 0.75, "B": 0.25}
    assert diff["composition_shift"] == pytest.approx(0.25, abs=1e-9)
    assert diff["material_shift"] is True
    assert diff["summary_hides_the_change"] is True

    # The provenance record is what makes the change visible: the sampling
    # frame field differs, and the changelog gained an entry naming why.
    assert diff["frame_changed"] is True
    assert diff["changelog_explains"] is True
    assert len(diff["changelog_new_entries"]) == 1
    assert "quota" in diff["changelog_new_entries"][0]
    assert "50% to 25%" in diff["changelog_new_entries"][0]

    # Both releases carry a complete datasheet, so the comparison above was
    # possible at all.
    for version in (v1, v2):
        assert et.check_datasheet(version.datasheet)["complete"] is True
