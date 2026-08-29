#!/usr/bin/env bash
# Tests for the Day 099 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This harness proves the claims the lesson makes, and proves them by running
# the code rather than by reading it:
#
#   * every hand-computed magnitude and distance in the lesson comes out of
#     the code with the value a reader gets on paper;
#   * the pure-Python implementation and NumPy agree operation by operation on
#     the same inputs, to a stated tolerance and never with ==;
#   * normalising really does produce a magnitude that is sometimes not
#     exactly 1.0 on this machine, which is the bug the lab exists to teach;
#   * L1 and L2 really do rank the same two candidates in opposite orders;
#   * the embedding's nearest-neighbour answers are the ones the lesson quotes;
#   * the starter suite is not vacuous: it goes fully green against the
#     reference implementation, and RED when one rule is broken.
#
# Deterministic, non-interactive, offline. Exits 0 only if every check passes.
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

contains() {
  # contains <label> <haystack> <needle>
  case "$2" in
    *"$3"*) check "$1" "yes" ;;
    *) check "$1" "no" ;;
  esac
}

# Resolve the tools: an explicit override, then this lab's own virtual
# environment, then whatever is on PATH. Fails loudly with instructions rather
# than skipping silently — a suite that quietly does nothing is worse than one
# that stops.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

install_hint() {
  echo "  Install this lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing environment:" >&2
  echo "    PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  install_hint
  exit 1
}

# The Python that owns that pytest is the one with numpy installed, unless an
# explicit PYTHON says otherwise.
if [ -n "${PYTHON:-}" ] && [ -x "${PYTHON}" ]; then
  python_bin="${PYTHON}"
else
  python_bin="$(dirname "${pytest_bin}")/python3"
  [ -x "${python_bin}" ] || python_bin="$(command -v python3 || true)"
fi
if [ -z "${python_bin}" ] || [ ! -x "${python_bin}" ]; then
  echo "FAIL: python3 not found." >&2
  install_hint
  exit 1
fi

if ! "${python_bin}" -c "import numpy" >/dev/null 2>&1; then
  echo "FAIL: numpy is not importable from ${python_bin}." >&2
  install_hint
  exit 1
fi

echo "Day 099 — Vectors You Can Hold"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

echo "     python  $("${python_bin}" -c 'import sys; print(sys.version.split()[0])')"
versions="$("${python_bin}" - <<'PY'
from importlib.metadata import version
for name in ("numpy", "pytest"):
    try:
        print(f"{name}=={version(name)}")
    except Exception:
        print(f"{name}==<not installed>")
PY
)"
printf '%s\n' "${versions}" | sed 's/^/     /'

for pin in "numpy==2.5.2" "pytest==9.1.1"; do
  contains "installed ${pin} matches requirements/requirements.txt" "${versions}" "${pin}"
done

# The lesson describes PyTorch, JAX and pandas from their documentation and
# reproduces no output from any of them. These checks keep that claim honest by
# confirming they really are absent here.
for absent in torch jax pandas; do
  if "${python_bin}" -c "import ${absent}" >/dev/null 2>&1; then
    check "${absent} is absent, as the lesson states" "no"
  else
    check "${absent} is absent, as the lesson states" "yes"
  fi
done

# --------------------------------------------------------------------------
echo
echo "2. The reference suite passes"
# --------------------------------------------------------------------------

tests_out="$(cd "${lab_dir}" && "${pytest_bin}" tests -q -p no:cacheprovider 2>&1)"
tests_exit=$?
if [ "${tests_exit}" -eq 0 ]; then
  check "pytest tests exits 0" "yes"
else
  check "pytest tests exits 0 (got ${tests_exit})" "no"
  printf '%s\n' "${tests_out}" | tail -40
fi
contains "pytest tests reports 79 passed" "${tests_out}" "79 passed"

collected="$(cd "${lab_dir}" && "${pytest_bin}" tests --collect-only -q -p no:cacheprovider 2>&1)"
for test_id in \
  "test_l2_norm_matches_the_hand_computed_answer" \
  "test_distance_is_the_norm_of_the_difference_by_construction" \
  "test_comparing_a_normalised_norm_with_exact_equality_really_does_fail" \
  "test_numpy_agrees_on_every_pairwise_distance" \
  "test_the_two_cooking_articles_are_the_closest_pair_in_the_catalogue" \
  "test_l1_and_l2_disagree_about_which_candidate_is_nearest" \
  "test_normalising_changes_the_nearest_article_for_a_short_query" \
  "test_the_triangle_inequality_holds"
do
  contains "collection finds ${test_id}" "${collected}" "${test_id}"
done

# The rule the whole lab is built on: no float is compared with == or !=
# inside an assertion. Every numeric assertion goes through math.isclose or
# numpy.allclose. This grep is the enforcement, and it is deliberate.
bad_float_asserts="$(grep -nE '^\s*assert .*[0-9]\.[0-9].*[!=]=' \
  "${lab_dir}/tests/test_vectors.py" "${lab_dir}/starter/test_starter.py" 2>/dev/null \
  | grep -v 'm != 1.0' | grep -v 'n != 1.0' || true)"
if [ -n "${bad_float_asserts}" ]; then
  check "no test compares a float with == or != (except the two that prove the trap)" "no"
  printf '%s\n' "${bad_float_asserts}" | sed 's/^/     /'
else
  check "no test compares a float with == or != (except the two that prove the trap)" "yes"
fi

# And the tolerance is stated in both suites rather than hidden.
for suite in tests/test_vectors.py starter/test_starter.py; do
  if grep -q "REL_TOL = 1e-9" "${lab_dir}/${suite}" \
     && grep -q "ABS_TOL = 1e-12" "${lab_dir}/${suite}"; then
    check "${suite} states its tolerance explicitly" "yes"
  else
    check "${suite} states its tolerance explicitly" "no"
  fi
done

# --------------------------------------------------------------------------
echo
echo "3. The hand-computable answers really are what the code produces"
# --------------------------------------------------------------------------

byhand_out="$(cd "${lab_dir}/examples" && "${python_bin}" byhand.py 2>&1)"
byhand_exit=$?
if [ "${byhand_exit}" -eq 0 ]; then
  check "examples/byhand.py exits 0" "yes"
else
  check "examples/byhand.py exits 0 (got ${byhand_exit})" "no"
fi

for fragment in \
  '= sqrt(9 + 16)' \
  '= sqrt(25)' \
  '= 5          computed: 5.0   agrees: True' \
  '= sqrt(4 + 9 + 36)' \
  '= 7          computed: 7.0   agrees: True' \
  '= sqrt(1 + 4 + 4)' \
  '= 3          computed: 3.0   agrees: True' \
  '= |[-3, -4]|' \
  '[3, 4]       L1 = 7.0000 L2 = 5.0000' \
  '[2, 2, 2]    L1 = 6.0000 L2 = 3.4641' \
  'all exact cases agree: True'
do
  contains "byhand shows: ${fragment}" "${byhand_out}" "${fragment}"
done

# --------------------------------------------------------------------------
echo
echo "4. Pure Python and NumPy agree, operation by operation"
# --------------------------------------------------------------------------

agree_out="$(cd "${lab_dir}/examples" && "${python_bin}" agreement.py 2>&1)"
agree_exit=$?
if [ "${agree_exit}" -eq 0 ]; then
  check "examples/agreement.py exits 0" "yes"
else
  check "examples/agreement.py exits 0 (got ${agree_exit})" "no"
fi

for fragment in \
  'every operation agrees: True' \
  'l2_norm(u)            13.0                              13.0                              True' \
  'dot(u, v)             55.0                              55.0                              True' \
  'matrix shape        = (3, 4)' \
  'norms of all rows   = [9.0554 8.2462 9.2736]' \
  'distances (NumPy)   = [8.0623 7.2801 9.3274]' \
  'ours  : ValueError: dimension mismatch: 2 and 3'
do
  contains "agreement shows: ${fragment}" "${agree_out}" "${fragment}"
done

# Count the agreement lines rather than trusting the summary line alone.
agree_true="$(printf '%s\n' "${agree_out}" | grep -c 'True$')"
if [ "${agree_true}" -ge 14 ]; then
  check "at least 14 individual agreement checks came back True (${agree_true})" "yes"
else
  check "at least 14 individual agreement checks came back True (${agree_true})" "no"
fi
if printf '%s\n' "${agree_out}" | grep -q 'False$'; then
  check "no agreement check came back False" "no"
else
  check "no agreement check came back False" "yes"
fi

# --------------------------------------------------------------------------
echo
echo "5. Normalisation, and the == trap it hides"
# --------------------------------------------------------------------------

norm_out="$(cd "${lab_dir}/examples" && "${python_bin}" normalise.py 2>&1)"
norm_exit=$?
if [ "${norm_exit}" -eq 0 ]; then
  check "examples/normalise.py exits 0" "yes"
else
  check "examples/normalise.py exits 0 (got ${norm_exit})" "no"
fi

for fragment in \
  'isclose 1.0 : 7 of 7' \
  '0.9999999999999999' \
  'cannot normalise the zero vector' \
  'recovers v: True'
do
  contains "normalise shows: ${fragment}" "${norm_out}" "${fragment}"
done

# The load-bearing claim: at least one vector normalises to something that is
# NOT exactly 1.0. If that ever stops being true on some machine, this check
# fails loudly rather than the lesson quietly telling a lie.
exact_line="$(printf '%s\n' "${norm_out}" | grep 'exactly 1.0 :' || true)"
exact_count="$(printf '%s' "${exact_line}" | awk '{print $4}')"
total_count="$(printf '%s' "${exact_line}" | awk '{print $6}')"
if [ -n "${exact_count}" ] && [ "${exact_count}" -lt "${total_count}" ]; then
  check "at least one normalised vector is NOT exactly 1.0 (${exact_count} of ${total_count} were)" "yes"
else
  check "at least one normalised vector is NOT exactly 1.0 — the == trap did not reproduce here" "no"
fi

# --------------------------------------------------------------------------
echo
echo "6. L1 and L2 rank the same two candidates in opposite orders"
# --------------------------------------------------------------------------

norms_out="$(cd "${lab_dir}/examples" && "${python_bin}" norms.py 2>&1)"
norms_exit=$?
if [ "${norms_exit}" -eq 0 ]; then
  check "examples/norms.py exits 0" "yes"
else
  check "examples/norms.py exits 0 (got ${norms_exit})" "no"
fi

for fragment in \
  'L2 = sqrt(16 + 0 + 0) = 4.0000' \
  'L2 = sqrt(4 + 4 + 4) = 3.4641' \
  'nearest under L2: spread' \
  'nearest under L1: spike' \
  'Both cases produced a disagreement: True'
do
  contains "norms shows: ${fragment}" "${norms_out}" "${fragment}"
done

disagreements="$(printf '%s\n' "${norms_out}" | grep -c 'the two norms disagree: True')"
if [ "${disagreements}" -eq 2 ]; then
  check "both cases reported a disagreement (${disagreements})" "yes"
else
  check "both cases reported a disagreement (got ${disagreements})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "7. The embedding answers the question it was built for"
# --------------------------------------------------------------------------

embed_out="$(cd "${lab_dir}/examples" && "${python_bin}" embeddings.py 2>&1)"
embed_exit=$?
if [ "${embed_exit}" -eq 0 ]; then
  check "examples/embeddings.py exits 0" "yes"
else
  check "examples/embeddings.py exits 0 (got ${embed_exit})" "no"
fi

for fragment in \
  '[9, 0, 1, 0] - [8, 0, 2, 0] = [1, 0, -1, 0]' \
  'squares: 1 + 0 + 1 + 0 = 2' \
  'sqrt(2) = 1.4142' \
  'squares: 64 + 0 + 64 + 0 = 128' \
  'sqrt(128) = 11.3137' \
  'roast-chicken        -> slow-cooker-stew     at 1.4142' \
  'marathon-plan        -> race-day-nutrition   at 5.7446' \
  'household-budget     -> race-day-nutrition   at 9.0000' \
  'storm-bulletin       -> marathon-plan        at 10.6771' \
  'distance after normalising both = 0.0000' \
  'nearest on raw counts : slow-cooker-stew at 7.2801' \
  'nearest normalised    : roast-chicken at 0.1106' \
  'they disagree         : True' \
  'raw rank of roast-chicken        : 3' \
  'normalised rank of roast-chicken : 1' \
  'Closest pair in the whole catalogue: roast-chicken and slow-cooker-stew at 1.4142'
do
  contains "embeddings shows: ${fragment}" "${embed_out}" "${fragment}"
done

# --------------------------------------------------------------------------
echo
echo "8. The starter is runnable before you start, and honest about it"
# --------------------------------------------------------------------------

starter_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
starter_exit=$?
if [ "${starter_exit}" -eq 0 ]; then
  check "pytest starter exits 0 with the exercises unfinished" "yes"
else
  check "pytest starter exits 0 with the exercises unfinished (got ${starter_exit})" "no"
fi
contains "the starter has 1 worked test and 11 skipped exercises" \
  "${starter_out}" "1 passed, 11 skipped"

progress_out="$(cd "${lab_dir}" && "${python_bin}" starter/vectors.py 2>&1)"
progress_exit=$?
if [ "${progress_exit}" -eq 0 ]; then
  check "starter/vectors.py runs before any exercise is done" "yes"
else
  check "starter/vectors.py runs before any exercise is done (got ${progress_exit})" "no"
fi
contains "starter reports its unfinished state honestly" \
  "${progress_out}" "0 of 9 exercises return something."

# The starter must not import numpy — the whole point is writing the loop first.
if grep -qE '^\s*(import|from)\s+numpy' "${lab_dir}/starter/vectors.py"; then
  check "starter/vectors.py does not import numpy" "no"
else
  check "starter/vectors.py does not import numpy" "yes"
fi
if grep -qE '^\s*(import|from)\s+numpy' "${lab_dir}/examples/vectors.py"; then
  check "examples/vectors.py does not import numpy either" "no"
else
  check "examples/vectors.py does not import numpy either" "yes"
fi

# --------------------------------------------------------------------------
echo
echo "9. The starter suite is not vacuous — green when solved, red when broken"
# --------------------------------------------------------------------------

# Drop the reference implementation in as the student's answer, un-skip
# everything, and demand a fully green run. A suite that cannot tell finished
# work from unfinished is worth nothing.
work="$(mktemp -d "${TMPDIR:-/tmp}/day099-solved.XXXXXX")"
cp "${lab_dir}/examples/vectors.py" "${work}/vectors.py"
cp "${lab_dir}/starter/pytest.ini" "${work}/pytest.ini"
grep -v '^@pytest\.mark\.skip' "${lab_dir}/starter/test_starter.py" > "${work}/test_starter.py"

solved_out="$(cd "${work}" && "${pytest_bin}" . -q -p no:cacheprovider 2>&1)"
solved_exit=$?
if [ "${solved_exit}" -eq 0 ]; then
  check "the starter suite goes fully green against the finished implementation" "yes"
else
  check "the starter suite goes fully green against the finished implementation (exit ${solved_exit})" "no"
  printf '%s\n' "${solved_out}" | tail -20
fi
contains "all 12 starter tests pass once the exercises are done" "${solved_out}" "12 passed"

# Now break exactly one thing — make l2_norm forget the square root, which is
# the single most common way to get this wrong — and demand the suite FAILS.
"${python_bin}" - "${work}/vectors.py" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
broken = text.replace(
    "    return math.sqrt(sum(a * a for a in v))",
    "    return sum(a * a for a in v)",
)
assert broken != text, "the l2_norm body was not found — this check would be vacuous"
path.write_text(broken, encoding="utf-8")
PY
broken_out="$(cd "${work}" && "${pytest_bin}" . -q -p no:cacheprovider 2>&1)"
broken_exit=$?
if [ "${broken_exit}" -ne 0 ]; then
  check "dropping the square root from l2_norm makes the suite FAIL (exit ${broken_exit})" "yes"
else
  check "dropping the square root from l2_norm makes the suite FAIL — it did not, so the norm checks are vacuous" "no"
fi
contains "the failing run names the magnitude test by id" \
  "${broken_out}" "test_exercise_5_l2_norm"
rm -rf "${work}"

# And the same proof for the reference suite: break the distance definition and
# demand tests/ goes red.
work2="$(mktemp -d "${TMPDIR:-/tmp}/day099-broken.XXXXXX")"
mkdir -p "${work2}/examples" "${work2}/tests"
cp "${lab_dir}/examples/vectors.py" "${lab_dir}/examples/embeddings.py" "${work2}/examples/"
cp "${lab_dir}/tests/test_vectors.py" "${work2}/tests/"
"${python_bin}" - "${work2}/examples/vectors.py" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
broken = text.replace(
    "    return l2_norm(subtract(u, v))\n\n\ndef l1_distance",
    "    return l2_norm(add(u, v))\n\n\ndef l1_distance",
)
assert broken != text, "the distance body was not found — this check would be vacuous"
path.write_text(broken, encoding="utf-8")
PY
red_out="$(cd "${work2}" && "${pytest_bin}" tests -q -p no:cacheprovider 2>&1)"
red_exit=$?
if [ "${red_exit}" -ne 0 ]; then
  check "swapping subtract for add in distance makes tests/ FAIL (exit ${red_exit})" "yes"
else
  check "swapping subtract for add in distance makes tests/ FAIL — it did not" "no"
fi
contains "the failing run names a distance test by id" \
  "${red_out}" "test_distance_matches_the_hand_computed_answer"
rm -rf "${work2}"

# --------------------------------------------------------------------------
echo
echo "10. The lab left nothing behind and reaches no network"
# --------------------------------------------------------------------------

# `.venv` is deliberately NOT in this list. The README tells the reader to
# create it, and the tool resolution at the top of this file looks inside
# it — so treating it as litter would fail the lab for following its own
# setup instructions.
for stray in "out" ".pytest_cache"; do
  if [ -e "${lab_dir}/${stray}" ]; then
    check "no ${stray} left inside the lab after a full run" "no"
  else
    check "no ${stray} left inside the lab after a full run" "yes"
  fi
done

# `.venv` is pruned from the searches below. A virtual environment ships the
# installed packages' own precompiled bytecode -- hundreds of __pycache__
# directories that came with NumPy or pytest and have nothing to do with
# whether THIS lab tidied up after itself. Without the prune, following the
# README's own setup instructions makes this check fail, which reports a
# problem the reader cannot fix and did not cause.
if find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -print -quit 2>/dev/null | grep -q .; then
  check "no __pycache__ left inside the lab after a full run" "no"
else
  check "no __pycache__ left inside the lab after a full run" "yes"
fi

# Nothing here reaches the network at run time. The only network step is the
# one-off pip install described in the README. Restricted to .py files on
# purpose: this script quotes the pattern it searches for, so scanning itself
# would always match.
if find "${lab_dir}/examples" "${lab_dir}/starter" "${lab_dir}/tests" -name '*.py' -print0 2>/dev/null \
     | xargs -0 grep -qE 'requests\.|urlopen|httpx\.|socket\.(create_connection|socket)\(' 2>/dev/null; then
  check "no lab source opens a network connection at run time" "no"
else
  check "no lab source opens a network connection at run time" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
