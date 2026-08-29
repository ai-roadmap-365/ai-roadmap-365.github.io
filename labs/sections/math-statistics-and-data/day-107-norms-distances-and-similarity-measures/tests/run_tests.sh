#!/usr/bin/env bash
# Tests for the Day 107 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * one query, three candidates, and L1, L2 and cosine naming three
#     DIFFERENT winners -- the disagreement the whole day is built on;
#   * the p-norm of (3, 4) is 7, 5 and 4 at p = 1, 2 and infinity, falls
#     monotonically in between, and matches numpy.linalg.norm(v, ord=p) to
#     1e-12 for every p tested;
#   * the L1, L2 and L-infinity unit balls are strictly nested, and counting
#     grid cells inside the L2 one recovers pi;
#   * all four norm axioms hold for L1, L2 and L-infinity, and SQUARED
#     Euclidean distance fails absolute homogeneity by a factor of 2;
#   * the triangle inequality holds for L1, L2 and L-infinity in all six
#     orderings, and FAILS for cosine distance on 326 of 3375 binary triples,
#     with the two-dimensional counter-example named;
#   * Jaccard distance and Hamming distance satisfy it on all 4096 triples;
#   * Chebyshev accepts a part that L1 and L2 both rank as the worse one,
#     because the acceptance rule is an L-infinity ball;
#   * Jaccard and cosine rank the same two sets in OPPOSITE orders;
#   * two points the same Euclidean distance from the mean are 1.1142 and
#     6.0 apart under Mahalanobis, and the pure-Python Gauss-Jordan inverse
#     and numpy.linalg.inv disagree in the last bit while both round to 6;
#   * standardising two columns in mismatched units changes the winner, and a
#     UNIT change alone changes it too;
#   * nothing is downloaded, nothing is written outside the lab, and nothing
#     is left behind on disk.
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

echo "Day 107 — Choose Your Distance on Purpose"
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

for script in 01_three_measures_three_winners 02_the_p_norm_family \
              03_metrics_and_non_metrics 04_choosing_by_the_shape_of_the_data \
              05_mahalanobis_distance 06_scaling_changes_the_answer; do
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
if [ "${ref_passed:-0}" -ge 100 ]; then
  check "the reference suite ran at least 100 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 100 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `measures` and
# `catalogue`, and pytest imports test files by putting their directory on
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
import itertools
import math

import numpy as np

import catalogue
import measures

TOL = measures.TOL
Q = catalogue.QUERY
A = catalogue.ARTICLES

# -- the opening disagreement
print("l1_winner", measures.winner(Q, A, measures.l1_distance))
print("l2_winner", measures.winner(Q, A, measures.l2_distance))
print("linf_winner", measures.winner(Q, A, measures.linf_distance))
print("cosine_winner",
      measures.winner(Q, A, measures.cosine_similarity, higher_is_better=True))
print("distinct_winners", len({
    measures.winner(Q, A, measures.l1_distance),
    measures.winner(Q, A, measures.l2_distance),
    measures.winner(Q, A, measures.cosine_similarity, higher_is_better=True),
}))
print("l1_values", [measures.l1_distance(Q, v) for v in A.values()])
print("l2_aisle_exact", measures.l2_distance(Q, A["Aisle"]) == 5.0)
print("cosine_cartogram_is_one",
      abs(measures.cosine_similarity(Q, A["Cartogram"]) - 1.0) <= TOL)
print("cartogram_worst_l2",
      measures.rank(Q, A, measures.l2_distance)[-1][0])

# -- the p-norm family
v = (3.0, 4.0)
print("p_norms", [measures.p_norm(v, p) for p in (1, 2, math.inf)])
sweep = [measures.p_norm(v, p) for p in (1, 1.5, 2, 3, 4, 8, 16, 64)]
print("p_sweep_monotone", all(b <= a + TOL for a, b in zip(sweep, sweep[1:])))
worst_norm = max(
    abs(measures.p_norm(v, math.inf if np.isinf(p) else p)
        - float(np.linalg.norm(np.asarray(v), ord=p)))
    for p in (1, 1.5, 2, 3, 8, np.inf))
print("p_norm_vs_numpy", worst_norm <= TOL)
try:
    measures.p_norm(v, 0.5)
except ValueError:
    print("p_norm_refuses_below_one", True)
else:
    print("p_norm_refuses_below_one", False)

# -- the unit balls, counted on the same grid the script draws
W, H = 61, 25
counts = {1: 0, 2: 0, 3: 0}
for row in range(H):
    y = 1.25 - 2.5 * row / (H - 1)
    for col in range(W):
        x = -1.25 + 2.5 * col / (W - 1)
        if measures.p_norm((x, y), 1) <= 1.0:
            counts[1] += 1
        if measures.p_norm((x, y), 2) <= 1.0:
            counts[2] += 1
        if measures.p_norm((x, y), math.inf) <= 1.0:
            counts[3] += 1
print("ball_counts", counts[1], counts[2], counts[3])
print("balls_nested", counts[1] < counts[2] < counts[3])
cell = (2.5 / (W - 1)) * (2.5 / (H - 1))
print("l2_ball_area_recovers_pi", abs(counts[2] * cell - math.pi) < 0.25)

# -- the norm axioms
av, k = catalogue.AXIOM_VECTOR, catalogue.AXIOM_SCALAR
w = catalogue.TRIANGLE_TRIPLE[1]
homog, tri, zero_ok = True, True, True
for fn in (measures.l1_norm, measures.l2_norm, measures.linf_norm):
    homog &= abs(fn([k * x for x in av]) - abs(k) * fn(av)) <= TOL
    tri &= fn([a + b for a, b in zip(av, w)]) <= fn(av) + fn(w) + TOL
    zero_ok &= fn((0.0, 0.0, 0.0)) == 0.0 and fn(av) > 0.0
print("norm_homogeneity", homog)
print("norm_triangle", tri)
print("norm_zero_only_at_zero", zero_ok)
sq = sum(x * x for x in av)
print("squared_l2_doubles_to", sum((2 * x) ** 2 for x in av) / sq)

# -- metrics and non-metrics
d = measures.cosine_distance
east, diag, north = catalogue.EAST, catalogue.DIAGONAL, catalogue.NORTH
print("cosine_detour", round(d(east, diag) + d(diag, north), 6))
print("cosine_direct", round(d(east, north), 6))
print("cosine_violates", d(east, diag) + d(diag, north) < d(east, north) - TOL)
print("cosine_zero_between_different_vectors",
      abs(d((1.0, 0.0), (2.0, 0.0))) <= TOL)
ok = True
for fn in (measures.l1_distance, measures.l2_distance, measures.linf_distance):
    for a, b, c in itertools.permutations(catalogue.TRIANGLE_TRIPLE):
        ok &= fn(a, b) + fn(b, c) >= fn(a, c) - TOL
print("lp_triangle_all_orderings", ok)

universe = ("a", "b", "c", "d")
subsets = [frozenset(c) for r in range(len(universe) + 1)
           for c in itertools.combinations(universe, r)]
jac_ok = all(
    measures.jaccard_distance(a, b) + measures.jaccard_distance(b, c)
    >= measures.jaccard_distance(a, c) - TOL
    for a, b, c in itertools.product(subsets, repeat=3))
print("jaccard_triples", len(subsets) ** 3)
print("jaccard_is_metric", jac_ok)

bits = list(itertools.product((0, 1), repeat=4))
ham_ok = all(
    measures.hamming_distance(a, b) + measures.hamming_distance(b, c)
    >= measures.hamming_distance(a, c)
    for a, b, c in itertools.product(bits, repeat=3))
print("hamming_is_metric", ham_ok)

vectors = [x for x in itertools.product((0, 1), repeat=4) if any(x)]
violations = sum(
    1 for a, b, c in itertools.product(vectors, repeat=3)
    if d(a, b) + d(b, c) < d(a, c) - TOL)
print("cosine_violations", violations, len(vectors) ** 3)

# -- the four data shapes
fa, fb = catalogue.FLOOR_FROM, catalogue.FLOOR_TO
print("warehouse", measures.l1_distance(fa, fb), measures.l2_distance(fa, fb),
      measures.linf_distance(fa, fb))
nominal, limit = catalogue.NOMINAL_PART, catalogue.PART_TOLERANCE_MM
pa = catalogue.MEASURED_PARTS["batch-A"]
pb = catalogue.MEASURED_PARTS["batch-B"]
print("batch_a_passes", measures.linf_distance(pa, nominal) <= limit + TOL)
print("batch_b_fails", measures.linf_distance(pb, nominal) > limit)
print("l1_prefers_batch_b",
      measures.l1_distance(pb, nominal) < measures.l1_distance(pa, nominal))
print("l2_prefers_batch_b",
      measures.l2_distance(pb, nominal) > measures.l2_distance(pa, nominal))

ref = catalogue.REFERENCE_RECORD
print("hamming_records", [measures.hamming_distance(ref, r)
                          for r in catalogue.CANDIDATE_RECORDS.values()])
print("hamming_flags",
      measures.hamming_distance(catalogue.FLAGS_A, catalogue.FLAGS_B))
print("hamming_equals_l1_on_bits",
      abs(measures.l1_distance(catalogue.FLAGS_A, catalogue.FLAGS_B)
          - measures.hamming_distance(catalogue.FLAGS_A,
                                      catalogue.FLAGS_B)) <= TOL)

rq = catalogue.RECIPE_QUERY
axes = measures.vocabulary(rq, *catalogue.RECIPES.values())
qv = measures.to_binary_vector(rq, axes)
jac = {n: measures.jaccard_similarity(rq, s)
       for n, s in catalogue.RECIPES.items()}
cos = {n: measures.cosine_similarity(qv, measures.to_binary_vector(s, axes))
       for n, s in catalogue.RECIPES.items()}
print("jaccard_recipe_winner", max(jac, key=jac.get))
print("cosine_recipe_winner", max(cos, key=cos.get))
print("recipe_winners_differ", max(jac, key=jac.get) != max(cos, key=cos.get))
print("jaccard_values", round(jac["Sachertorte"], 6), round(jac["Shortbread"], 6))
print("cosine_values", round(cos["Sachertorte"], 6), round(cos["Shortbread"], 6))

# -- Mahalanobis
data = catalogue.SENSOR_READINGS
mean = measures.column_means(data)
cov = measures.covariance_matrix(data)
inv = measures.inverse(cov)
print("covariance", cov)
print("covariance_det", round(cov[0][0] * cov[1][1] - cov[0][1] * cov[1][0], 10))
print("inverse_matches_numpy",
      float(np.max(np.abs(np.asarray(inv) - np.linalg.inv(np.asarray(cov)))))
      <= TOL)
eu_a = measures.l2_distance(catalogue.PROBE_ALONG, mean)
eu_x = measures.l2_distance(catalogue.PROBE_ACROSS, mean)
print("probes_equidistant_euclidean", abs(eu_a - eu_x) <= TOL)
print("euclidean_probe_distance", round(eu_a, 6))
ma_a = measures.mahalanobis_distance(catalogue.PROBE_ALONG, mean, inv)
ma_x = measures.mahalanobis_distance(catalogue.PROBE_ACROSS, mean, inv)
print("mahalanobis_along", round(ma_a, 6))
print("mahalanobis_across", round(ma_x, 6))
print("mahalanobis_across_repr", repr(ma_x))
inv_np = np.linalg.inv(np.asarray(cov))
z = np.asarray(catalogue.PROBE_ACROSS)
print("mahalanobis_across_numpy_repr", repr(float(math.sqrt(z @ inv_np @ z))))
print("mahalanobis_routes_agree_within_tol",
      abs(ma_x - float(math.sqrt(z @ inv_np @ z))) <= TOL)
identity = [[1.0, 0.0], [0.0, 1.0]]
print("identity_gives_euclidean", max(
    abs(measures.mahalanobis_distance(p, mean, identity)
        - measures.l2_distance(p, mean))
    for p in (catalogue.PROBE_ALONG, catalogue.PROBE_ACROSS,
              (-2.5, 4.75))) <= TOL)
print("eigenvalues", sorted(round(float(x), 10)
                            for x in np.linalg.eigvalsh(np.asarray(cov))))

# -- scaling
B, BQ = catalogue.BEARINGS, catalogue.BEARING_QUERY
rows = list(B.values())
raw_order = [n for n, _ in measures.rank(BQ, B, measures.l2_distance)]
means, stds = measures.column_means(rows), measures.column_stds(rows)
qs = measures.standardise([BQ], means, stds)[0]
bs = {n: measures.standardise([v], means, stds)[0] for n, v in B.items()}
std_order = [n for n, _ in measures.rank(qs, bs, measures.l2_distance)]
print("raw_bearing_order", raw_order)
print("standardised_bearing_order", std_order)
print("bearing_winner_changed", raw_order[0] != std_order[0])
print("bore_share_max", "%.3e" % max(
    (BQ[0] - r[0]) ** 2 / ((BQ[0] - r[0]) ** 2 + (BQ[1] - r[1]) ** 2)
    for r in rows if r != tuple(BQ)))
micro_q = (BQ[0] * 1e6, BQ[1])
micro = {n: (v[0] * 1e6, v[1]) for n, v in B.items()}
print("unit_change_winner",
      measures.winner(micro_q, micro, measures.l2_distance))
maha_order = [n for n, _ in measures.rank(
    BQ, B, lambda a, b: measures.mahalanobis_distance(
        a, b, measures.inverse(measures.covariance_matrix(rows))))]
print("mahalanobis_bearing_order", maha_order)
print("cosine_not_unit_invariant",
      [n for n, _ in measures.rank(BQ, B, measures.cosine_similarity,
                                   higher_is_better=True)]
      != [n for n, _ in measures.rank(micro_q, micro,
                                      measures.cosine_similarity,
                                      higher_is_better=True)])
doubled = {n: tuple(2 * c for c in v) for n, v in B.items()}
print("cosine_vector_scale_invariant",
      [n for n, _ in measures.rank(BQ, B, measures.cosine_similarity,
                                   higher_is_better=True)]
      == [n for n, _ in measures.rank(BQ, doubled, measures.cosine_similarity,
                                      higher_is_better=True)])

# -- the seeded sweep
rng = np.random.default_rng(107)
spread = np.array([0.04, 500.0])
flips = 0
for _ in range(2000):
    cat = rng.random((6, 2)) * spread
    query = rng.random(2) * spread
    raw_best = int(np.argmin(np.linalg.norm(cat - query, axis=1)))
    mu, sd = cat.mean(axis=0), cat.std(axis=0)
    std_best = int(np.argmin(
        np.linalg.norm((cat - mu) / sd - (query - mu) / sd, axis=1)))
    flips += raw_best != std_best
print("seeded_sweep_flips", flips)
print("seeded_sweep_in_range", 0.35 <= flips / 2000 <= 0.75)

# -- guard rails
try:
    measures.l2_distance((1.0, 2.0, 3.0), (1.0, 2.0))
except measures.DimensionMismatch:
    print("length_mismatch_raises", True)
else:
    print("length_mismatch_raises", False)
try:
    measures.cosine_similarity((0.0, 0.0), (1.0, 1.0))
except ValueError:
    print("zero_vector_raises", True)
else:
    print("zero_vector_raises", False)
try:
    measures.inverse([[1.0, 2.0], [2.0, 4.0]])
except ValueError:
    print("singular_matrix_raises", True)
else:
    print("singular_matrix_raises", False)
print("ties_break_by_name", [n for n, _ in measures.rank(
    (0.0, 0.0), {"zulu": (1.0, 1.0), "alpha": (1.0, 1.0), "mike": (1.0, 1.0)},
    measures.l2_distance)])
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "L1 picks Aisle" "Aisle" "$(get l1_winner)"
check_eq "L2 picks Beacon" "Beacon" "$(get l2_winner)"
check_eq "L-infinity also picks Beacon" "Beacon" "$(get linf_winner)"
check_eq "cosine picks Cartogram" "Cartogram" "$(get cosine_winner)"
check_eq "three measures name three DIFFERENT winners" "3" \
  "$(get distinct_winners)"
check_eq "the L1 distances are 5, 6 and 20" "[5, 6, 20]" "$(get l1_values)"
check_eq "the L2 distance to Aisle is exactly 5" "True" "$(get l2_aisle_exact)"
check_eq "the cosine to Cartogram is 1 within tolerance" "True" \
  "$(get cosine_cartogram_is_one)"
check_eq "and Cartogram is the WORST answer under L2" "Cartogram" \
  "$(get cartogram_worst_l2)"

check_eq "the p-norm of (3, 4) is 7, 5 and 4 at p = 1, 2 and infinity" \
  "[7.0, 5.0, 4.0]" "$(get p_norms)"
check_eq "the p-norm falls as p rises" "True" "$(get p_sweep_monotone)"
check_eq "and matches numpy.linalg.norm(v, ord=p) within 1e-12" "True" \
  "$(get p_norm_vs_numpy)"
check_eq "p below 1 is refused rather than answered" "True" \
  "$(get p_norm_refuses_below_one)"
check_eq "the three unit balls contain 469, 723 and 931 grid cells" \
  "469 723 931" "$(get ball_counts)"
check_eq "so the L1 ball sits inside L2 sits inside L-infinity" "True" \
  "$(get balls_nested)"
check_eq "and counting cells inside the L2 ball recovers pi" "True" \
  "$(get l2_ball_area_recovers_pi)"

check_eq "absolute homogeneity holds for L1, L2 and L-infinity" "True" \
  "$(get norm_homogeneity)"
check_eq "the triangle inequality holds for all three" "True" \
  "$(get norm_triangle)"
check_eq "and each is zero only at the zero vector" "True" \
  "$(get norm_zero_only_at_zero)"
check_eq "doubling a vector QUADRUPLES squared Euclidean distance" "4.0" \
  "$(get squared_l2_doubles_to)"

check_eq "cosine distance via the diagonal costs 0.585786" "0.585786" \
  "$(get cosine_detour)"
check_eq "and going direct costs 1.0, which is more" "1.0" \
  "$(get cosine_direct)"
# Section 6 re-runs this script with D107_SELF_TEST=1, which swaps ONE
# expectation below for a deliberately wrong one -- the naive belief that
# cosine distance behaves like a distance. That is how the harness proves it
# can fail rather than merely asserting that it could.
expected_cosine_violates="True"
if [ -n "${D107_SELF_TEST:-}" ]; then
  expected_cosine_violates="False"   # the naive belief, deliberately wrong here
fi
check_eq "so cosine distance VIOLATES the triangle inequality" \
  "${expected_cosine_violates}" "$(get cosine_violates)"
check_eq "cosine distance is also 0 between two different vectors" "True" \
  "$(get cosine_zero_between_different_vectors)"
check_eq "L1, L2 and L-infinity hold in all six orderings" "True" \
  "$(get lp_triangle_all_orderings)"
check_eq "Jaccard distance was checked on 4096 triples" "4096" \
  "$(get jaccard_triples)"
check_eq "and is a metric on every one of them" "True" \
  "$(get jaccard_is_metric)"
check_eq "Hamming distance is a metric on all 4096 bit triples" "True" \
  "$(get hamming_is_metric)"
check_eq "cosine distance fails on 326 of 3375 binary triples" "326 3375" \
  "$(get cosine_violations)"

check_eq "one displacement gives 14, 10 and 8" "14.0 10.0 8.0" \
  "$(get warehouse)"
check_eq "Chebyshev ACCEPTS batch-A" "True" "$(get batch_a_passes)"
check_eq "and REJECTS batch-B" "True" "$(get batch_b_fails)"
check_eq "even though L1 ranks batch-B as the better part" "True" \
  "$(get l1_prefers_batch_b)"
check_eq "and L2 ranks it the other way, so L1 and L2 disagree too" "True" \
  "$(get l2_prefers_batch_b)"

check_eq "Hamming on the parts register gives 1, 3 and 6" "[1, 3, 6]" \
  "$(get hamming_records)"
check_eq "and 2 on the bit flags" "2" "$(get hamming_flags)"
check_eq "on bits, Hamming equals L1 exactly" "True" \
  "$(get hamming_equals_l1_on_bits)"

check_eq "Jaccard prefers Shortbread" "Shortbread" \
  "$(get jaccard_recipe_winner)"
check_eq "cosine prefers Sachertorte on the SAME two sets" "Sachertorte" \
  "$(get cosine_recipe_winner)"
check_eq "so the two rank set data in opposite orders" "True" \
  "$(get recipe_winners_differ)"
check_eq "Jaccard: 4/11 against 2/5" "0.363636 0.4" "$(get jaccard_values)"
check_eq "cosine: 4/sqrt(44) against 2/sqrt(12)" "0.603023 0.57735" \
  "$(get cosine_values)"

check_eq "the covariance of the readings is exactly [[7.5, 7], [7, 7.5]]" \
  "[[7.5, 7.0], [7.0, 7.5]]" "$(get covariance)"
check_eq "its determinant is exactly 7.25" "7.25" "$(get covariance_det)"
check_eq "the pure-Python inverse matches numpy.linalg.inv" "True" \
  "$(get inverse_matches_numpy)"
check_eq "both probes are the same Euclidean distance from the mean" "True" \
  "$(get probes_equidistant_euclidean)"
check_eq "that distance is sqrt(18) = 4.242641" "4.242641" \
  "$(get euclidean_probe_distance)"
check_eq "Mahalanobis says 1.114172 ALONG the grain" "1.114172" \
  "$(get mahalanobis_along)"
check_eq "and 6.0 ACROSS it" "6.0" "$(get mahalanobis_across)"
check_eq "Gauss-Jordan gives exactly 6.0" "6.0" \
  "$(get mahalanobis_across_repr)"
check_eq "numpy.linalg.inv gives 5.999999999999999 for the same quantity" \
  "5.999999999999999" "$(get mahalanobis_across_numpy_repr)"
check_eq "the two routes agree within the stated tolerance" "True" \
  "$(get mahalanobis_routes_agree_within_tol)"
check_eq "substituting the identity gives back Euclidean exactly" "True" \
  "$(get identity_gives_euclidean)"
check_eq "the covariance eigenvalues are 0.5 and 14.5" "[0.5, 14.5]" \
  "$(get eigenvalues)"

check_eq "raw Euclidean ranks the bearings R, U, P, S, T, V" \
  "['R', 'U', 'P', 'S', 'T', 'V']" "$(get raw_bearing_order)"
check_eq "standardised, it ranks them P, U, R, S, T, V" \
  "['P', 'U', 'R', 'S', 'T', 'V']" "$(get standardised_bearing_order)"
check_eq "so standardising CHANGES the winner" "True" \
  "$(get bearing_winner_changed)"
check_eq "and before scaling the bore column contributes at most 0.0036%" \
  "3.600e-05" "$(get bore_share_max)"
check_eq "changing the bore unit ALONE also changes the winner" "P" \
  "$(get unit_change_winner)"
check_eq "Mahalanobis on the raw numbers gives a third answer" \
  "['U', 'P', 'S', 'T', 'R', 'V']" "$(get mahalanobis_bearing_order)"
check_eq "cosine is NOT invariant to a change of column units" "True" \
  "$(get cosine_not_unit_invariant)"
check_eq "cosine IS invariant to scaling a whole vector" "True" \
  "$(get cosine_vector_scale_invariant)"
check_eq "in 2000 seeded random catalogues the winner changed 1090 times" \
  "1090" "$(get seeded_sweep_flips)"
check_eq "which is between a third and three quarters" "True" \
  "$(get seeded_sweep_in_range)"

check_eq "comparing different lengths raises rather than truncating" "True" \
  "$(get length_mismatch_raises)"
check_eq "cosine of the zero vector raises rather than returning 0" "True" \
  "$(get zero_vector_raises)"
check_eq "a singular covariance refuses to invert" "True" \
  "$(get singular_matrix_raises)"
check_eq "ranking ties break by name, so runs are deterministic" \
  "['alpha', 'mike', 'zulu']" "$(get ties_break_by_name)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for the naive belief that cosine distance satisfies the triangle inequality,
# and asserts that the re-run reports the failure and exits non-zero. If this
# section passes, section 5 is not decorative.
if [ -z "${D107_SELF_TEST:-}" ]; then
  self_out="$(D107_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: so cosine distance VIOLATES the triangle inequality"*)
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

# Every dataset in this lab is written out in catalogue.py. If a data file
# appears in the lab's own tree, either something was committed by mistake or a
# script wrote one and failed to clean up. NumPy ships plenty of its own data
# inside site-packages, so .venv is pruned here too.
data_files="$(find "${lab_dir}" -name '.venv' -prune -o -type f \
  \( -name '*.csv' -o -name '*.json' -o -name '*.npy' -o -name '*.npz' \
     -o -name '*.parquet' -o -name '*.db' -o -name '*.sqlite' \) -print 2>/dev/null \
  | wc -l | tr -d ' ')"
check_eq "no data file in the lab's own tree: every dataset is in the source" \
  "0" "${data_files}"

if grep -rqE 'urlopen|requests\.|socket\.|http://|https://' \
     "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null; then
  check "no lab source opens a network connection" "no"
else
  check "no lab source opens a network connection" "yes"
fi

# measures.py must not import NumPy. The whole evidential value of agreeing
# with numpy.linalg.norm depends on it, so it is checked rather than trusted.
if grep -qE '^\s*(import|from)\s+numpy' "${lab_dir}/examples/measures.py" \
     "${lab_dir}/starter/measures.py" 2>/dev/null; then
  check "measures.py computes without NumPy, so agreeing with it means something" "no"
else
  check "measures.py computes without NumPy, so agreeing with it means something" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
