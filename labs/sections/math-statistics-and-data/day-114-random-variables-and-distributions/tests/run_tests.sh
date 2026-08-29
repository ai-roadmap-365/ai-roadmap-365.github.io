#!/usr/bin/env bash
# Tests for the Day 114 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * the two-dice sum pmf is exact Fraction arithmetic, and 7 is exactly
#     six times as likely as 2 -- the distribution is nowhere near uniform;
#   * the cdf is monotone, ends at exactly 1, and a cdf difference recovers
#     a pmf value exactly;
#   * expectation and variance computed from the definition agree with a
#     large seeded simulation, within three standard errors;
#   * E[X+Y] = E[X] + E[Y] EXACTLY for a dependent pair (X = first die,
#     Y = the sum), with no independence assumption anywhere;
#   * Var[X+Y] != Var[X] + Var[Y] for that same pair, but DOES equal
#     Var[X] + Var[Y] + 2*Cov(X,Y) exactly -- the asymmetry stated plainly;
#   * E[X^2] > (E[X])^2 for a die, and the gap is exactly Var[X];
#   * an inverse-CDF sampler written from scratch reproduces an arbitrary
#     discrete pmf within tolerance, and the same seed reproduces the same
#     draws;
#   * an exponential sampler written from scratch as -ln(U)/lambda agrees
#     with NumPy's own, both on sample mean and on a hand-written max-gap
#     statistic between their empirical cdfs (scipy is not installed);
#   * the Binomial(n, lambda/n) pmf converges to the Poisson(lambda) pmf as
#     n grows, measured as a monotonically shrinking maximum gap;
#   * Uniform(0, 0.5) has density 2 -- above 1 -- everywhere on its support,
#     while its numeric integral over that support is exactly 1;
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

# The Python that owns that pytest is the one with numpy installed.
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

echo "Day 114 — Random Variables and Distributions"
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

for script in 01_pmf_of_a_sum 02_cdf_from_pmf 03_expectation_and_variance \
              04_linearity_with_dependence 05_variance_is_not_additive \
              06_jensens_inequality 07_inverse_cdf_discrete_sampler \
              08_exponential_from_scratch 09_poisson_as_binomial_limit \
              10_density_above_one; do
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
if [ "${ref_passed:-0}" -ge 60 ]; then
  check "the reference suite ran at least 60 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 60 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `distributions`,
# `sampling`, `dataset` and `answers`, and pytest imports test files by
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
from fractions import Fraction

import numpy as np

import dataset as D
import distributions as dist
import sampling as samp

# -- exercise 1: the pmf of a sum -------------------------------------------
pmf = dist.dice_sum_pmf()
print("pmf_p7", pmf[7])
print("pmf_p2", pmf[2])
print("pmf_ratio", pmf[7] / pmf[2])
print("pmf_not_uniform", len(set(pmf.values())) > 1)

# -- exercise 2: the cdf ------------------------------------------------------
cdf = dist.cdf_from_pmf(pmf)
values = [cdf[k] for k in sorted(cdf)]
print("cdf_monotone", all(a <= b for a, b in zip(values, values[1:])))
print("cdf_ends_at_one", cdf[12] == 1)
print("cdf_diff_matches_pmf", cdf[7] - cdf[6] == pmf[7])

# -- exercise 3: expectation and variance ------------------------------------
exact_mean = dist.expectation_pmf(pmf)
exact_var = dist.variance_pmf(pmf)
print("exact_mean", exact_mean)
print("exact_var", exact_var)

rng = np.random.default_rng(D.SEED)
first = rng.integers(1, 7, size=D.EV_SIMULATION_TRIALS)
second = rng.integers(1, 7, size=D.EV_SIMULATION_TRIALS)
sample = (first + second).astype(float)
mean_tol = 3.0 * D.standard_error_of_mean(float(exact_var), D.EV_SIMULATION_TRIALS)
print("mean_within_tol", abs(sample.mean() - float(exact_mean)) < mean_tol)

# -- exercises 4, 5: linearity and non-additivity ----------------------------
outcomes, weight = D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT
E_X = dist.expectation_over(outcomes, weight, D.first_die)
E_Y = dist.expectation_over(outcomes, weight, D.dice_sum)
E_XY = dist.expectation_over(outcomes, weight, lambda o: D.first_die(o) + D.dice_sum(o))
print("E_X", E_X)
print("E_Y", E_Y)
print("linearity_exact", E_XY == E_X + E_Y)

Var_X = dist.variance_over(outcomes, weight, D.first_die)
Var_Y = dist.variance_over(outcomes, weight, D.dice_sum)
Var_XY = dist.variance_over(outcomes, weight, lambda o: D.first_die(o) + D.dice_sum(o))
Cov_XY = dist.covariance_over(outcomes, weight, D.first_die, D.dice_sum)
print("variance_naive_wrong", Var_XY != Var_X + Var_Y)
print("variance_full_formula_exact", Var_XY == Var_X + Var_Y + 2 * Cov_XY)
print("covariance_nonzero", Cov_XY != 0)

# -- exercise 6: Jensens inequality -------------------------------------------
die_outcomes, die_weight = D.DIE_FACES, D.ONE_DIE_WEIGHT
EX2 = dist.expectation_over(die_outcomes, die_weight, lambda x: x * x)
EX = dist.expectation_over(die_outcomes, die_weight, lambda x: x)
VarX = dist.variance_over(die_outcomes, die_weight, lambda x: x)
print("jensen_strict", EX2 > EX**2)
print("jensen_gap_exact", (EX2 - EX**2) == VarX)

# -- exercise 7: inverse-CDF discrete sampler --------------------------------
pmf_float = {k: float(v) for k, v in pmf.items()}
rng7 = np.random.default_rng(D.SEED)
draws = samp.sample_discrete_inverse_cdf(pmf_float, rng7, D.DISCRETE_SAMPLER_TRIALS)
values7, counts7 = np.unique(draws, return_counts=True)
empirical = dict(zip(values7.astype(int), counts7 / D.DISCRETE_SAMPLER_TRIALS))
worst_se = max(D.standard_error_of_proportion(p, D.DISCRETE_SAMPLER_TRIALS) for p in pmf_float.values())
max_gap7 = max(abs(pmf_float[k] - empirical.get(k, 0.0)) for k in pmf_float)
print("sampler_within_tol", max_gap7 < 3.0 * worst_se)

rng_a = np.random.default_rng(D.SEED)
rng_b = np.random.default_rng(D.SEED)
d_a = samp.sample_discrete_inverse_cdf(pmf_float, rng_a, 1000)
d_b = samp.sample_discrete_inverse_cdf(pmf_float, rng_b, 1000)
print("sampler_reproducible", np.array_equal(d_a, d_b))

# -- exercise 8: exponential from scratch, and the max-gap statistic --------
rng8 = np.random.default_rng(D.SEED)
scratch = samp.sample_exponential_scratch(D.EXPONENTIAL_RATE, rng8, D.EXPONENTIAL_SAMPLE_SIZE)
built_in = rng8.exponential(scale=1.0 / D.EXPONENTIAL_RATE, size=D.EXPONENTIAL_SAMPLE_SIZE)
target = 1.0 / D.EXPONENTIAL_RATE
tol8 = 3.0 * D.standard_error_of_mean(target**2, D.EXPONENTIAL_SAMPLE_SIZE)
print("exp_scratch_mean_ok", abs(scratch.mean() - target) < tol8)
print("exp_builtin_mean_ok", abs(built_in.mean() - target) < tol8)
gap8 = samp.max_gap_statistic(scratch, built_in)
threshold8 = D.dkw_two_sample_threshold(D.EXPONENTIAL_SAMPLE_SIZE, D.EXPONENTIAL_SAMPLE_SIZE)
print("exp_max_gap_below_threshold", gap8 < threshold8)
print("exp_max_gap", f"{gap8:.6f}")
print("exp_threshold", f"{threshold8:.6f}")

# -- exercise 9: Poisson as a Binomial limit ---------------------------------
lam = D.POISSON_LAMBDA
gaps9 = [
    dist.max_binomial_poisson_gap(n, lam / n, lam, D.POISSON_COMPARISON_KS)
    for n in D.POISSON_LIMIT_NS
]
print("poisson_limit_monotone", all(a > b for a, b in zip(gaps9, gaps9[1:])))
print("poisson_limit_last_tiny", gaps9[-1] < 1e-3)

# -- exercise 10: density above 1 ---------------------------------------------
density10 = dist.uniform_density(0.25, D.UNIFORM_LOW, D.UNIFORM_HIGH)
integral10 = dist.numeric_integral(
    lambda x: dist.uniform_density(x, D.UNIFORM_LOW, D.UNIFORM_HIGH),
    D.UNIFORM_LOW, D.UNIFORM_HIGH, 100_000,
)
print("density_is_two", density10 == 2.0)
print("density_exceeds_one", density10 > 1.0)
print("integral_is_one", round(integral10, 6) == 1.0)
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "P(sum=7) is exactly 1/6" "1/6" "$(get pmf_p7)"
check_eq "P(sum=2) is exactly 1/36" "1/36" "$(get pmf_p2)"
check_eq "7 is exactly six times as likely as 2" "6" "$(get pmf_ratio)"
check_eq "the distribution is not uniform" "True" "$(get pmf_not_uniform)"
check_eq "the cdf is monotone non-decreasing" "True" "$(get cdf_monotone)"
check_eq "the cdf ends at exactly 1" "True" "$(get cdf_ends_at_one)"
check_eq "F(7) - F(6) equals P(sum=7) exactly" "True" "$(get cdf_diff_matches_pmf)"
check_eq "E[Y] is exactly 7" "7" "$(get exact_mean)"
check_eq "Var[Y] is exactly 35/6" "35/6" "$(get exact_var)"
check_eq "the simulated mean lands within 3 standard errors" "True" "$(get mean_within_tol)"
check_eq "E[X] is 7/2" "7/2" "$(get E_X)"
check_eq "E[Y] (joint) is 7" "7" "$(get E_Y)"
check_eq "E[X+Y] equals E[X]+E[Y] EXACTLY for the dependent pair" "True" "$(get linearity_exact)"
check_eq "Var[X+Y] does NOT equal Var[X]+Var[Y]" "True" "$(get variance_naive_wrong)"
check_eq "Var[X+Y] EXACTLY equals Var[X]+Var[Y]+2*Cov(X,Y)" "True" "$(get variance_full_formula_exact)"
check_eq "Cov(X,Y) is non-zero for this dependent pair" "True" "$(get covariance_nonzero)"
check_eq "E[X^2] > (E[X])^2 for a die (Jensen)" "True" "$(get jensen_strict)"
check_eq "the Jensen gap equals Var[X] exactly" "True" "$(get jensen_gap_exact)"
check_eq "the inverse-CDF sampler matches the pmf within tolerance" "True" "$(get sampler_within_tol)"
check_eq "the same seed reproduces identical discrete draws" "True" "$(get sampler_reproducible)"
check_eq "the from-scratch exponential sampler's mean is within tolerance" "True" "$(get exp_scratch_mean_ok)"
check_eq "NumPy's own exponential sampler's mean is within tolerance" "True" "$(get exp_builtin_mean_ok)"
check_eq "the max-gap statistic is below the DKW-derived threshold" "True" "$(get exp_max_gap_below_threshold)"
echo "  (measured on this run: max-gap statistic $(get exp_max_gap) against threshold $(get exp_threshold) -- reported, not asserted to a value)"
check_eq "the Binomial-to-Poisson pmf gap shrinks monotonically with n" "True" "$(get poisson_limit_monotone)"
check_eq "the gap at n=10,000 is under 0.001" "True" "$(get poisson_limit_last_tiny)"
check_eq "Uniform(0, 0.5)'s density is exactly 2" "True" "$(get density_is_two)"
check_eq "that density exceeds 1" "True" "$(get density_exceeds_one)"
check_eq "the numeric integral of that density is 1 to six decimals" "True" "$(get integral_is_one)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the reference pytest suite with ONE assertion deliberately
# swapped for a wrong one -- claiming Var[X+Y] == Var[X]+Var[Y], the naive
# belief the lesson spends a whole exercise refuting -- and asserts that the
# re-run reports exactly one failure and a non-zero exit. If this section
# passes, section 5 is not decorative.

self_test_marker="test_variance_of_sum_is_not_the_naive_sum"
original_file="${lab_dir}/examples/test_reference.py"
backup_file="$(mktemp)"
cp "${original_file}" "${backup_file}"

python3 - "${original_file}" "${self_test_marker}" <<'PY'
import re
import sys

path, marker = sys.argv[1], sys.argv[2]
text = open(path).read()
needle = (
    "def test_variance_of_sum_is_not_the_naive_sum():\n"
    "    outcomes, weight = D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT\n"
    "    var_x = dist.variance_over(outcomes, weight, D.first_die)\n"
    "    var_y = dist.variance_over(outcomes, weight, D.dice_sum)\n"
    "    var_sum = dist.variance_over(outcomes, weight, lambda o: D.first_die(o) + D.dice_sum(o))\n"
    "    assert var_sum != var_x + var_y\n"
)
replacement = needle.replace("assert var_sum != var_x + var_y", "assert var_sum == var_x + var_y")
assert needle in text, "self-test marker not found -- test_reference.py has drifted"
text = text.replace(needle, replacement)
open(path, "w").write(text)
PY

self_out="$(cd "${lab_dir}" && "${pytest_bin}" examples -q -p no:cacheprovider 2>&1)"
self_status=$?
cp "${backup_file}" "${original_file}"
rm -f "${backup_file}"
find "${lab_dir}/examples" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

if [ "${self_status}" -ne 0 ]; then
  check "a deliberately wrong assertion makes the reference suite exit non-zero (${self_status})" "yes"
else
  check "a deliberately wrong assertion makes the reference suite exit non-zero" "no"
fi
case "${self_out}" in
  *"${self_test_marker}"*)
    check "the failing test is named in the output" "yes" ;;
  *) check "the failing test is named in the output" "no" ;;
esac
case "${self_out}" in
  *"1 failed"*)
    check "the summary line counts exactly one failure" "yes" ;;
  *) check "the summary line counts exactly one failure" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "7. Nothing was left behind"
# --------------------------------------------------------------------------

# `.venv` is pruned from both searches below. The virtual environment ships
# NumPy's and pytest's own precompiled bytecode -- hundreds of __pycache__
# directories that came with the packages and have nothing to do with whether
# THIS lab tidied up after itself. Searching them would report a failure the
# reader cannot fix and did not cause. Everything the lab itself writes lives
# outside `.venv`, which is exactly what these two checks look at.

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
