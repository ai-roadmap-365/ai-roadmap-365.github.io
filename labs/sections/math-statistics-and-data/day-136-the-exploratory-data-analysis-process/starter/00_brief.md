# The nine exercises

Work through these in order, in `exploration.py`. Check yourself as you go:

```bash
.venv/bin/pytest starter -q
```

Unattempted work reports as **skipped**, never failed. Wrong work **fails**
with your answer printed beside the correct one.

## 1. Forking paths, measured

`simulate_forking_paths(rng, k, families, n_per_group, alpha)`. Draw real
two-group samples for `families * k` independent comparisons at once
(vectorised: `rng.standard_normal((families, k, n_per_group))` for each
group), reduce to each comparison's z-statistic, and measure the fraction
of families with at least one significant comparison. Compare against the
exact formula `1 - (1 - alpha)**k` for k = 5, 20, 40, and assert the
simulated rate lands within three standard errors of it.

## 2. A plausible story for noise

`scan_narrative_frame(df, subset_cols, outcome_cols)`,
`best_significant_result(results)`. Run every (subset column, outcome
column, cut) combination as a real two-sample z-test with pandas, on data
built with `dataset.build_narrative_frame` -- no real signal anywhere.
Assert the winning comparison's effect size clears the conventional
"medium vs. large" boundary (d = 0.5), so you can see why a forking-paths
result is tempting to report, not just technically wrong.

## 3. The holdout rescues you -- the day's centrepiece

`build_holdout_frame`, `split_exploration_confirmation`,
`test_column_by_group`, `best_spurious_column`. Build one dataset with a
REAL planted effect and thirty SPURIOUS columns. Split it in half before
looking at anything. Test the real effect and the best-looking spurious
column (chosen from exploration only) on both halves. Assert the real
effect is significant on both; assert the spurious one is significant on
exploration but NOT on confirmation.

## 4. Choices are comparisons

`build_choices_frame`, `best_of_choice_grid`,
`simulate_choice_grid_best_p_rate`. Vary a recency cutoff and an outcome
definition -- ten silent variants, no test declared per variant -- and
measure how often the single best-looking cell is "significant" under a
true null, versus how often one pre-declared comparison is. Assert the
naive rate is well above alpha and the pre-declared rate sits near it.

## 5. Bonferroni, and its limit

`bonferroni_alpha(alpha, m)`, `simulate_family_wise_rate(rng, k, families,
alpha)`. Assert the corrected alpha restores the family-wise rate near
nominal when `m` is known and correct. Then assert that applying the SAME
corrected alpha to a search that actually ran more comparisons than were
reported pushes the real rate well back above alpha.

## 6. The research log as a data structure

`ResearchLog.record`, `.comparison_count`, `.null_count`, `.findings()`.
Every recorded question carries a timestamp, a look, and an outcome --
including `None` for "nothing found". Assert the log's own length equals
the number of comparisons actually run.

## 7. Triage

`triage_score(candidate)`, `rank_candidates(candidates)`. Score
`(expected_information * decision_relevance) / cost_hours` and rank
descending. Assert a cheap, decision-relevant question outranks an
expensive, less relevant one.

## 8. A stopping rule

`time_boxed_false_positive_rate`, `stop_when_significant_rate`. Both
simulate sessions of up to `budget_questions` looks at data with no real
signal. The time-boxed version reports a false positive only if the last
(pre-declared) question is significant; the "stop when significant"
version reports one if ANY question along the way was. Assert the first
sits near alpha and the second is several times higher.

## 9. The handoff to Day 133

`build_handoff`, `validate_handoff`, `write_report_stub`. Assemble the
object the report stage needs: the finding, its confirmation-set result,
and the comparison count. Assert it is refused when any field is missing,
and that `write_report_stub` refuses to run without a valid handoff.
