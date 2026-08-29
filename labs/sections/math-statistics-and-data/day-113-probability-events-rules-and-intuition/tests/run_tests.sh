#!/usr/bin/env bash
# Tests for the Day 113 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * P(two dice sum to 7) is exactly Fraction(1, 6), by enumeration;
#   * the naive addition-rule sum overstates the true union by exactly
#     P(A and B), and the exact size of that error is checked;
#   * de Méré's two bets -- 1 - (5/6)^4 and 1 - (35/36)^24 -- are computed
#     exactly and both round to the historical figures, 0.5177 and 0.4914,
#     and both are confirmed by simulation within three standard errors;
#   * a genuinely independent pair of dice events satisfies P(A and B) ==
#     P(A) x P(B) exactly, and a genuinely dependent pair does not;
#   * a mutually exclusive pair with non-zero probabilities has P(A | B) ==
#     0 while P(A) != 0, proving mutual exclusivity implies dependence;
#   * conditioning by formula and conditioning by filtering the sample space
#     agree exactly;
#   * the law of total probability over two urns matches a direct
#     enumeration of the combined experiment;
#   * Monte Carlo error shrinks like 1/sqrt(n), asserted as a trend averaged
#     over twenty seeds, never a single sampled value;
#   * the same seed gives byte-identical simulated results, and a different
#     seed gives a different but still-close one;
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

echo "Day 113 — Probability You Can Count"
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

for script in 01_sample_space_and_events 02_addition_rule 03_de_mere \
              04_independence_vs_dependence 05_mutual_exclusivity_implies_dependence \
              06_conditioning_by_restriction 07_law_of_total_probability \
              08_monte_carlo_error_scaling 09_reproducibility; do
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
if [ "${ref_passed:-0}" -ge 80 ]; then
  check "the reference suite ran at least 80 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 80 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `probability`,
# `simulate`, `dataset` and `answers`, and pytest imports test files by
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
import probability as P
import simulate as S

space = P.sample_space_two_dice()
print("space_size", len(space))

a = P.event(space, D.ADDITION_EVENT_A)
b = P.event(space, D.ADDITION_EVENT_B)
p_a, p_b = P.probability(a, space), P.probability(b, space)
p_ab = P.probability(a & b, space)
naive = P.naive_sum(p_a, p_b)
true_union = P.addition_rule(p_a, p_b, p_ab)
print("addition_naive", naive)
print("addition_true", true_union)
print("addition_error", naive - true_union)
print("addition_error_equals_intersection", (naive - true_union) == p_ab)

single = P.at_least_one(Fraction(1, 6), D.DE_MERE_SINGLE_ROLLS)
double = P.at_least_one(Fraction(1, 36), D.DE_MERE_DOUBLE_ROLLS)
print("de_mere_single_rounded", round(float(single), 4))
print("de_mere_double_rounded", round(float(double), 4))
print("de_mere_single_favourable", single > Fraction(1, 2))
print("de_mere_double_favourable", double > Fraction(1, 2))

rng = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
sim_single = S.simulate_at_least_one_six(rng, D.DE_MERE_SIM_TRIALS)
sim_double = S.simulate_at_least_one_double_six(rng, D.DE_MERE_SIM_TRIALS)
print("de_mere_single_sim_within_tol", abs(sim_single - float(single)) < D.DE_MERE_SINGLE_TOL)
print("de_mere_double_sim_within_tol", abs(sim_double - float(double)) < D.DE_MERE_DOUBLE_TOL)

ip_a, ip_b = D.INDEPENDENT_PAIR
ia, ib = P.event(space, ip_a), P.event(space, ip_b)
p_ia, p_ib = P.probability(ia, space), P.probability(ib, space)
p_iab = P.probability(ia & ib, space)
print("independent_holds", P.is_independent(p_ia, p_ib, p_iab))

dp_a, dp_b = D.DEPENDENT_PAIR
da, db = P.event(space, dp_a), P.event(space, dp_b)
p_da, p_db = P.probability(da, space), P.probability(db, space)
p_dab = P.probability(da & db, space)
print("dependent_holds", P.is_independent(p_da, p_db, p_dab))

me_a, me_b = D.MUTUALLY_EXCLUSIVE_PAIR
ma, mb = P.event(space, me_a), P.event(space, me_b)
p_ma = P.probability(ma, space)
p_mab = P.probability(ma & mb, space)
p_mb = P.probability(mb, space)
p_ma_given_mb = P.conditional(p_mab, p_mb)
print("mutually_exclusive_conditional_is_zero", p_ma_given_mb == 0)
print("mutually_exclusive_implies_dependent", p_ma_given_mb != p_ma)

ca = P.event(space, D.CONDITIONING_EVENT_A)
cb = P.event(space, D.CONDITIONING_EVENT_B)
p_ca_cb = P.probability(ca & cb, space)
p_cb = P.probability(cb, space)
by_formula = P.conditional(p_ca_cb, p_cb)
by_filtering = P.probability(P.event(cb, D.CONDITIONING_EVENT_A), cb)
print("conditioning_agrees", by_formula == by_filtering == Fraction(1, 6))

total = P.total_probability(D.URN_PRIOR, D.URN_CONDITIONAL_RED)
urn1 = ["red"] * D.URN_1_RED + ["blue"] * D.URN_1_BLUE
urn2 = ["red"] * D.URN_2_RED + ["blue"] * D.URN_2_BLUE
combined = [("u1", x) for x in urn1] + [("u2", x) for x in urn2]
reds = [o for o in combined if o[1] == "red"]
enumerated = Fraction(len(reds), len(combined))
print("urn_total", total)
print("urn_matches_enumeration", total == enumerated)

target = float(D.MONTE_CARLO_TARGET)
means = []
for n in D.MONTE_CARLO_SAMPLE_SIZES:
    errors = [
        abs(S.simulate_sum_seven(np.random.default_rng(seed), n) - target)
        for seed in D.MONTE_CARLO_SEEDS
    ]
    means.append(sum(errors) / len(errors))
print("mc_error_monotone_decreasing", all(means[i + 1] < means[i] for i in range(len(means) - 1)))
n_ratio = D.MONTE_CARLO_SAMPLE_SIZES[-1] / D.MONTE_CARLO_SAMPLE_SIZES[0]
error_ratio = means[0] / means[-1]
sqrt_pred = n_ratio ** 0.5
print("mc_error_ratio_near_sqrt_n", 0.3 * sqrt_pred < error_ratio < 3.0 * sqrt_pred)
print("mc_error_ratio_far_from_linear", error_ratio < n_ratio / 10.0)

a1 = S.simulate_sum_seven(np.random.default_rng(D.REPRODUCIBILITY_SEED_A), D.REPRODUCIBILITY_TRIALS)
a2 = S.simulate_sum_seven(np.random.default_rng(D.REPRODUCIBILITY_SEED_A), D.REPRODUCIBILITY_TRIALS)
b1 = S.simulate_sum_seven(np.random.default_rng(D.REPRODUCIBILITY_SEED_B), D.REPRODUCIBILITY_TRIALS)
print("same_seed_identical", a1 == a2)
print("different_seed_differs", a1 != b1)
tol = 4.0 * D.standard_error(target, D.REPRODUCIBILITY_TRIALS)
print("both_seeds_within_tolerance", abs(a1 - target) < tol and abs(b1 - target) < tol)
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "the sample space has 36 outcomes" "36" "$(get space_size)"
check_eq "the naive addition-rule sum is 1/3" "1/3" "$(get addition_naive)"
check_eq "the true union is 11/36" "11/36" "$(get addition_true)"
check_eq "the naive sum's error is exactly 1/36" "1/36" "$(get addition_error)"
check_eq "and that error equals P(A and B) exactly" "True" "$(get addition_error_equals_intersection)"
check_eq "de Méré's single-die bet rounds to 0.5177" "0.5177" "$(get de_mere_single_rounded)"
check_eq "de Méré's double-dice bet rounds to 0.4914" "0.4914" "$(get de_mere_double_rounded)"
check_eq "the single-die bet favours the player" "True" "$(get de_mere_single_favourable)"
check_eq "the double-dice bet does NOT favour the player" "False" "$(get de_mere_double_favourable)"
check_eq "the single-die simulation lands within 3 standard errors" "True" "$(get de_mere_single_sim_within_tol)"
check_eq "the double-dice simulation lands within 3 standard errors" "True" "$(get de_mere_double_sim_within_tol)"
check_eq "the independent pair satisfies P(A and B) == P(A) x P(B)" "True" "$(get independent_holds)"
check_eq "the dependent pair does NOT satisfy it" "False" "$(get dependent_holds)"
check_eq "a mutually exclusive pair has P(A | B) exactly 0" "True" "$(get mutually_exclusive_conditional_is_zero)"
check_eq "so mutual exclusivity implies dependence" "True" "$(get mutually_exclusive_implies_dependent)"
check_eq "conditioning by formula and by filtering agree exactly at 1/6" "True" "$(get conditioning_agrees)"
check_eq "the urns' weighted total probability of red is 9/20" "9/20" "$(get urn_total)"
check_eq "and it matches the direct enumeration of the combined experiment" "True" "$(get urn_matches_enumeration)"
check_eq "Monte Carlo error falls monotonically across four decades of n" "True" "$(get mc_error_monotone_decreasing)"
check_eq "the observed shrink is close to the sqrt(n) prediction" "True" "$(get mc_error_ratio_near_sqrt_n)"
check_eq "and far from the false 1/n prediction" "True" "$(get mc_error_ratio_far_from_linear)"
check_eq "the same seed gives byte-identical simulated results" "True" "$(get same_seed_identical)"
check_eq "a different seed gives a different result" "True" "$(get different_seed_differs)"
check_eq "and both seeds still land within tolerance of the truth" "True" "$(get both_seeds_within_tolerance)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the reference pytest suite with one assertion deliberately
# broken -- the addition-rule error amount replaced with the wrong value --
# and asserts that the run reports the failure and exits non-zero.
sentinel_file="${lab_dir}/examples/test_reference.py"
if grep -q "def test_naive_sum_overstates_by_exactly_the_intersection" "${sentinel_file}"; then
  backup="$(mktemp)"
  cp "${sentinel_file}" "${backup}"
  python3 - "${sentinel_file}" <<'PY'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert naive - true_union == p_ab"
replacement = "assert naive - true_union == p_ab * 2  # DELIBERATELY WRONG: self-test only"
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
    *"test_naive_sum_overstates_by_exactly_the_intersection"*"failed"*|*"FAILED"*"test_naive_sum_overstates_by_exactly_the_intersection"*)
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
