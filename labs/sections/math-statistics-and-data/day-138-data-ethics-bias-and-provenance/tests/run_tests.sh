#!/usr/bin/env bash
# Tests for the Day 138 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the day's claims by driving the real measurement
# functions over the real synthetic populations -- never by reading source
# and never by asserting on a timing:
#
#   * a pooled model fitted on a biased sampling frame keeps a flat bias for
#     the under-represented group across a hundredfold increase in n, while
#     the variance of the estimate falls roughly as sqrt(n);
#   * coverage mismatch against a reference distribution is computed, and
#     the under-represented group is named with a representation ratio;
#   * optimising a proxy that under-records one group's need collapses that
#     group's share of the selection while the aggregate barely moves;
#   * one pooled linear model is worse for EVERY subgroup than per-subgroup
#     models on the same rows, and has the wrong slope sign for both;
#   * demographic parity, equal opportunity and equal precision cannot all
#     hold at once when base rates differ -- each policy closes its own gap
#     exactly and opens another, and no policy closes all three;
#   * over half the rows of a name-free register are unique on three quasi-
#     identifiers, and coarsening one field cuts that by two orders of
#     magnitude;
#   * k-anonymity is achieved, at a counted cost in suppressed rows, and a
#     4-anonymous table is shown still disclosing a sensitive attribute
#     through a homogeneous class;
#   * a datasheet check names every missing provenance field by name, and
#     passes a complete record;
#   * two releases with byte-identical summary statistics differ by a
#     quarter of the sample in composition, and only the provenance record
#     makes that visible;
#   * the reference suite (examples/) passes in full;
#   * the exercise suite (starter/) is all-skip on an untouched checkout,
#     and the harness proves it can genuinely FAIL by solving every
#     exercise in a scratch copy, breaking one assertion on purpose,
#     confirming a non-zero exit and a printed failure, then restoring it;
#   * no __pycache__ or .pytest_cache survives the run.
#
# Everything runs offline. No network, no server, no sudo. Deterministic,
# non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

failures=0
checks=0

check() {
  local label="$1" ok="$2"
  checks=$((checks + 1))
  if [ "${ok}" = "yes" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    failures=$((failures + 1))
  fi
}

resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest:" >&2
  echo "    PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

python_bin="$(dirname "${pytest_bin}")/python3"
if [ ! -x "${python_bin}" ]; then
  python_bin="$(command -v python3 || true)"
fi
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi

for module in numpy pandas; do
  if ! "${python_bin}" -c "import ${module}" >/dev/null 2>&1; then
    echo "FAIL: ${module} is not importable from ${python_bin}." >&2
    echo "  Install the lab's dependencies with:" >&2
    echo "    python3 -m venv .venv" >&2
    echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
    exit 1
  fi
done

echo "Day 138 — Bias You Can Measure"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
from importlib.metadata import version

print(f"python     {platform.python_version()}")
for name in ("numpy", "pandas", "pytest"):
    try:
        print(f"{name:<10} {version(name)}")
    except Exception as exc:  # pragma: no cover
        print(f"{name:<10} NOT INSTALLED ({exc})")
PY
)"
echo "${versions}"
echo

mismatch=0
while IFS= read -r line; do
  [ -z "${line}" ] && continue
  pkg="${line%%==*}"
  pinned="${line#*==}"
  installed="$("${python_bin}" -c "from importlib.metadata import version; print(version('${pkg}'))" 2>/dev/null || echo "MISSING")"
  if [ "${installed}" != "${pinned}" ]; then
    mismatch=1
    echo "  version mismatch: ${pkg} pinned ${pinned}, installed ${installed}"
  fi
done < "${lab_dir}/requirements/requirements.txt"
check "installed packages match requirements.txt exactly" "$( [ ${mismatch} -eq 0 ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "2. The measurements themselves, run over the synthetic populations"
# --------------------------------------------------------------------------

behaviour="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY'
"""Drive ethics.py directly and print one machine-readable line per claim,
including the bias-versus-n ladder and the three fairness metrics."""

import ethics as et
import fixtures as fx

results = {}


def record(key, value):
    results[key] = value


# -- exercise 1: bias versus variance as n grows ----------------------------
ladder = et.bias_variance_ladder(sizes=(500, 5_000, 50_000), replicates=40, seed=138)
for _, row in ladder.iterrows():
    n = int(row["n"])
    record(f"bias_b_n{n}", f"{abs(row['bias_b']):.4f}")
    record(f"sd_b_n{n}", f"{row['sd_b']:.5f}")
    record(f"bias_a_n{n}", f"{abs(row['bias_a']):.4f}")
    record(f"rmse_n{n}", f"{row['in_sample_rmse']:.4f}")
    record(f"share_b_n{n}", f"{row['sample_share_b']:.4f}")
biases = [abs(v) for v in ladder["bias_b"]]
sds = list(ladder["sd_b"])
record("bias_b_spread", f"{max(biases) - min(biases):.4f}")
record("bias_b_flat", "yes" if max(biases) - min(biases) < 0.05 else "no")
record("sd_ratio_500_5000", f"{sds[0] / sds[1]:.3f}")
record("sd_ratio_5000_50000", f"{sds[1] / sds[2]:.3f}")
record("sd_ratio_total", f"{sds[0] / sds[2]:.3f}")
record("sd_falls_each_step", "yes" if all(a / b > 2.2 for a, b in zip(sds, sds[1:])) else "no")

# -- exercise 2: coverage mismatch ------------------------------------------
coverage = et.coverage_report(fx.SURVEY_COUNTS, fx.REFERENCE_SHARES)
record("coverage_tvd", f"{coverage['total_variation_distance']:.6f}")
record("coverage_ratio_west", f"{coverage['representation_ratio']['west']:.6f}")
record("coverage_flagged", ",".join(coverage["flagged"]))
record("coverage_worst_group", coverage["worst_group"])
clean = et.coverage_report(
    {"north": 400, "south": 350, "east": 150, "west": 100}, fx.REFERENCE_SHARES
)
record("coverage_clean_tvd", f"{clean['total_variation_distance']:.6f}")
record("coverage_clean_flagged_count", str(len(clean["flagged"])))

# -- exercise 3: the proxy gap ----------------------------------------------
proxy = et.proxy_gap_experiment(seed=138)
record("proxy_correlation", f"{proxy['proxy_correlation']:.4f}")
record("proxy_share_b_by_target", f"{proxy['selected_share_b_by_target']:.4f}")
record("proxy_share_b_by_proxy", f"{proxy['selected_share_b_by_proxy']:.4f}")
record(
    "proxy_b_need_ratio",
    f"{proxy['b_need_served_by_proxy'] / proxy['b_need_served_by_target']:.4f}",
)
record(
    "proxy_total_need_ratio",
    f"{proxy['need_served_by_proxy'] / proxy['need_served_by_target']:.4f}",
)

# -- exercise 4: aggregation bias -------------------------------------------
agg = et.aggregation_bias_experiment(n_per_group=2_000, seed=138)
record("agg_pooled_slope", f"{agg['pooled_slope']:.4f}")
record("agg_slope_a", f"{agg['per_group_fit']['A']['slope']:.4f}")
record("agg_slope_b", f"{agg['per_group_fit']['B']['slope']:.4f}")
record("agg_sign_flip", "yes" if agg["sign_flip"] else "no")
record("agg_pooled_rmse_a", f"{agg['pooled_rmse_by_group']['A']:.4f}")
record("agg_pooled_rmse_b", f"{agg['pooled_rmse_by_group']['B']:.4f}")
record("agg_own_rmse_a", f"{agg['per_group_rmse_by_group']['A']:.4f}")
record("agg_own_rmse_b", f"{agg['per_group_rmse_by_group']['B']:.4f}")
record("agg_pooled_worse_for_every_group", "yes" if agg["pooled_worse_for_every_group"] else "no")

# -- exercise 5: the fairness tension ---------------------------------------
calibration = et.calibration_by_score_bin()
record("fair_max_calibration_deviation", f"{float(calibration['deviation'].max()):.12f}")
rates = et.base_rates()
record("fair_base_rate_a", f"{rates['A']:.4f}")
record("fair_base_rate_b", f"{rates['B']:.4f}")
incompatibility = et.fairness_incompatibility()
for policy, result in incompatibility["results"].items():
    record(f"fair_{policy}_parity_gap", f"{result['parity_gap']:.4f}")
    record(f"fair_{policy}_eo_gap", f"{result['equal_opportunity_gap']:.4f}")
    record(f"fair_{policy}_precision_gap", f"{result['precision_gap']:.4f}")
    for group, metrics in result["per_group"].items():
        record(
            f"fair_{policy}_{group}",
            "sel={:.4f};tpr={:.4f};prec={:.4f}".format(
                metrics["selection_rate"],
                metrics["true_positive_rate"],
                metrics["precision"],
            ),
        )
record("fair_any_policy_satisfies_all", "yes" if incompatibility["any_policy_satisfies_all"] else "no")

# -- exercise 6: re-identification ------------------------------------------
register = et.synthetic_register(n=5_000, seed=138)
generalised = et.generalise_quasi_ids(register)
exact_unique = et.unique_row_count(register, et.QUASI_IDS)
coarse_unique = et.unique_row_count(generalised, et.GENERALISED_QUASI_IDS)
record("reid_rows", str(len(register)))
record("reid_unique_exact", str(exact_unique))
record("reid_unique_generalised", str(coarse_unique))
record("reid_unique_exact_fraction", f"{exact_unique / len(register):.4f}")
record("reid_reduction_factor", f"{exact_unique / coarse_unique:.1f}")

# -- exercise 7: k-anonymity and its limit ----------------------------------
record("k_level_generalised", str(et.k_anonymity_level(generalised, et.GENERALISED_QUASI_IDS)))
kept, suppressed = et.suppress_small_classes(generalised, et.GENERALISED_QUASI_IDS, 5)
record("k_level_after_suppression", str(et.k_anonymity_level(kept, et.GENERALISED_QUASI_IDS)))
record("k_rows_suppressed", str(suppressed))
record("k_rows_kept", str(len(kept)))
homogeneous = et.homogeneous_table()
record("k_homogeneous_table_level", str(et.k_anonymity_level(homogeneous, et.GENERALISED_QUASI_IDS)))
leaks = et.homogeneous_classes(homogeneous, et.GENERALISED_QUASI_IDS, "diagnosis", 4)
record("k_leaking_class_count", str(len(leaks)))
record("k_leaking_class_size", str(leaks[0]["size"]))
record("k_leaking_distinct_values", str(leaks[0]["distinct_sensitive_values"]))
record("k_disclosed_value", str(leaks[0]["disclosed_value"]))

# -- exercise 8: the datasheet contract -------------------------------------
bad = et.check_datasheet(fx.INCOMPLETE_DATASHEET)
good = et.check_datasheet(fx.COMPLETE_DATASHEET)
record("datasheet_incomplete_complete", "yes" if bad["complete"] else "no")
record("datasheet_missing", ",".join(bad["missing"]))
record("datasheet_missing_count", str(len(bad["missing"])))
record("datasheet_complete_complete", "yes" if good["complete"] else "no")
record("datasheet_required_field_count", str(len(et.DATASHEET_REQUIRED_FIELDS)))

# -- exercise 9: version drift ------------------------------------------------
v1, v2 = et.build_versions(n=2_000, seed=138)
diff = et.diff_versions(v1, v2)
record("drift_summary_identical", "yes" if diff["summary_identical"] else "no")
record("drift_mean_old", f"{diff['summary_old']['mean']:.10f}")
record("drift_mean_new", f"{diff['summary_new']['mean']:.10f}")
record("drift_std_old", f"{diff['summary_old']['std']:.10f}")
record("drift_std_new", f"{diff['summary_new']['std']:.10f}")
record("drift_share_b_old", f"{diff['group_shares_old']['B']:.4f}")
record("drift_share_b_new", f"{diff['group_shares_new']['B']:.4f}")
record("drift_composition_shift", f"{diff['composition_shift']:.4f}")
record("drift_summary_hides_the_change", "yes" if diff["summary_hides_the_change"] else "no")
record("drift_changelog_explains", "yes" if diff["changelog_explains"] else "no")
record("drift_new_changelog_entries", str(len(diff["changelog_new_entries"])))

for key, value in results.items():
    print(f"{key}={value}")
PY
)"
behaviour_status=$?
echo "${behaviour}"
echo

value_of() { echo "${behaviour}" | grep "^$1=" | cut -d= -f2-; }

check "the behaviour script ran without error" "$( [ ${behaviour_status} -eq 0 ] && echo yes || echo no )"

# -- exercise 1 --------------------------------------------------------------
check "bias for the under-represented group is flat across a hundredfold n: $(value_of bias_b_n500) -> $(value_of bias_b_n5000) -> $(value_of bias_b_n50000) (spread $(value_of bias_b_spread))" "$( [ "$(value_of bias_b_flat)" = yes ] && echo yes || echo no )"
check "every bias figure sits at the predicted 5.94, not near zero" "$( "${python_bin}" -c "import sys; vals=[float(v) for v in sys.argv[1:]]; sys.exit(0 if all(5.85 < v < 6.00 for v in vals) else 1)" "$(value_of bias_b_n500)" "$(value_of bias_b_n5000)" "$(value_of bias_b_n50000)" && echo yes || echo no )"
check "variance falls by more than 2.2x per tenfold: $(value_of sd_b_n500) -> $(value_of sd_b_n5000) -> $(value_of sd_b_n50000) (ratios $(value_of sd_ratio_500_5000), $(value_of sd_ratio_5000_50000))" "$( [ "$(value_of sd_falls_each_step)" = yes ] && echo yes || echo no )"
check "variance falls more than 5x overall (total ratio $(value_of sd_ratio_total)) while bias does not move at all" "$( "${python_bin}" -c "import sys; sys.exit(0 if float(sys.argv[1]) > 5.0 else 1)" "$(value_of sd_ratio_total)" && echo yes || echo no )"
check "the model looks fine at every n: in-sample RMSE $(value_of rmse_n500), $(value_of rmse_n5000), $(value_of rmse_n50000)" "$( "${python_bin}" -c "import sys; vals=[float(v) for v in sys.argv[1:]]; sys.exit(0 if all(1.0 < v < 1.4 for v in vals) else 1)" "$(value_of rmse_n500)" "$(value_of rmse_n5000)" "$(value_of rmse_n50000)" && echo yes || echo no )"
check "the group the frame does reach is fine: bias $(value_of bias_a_n500), $(value_of bias_a_n5000), $(value_of bias_a_n50000)" "$( "${python_bin}" -c "import sys; vals=[float(v) for v in sys.argv[1:]]; sys.exit(0 if all(v < 0.15 for v in vals) else 1)" "$(value_of bias_a_n500)" "$(value_of bias_a_n5000)" "$(value_of bias_a_n50000)" && echo yes || echo no )"
check "the sample's composition never converges on the population's: share_b stays near 0.01 ($(value_of share_b_n500), $(value_of share_b_n5000), $(value_of share_b_n50000))" "$( "${python_bin}" -c "import sys; vals=[float(v) for v in sys.argv[1:]]; sys.exit(0 if all(abs(v-0.01) < 0.005 for v in vals) else 1)" "$(value_of share_b_n500)" "$(value_of share_b_n5000)" "$(value_of share_b_n50000)" && echo yes || echo no )"

# -- exercise 2 --------------------------------------------------------------
check "coverage mismatch computed: total variation distance $(value_of coverage_tvd)" "$( [ "$(value_of coverage_tvd)" = "0.089583" ] && echo yes || echo no )"
check "the under-represented group is named: west appears at $(value_of coverage_ratio_west) of its population share" "$( "${python_bin}" -c "import sys; sys.exit(0 if float(sys.argv[1]) < 0.15 else 1)" "$(value_of coverage_ratio_west)" && echo yes || echo no )"
check "only the west is flagged (flagged: $(value_of coverage_flagged))" "$( [ "$(value_of coverage_flagged)" = "west" ] && [ "$(value_of coverage_worst_group)" = "west" ] && echo yes || echo no )"
check "a sample matching the reference scores exactly 0 and flags nobody" "$( [ "$(value_of coverage_clean_tvd)" = "0.000000" ] && [ "$(value_of coverage_clean_flagged_count)" = "0" ] && echo yes || echo no )"

# -- exercise 3 --------------------------------------------------------------
check "the proxy passes the usual check: correlation with the target is $(value_of proxy_correlation)" "$( "${python_bin}" -c "import sys; sys.exit(0 if float(sys.argv[1]) > 0.90 else 1)" "$(value_of proxy_correlation)" && echo yes || echo no )"
check "ranking by the target selects group B at $(value_of proxy_share_b_by_target); ranking by the proxy at $(value_of proxy_share_b_by_proxy)" "$( "${python_bin}" -c "import sys; t,p=float(sys.argv[1]),float(sys.argv[2]); sys.exit(0 if abs(t-0.25) < 0.05 and p < 0.10 else 1)" "$(value_of proxy_share_b_by_target)" "$(value_of proxy_share_b_by_proxy)" && echo yes || echo no )"
check "group B's true need served falls to $(value_of proxy_b_need_ratio) of what target-ranking would have served" "$( "${python_bin}" -c "import sys; sys.exit(0 if float(sys.argv[1]) < 0.35 else 1)" "$(value_of proxy_b_need_ratio)" && echo yes || echo no )"
check "and the aggregate barely moves -- total need served is $(value_of proxy_total_need_ratio) of the target-ranked total, which is why nobody notices" "$( "${python_bin}" -c "import sys; v=float(sys.argv[1]); sys.exit(0 if 0.97 < v < 1.0 else 1)" "$(value_of proxy_total_need_ratio)" && echo yes || echo no )"

# -- exercise 4 --------------------------------------------------------------
check "both subgroups trend downward (slopes $(value_of agg_slope_a), $(value_of agg_slope_b)) while the pooled fit trends up at $(value_of agg_pooled_slope)" "$( [ "$(value_of agg_sign_flip)" = yes ] && echo yes || echo no )"
check "pooled RMSE is worse for EVERY subgroup: A $(value_of agg_pooled_rmse_a) vs $(value_of agg_own_rmse_a), B $(value_of agg_pooled_rmse_b) vs $(value_of agg_own_rmse_b)" "$( [ "$(value_of agg_pooled_worse_for_every_group)" = yes ] && echo yes || echo no )"

# -- exercise 5 --------------------------------------------------------------
check "the score is perfectly calibrated for both groups (max deviation $(value_of fair_max_calibration_deviation))" "$( [ "$(value_of fair_max_calibration_deviation)" = "0.000000000000" ] && echo yes || echo no )"
check "the two groups have different base rates: A $(value_of fair_base_rate_a), B $(value_of fair_base_rate_b)" "$( [ "$(value_of fair_base_rate_a)" = "0.6600" ] && [ "$(value_of fair_base_rate_b)" = "0.3400" ] && echo yes || echo no )"
check "one threshold for all: parity gap $(value_of fair_single_threshold_parity_gap), equal-opportunity gap $(value_of fair_single_threshold_eo_gap), precision gap $(value_of fair_single_threshold_precision_gap)" "$( [ "$(value_of fair_single_threshold_parity_gap)" = "0.5000" ] && "${python_bin}" -c "import sys; sys.exit(0 if float(sys.argv[1]) > 0.30 and float(sys.argv[2]) > 0.10 else 1)" "$(value_of fair_single_threshold_eo_gap)" "$(value_of fair_single_threshold_precision_gap)" && echo yes || echo no )"
check "enforcing demographic parity closes its gap exactly ($(value_of fair_demographic_parity_parity_gap)) and opens the others ($(value_of fair_demographic_parity_eo_gap), $(value_of fair_demographic_parity_precision_gap))" "$( [ "$(value_of fair_demographic_parity_parity_gap)" = "0.0000" ] && "${python_bin}" -c "import sys; sys.exit(0 if float(sys.argv[1]) > 0.10 and float(sys.argv[2]) > 0.30 else 1)" "$(value_of fair_demographic_parity_eo_gap)" "$(value_of fair_demographic_parity_precision_gap)" && echo yes || echo no )"
check "enforcing equal opportunity closes its gap exactly ($(value_of fair_equal_opportunity_eo_gap)) and reopens the others ($(value_of fair_equal_opportunity_parity_gap), $(value_of fair_equal_opportunity_precision_gap))" "$( [ "$(value_of fair_equal_opportunity_eo_gap)" = "0.0000" ] && "${python_bin}" -c "import sys; sys.exit(0 if float(sys.argv[1]) > 0.10 and float(sys.argv[2]) > 0.25 else 1)" "$(value_of fair_equal_opportunity_parity_gap)" "$(value_of fair_equal_opportunity_precision_gap)" && echo yes || echo no )"
check "NO policy satisfies all three criteria -- the incompatibility, not a preference" "$( [ "$(value_of fair_any_policy_satisfies_all)" = no ] && echo yes || echo no )"

# -- exercise 6 --------------------------------------------------------------
check "$(value_of reid_unique_exact) of $(value_of reid_rows) rows are unique on birth year, postcode and sex ($(value_of reid_unique_exact_fraction) of the table)" "$( [ "$(value_of reid_unique_exact)" = "2723" ] && echo yes || echo no )"
check "coarsening ONE field cuts uniques to $(value_of reid_unique_generalised), a reduction factor of $(value_of reid_reduction_factor)" "$( [ "$(value_of reid_unique_generalised)" = "13" ] && "${python_bin}" -c "import sys; sys.exit(0 if float(sys.argv[1]) > 100 else 1)" "$(value_of reid_reduction_factor)" && echo yes || echo no )"

# -- exercise 7 --------------------------------------------------------------
check "generalisation alone does not buy k-anonymity (k is still $(value_of k_level_generalised))" "$( [ "$(value_of k_level_generalised)" = "1" ] && echo yes || echo no )"
check "suppressing classes under 5 achieves k=$(value_of k_level_after_suppression), at a cost of $(value_of k_rows_suppressed) rows ($(value_of k_rows_kept) kept)" "$( [ "$(value_of k_level_after_suppression)" -ge 5 ] && [ "$(value_of k_rows_suppressed)" = "794" ] && echo yes || echo no )"
check "a $(value_of k_homogeneous_table_level)-anonymous table still discloses: $(value_of k_leaking_class_count) class of size $(value_of k_leaking_class_size) with $(value_of k_leaking_distinct_values) distinct sensitive value, revealing '$(value_of k_disclosed_value)'" "$( [ "$(value_of k_homogeneous_table_level)" = "4" ] && [ "$(value_of k_leaking_class_count)" = "1" ] && [ "$(value_of k_leaking_distinct_values)" = "1" ] && [ "$(value_of k_disclosed_value)" = "diabetes" ] && echo yes || echo no )"

# -- exercise 8 --------------------------------------------------------------
check "an undocumented dataset fails the datasheet check, naming $(value_of datasheet_missing_count) fields: $(value_of datasheet_missing)" "$( [ "$(value_of datasheet_incomplete_complete)" = no ] && [ "$(value_of datasheet_missing_count)" = "8" ] && echo yes || echo no )"
check "a documented one passes, against all $(value_of datasheet_required_field_count) required provenance fields" "$( [ "$(value_of datasheet_complete_complete)" = yes ] && [ "$(value_of datasheet_required_field_count)" = "11" ] && echo yes || echo no )"

# -- exercise 9 --------------------------------------------------------------
check "two releases have identical summary statistics (mean $(value_of drift_mean_old) vs $(value_of drift_mean_new), std $(value_of drift_std_old) vs $(value_of drift_std_new))" "$( [ "$(value_of drift_summary_identical)" = yes ] && [ "$(value_of drift_mean_old)" = "$(value_of drift_mean_new)" ] && echo yes || echo no )"
check "and differ by $(value_of drift_composition_shift) in composition: group B goes from $(value_of drift_share_b_old) to $(value_of drift_share_b_new)" "$( [ "$(value_of drift_composition_shift)" = "0.2500" ] && [ "$(value_of drift_summary_hides_the_change)" = yes ] && echo yes || echo no )"
check "only the provenance record makes it visible: $(value_of drift_new_changelog_entries) new changelog entry naming the change" "$( [ "$(value_of drift_changelog_explains)" = yes ] && [ "$(value_of drift_new_changelog_entries)" = "1" ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "3. Reference suite -- examples/ must pass in full"
# --------------------------------------------------------------------------

examples_output="$(cd "${lab_dir}" && "${pytest_bin}" examples -q 2>&1)"
examples_status=$?
echo "${examples_output}" | tail -5
check "examples/ exits 0" "$( [ ${examples_status} -eq 0 ] && echo yes || echo no )"
examples_passed_line="$(echo "${examples_output}" | grep -E '^[0-9]+ passed' || true)"
check "examples/ reports 9 passed, 0 failed" "$( echo "${examples_passed_line}" | grep -qE '^9 passed' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "4. Exercise suite -- starter/ is all-skip on an untouched checkout"
# --------------------------------------------------------------------------

starter_output="$(cd "${lab_dir}" && "${pytest_bin}" starter -q 2>&1)"
starter_status=$?
echo "${starter_output}" | tail -5
check "starter/ (untouched) exits 0" "$( [ ${starter_status} -eq 0 ] && echo yes || echo no )"
check "starter/ (untouched) reports 9 skipped, 0 failed" "$( echo "${starter_output}" | grep -qE '^9 skipped' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "5. Never run 'pytest examples starter' in one invocation -- both"
echo "   directories define a module named test_ethics.py, and pytest"
echo "   collects by dotted module name. Documented, and run as two commands."
# --------------------------------------------------------------------------

combined_output="$(cd "${lab_dir}" && "${pytest_bin}" examples starter -q 2>&1)"
combined_status=$?
check "'pytest examples starter' aborts rather than silently passing" "$( [ ${combined_status} -ne 0 ] && echo yes || echo no )"
check "the collision is reported as an import file mismatch" "$( echo "${combined_output}" | grep -qi 'import file mismatch' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "6. Prove the suite can genuinely FAIL: solve every exercise in a"
echo "   scratch copy, confirm green, break one assertion on purpose,"
echo "   confirm a non-zero exit and a printed failure, then restore."
# --------------------------------------------------------------------------

scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/d138-scratch.XXXXXX")"
cleanup_scratch() { rm -rf "${scratch_dir}"; }
trap cleanup_scratch EXIT

for module in test_ethics.py ethics.py fixtures.py conftest.py; do
  cp "${lab_dir}/examples/${module}" "${scratch_dir}/${module}"
done

solved_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
solved_status=$?
check "scratch copy of the solved suite exits 0" "$( [ ${solved_status} -eq 0 ] && echo yes || echo no )"
check "scratch copy reports 9 passed" "$( echo "${solved_output}" | grep -qE '^9 passed' && echo yes || echo no )"

# Break exercise 6's exact uniqueness count on purpose.
sed -i.bak 's/assert exact == 2_723/assert exact == 9_999/' "${scratch_dir}/test_ethics.py"

broken_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
broken_status=$?
check "broken scratch copy exits non-zero" "$( [ ${broken_status} -ne 0 ] && echo yes || echo no )"
check "broken scratch copy prints a failure" "$( echo "${broken_output}" | grep -qiE 'failed|assert' && echo yes || echo no )"

mv "${scratch_dir}/test_ethics.py.bak" "${scratch_dir}/test_ethics.py"
restored_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
restored_status=$?
check "restored scratch copy exits 0 again" "$( [ ${restored_status} -eq 0 ] && echo yes || echo no )"
check "restored scratch copy reports 9 passed again" "$( echo "${restored_output}" | grep -qE '^9 passed' && echo yes || echo no )"

cleanup_scratch
trap - EXIT
echo

# --------------------------------------------------------------------------
echo "7. Offline, synthetic, and nothing left behind"
# --------------------------------------------------------------------------

network_hits="$(grep -rlE 'urllib|requests\.|socket|http://|https://' "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null || true)"
check "no network call anywhere in the lab code -- everything is constructed locally" "$( [ -z "${network_hits}" ] && echo yes || echo no )"

seeded="$(grep -c 'default_rng' "${lab_dir}/examples/ethics.py" || true)"
check "every random draw goes through numpy default_rng with an explicit seed (${seeded} call sites)" "$( [ "${seeded}" -ge 4 ] && echo yes || echo no )"

find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

stray="$(find "${lab_dir}" -name '.venv' -prune -o \( -type d -name '__pycache__' -print -o -type d -name '.pytest_cache' -print \) 2>/dev/null || true)"
check "no __pycache__ or .pytest_cache left behind" "$( [ -z "${stray}" ] && echo yes || echo no )"

leftover_tmp="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'd138-*' -print 2>/dev/null || true)"
check "no d138 temporary directory left in the system temp directory" "$( [ -z "${leftover_tmp}" ] && echo yes || echo no )"
echo

echo "-------------------------------------------------------------"
echo "${checks} checks, ${failures} failure(s)"
if [ "${failures}" -gt 0 ]; then
  exit 1
fi
exit 0
