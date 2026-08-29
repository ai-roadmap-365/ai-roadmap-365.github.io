#!/usr/bin/env bash
# Tests for the Day 115 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * the opening posterior -- 99% sensitive, 99% specific, 1-in-1000
#     prevalence -- is exactly 99/1098 (about 0.0902), and NOT 0.99;
#   * the 100,000-person natural-frequency table's TP/(TP+FP) matches the
#     formula exactly;
#   * a 2,000,000-person seeded simulation lands within 3 standard errors
#     of the exact posterior;
#   * the posterior is strictly increasing in prevalence, and at a
#     prevalence of 1/2 it is EXACTLY 0.99 -- the naive guess, correct for
#     a different question;
#   * posterior odds equal prior odds times the likelihood ratio, exactly;
#   * two different tests, updated sequentially, give an identical
#     posterior regardless of the order they are applied in;
#   * a correlated pair of same-sample tests has a naive (assumes-
#     independence) posterior that is strictly, and substantially, higher
#     than the correct correlation-aware one;
#   * a from-scratch naive Bayes classifier with Laplace smoothing
#     correctly classifies held-out documents, and without smoothing a
#     single absent word collapses a class's probability to exactly zero;
#   * multiplying 500 factors of 0.01 underflows to exactly 0.0 in
#     float64, while the corresponding sum of logs stays finite;
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

echo "Day 115 — Bayes You Can Trust"
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

for script in 01_opening_posterior 02_natural_frequencies 03_simulation \
              04_prevalence_sweep 05_odds_form 06_sequential_updating \
              07_correlated_tests 08_naive_bayes_smoothing 09_log_space; do
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

# The import guard. Both directories contain modules called `bayes`,
# `simulate`, `naive_bayes`, `dataset` and `answers`, and pytest imports test
# files by putting their directory on sys.path -- so collecting both suites
# at once would otherwise let the starter tests import the REFERENCE
# solution and report unwritten exercises as passing. Each directory's
# conftest.py prevents that. This check proves it still does: across both
# suites, the skip count must be unchanged.
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
import math
from fractions import Fraction

import numpy as np

import bayes as B
import dataset as D
import naive_bayes as NB
import simulate as S

result = B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY)
print("opening_posterior", result)
print("opening_posterior_rounded", round(float(result), 4))
print("opening_posterior_not_naive", result != Fraction(99, 100))

total_positive = D.NATURAL_FREQUENCY_TP + D.NATURAL_FREQUENCY_FP
natural_ratio = Fraction(D.NATURAL_FREQUENCY_TP, total_positive)
print("natural_total_positive", total_positive)
print("natural_ratio_matches_formula", natural_ratio == result)

rng = np.random.default_rng(D.SIMULATION_SEED)
counts = S.simulate_population(
    rng, D.SIMULATION_POPULATION, float(D.PREVALENCE), float(D.SENSITIVITY), float(D.SPECIFICITY)
)
exact = float(result)
tol = 3.0 * D.standard_error(exact, counts.positives)
print("simulation_within_tolerance", abs(counts.empirical_posterior - exact) < tol)

sweep = [B.posterior(p, D.SENSITIVITY, D.SPECIFICITY) for p in D.PREVALENCE_SWEEP]
print("sweep_increasing", all(sweep[i] < sweep[i + 1] for i in range(len(sweep) - 1)))
print("sweep_half_is_099", B.posterior(Fraction(1, 2), D.SENSITIVITY, D.SPECIFICITY) == Fraction(99, 100))

prior_odds = B.probability_to_odds(D.PREVALENCE)
ratio = B.likelihood_ratio(D.SENSITIVITY, D.SPECIFICITY)
posterior_odds = B.update_odds(prior_odds, ratio)
print("odds_form_matches", posterior_odds == prior_odds * ratio)
print("odds_form_probability_matches_direct", B.odds_to_probability(posterior_odds) == result)

test_a = (D.TEST_A_SENSITIVITY, D.TEST_A_SPECIFICITY)
test_b = (D.TEST_B_SENSITIVITY, D.TEST_B_SPECIFICITY)
seq_ab = B.sequential_posterior(D.PREVALENCE, [test_a, test_b])
seq_ba = B.sequential_posterior(D.PREVALENCE, [test_b, test_a])
print("sequential_posterior", seq_ab)
print("sequential_order_independent", seq_ab == seq_ba)

naive_tp = B.independent_pair_probability(D.CORRELATED_SENSITIVITY)
naive_fp = B.independent_pair_probability(1 - D.CORRELATED_SPECIFICITY)
naive_post = B.posterior_general(D.PREVALENCE, naive_tp, naive_fp)
corr_tp = B.correlated_pair_probability(D.CORRELATED_SENSITIVITY, D.CORRELATION_WEIGHT)
corr_fp = B.correlated_pair_probability(1 - D.CORRELATED_SPECIFICITY, D.CORRELATION_WEIGHT)
corr_post = B.posterior_general(D.PREVALENCE, corr_tp, corr_fp)
print("correlated_naive_posterior", naive_post)
print("correlated_correct_posterior", corr_post)
print("correlated_naive_higher", naive_post > corr_post)

model = NB.train({"spam": D.SPAM_DOCS, "ham": D.HAM_DOCS})
smoothed_winner, _ = NB.classify(model, D.HELD_OUT_VETO_CASE, alpha=D.LAPLACE_ALPHA)
_, unsmoothed_scores = NB.classify(model, D.HELD_OUT_VETO_CASE, alpha=0)
print("veto_smoothed_winner", smoothed_winner)
print("veto_unsmoothed_ham_zero", unsmoothed_scores["ham"] == 0)

factors = [0.01] * 500
product = NB.multiply_probabilities(factors)
logsum = NB.sum_of_logs(factors)
print("underflow_is_zero", product == 0.0)
print("logsum_finite", math.isfinite(logsum))
print("logsum_matches_measured", logsum == D.UNDERFLOW_LOG_SUM)
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "the opening posterior is exactly 99/1098, reduced to 11/122" "11/122" "$(get opening_posterior)"
check_eq "which rounds to 0.0902" "0.0902" "$(get opening_posterior_rounded)"
check_eq "and is NOT the naive 0.99 guess" "True" "$(get opening_posterior_not_naive)"
check_eq "the natural-frequency table has 1098 total positives" "1098" "$(get natural_total_positive)"
check_eq "TP/(TP+FP) matches the formula's answer exactly" "True" "$(get natural_ratio_matches_formula)"
check_eq "the 2,000,000-person simulation lands within 3 standard errors" "True" "$(get simulation_within_tolerance)"
check_eq "the prevalence sweep is strictly increasing" "True" "$(get sweep_increasing)"
check_eq "at prevalence 1/2 the posterior is exactly 0.99" "True" "$(get sweep_half_is_099)"
check_eq "posterior odds equal prior odds times the likelihood ratio, exactly" "True" "$(get odds_form_matches)"
check_eq "the odds-form probability matches the direct formula exactly" "True" "$(get odds_form_probability_matches_direct)"
check_eq "the two-test sequential posterior is exactly 1045/1267" "1045/1267" "$(get sequential_posterior)"
check_eq "updating in either order gives an identical result" "True" "$(get sequential_order_independent)"
check_eq "the naive correlated-test posterior is exactly 363/400" "363/400" "$(get correlated_naive_posterior)"
check_eq "the correct correlated posterior is exactly 2189/13400" "2189/13400" "$(get correlated_correct_posterior)"
check_eq "the naive posterior is strictly higher than the correct one" "True" "$(get correlated_naive_higher)"
check_eq "the veto-case document classifies ham with smoothing" "ham" "$(get veto_smoothed_winner)"
check_eq "and ham's score is exactly zero without smoothing" "True" "$(get veto_unsmoothed_ham_zero)"
check_eq "500 factors of 0.01 underflow to exactly 0.0" "True" "$(get underflow_is_zero)"
check_eq "the corresponding sum of logs is finite" "True" "$(get logsum_finite)"
check_eq "and matches the independently measured value" "True" "$(get logsum_matches_measured)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the reference pytest suite with one assertion deliberately
# broken -- the naive-correlated-posterior comparison flipped -- and asserts
# that the run reports the failure and exits non-zero.
sentinel_file="${lab_dir}/examples/test_reference.py"
if grep -q "def test_naive_posterior_is_strictly_higher_than_the_correlated_posterior" "${sentinel_file}"; then
  backup="$(mktemp)"
  cp "${sentinel_file}" "${backup}"
  python3 - "${sentinel_file}" <<'PY'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "    assert naive > correlated\n\n\ndef test_correlated_posterior_still_exceeds_a_single_tests_posterior"
replacement = (
    "    assert naive < correlated  # DELIBERATELY WRONG: self-test only\n\n\n"
    "def test_correlated_posterior_still_exceeds_a_single_tests_posterior"
)
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
    *"test_naive_posterior_is_strictly_higher_than_the_correlated_posterior"*"failed"*|*"FAILED"*"test_naive_posterior_is_strictly_higher_than_the_correlated_posterior"*)
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
