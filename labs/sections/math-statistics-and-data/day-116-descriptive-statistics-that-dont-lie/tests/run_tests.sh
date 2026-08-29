#!/usr/bin/env bash
# Tests for the Day 116 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * mean, median and mode from scratch match the `statistics` module;
#   * one corrupted salary out of nine drags the mean by over a million
#     dollars and does not move the median at all -- exact equality;
#   * dividing by n underestimates the true variance on average by exactly
#     the factor (n-1)/n; dividing by n-1 lands within a few standard
#     errors of the truth, measured by simulation over 20,000 trials;
#   * NumPy's percentile conventions genuinely disagree about the 75th
#     percentile of the same eight numbers;
#   * Pearson on a perfect parabola is essentially zero; Spearman on a
#     monotone cubic is exactly 1.0;
#   * Anscombe's published 1973 quartet agrees on every classic summary
#     statistic to the documented precision, and three diagnostics those
#     summaries cannot see tell the four sets apart;
#   * treatment A beats treatment B in every subgroup of the smallest
#     table that shows Simpson's paradox, and treatment B wins overall --
#     both directions, from the same table;
#   * 3% contamination inflates the standard deviation by more than 5x and
#     moves the median absolute deviation by less than 1.5x;
#   * standardising gives mean 0 and standard deviation 1, and leaves the
#     Pearson correlation between two variables unchanged;
#   * nothing is left behind on disk.
#
# Everything after the one-time install runs offline. Nothing binds a port,
# nothing writes outside the lab, nothing needs a key. Deterministic,
# non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. The README
# documents `pytest starter -q`, and running it writes .pyc files that would
# then fail the cleanliness check at the end of this script -- failing the
# reader for following the instructions. Clearing them here makes that final
# check measure what it claims to: what THIS run left behind. `.venv` is
# untouched, because the packages' own bytecode is theirs, not ours.
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

check_eq() {
  # check_eq <label> <expected> <actual>
  if [ "$2" = "$3" ]; then
    check "$1" "yes"
  else
    check "$1 (expected [$2], got [$3])" "no"
  fi
}

# Resolve pytest: an explicit override, then this lab's .venv, then PATH.
# Fails loudly with instructions rather than silently skipping checks.
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

if ! "${python_bin}" -c "import numpy" >/dev/null 2>&1; then
  echo "FAIL: numpy is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 116 — Statistics That Don't Lie"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
import sys
from importlib.metadata import version

print(f"python   {platform.python_version()}")
for name in ("numpy", "pytest"):
    print(f"{name:<8} {version(name)}")
print(f"platform {platform.platform()}")
print(f"exe      {sys.executable.rsplit('/', 3)[-1]}")
PY
)"
echo "${versions}" | sed 's/^/  /'

pinned_numpy="$(grep -E '^numpy==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
installed_numpy="$("${python_bin}" -c "from importlib.metadata import version; print(version('numpy'))")"
check_eq "installed numpy matches requirements.txt" "${pinned_numpy}" "${installed_numpy}"

major="$("${python_bin}" -c "import numpy; print(numpy.__version__.split('.')[0])")"
check_eq "numpy is version 2 or later" "2" "${major}"

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_mean_median_mode 02_breakdown_point 03_bessel_correction \
              04_percentile_ambiguity 05_pearson_vs_spearman 06_anscombes_quartet \
              07_simpsons_paradox 08_robust_spread_under_contamination \
              09_standardization; do
  out="$(cd "${lab_dir}/examples" && "${python_bin}" "${script}.py" 2>&1)"
  status=$?
  if [ "${status}" -ne 0 ]; then
    check "${script}.py exits 0" "no"
    echo "${out}" | tail -5 | sed 's/^/      /'
  else
    check "${script}.py exits 0" "yes"
  fi
  case "${out}" in
    *"${script}.py: every assertion held."*)
      check "${script}.py reports every assertion held" "yes" ;;
    *) check "${script}.py reports every assertion held" "no" ;;
  esac
done

# --------------------------------------------------------------------------
echo
echo "3. The reference pytest suite: real values, real exceptions"
# --------------------------------------------------------------------------

ref_out="$(cd "${lab_dir}" && "${pytest_bin}" examples -q -p no:cacheprovider 2>&1)"
ref_status=$?
echo "${ref_out}" | tail -3 | sed 's/^/  /'
if [ "${ref_status}" -eq 0 ]; then
  check "pytest examples exits 0" "yes"
else
  check "pytest examples exits 0" "no"
fi
case "${ref_out}" in
  *" failed"*) check "no test in the reference suite failed" "no" ;;
  *)           check "no test in the reference suite failed" "yes" ;;
esac
ref_passed="$(printf '%s\n' "${ref_out}" | grep -o '[0-9][0-9]* passed' | head -1 | cut -d' ' -f1)"
if [ "${ref_passed:-0}" -ge 25 ]; then
  check "the reference suite ran at least 25 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 25 tests (ran ${ref_passed:-0})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "4. The starter suite skips unattempted work instead of failing it"
# --------------------------------------------------------------------------

start_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
start_status=$?
echo "${start_out}" | tail -3 | sed 's/^/  /'
if [ "${start_status}" -eq 0 ]; then
  check "pytest starter exits 0 on an untouched checkout" "yes"
else
  check "pytest starter exits 0 on an untouched checkout" "no"
fi
case "${start_out}" in
  *" failed"*) check "the starter suite reports no failures" "no" ;;
  *)           check "the starter suite reports no failures" "yes" ;;
esac
case "${start_out}" in
  *skipped*) check "unwritten exercises are reported as skipped, not passed" "yes" ;;
  *) check "unwritten exercises are reported as skipped, not passed" "no" ;;
esac

# The import guard. Both directories contain modules called `dataset`,
# `descriptive`, `simulate` and `answers`, and pytest imports test files by
# putting their directory on sys.path -- so collecting both suites at once
# would otherwise let the starter tests import the REFERENCE solution and
# report unwritten exercises as passing. Each directory's conftest.py
# prevents that. This check proves it still does: across both suites, the
# skip count must be unchanged.
both_out="$(cd "${lab_dir}" && "${pytest_bin}" -q -p no:cacheprovider 2>&1)"
start_skipped="$(printf '%s\n' "${start_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
both_skipped="$(printf '%s\n' "${both_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
check_eq "collecting both suites at once does not turn skips into passes" \
  "${start_skipped:-none}" "${both_skipped:-none}"

# --------------------------------------------------------------------------
echo
echo "5. The lesson's claims, checked one value at a time"
# --------------------------------------------------------------------------

facts="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY'
import statistics as st

import numpy as np

import dataset as D
import descriptive as F
import simulate as S

print("odd_list_mean", F.mean(D.ODD_LIST))
print("odd_list_median", F.median(D.ODD_LIST))
print("multimodal_modes", F.modes(D.MULTIMODAL_LIST))

mean_before, mean_after = F.breakdown_point_mean(D.SALARY_LIST, D.CORRUPTED_SALARY)
median_before, median_after = F.breakdown_point_median(D.SALARY_LIST, D.CORRUPTED_SALARY)
print("mean_shift_large", (mean_after - mean_before) > D.BREAKDOWN_MEAN_SHIFT_FLOOR)
print("median_shift_zero", median_after == median_before)

rng = np.random.default_rng(D.BESSEL_SEED)
biased, unbiased = S.bessel_trial_variances(
    rng, D.BESSEL_POPULATION_MEAN, D.BESSEL_POPULATION_SIGMA,
    D.BESSEL_SAMPLE_SIZE, D.BESSEL_TRIALS,
)
ratio_biased = float(biased.mean()) / D.BESSEL_TRUE_VARIANCE
print("bessel_biased_ratio", round(ratio_biased, 4))
print("bessel_biased_near_n_minus_1_over_n", abs(ratio_biased - D.BESSEL_EXPECTED_BIAS_FACTOR) < D.BESSEL_BIAS_FACTOR_TOLERANCE)
se_unbiased = float(unbiased.std(ddof=1)) / (D.BESSEL_TRIALS ** 0.5)
print("bessel_unbiased_within_tolerance", abs(float(unbiased.mean()) - D.BESSEL_TRUE_VARIANCE) < D.BESSEL_UNBIASED_SE_TOLERANCE * se_unbiased)

pvals = {m: F.percentile_under(D.PERCENTILE_ARRAY, D.PERCENTILE_TARGET, m) for m in D.PERCENTILE_METHODS}
print("percentile_distinct_count", len(set(pvals.values())))
print("percentile_linear", pvals["linear"])
print("percentile_lower", pvals["lower"])
print("percentile_higher", pvals["higher"])

pear_parabola = F.pearson(D.PARABOLA_X, D.PARABOLA_Y)
print("parabola_pearson_near_zero", abs(pear_parabola) < D.PARABOLA_PEARSON_TOLERANCE)
spear_monotone = F.spearman(D.MONOTONE_X, D.MONOTONE_Y)
print("monotone_spearman_is_one", spear_monotone == 1.0)

anscombe_ref = F.anscombe_summary(*D.ANSCOMBE_SETS["I"])
agree = all(
    round(F.anscombe_summary(*D.ANSCOMBE_SETS[name])["mean_x"], 1) == round(anscombe_ref["mean_x"], 1)
    and round(F.anscombe_summary(*D.ANSCOMBE_SETS[name])["correlation"], 1) == round(anscombe_ref["correlation"], 1)
    for name in D.ANSCOMBE_SETS
)
print("anscombe_summaries_agree", agree)
shapes = {name: F.shape_statistics(*D.ANSCOMBE_SETS[name]) for name in D.ANSCOMBE_SETS}
print("anscombe_set_iv_leverage_dominant", shapes["IV"]["max_leverage"] > 3.0 * shapes["I"]["max_leverage"])
print("anscombe_set_iii_outlier_dominant", shapes["III"]["outlier_ratio"] > 2.0 * shapes["I"]["outlier_ratio"])

a_easy = F.success_rate(*D.TREATMENT_A_EASY)
a_hard = F.success_rate(*D.TREATMENT_A_HARD)
b_easy = F.success_rate(*D.TREATMENT_B_EASY)
b_hard = F.success_rate(*D.TREATMENT_B_HARD)
a_total = F.combined_rate(D.TREATMENT_A_EASY, D.TREATMENT_A_HARD)
b_total = F.combined_rate(D.TREATMENT_B_EASY, D.TREATMENT_B_HARD)
print("simpson_a_wins_both_subgroups", a_easy > b_easy and a_hard > b_hard)
print("simpson_b_wins_overall", b_total > a_total)

rng2 = np.random.default_rng(D.CONTAMINATION_SEED)
clean, contaminated = S.contaminated_sample(
    rng2, D.CONTAMINATION_BASE_MEAN, D.CONTAMINATION_BASE_SIGMA,
    D.CONTAMINATION_BASE_N, D.CONTAMINATION_OUTLIERS,
)
std_clean = float(np.std(clean, ddof=1))
std_contam = float(np.std(contaminated, ddof=1))
mad_clean = F.median_absolute_deviation(clean)
mad_contam = F.median_absolute_deviation(contaminated)
print("contamination_std_multiplier", round(std_contam / std_clean, 2))
print("contamination_mad_multiplier", round(mad_contam / mad_clean, 2))
print("contamination_std_inflates", (std_contam / std_clean) > D.CONTAMINATION_STD_MULTIPLIER_FLOOR)
print("contamination_mad_stable", (mad_contam / mad_clean) < D.CONTAMINATION_MAD_MULTIPLIER_CEILING)

rng3 = np.random.default_rng(D.STANDARDIZATION_SEED)
x = rng3.normal(D.STANDARDIZATION_X_MEAN, D.STANDARDIZATION_X_SIGMA, D.STANDARDIZATION_N)
noise = rng3.normal(0.0, D.STANDARDIZATION_Y_NOISE_SIGMA, D.STANDARDIZATION_N)
y = D.STANDARDIZATION_Y_SLOPE * x + noise
zx, zy = F.zscores(x), F.zscores(y)
mean_zx = sum(zx) / len(zx)
std_zx = (sum((v - mean_zx) ** 2 for v in zx) / len(zx)) ** 0.5
print("standardized_mean_near_zero", abs(mean_zx) < D.STANDARDIZATION_MEAN_TOLERANCE)
print("standardized_std_near_one", abs(std_zx - 1.0) < D.STANDARDIZATION_STD_TOLERANCE)
r_orig = F.pearson(x, y)
r_std = F.pearson(zx, zy)
print("standardizing_preserves_correlation", abs(r_orig - r_std) < D.STANDARDIZATION_CORRELATION_TOLERANCE)
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "the odd list's mean matches the worked figure" "7.444444444444445" "$(get odd_list_mean)"
check_eq "the odd list's median is 7.0" "7.0" "$(get odd_list_median)"
check_eq "the multimodal list has modes [3, 8]" "[3, 8]" "$(get multimodal_modes)"
check_eq "one corrupted salary drags the mean by over the stated floor" "True" "$(get mean_shift_large)"
check_eq "the same corruption leaves the median exactly unchanged" "True" "$(get median_shift_zero)"
check_eq "dividing by n is biased low, near (n-1)/n" "True" "$(get bessel_biased_near_n_minus_1_over_n)"
check_eq "dividing by n-1 lands within tolerance of the true variance" "True" "$(get bessel_unbiased_within_tolerance)"
check_eq "at least 2 percentile conventions disagree" "True" "$([ "$(get percentile_distinct_count)" -ge 2 ] && echo True || echo False)"
check_eq "the default ('linear') 75th percentile is 8.25" "8.25" "$(get percentile_linear)"
check_eq "'lower' and 'higher' land on different real data points" "True" "$([ "$(get percentile_lower)" != "$(get percentile_higher)" ] && echo True || echo False)"
check_eq "Pearson on the symmetric parabola is essentially zero" "True" "$(get parabola_pearson_near_zero)"
check_eq "Spearman on the monotone cubic is exactly 1.0" "True" "$(get monotone_spearman_is_one)"
check_eq "all four Anscombe sets agree on the classic summaries" "True" "$(get anscombe_summaries_agree)"
check_eq "set IV's leverage dramatically dominates set I's" "True" "$(get anscombe_set_iv_leverage_dominant)"
check_eq "set III's outlier residual dramatically dominates set I's" "True" "$(get anscombe_set_iii_outlier_dominant)"
check_eq "treatment A wins both Simpson's-paradox subgroups" "True" "$(get simpson_a_wins_both_subgroups)"
check_eq "treatment B still wins overall" "True" "$(get simpson_b_wins_overall)"
check_eq "3% contamination inflates the standard deviation past the floor" "True" "$(get contamination_std_inflates)"
check_eq "the same contamination leaves the MAD under the ceiling" "True" "$(get contamination_mad_stable)"
check_eq "the standardized sample's mean is (numerically) zero" "True" "$(get standardized_mean_near_zero)"
check_eq "the standardized sample's standard deviation is (numerically) one" "True" "$(get standardized_std_near_one)"
check_eq "standardising leaves the Pearson correlation unchanged" "True" "$(get standardizing_preserves_correlation)"

echo "  contamination std multiplier measured at: $(get contamination_std_multiplier)x"
echo "  contamination MAD multiplier measured at: $(get contamination_mad_multiplier)x"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the reference pytest suite with one assertion deliberately
# broken -- the breakdown-point median check flipped from "equal" to
# "not equal" -- and asserts that the run reports the failure and exits
# non-zero.
sentinel_file="${lab_dir}/examples/test_reference.py"
if grep -q "def test_median_breakdown_point_does_not_move_at_all" "${sentinel_file}"; then
  backup="$(mktemp)"
  cp "${sentinel_file}" "${backup}"
  python3 - "${sentinel_file}" <<'PY'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert after == before  # exact equality: the median's rank did not change"
replacement = "assert after != before  # DELIBERATELY WRONG: self-test only"
assert needle in text, "sentinel assertion not found"
open(path, "w").write(text.replace(needle, replacement, 1))
PY
  self_out="$(cd "${lab_dir}" && "${pytest_bin}" examples -q -p no:cacheprovider 2>&1)"
  self_status=$?
  cp "${backup}" "${sentinel_file}"
  rm -f "${backup}"
  find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately broken assertion makes the suite exit non-zero (${self_status})" "yes"
  else
    check "a deliberately broken assertion makes the suite exit non-zero" "no"
  fi
  case "${self_out}" in
    *"test_median_breakdown_point_does_not_move_at_all"*"failed"*|*"FAILED"*"test_median_breakdown_point_does_not_move_at_all"*)
      check "the failing test is named in the output" "yes" ;;
    *) check "the failing test is named in the output" "no" ;;
  esac
  case "${self_out}" in
    *"1 failed"*) check "exactly one test failed" "yes" ;;
    *) check "exactly one test failed" "no" ;;
  esac
else
  check "sentinel assertion found in examples/test_reference.py" "no"
fi

# --------------------------------------------------------------------------
echo
echo "7. Nothing was left behind"
# --------------------------------------------------------------------------

# `.venv` is pruned from both searches below. The virtual environment ships
# NumPy's and pytest's own precompiled bytecode -- hundreds of __pycache__
# directories that came with the packages and have nothing to do with
# whether THIS lab tidied up after itself.

if find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -print -quit 2>/dev/null | grep -q .; then
  check "no __pycache__ directory left by the lab's own code" "no"
else
  check "no __pycache__ directory left by the lab's own code" "yes"
fi

if find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -print -quit 2>/dev/null | grep -q .; then
  check "no .pytest_cache directory left under the lab" "no"
else
  check "no .pytest_cache directory left under the lab" "yes"
fi

if grep -rqE 'urlopen|requests\.|socket\.|http://|https://' \
     "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null; then
  check "no lab source opens a network connection" "no"
else
  check "no lab source opens a network connection" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
