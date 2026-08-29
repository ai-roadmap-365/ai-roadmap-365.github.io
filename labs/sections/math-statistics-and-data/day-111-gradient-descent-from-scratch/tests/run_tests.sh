#!/usr/bin/env bash
# Tests for the Day 111 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * the whole training loop is one line, x <- x - lr * grad(x), and its
#     closed form on a quadratic, x_n = x0 * (1 - lr*a)^n, is measured
#     against a real loop rather than assumed;
#   * four learning rates on the same quadratic land in four different
#     regimes -- monotone, exact, oscillating, divergent -- with the exact
#     boundaries at 1/a and 2/a;
#   * the per-step contraction ratio measured from a real run equals
#     |1 - lr*a| to float precision;
#   * an ill-conditioned bowl needs more steps as its condition number
#     grows, and an isotropic bowl solves in exactly one step at the
#     optimal learning rate;
#   * momentum, given the SAME learning rate as plain descent, needs
#     strictly fewer steps on the same ill-conditioned bowl;
#   * a gradient check built from a central difference flags exactly the
#     one component of a deliberately broken analytic gradient;
#   * two starting points on a non-convex function converge to two
#     different minima;
#   * a naive "the loss stopped changing" stopping rule is caught firing
#     early, while the gradient itself is still well above its own
#     tolerance;
#   * a learning rate only slightly too large makes the loss climb every
#     step until the run overflows to inf and then nan, without raising;
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

echo "Day 111 — Descent by Hand"
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

float_width="$("${python_bin}" -c "import sys; print(sys.float_info.mant_dig)")"
check_eq "Python floats are IEEE-754 doubles with a 53-bit significand" "53" "${float_width}"

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_the_hook 02_regimes_and_contraction \
              03_ill_conditioning_and_momentum 04_checking_landscapes_and_traps; do
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
echo "3. The reference pytest suite: real values, real behaviour"
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
if [ "${ref_passed:-0}" -ge 20 ]; then
  check "the reference suite ran at least 20 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 20 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `dataset` and
# `descent`, and pytest imports test files by putting their directory on
# sys.path -- so collecting both suites at once would otherwise let the
# starter tests import the REFERENCE solution and report unwritten
# exercises as passing. Each directory's conftest.py prevents that. This
# check proves it still does: across both suites, the skip count must be
# unchanged.
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

import numpy as np

import dataset as D
import descent as G

print("a", D.A)
print("critical_lr", D.CRITICAL_LR)
print("divergence_lr", D.DIVERGENCE_LR)

regime_lrs = {
    "monotone": D.LR_MONOTONE,
    "exact": D.LR_EXACT,
    "oscillating": D.LR_OSCILLATING,
    "divergent": D.LR_DIVERGENT,
}
regime_paths = {
    name: G.gradient_descent(lambda x: D.A * x, D.X0_1D, lr, D.REGIME_ITERS)
    for name, lr in regime_lrs.items()
}
for name, path in regime_paths.items():
    print(f"regime_{name}", G.classify_regime(path, D.A, regime_lrs[name]))
print("exact_second_value", regime_paths["exact"][1])
print("divergent_grows", abs(regime_paths["divergent"][-1]) > abs(regime_paths["divergent"][0]) * 10)

ratio_mono = G.per_step_ratios(G.gradient_descent(lambda x: D.A * x, D.X0_1D, D.LR_MONOTONE, 10))[0]
ratio_osc = G.per_step_ratios(G.gradient_descent(lambda x: D.A * x, D.X0_1D, D.LR_OSCILLATING, 10))[0]
ratio_div = G.per_step_ratios(G.gradient_descent(lambda x: D.A * x, D.X0_1D, D.LR_DIVERGENT, 10))[0]
print("ratio_monotone", ratio_mono)
print("ratio_oscillating", ratio_osc)
print("ratio_divergent", ratio_div)
print("ratio_monotone_matches", abs(ratio_mono - abs(1 - D.LR_MONOTONE * D.A)) < D.EXACT_TOL)
print("ratio_oscillating_matches", abs(ratio_osc - abs(1 - D.LR_OSCILLATING * D.A)) < D.EXACT_TOL)
print("ratio_divergent_matches", abs(ratio_div - abs(1 - D.LR_DIVERGENT * D.A)) < D.EXACT_TOL)

counts = [
    G.steps_to_tolerance(D.bowl_grad(k), np.array(D.KAPPA_START), D.kappa_lr(k), D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS)
    for k in D.KAPPA_VALUES
]
print("kappa_steps", "|".join(str(c) for c in counts))
print("kappa_nondecreasing", all(counts[i] <= counts[i + 1] for i in range(len(counts) - 1)))
print("kappa_order_of_magnitude", counts[-1] >= 10 * max(counts[0], 1))
print("kappa_one_step_isotropic", counts[0] == 1)

k = D.MOMENTUM_KAPPA
plain_steps = G.steps_to_tolerance(D.bowl_grad(k), np.array(D.KAPPA_START), D.kappa_lr(k), D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS)
momentum_steps = G.steps_to_tolerance_momentum(
    D.bowl_grad(k), np.array(D.KAPPA_START), D.MOMENTUM_LR, D.MOMENTUM_BETA, D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS
)
print("momentum_plain_steps", plain_steps)
print("momentum_steps", momentum_steps)
print("momentum_faster", momentum_steps < plain_steps)

correct_flags = G.gradient_check(D.check_function, D.check_gradient_correct, D.CHECK_POINT, D.NUMERIC_H, D.CHECK_TOL)
buggy_flags = G.gradient_check(D.check_function, D.check_gradient_buggy, D.CHECK_POINT, D.NUMERIC_H, D.CHECK_TOL)
print("check_correct_all_pass", all(correct_flags))
print("check_buggy_flags", "|".join(str(f) for f in buggy_flags))

left = G.gradient_descent(D.two_minima_grad, D.TWO_MINIMA_LEFT_START, D.TWO_MINIMA_LR, D.TWO_MINIMA_ITERS)
right = G.gradient_descent(D.two_minima_grad, D.TWO_MINIMA_RIGHT_START, D.TWO_MINIMA_LR, D.TWO_MINIMA_ITERS)
print("two_minima_differ", G.minima_differ(left[-1], right[-1], D.TWO_MINIMA_MARGIN))
print("two_minima_left_near_neg1", abs(left[-1] + 1.0) < 1e-3)
print("two_minima_right_near_pos1", abs(right[-1] - 1.0) < 1e-3)

r = G.stopping_criteria_disagree(D.PLATEAU_X0, D.plateau_grad, D.plateau_value, D.PLATEAU_LR, D.PLATEAU_GRAD_TOL, D.PLATEAU_DELTA_F_TOL)
print("plateau_grad_above_tol", r["grad_norm"] >= D.PLATEAU_GRAD_TOL)
print("plateau_delta_f_below_tol", r["delta_f"] < D.PLATEAU_DELTA_F_TOL)
print("plateau_naive_stops_early", r["naive_stops_early"])

hook_path = G.gradient_descent(lambda x: D.HOOK_A * x, D.HOOK_X0, D.HOOK_LR, D.HOOK_ITERS)
first_inf = next(i for i, v in enumerate(hook_path) if math.isinf(v))
first_nan = next(i for i, v in enumerate(hook_path) if math.isnan(v))
print("hook_nan_follows_inf", first_nan == first_inf + 1)
losses20 = [0.5 * D.HOOK_A * v * v for v in hook_path[:21]]
print("hook_loss_always_increases", all(losses20[i + 1] > losses20[i] for i in range(len(losses20) - 1)))
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "the quadratic used throughout has a = 5" "5.0" "$(get a)"
check_eq "the exact-landing boundary is 1/a = 0.2" "0.2" "$(get critical_lr)"
check_eq "the divergence boundary is 2/a = 0.4" "0.4" "$(get divergence_lr)"

check_eq "eta=0.10 (0 < eta < 1/a) is classified monotone" "monotone" "$(get regime_monotone)"
check_eq "eta=0.20 (eta = 1/a) is classified exact" "exact" "$(get regime_exact)"
check_eq "eta=0.35 (1/a < eta < 2/a) is classified oscillating" "oscillating" "$(get regime_oscillating)"
check_eq "eta=0.45 (eta > 2/a) is classified divergent" "divergent" "$(get regime_divergent)"
check_eq "at eta = 1/a, x lands exactly on 0 after one step" "0.0" "$(get exact_second_value)"
check_eq "the divergent run grows by more than 10x over 30 steps" "True" "$(get divergent_grows)"

check_eq "the monotone ratio matches |1 - eta*a| = 0.5" "True" "$(get ratio_monotone_matches)"
check_eq "the oscillating ratio matches |1 - eta*a| = 0.75" "True" "$(get ratio_oscillating_matches)"
check_eq "the divergent ratio matches |1 - eta*a| = 1.25" "True" "$(get ratio_divergent_matches)"
echo "  (measured on this run: monotone ratio $(get ratio_monotone), oscillating ratio $(get ratio_oscillating), divergent ratio $(get ratio_divergent))"

check_eq "steps to converge are non-decreasing as kappa grows" "True" "$(get kappa_nondecreasing)"
check_eq "kappa=100 needs at least 10x the steps of kappa=1" "True" "$(get kappa_order_of_magnitude)"
check_eq "the isotropic bowl (kappa=1) converges in exactly one step" "True" "$(get kappa_one_step_isotropic)"
echo "  (measured on this run: steps for kappa in {1,5,20,100} were $(get kappa_steps))"

check_eq "momentum needs strictly fewer steps than plain descent at the same eta" "True" "$(get momentum_faster)"
echo "  (measured on this run: plain $(get momentum_plain_steps) steps, momentum $(get momentum_steps) steps)"

check_eq "the correct gradient passes every component of the check" "True" "$(get check_correct_all_pass)"
check_eq "the buggy gradient is flagged on exactly component 1" "True|False|True" "$(get check_buggy_flags)"

check_eq "the two initialisations converge to minima farther apart than the margin" "True" "$(get two_minima_differ)"
check_eq "the left run converges to -1" "True" "$(get two_minima_left_near_neg1)"
check_eq "the right run converges to +1" "True" "$(get two_minima_right_near_pos1)"

check_eq "on the plateau, the gradient stays at or above its own tolerance" "True" "$(get plateau_grad_above_tol)"
check_eq "and the loss change falls below its own tolerance" "True" "$(get plateau_delta_f_below_tol)"
# Section 6 re-runs this script with D111_SELF_TEST=1, which swaps ONE
# expectation below for a deliberately wrong one. That is how the harness
# proves it can fail rather than merely asserting that it could.
expected_naive_stop="True"
if [ -n "${D111_SELF_TEST:-}" ]; then
  expected_naive_stop="False"   # the belief that a flat loss always means convergence
fi
check_eq "so the naive |delta f| stopping rule fires early" "${expected_naive_stop}" "$(get plateau_naive_stops_early)"

check_eq "the diverging run's nan follows its inf on the very next step" "True" "$(get hook_nan_follows_inf)"
check_eq "the loss increases on every one of the first 20 steps before it overflows" "True" "$(get hook_loss_always_increases)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for a wrong one -- the belief that a flat loss always means convergence --
# and asserts that the re-run reports the failure and exits non-zero. If
# this section passes, section 5 is not decorative.
if [ -z "${D111_SELF_TEST:-}" ]; then
  self_out="$(D111_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: so the naive |delta f| stopping rule fires early"*)
      check "the failing check is named in the output with both values" "yes" ;;
    *) check "the failing check is named in the output with both values" "no" ;;
  esac
  case "${self_out}" in
    *", 1 failure(s)."*)
      check "the summary line counts exactly one failure" "yes" ;;
    *) check "the summary line counts exactly one failure" "no" ;;
  esac
else
  echo "  (self-test run: section 6 does not recurse)"
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
