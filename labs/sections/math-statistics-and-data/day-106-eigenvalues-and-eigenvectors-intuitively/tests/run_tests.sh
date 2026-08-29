#!/usr/bin/env bash
# Tests for the Day 106 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * out of twenty-four directions spread around the circle, exactly two come
#     back on their own line -- and those two are the SAME line pointing
#     opposite ways, so one line survived, not two;
#   * a sweep of 180,000 directions finds the second eigen-line the coarse fan
#     stepped straight over, at 116.565 degrees;
#   * the hand solution -- trace 7, determinant 10, discriminant 9, eigenvalues
#     5 and 2 -- agrees with numpy.linalg.eig to 1e-9;
#   * numpy.linalg.eig returns complex128 for a real matrix with two real
#     eigenvalues, which contradicts its own docstring and is recorded as
#     measured rather than smoothed over;
#   * a shear has ONE eigen-line while eig returns TWO columns, and both
#     columns lie on that one line;
#   * a plane rotation has no real eigenvalues at all, and taking .real without
#     checking silently reports two eigenvalues of magnitude 1 as 0;
#   * the eigenvalues of every matrix here multiply to the determinant and add
#     to the trace;
#   * the power method converges in 25 iterations to 1e-10, its error shrinks
#     by the eigenvalue ratio 0.4 every round, and the same code needs 962
#     iterations when that ratio is 0.98;
#   * un-normalised iteration overflows to inf and then to nan, destroying a
#     direction that was already correct;
#   * PCA on a cloud built along 30 degrees recovers 30.101 degrees from the
#     coordinates alone -- and returns it with the sign flipped, which is
#     correct and is the trap the whole lab is built around;
#   * forgetting to centre gives a confident answer 136.58 degrees wrong;
#   * nothing is downloaded, and nothing is left behind on disk.
#
# Everything runs offline. Nothing binds a port, nothing writes outside the
# lab or a temporary directory, nothing needs a key. Deterministic,
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

echo "Day 106 — The Vectors That Keep Their Direction"
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

for package in numpy pytest; do
  pinned="$(grep -iE "^${package}==" "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
  installed="$("${python_bin}" -c "from importlib.metadata import version; print(version('${package}'))")"
  check_eq "installed ${package} matches requirements.txt" "${pinned}" "${installed}"
done

major="$("${python_bin}" -c "import numpy; print(numpy.__version__.split('.')[0])")"
check_eq "numpy is version 2 or later" "2" "${major}"

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_the_fan_of_vectors 02_by_hand_2x2 03_standard_transformations \
              04_power_method 05_pca_from_covariance 06_eig_against_eigh; do
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
echo "3. The reference pytest suite: real values, stated tolerances"
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
if [ "${ref_passed:-0}" -ge 90 ]; then
  check "the reference suite ran at least 90 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 90 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `eigen` and
# `dataset`, and pytest imports test files by putting their directory on
# sys.path -- so collecting both suites at once would otherwise let the starter
# tests import the REFERENCE solution and report unwritten exercises as
# passing. Each directory's conftest.py prevents that. This check proves it
# still does: across both suites, the skip count must be unchanged.
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
import numpy as np

import dataset
import eigen
from dataset import (
    A, A_EIGENVALUES, A_EIGENVECTORS, ELONGATION_DEG, PROJECTION_ONTO_X,
    REFLECTION_IN_X, ROTATION_60, ROTATION_90, SHEAR, SPREAD_ALONG,
    STANDARD_TRANSFORMATIONS, SYMMETRIC, SYMMETRIC_3X3, elongation_direction,
    make_cloud, power_method_start,
)

# -- the fan of vectors
kept = [
    a for a in range(0, 360, 15)
    if eigen.deviation_degrees(
        [np.cos(np.radians(a)), np.sin(np.radians(a))],
        A @ np.array([np.cos(np.radians(a)), np.sin(np.radians(a))]),
    ) < 1e-9
]
print("fan_kept", kept)
up = np.array([np.cos(np.radians(45)), np.sin(np.radians(45))])
down = np.array([np.cos(np.radians(225)), np.sin(np.radians(225))])
print("fan_45_and_225_same_line", bool(np.allclose(down, -up, atol=1e-12)))
print("fan_x_axis_swing", round(eigen.deviation_degrees([1.0, 0.0], A @ np.array([1.0, 0.0])), 6))

swept = eigen.eigen_lines_by_sweep(A)
print("sweep_verdict", swept["verdict"])
print("sweep_line_count", len(swept["lines"]))
print("sweep_lines_match_exact_angles",
      bool(np.allclose(swept["lines"], dataset.A_EIGEN_ANGLES_DEG, atol=1e-2)))

for angle, expected in zip(dataset.A_EIGEN_ANGLES_DEG, A_EIGENVALUES):
    v = np.array([np.cos(np.radians(angle)), np.sin(np.radians(angle))])
    print(f"stretch_at_{expected:.0f}", round(float(np.linalg.norm(A @ v)), 12))

print("integer_checks_hold", bool(all(
    np.allclose(A @ np.array(v), lam * np.array(v), atol=1e-12)
    for v, lam in zip(A_EIGENVECTORS, A_EIGENVALUES))))
print("zero_vector_fits_every_lambda", bool(all(
    np.allclose(A @ np.zeros(2), c * np.zeros(2), atol=1e-12)
    for c in (5.0, 2.0, 0.0, -3.5, 1000.0))))

# -- the hand solution
trace, det = eigen.characteristic_coefficients(A)
print("trace", trace)
print("determinant", det)
print("discriminant", trace * trace - 4.0 * det)
hand = sorted(v.real for v in eigen.eigenvalues_2x2(A))
print("hand_eigenvalues", [round(v, 12) for v in hand])
print("hand_matches_numpy",
      bool(np.allclose(hand, sorted(np.linalg.eig(A)[0].real), atol=1e-9)))
print("det_of_a_minus_lambda_i_is_zero", bool(all(
    abs(float(np.linalg.det(A - lam * np.eye(2)))) < 1e-12 for lam in A_EIGENVALUES)))

# -- what numpy actually returns
values, vectors = np.linalg.eig(A)
print("eig_dtype", str(values.dtype))
print("eig_imag_all_zero", bool(np.all(values.imag == 0.0)))
print("eig_dtype_on_identity", str(np.linalg.eig(np.eye(2))[0].dtype))
smaller = int(np.argmin(values.real))
mine = np.array(A_EIGENVECTORS[1], dtype=float)
mine = mine / np.linalg.norm(mine)
theirs = vectors.real[:, smaller]
print("sign_flip_allclose_says_false", bool(not np.allclose(mine, theirs, atol=1e-6)))
print("sign_flip_is_exact_negative", bool(np.allclose(mine, -theirs, atol=1e-9)))
print("sign_flip_abs_cosine", round(eigen.abs_cosine(mine, theirs), 12))

worst = 0.0
for m in (A, SYMMETRIC, SHEAR, REFLECTION_IN_X, PROJECTION_ONTO_X):
    vals, vecs = np.linalg.eig(m)
    for i in range(len(vals)):
        worst = max(worst, float(np.abs(m @ vecs[:, i] - vals[i] * vecs[:, i]).max()))
print("worst_a_v_minus_lambda_v_residual_below_1e12", bool(worst < 1e-12))

# -- the standard transformations
shear_found = eigen.eigen_lines_by_sweep(SHEAR)
sv, svec = np.linalg.eig(SHEAR)
print("shear_eigen_lines", len(shear_found["lines"]))
print("shear_eig_columns", svec.shape[1])
print("shear_columns_same_line",
      round(eigen.abs_cosine(svec.real[:, 0], svec.real[:, 1]), 8))
print("shear_eigenvalues", [round(float(v), 12) for v in sv.real])
print("shear_eigenvector_matrix_is_singular",
      bool(abs(float(np.linalg.det(svec.real))) < 1e-15))

for name, rot in (("90", ROTATION_90), ("60", ROTATION_60)):
    rv = np.linalg.eig(rot)[0]
    print(f"rotation{name}_all_complex", bool(np.all(np.abs(rv.imag) > 0.5)))
    print(f"rotation{name}_magnitudes_are_one", bool(np.allclose(np.abs(rv), 1.0, atol=1e-9)))
    print(f"rotation{name}_verdict", eigen.eigen_lines_by_sweep(rot)["verdict"])
print("rotation90_real_parts_destroy_the_answer",
      bool(np.allclose(np.linalg.eig(ROTATION_90)[0].real, 0.0, atol=1e-9)))
rt, rd = eigen.characteristic_coefficients(ROTATION_90)
print("rotation90_discriminant", rt * rt - 4.0 * rd)

print("identity_verdict", eigen.eigen_lines_by_sweep(np.eye(2))["verdict"])
print("uniform_scale_verdict", eigen.eigen_lines_by_sweep(2.0 * np.eye(2))["verdict"])
print("reflection_eigenvalues",
      [round(float(v), 12) for v in np.sort(np.linalg.eig(REFLECTION_IN_X)[0].real)])
print("projection_eigenvalues",
      [round(float(v), 12) for v in np.sort(np.linalg.eig(PROJECTION_ONTO_X)[0].real)])
print("projection_determinant", round(float(np.linalg.det(PROJECTION_ONTO_X)), 12))
_devs, collapsed = eigen.sweep_deviations(PROJECTION_ONTO_X, [0.0, 45.0, 90.0])
print("projection_collapses_the_y_axis", collapsed.tolist())

prod_ok = trace_ok = True
for name in STANDARD_TRANSFORMATIONS:
    m = STANDARD_TRANSFORMATIONS[name][0]
    vals = np.linalg.eig(m)[0]
    prod_ok &= abs(complex(np.prod(vals)).real - float(np.linalg.det(m))) < 1e-9
    trace_ok &= abs(complex(np.sum(vals)).real - float(np.trace(m))) < 1e-9
print("eigenvalues_multiply_to_determinant_on_all_eight", bool(prod_ok))
print("eigenvalues_add_to_trace_on_all_eight", bool(trace_ok))

for label, m in (("2x2", SYMMETRIC), ("3x3", SYMMETRIC_3X3)):
    vals, vecs = np.linalg.eigh(m)
    print(f"symmetric_{label}_dtype", str(vals.dtype))
    print(f"symmetric_{label}_orthogonal",
          bool(float(np.abs(vecs.T @ vecs - np.eye(len(vals))).max()) < 1e-12))
print("eigh_sorted_ascending", bool(np.all(np.diff(np.linalg.eigh(SYMMETRIC)[0]) >= 0)))
print("eigh_on_non_symmetric_is_silently_wrong", bool(
    np.allclose(np.linalg.eigh(A)[0], np.linalg.eigvalsh([[4.0, 2.0], [2.0, 3.0]]), atol=1e-12)
    and not np.allclose(np.sort(np.linalg.eigh(A)[0]), sorted(A_EIGENVALUES), atol=1e-6)))

vals, vecs = np.linalg.eig(A)
rebuilt = vecs @ np.diag(vals) @ np.linalg.inv(vecs)
print("diagonalisation_rebuilds_a", bool(np.allclose(rebuilt.real, A, atol=1e-9)))

# -- the power method
result = eigen.power_method(A, power_method_start(), tol=1e-10)
print("power_iterations", result["iterations"])
print("power_converged", result["converged"])
print("power_change_below_tolerance", bool(result["change"] < 1e-10))
print("power_direction", round(eigen.direction_degrees(result["vector"]), 6))
print("power_eigenvalue", round(result["eigenvalue"], 9))
print("power_abs_cosine_with_1_1", round(eigen.abs_cosine(result["vector"], (1.0, 1.0)), 12))
top = int(np.argmax(np.abs(np.linalg.eig(A)[0].real)))
print("power_agrees_with_numpy_eigenvalue", bool(
    abs(result["eigenvalue"] - float(np.linalg.eig(A)[0].real[top])) < 1e-9))
hist = result["history"]
print("power_ratio_at_step_14", round(hist[13] / hist[12], 6))
slow = eigen.power_method(np.diag([5.0, 4.9]), np.array([0.6, 0.8]), tol=1e-10)
print("power_close_eigenvalues_iterations", slow["iterations"])
print("power_negative_dominant_converges", eigen.power_method(
    np.diag([-5.0, 2.0]), np.array([0.6, 0.8]), tol=1e-10)["converged"])
print("power_rayleigh_exact_on_true_eigenvector", bool(all(
    abs(eigen.rayleigh_quotient(A, v) - lam) < 1e-12
    for v, lam in zip(A_EIGENVECTORS, A_EIGENVALUES))))
print("power_reports_failure_rather_than_lying", eigen.power_method(
    A, power_method_start(), tol=1e-16, max_iter=5)["converged"])

v = power_method_start()
with np.errstate(over="ignore"):
    for _ in range(600):
        v = A @ v
print("unnormalised_overflows", bool(not np.all(np.isfinite(v))))
with np.errstate(invalid="ignore"):
    print("unnormalised_then_normalised_is_nan",
          bool(np.all(np.isnan(v / np.linalg.norm(v)))))

# -- PCA
cloud = make_cloud()
print("cloud_shape", cloud.shape)
print("cloud_is_reproducible", bool(np.array_equal(make_cloud(), make_cloud())))
cov = eigen.covariance_matrix(cloud)
print("covariance_matches_numpy_cov",
      bool(np.allclose(cov, np.cov(cloud, rowvar=False), atol=1e-12)))
print("covariance_is_symmetric", bool(np.allclose(cov, cov.T, atol=1e-15)))
print("covariance_shape", cov.shape)
variances, directions = eigen.principal_components(cloud)
truth = elongation_direction()
print("pca_top_direction", round(eigen.direction_degrees(directions[:, 0]), 6))
print("pca_true_direction", ELONGATION_DEG)
print("pca_abs_cosine", round(eigen.abs_cosine(directions[:, 0], truth), 10))
print("pca_top_component_points_the_other_way",
      bool(float(np.dot(directions[:, 0], truth)) < 0.0))
print("pca_allclose_says_false_on_a_correct_answer",
      bool(not np.allclose(directions[:, 0], truth, atol=1e-3)))
print("pca_sqrt_top_eigenvalue", round(float(np.sqrt(variances[0])), 6))
print("pca_sqrt_second_eigenvalue", round(float(np.sqrt(variances[1])), 6))
print("pca_variance_explained", round(float(variances[0] / variances.sum()), 6))
print("pca_components_perpendicular",
      bool(abs(float(np.dot(directions[:, 0], directions[:, 1]))) < 1e-12))
projected = (cloud - cloud.mean(axis=0)) @ directions
print("pca_projections_uncorrelated",
      bool(abs(float(np.corrcoef(projected.T)[0, 1])) < 1e-12))

uncentred = (cloud.T @ cloud) / (cloud.shape[0] - 1)
uv, uvec = np.linalg.eigh(uncentred)
uncentred_deg = eigen.direction_degrees(uvec[:, int(np.argmax(uv))])
print("pca_uncentred_direction", round(uncentred_deg, 6))
print("pca_uncentred_error", round(abs(uncentred_deg - ELONGATION_DEG), 6))
print("pca_eig_and_eigh_agree_on_covariance", bool(np.allclose(
    np.sort(np.linalg.eig(cov)[0].real), np.sort(np.linalg.eigh(cov)[0]), atol=1e-12)))
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

# -- the fan
check_eq "of 24 directions, exactly 45 and 225 degrees keep their line" \
  "[45, 225]" "$(get fan_kept)"
check_eq "and 45 and 225 are the SAME line, so one line survived, not two" \
  "True" "$(get fan_45_and_225_same_line)"
check_eq "the x-axis is knocked 26.565051 degrees off its line" \
  "26.565051" "$(get fan_x_axis_swing)"
check_eq "a 180,000-direction sweep finds surviving lines" \
  "some" "$(get sweep_verdict)"
check_eq "and finds TWO of them: the coarse fan stepped over the second" \
  "2" "$(get sweep_line_count)"
check_eq "both agree with the exact angles 45 and 116.565051 to 0.01 degrees" \
  "True" "$(get sweep_lines_match_exact_angles)"
check_eq "the 45-degree direction is stretched by exactly 5" \
  "5.0" "$(get stretch_at_5)"
check_eq "the 116.565-degree direction is stretched by exactly 2" \
  "2.0" "$(get stretch_at_2)"
check_eq "the integer eigenvectors (1,1) and (1,-2) check out on paper" \
  "True" "$(get integer_checks_hold)"
check_eq "the zero vector satisfies A v = lambda v for EVERY lambda, so it is excluded" \
  "True" "$(get zero_vector_fits_every_lambda)"

# -- the hand solution
check_eq "trace of A is 7" "7.0" "$(get trace)"
check_eq "determinant of A is 10" "10.0" "$(get determinant)"
check_eq "discriminant is 9, so two distinct real eigenvalues" "9.0" "$(get discriminant)"
check_eq "the hand quadratic gives exactly 2 and 5" \
  "[2.0, 5.0]" "$(get hand_eigenvalues)"
check_eq "and matches numpy.linalg.eig, sorted, to 1e-9" \
  "True" "$(get hand_matches_numpy)"
check_eq "det(A - lambda I) is zero at each eigenvalue, which is the whole derivation" \
  "True" "$(get det_of_a_minus_lambda_i_is_zero)"

# -- what numpy returns
check_eq "numpy.linalg.eig returns complex128 for a real matrix" \
  "complex128" "$(get eig_dtype)"
check_eq "with every imaginary part exactly zero" "True" "$(get eig_imag_all_zero)"
check_eq "and does the same for numpy.eye(2), whose eigenvalues are both 1" \
  "complex128" "$(get eig_dtype_on_identity)"
check_eq "numpy.allclose says False on a CORRECT eigenvector" \
  "True" "$(get sign_flip_allclose_says_false)"
check_eq "because the two answers are exact negatives of each other" \
  "True" "$(get sign_flip_is_exact_negative)"
check_eq "and the absolute cosine, which asks the right question, says 1" \
  "1.0" "$(get sign_flip_abs_cosine)"
check_eq "every pair numpy returned satisfies A v = lambda v below 1e-12" \
  "True" "$(get worst_a_v_minus_lambda_v_residual_below_1e12)"

# -- the standard transformations
#
# Section 6 re-runs this script with D106_SELF_TEST=1, which swaps ONE
# expectation below for the naive belief that counting eig's columns counts
# eigendirections. That is how the harness proves it can fail rather than
# merely asserting that it could.
expected_shear_lines="1"
if [ -n "${D106_SELF_TEST:-}" ]; then
  expected_shear_lines="2"   # the naive belief, deliberately wrong here
fi
check_eq "a shear has exactly ONE eigen-line" \
  "${expected_shear_lines}" "$(get shear_eigen_lines)"
check_eq "while numpy.linalg.eig returns TWO columns for it" \
  "2" "$(get shear_eig_columns)"
check_eq "and those two columns lie on the same line" \
  "1.0" "$(get shear_columns_same_line)"
check_eq "its eigenvalue is 1, repeated" "[1.0, 1.0]" "$(get shear_eigenvalues)"
check_eq "so its eigenvector matrix is singular and it cannot be diagonalised" \
  "True" "$(get shear_eigenvector_matrix_is_singular)"

check_eq "a 90-degree rotation has no real eigenvalues" \
  "True" "$(get rotation90_all_complex)"
check_eq "both of magnitude 1, because a rotation changes no lengths" \
  "True" "$(get rotation90_magnitudes_are_one)"
check_eq "and a 180,000-direction sweep finds nothing that kept its line" \
  "none" "$(get rotation90_verdict)"
check_eq "the same holds for a 60-degree rotation" \
  "True" "$(get rotation60_all_complex)"
check_eq "with the same verdict from measurement" "none" "$(get rotation60_verdict)"
check_eq "taking .real without checking reports both eigenvalues as 0" \
  "True" "$(get rotation90_real_parts_destroy_the_answer)"
check_eq "the negative discriminant is the algebra reporting the geometry" \
  "-4.0" "$(get rotation90_discriminant)"

check_eq "the identity keeps EVERY direction" \
  "every direction" "$(get identity_verdict)"
check_eq "and so does a uniform scaling" \
  "every direction" "$(get uniform_scale_verdict)"
check_eq "a reflection has eigenvalues 1 and -1: one direction reversed" \
  "[-1.0, 1.0]" "$(get reflection_eigenvalues)"
check_eq "a projection has eigenvalue 0" "[0.0, 1.0]" "$(get projection_eigenvalues)"
check_eq "and determinant 0, which is Day 102's news arriving twice" \
  "0.0" "$(get projection_determinant)"
check_eq "the collapsed y-axis has no direction left to measure" \
  "[False, False, True]" "$(get projection_collapses_the_y_axis)"
check_eq "on all eight transformations the eigenvalues multiply to the determinant" \
  "True" "$(get eigenvalues_multiply_to_determinant_on_all_eight)"
check_eq "and add to the trace" "True" "$(get eigenvalues_add_to_trace_on_all_eight)"

check_eq "a symmetric 2x2 gives eigh real float64 values" \
  "float64" "$(get symmetric_2x2_dtype)"
check_eq "with eigenvectors at right angles" "True" "$(get symmetric_2x2_orthogonal)"
check_eq "and the same holds for a symmetric 3x3, so it is not a 2x2 accident" \
  "True" "$(get symmetric_3x3_orthogonal)"
check_eq "eigh returns its values sorted ascending; eig promises no order" \
  "True" "$(get eigh_sorted_ascending)"
check_eq "eigh on NON-symmetric input answers a different question, silently" \
  "True" "$(get eigh_on_non_symmetric_is_silently_wrong)"
check_eq "diagonalisation V D V-inverse rebuilds A exactly" \
  "True" "$(get diagonalisation_rebuilds_a)"

# -- the power method
check_eq "the power method converges in 25 iterations to 1e-10" \
  "25" "$(get power_iterations)"
check_eq "and says so rather than being assumed" "True" "$(get power_converged)"
check_eq "with the final change below the stated tolerance" \
  "True" "$(get power_change_below_tolerance)"
check_eq "it lands on the 45-degree eigen-line" "45.0" "$(get power_direction)"
check_eq "with abs_cosine 1 against (1, 1)" "1.0" "$(get power_abs_cosine_with_1_1)"
check_eq "and a Rayleigh quotient of 5 to nine decimal places" \
  "5.0" "$(get power_eigenvalue)"
check_eq "agreeing with numpy.linalg.eig to 1e-9" \
  "True" "$(get power_agrees_with_numpy_eigenvalue)"
check_eq "its error shrinks by the eigenvalue ratio 2/5 every round" \
  "0.399999" "$(get power_ratio_at_step_14)"
check_eq "eigenvalues of 5 and 4.9 need 962 iterations instead of 25" \
  "962" "$(get power_close_eigenvalues_iterations)"
check_eq "a NEGATIVE dominant eigenvalue still converges, given sign alignment" \
  "True" "$(get power_negative_dominant_converges)"
check_eq "the Rayleigh quotient is exact on a true eigenvector" \
  "True" "$(get power_rayleigh_exact_on_true_eigenvector)"
check_eq "and non-convergence is REPORTED, not hidden" \
  "False" "$(get power_reports_failure_rather_than_lying)"
check_eq "600 un-normalised rounds overflow to infinity" \
  "True" "$(get unnormalised_overflows)"
check_eq "and normalising afterwards gives nan: the direction is unrecoverable" \
  "True" "$(get unnormalised_then_normalised_is_nan)"

# -- PCA
check_eq "the cloud is 400 points in 2 dimensions" "(400, 2)" "$(get cloud_shape)"
check_eq "generated from a seed, so it is identical on every run" \
  "True" "$(get cloud_is_reproducible)"
check_eq "the from-scratch covariance matches numpy.cov to 1e-12" \
  "True" "$(get covariance_matches_numpy_cov)"
check_eq "a covariance matrix is always symmetric" \
  "True" "$(get covariance_is_symmetric)"
check_eq "and is 2 by 2 for a (400, 2) dataset, not 400 by 400" \
  "(2, 2)" "$(get covariance_shape)"
check_eq "PCA recovers 30.101134 degrees from the coordinates alone" \
  "30.101134" "$(get pca_top_direction)"
check_eq "against a true elongation of 30.0 degrees it was never told" \
  "30.0" "$(get pca_true_direction)"
check_eq "abs_cosine with the truth is 0.9999984422" \
  "0.9999984422" "$(get pca_abs_cosine)"
check_eq "and the component came back pointing the OTHER way along that line" \
  "True" "$(get pca_top_component_points_the_other_way)"
check_eq "so numpy.allclose says False on an answer that is exactly right" \
  "True" "$(get pca_allclose_says_false_on_a_correct_answer)"
check_eq "the top eigenvalue's square root recovers the spread 3.0 it was built with" \
  "2.902251" "$(get pca_sqrt_top_eigenvalue)"
check_eq "and the second recovers the across-spread 0.4" \
  "0.420504" "$(get pca_sqrt_second_eigenvalue)"
check_eq "the first component alone carries 97.9439% of the variance" \
  "0.979439" "$(get pca_variance_explained)"
check_eq "the two components are perpendicular" \
  "True" "$(get pca_components_perpendicular)"
check_eq "and the projections onto them are uncorrelated" \
  "True" "$(get pca_projections_uncorrelated)"
check_eq "forgetting to centre points the answer at 166.583965 degrees" \
  "166.583965" "$(get pca_uncentred_direction)"
check_eq "which is 136.583965 degrees wrong, with no error and no warning" \
  "136.583965" "$(get pca_uncentred_error)"
check_eq "eig and eigh agree on the covariance matrix" \
  "True" "$(get pca_eig_and_eigh_agree_on_covariance)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for the naive belief that a shear has two eigendirections because eig returns
# two columns, and asserts that the re-run reports the failure and exits
# non-zero. If this section passes, section 5 is not decorative.
if [ -z "${D106_SELF_TEST:-}" ]; then
  self_out="$(D106_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: a shear has exactly ONE eigen-line"*)
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
echo "7. Nothing was downloaded, and nothing was left behind"
# --------------------------------------------------------------------------

# Every find below PRUNES .venv first, and it is not optional. The README tells
# you to create a lab-local virtual environment, so `.venv` is the documented
# setup rather than litter -- and NumPy ships its own compiled bytecode inside
# it. Without the prune, this section would fail the lab for following its own
# installation instructions.
if find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -print -quit 2>/dev/null | grep -q .; then
  check "no __pycache__ directory left under the lab (ignoring .venv)" "no"
else
  check "no __pycache__ directory left under the lab (ignoring .venv)" "yes"
fi

if find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -print -quit 2>/dev/null | grep -q .; then
  check "no .pytest_cache directory left under the lab (ignoring .venv)" "no"
else
  check "no .pytest_cache directory left under the lab (ignoring .venv)" "yes"
fi

# The dataset is GENERATED from a seed, not downloaded and not committed. If a
# data file ever appears in the lab's own tree, either something was committed
# by mistake or a script wrote one and failed to clean up. NumPy ships plenty
# of its own data inside site-packages, so .venv is pruned here too.
data_files="$(find "${lab_dir}" -name '.venv' -prune -o -type f \
  \( -name '*.csv' -o -name '*.npy' -o -name '*.npz' -o -name '*.json' \
     -o -name '*.parquet' -o -name '*.pkl' \) -print 2>/dev/null \
  | wc -l | tr -d ' ')"
check_eq "no data file in the lab's own tree: the cloud is generated from a seed" \
  "0" "${data_files}"

if grep -rqE 'urlopen|requests\.|socket\.|http://|https://' \
     "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null; then
  check "no lab source opens a network connection" "no"
else
  check "no lab source opens a network connection" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
