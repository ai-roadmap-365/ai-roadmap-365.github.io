#!/usr/bin/env bash
# Tests for the Day 103 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves seven specific claims the lesson makes, and it proves each
# one by running code and reading real values rather than by reading source:
#
#   * Euclidean distance calls an article's own doubled copy FURTHER away than
#     a different article is, while cosine similarity calls it identical —
#     the day's motivating failure, computed, not asserted;
#   * the from-scratch dot product, cosine similarity and cosine distance
#     agree with NumPy on every pair in the catalogue, to a stated tolerance;
#   * the sign of the dot product tracks the angle: positive under 90 degrees,
#     zero at exactly 90, negative above;
#   * on NORMALISED vectors, ranking by cosine and ranking by Euclidean
#     distance produce the identical order — and on raw vectors they do not;
#   * cosine distance fails the triangle inequality on a concrete triple;
#   * the semantic search returns the expected top hit for two queries, and
#     the query's own magnitude changes nothing;
#   * mean absolute cosine similarity between random vectors falls towards
#     zero as the dimension grows, from a seeded generator.
#
# Everything runs offline. Nothing binds a port, nothing writes outside the
# lab, nothing needs a key. Deterministic, non-interactive, exits 0 only if
# every check passes.
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

echo "Day 103 — Which Question Are You Asking?"
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
check_eq "numpy is version 2 or later (numpy.random.default_rng and the 2.x repr)" "2" "${major}"

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_the_length_confound 02_dot_product_and_sign \
              03_from_scratch_vs_numpy 04_same_ranking_on_the_sphere \
              05_not_a_metric 06_semantic_search 07_curse_of_dimensionality; do
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
echo "3. The reference pytest suite: real values, real rankings"
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
if [ "${ref_passed:-0}" -ge 70 ]; then
  check "the reference suite ran at least 70 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 70 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain a module called `similarity`, and
# pytest imports test files by putting their directory on sys.path — so
# collecting both suites at once would otherwise let the starter tests import
# the REFERENCE solution and report unwritten exercises as passing. Each
# directory's conftest.py prevents that. This check proves it still does:
# across both suites, the skip count must be unchanged.
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

from catalogue import CATALOGUE, LONG_ROAST_CHICKEN, QUERIES, TRIANGLE_A, TRIANGLE_B, TRIANGLE_C
from similarity import (
    angle_degrees,
    cosine_distance,
    cosine_similarity,
    dot,
    euclidean_distance,
    normalise,
    normalise_all,
    rank_by_cosine,
    rank_by_euclidean,
)

short = CATALOGUE["roast-chicken"]
rival = CATALOGUE["race-day-nutrition"]

# The confound.
print("dist_to_doubled", f"{euclidean_distance(short, LONG_ROAST_CHICKEN):.4f}")
print("dist_to_rival", f"{euclidean_distance(short, rival):.4f}")
print("confound", euclidean_distance(short, LONG_ROAST_CHICKEN) > euclidean_distance(short, rival))
print("cos_to_doubled", f"{cosine_similarity(short, LONG_ROAST_CHICKEN):.10f}")

# Agreement with NumPy across every pair.
worst = 0.0
for a in CATALOGUE.values():
    for b in CATALOGUE.values():
        theirs = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        worst = max(worst, abs(cosine_similarity(a, b) - theirs))
print("numpy_agreement", worst < 1e-12)

# The signs.
print("signs", int(dot([3, 0], [6, 0])), int(dot([3, 0], [0, 5])), int(dot([3, 0], [-6, 0])))
print("angles", f"{angle_degrees([3, 0], [1, 1]):.2f}", f"{angle_degrees([3, 0], [-2, 2]):.2f}")

# The ranking equivalence.
units = normalise_all(CATALOGUE)
q = units["roast-chicken"]
by_cos = [k for k, _ in rank_by_cosine(q, units)]
by_euc = [k for k, _ in rank_by_euclidean(q, units)]
print("normalised_orders_match", by_cos == by_euc)

raw = dict(CATALOGUE)
raw["roast-chicken (2x)"] = LONG_ROAST_CHICKEN
raw_cos = [k for k, _ in rank_by_cosine(short, raw)]
raw_euc = [k for k, _ in rank_by_euclidean(short, raw)]
print("raw_orders_match", raw_cos == raw_euc)

# The identity behind it.
u, v = units["roast-chicken"], units["marathon-plan"]
print("sphere_identity", abs(euclidean_distance(u, v) - math.sqrt(2 - 2 * cosine_similarity(u, v))) < 1e-9)

# The triangle inequality.
ab = cosine_distance(TRIANGLE_A, TRIANGLE_B)
bc = cosine_distance(TRIANGLE_B, TRIANGLE_C)
ac = cosine_distance(TRIANGLE_A, TRIANGLE_C)
print("triangle_cosine_fails", ac > ab + bc, f"{ab + bc:.6f}", f"{ac:.6f}")
ea = euclidean_distance(TRIANGLE_A, TRIANGLE_B) + euclidean_distance(TRIANGLE_B, TRIANGLE_C)
print("triangle_euclid_holds", euclidean_distance(TRIANGLE_A, TRIANGLE_C) <= ea + 1e-12)

# The search.
r1 = rank_by_cosine(QUERIES["roast it"], CATALOGUE)
r2 = rank_by_cosine(QUERIES["training for a race and what to eat"], CATALOGUE)
print("search_top1", r1[0][0], f"{r1[0][1]:.6f}")
print("search_top2", r2[0][0], f"{r2[0][1]:.6f}")
print("euclid_top1", rank_by_euclidean(QUERIES["roast it"], CATALOGUE)[0][0])
scaled = [100 * x for x in QUERIES["roast it"]]
print("scale_invariant", [k for k, _ in rank_by_cosine(scaled, CATALOGUE)] == [k for k, _ in r1])

# The zero vector is refused rather than returning NaN.
try:
    cosine_similarity([0, 0, 0, 0], short)
except ValueError:
    print("zero_vector", "ValueError")
else:
    print("zero_vector", "NOTHING_RAISED")

# The clamp: at least one article rounds above 1.0 through the naive formula.
above = 0
for vec in CATALOGUE.values():
    length = math.sqrt(sum(x * x for x in vec))
    if sum(x * y for x, y in zip(vec, vec)) / (length * length) > 1.0:
        above += 1
print("rounds_above_one", above >= 1, all(cosine_similarity(v, v) <= 1.0 for v in CATALOGUE.values()))

# The curse, seeded so it is reproducible.
rng = np.random.default_rng(103)
means = []
for dimension in (2, 32, 512, 8192):
    a = rng.standard_normal((2000, dimension))
    b = rng.standard_normal((2000, dimension))
    num = np.einsum("ij,ij->i", a, b)
    den = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    means.append(float(np.mean(np.abs(num / den))))
print("curse_monotone", all(y < x for x, y in zip(means, means[1:])))
print("curse_values", " ".join(f"{m:.4f}" for m in means))
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "the doubled copy is 9.0554 away, which is the article's own length" \
  "9.0554" "$(get dist_to_doubled)"
check_eq "race-day-nutrition is only 8.0623 away" "8.0623" "$(get dist_to_rival)"
check_eq "so Euclidean puts the doubled copy FURTHER than a different article" \
  "True" "$(get confound)"
check_eq "cosine calls the doubled copy identical" "1.0000000000" "$(get cos_to_doubled)"
check_eq "every from-scratch cosine agrees with NumPy inside 1e-12" \
  "True" "$(get numpy_agreement)"
check_eq "the three sign cases give 18, 0 and -18" "18 0 -18" "$(get signs)"
check_eq "the 45 and 135 degree cases measure 45.00 and 135.00" \
  "45.00 135.00" "$(get angles)"
# Section 6 re-runs this script with D103_SELF_TEST=1, which swaps ONE
# expectation below for a deliberately wrong one. That is how the harness
# proves it can fail rather than merely asserting that it could.
expected_normalised="True"
if [ -n "${D103_SELF_TEST:-}" ]; then
  expected_normalised="False"   # deliberately wrong here
fi
check_eq "on normalised vectors the two rankings are identical" \
  "${expected_normalised}" "$(get normalised_orders_match)"
check_eq "on raw vectors with the doubled copy they are NOT" \
  "False" "$(get raw_orders_match)"
check_eq "the unit-sphere identity sqrt(2 - 2cos) matches the measured distance" \
  "True" "$(get sphere_identity)"
check_eq "cosine distance fails the triangle inequality (0.585786 < 1.000000)" \
  "True 0.585786 1.000000" "$(get triangle_cosine_fails)"
check_eq "Euclidean distance holds it on the same triple" \
  "True" "$(get triangle_euclid_holds)"
check_eq "the cooking note retrieves roast-chicken" \
  "roast-chicken 0.993884" "$(get search_top1)"
check_eq "the training query retrieves race-day-nutrition" \
  "race-day-nutrition 0.903482" "$(get search_top2)"
check_eq "raw Euclidean gets the cooking note wrong" \
  "slow-cooker-stew" "$(get euclid_top1)"
check_eq "scaling the query by 100 changes nothing" "True" "$(get scale_invariant)"
check_eq "the zero vector raises rather than returning NaN" \
  "ValueError" "$(get zero_vector)"
check_eq "the naive formula rounds above 1.0 and the clamp catches it" \
  "True True" "$(get rounds_above_one)"
check_eq "mean absolute cosine falls at every step up in dimension" \
  "True" "$(get curse_monotone)"
check_eq "and the measured values are reproducible from seed 103" \
  "0.6435 0.1440 0.0353 0.0088" "$(get curse_values)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for the WRONG answer, and asserts that the re-run reports the failure and
# exits non-zero. If this section passes, section 5 is not decorative.
if [ -z "${D103_SELF_TEST:-}" ]; then
  self_out="$(D103_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: on normalised vectors the two rankings are identical"*)
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

# `.venv` is pruned from the searches below. A virtual environment ships the
# installed packages' own precompiled bytecode -- hundreds of __pycache__
# directories that came with NumPy or pytest and have nothing to do with
# whether THIS lab tidied up after itself. Without the prune, following the
# README's own setup instructions makes this check fail, which reports a
# problem the reader cannot fix and did not cause.
if find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -print -quit 2>/dev/null | grep -q .; then
  check "no __pycache__ directory anywhere under the lab after a full run" "no"
else
  check "no __pycache__ directory anywhere under the lab after a full run" "yes"
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
