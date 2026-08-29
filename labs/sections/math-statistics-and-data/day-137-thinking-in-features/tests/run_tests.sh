#!/usr/bin/env bash
# Tests for the Day 137 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the day's claims by running the real experiments and
# reading the numbers they produce -- never by reading source:
#
#   * a feature derived from the outcome scores 1.00, and removing it
#     drops the same model to an honest 0.64;
#   * a scaler fitted on all the data before the split buys essentially
#     nothing (measured over 200 splits), while a group-mean imputer
#     fitted the same way buys eight points;
#   * a target encoding computed before the split beats an out-of-fold
#     one, and restricting it to the training rows removes the gap;
#   * a random split scores 0.88 on time-ordered data where a
#     time-ordered split scores 0.07 -- below the majority baseline;
#   * hour 23 and hour 0 sit 23 apart as integers and 2*sin(pi/24) apart
#     on the circle, exactly, as does every other adjacent pair;
#   * an ordinal code forces monotone predictions where one-hot does not;
#   * a ratio separates classes that neither of its components separates;
#   * a vocabulary chosen on all the documents beats one chosen on the
#     training documents, and unseen test words are dropped not crashed on;
#   * the leakage audit catches both planted leaks and flags none of the
#     four honest columns;
#   * the reference suite (`examples/`) passes in full;
#   * the exercise suite (`starter/`) is all-skip on an untouched
#     checkout, and the harness proves the suite can genuinely FAIL by
#     solving every exercise in a scratch copy, breaking one assertion on
#     purpose, confirming a non-zero exit, then restoring it;
#   * nothing is left behind anywhere.
#
# Everything after the one-time install runs offline. Nothing binds a
# port, nothing needs a key. Deterministic, non-interactive, exits 0 only
# if every check passes.
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

if ! "${python_bin}" -c "import pandas, numpy" >/dev/null 2>&1; then
  echo "FAIL: pandas or numpy is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 137 — Features That Do Not Cheat"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
from importlib.metadata import version

print(f"python     {platform.python_version()}")
for name in ("pandas", "numpy", "pytest"):
    try:
        print(f"{name:<10} {version(name)}")
    except Exception as exc:  # pragma: no cover
        print(f"{name:<10} NOT INSTALLED ({exc})")
try:
    import sklearn  # noqa: F401

    print("sklearn    INSTALLED — this lab was written without it")
except ImportError:
    print("sklearn    not installed (expected; every model here is written out)")
PY
)"
echo "${versions}"
echo

check "scikit-learn is absent, as the lab's text states" \
  "$( echo "${versions}" | grep -q 'sklearn    not installed' && echo yes || echo no )"

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
echo "2. The nine measurements, run for real"
# --------------------------------------------------------------------------

measured="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY'
"""Run every experiment and print one machine-readable line per number."""
import numpy as np

import data
import experiments as E
import features as F

out = {}


def record(key, value):
    if isinstance(value, bool):
        out[key] = "yes" if value else "no"
    elif isinstance(value, float):
        out[key] = f"{value:.4f}"
    else:
        out[key] = str(value)


leak = E.target_leakage()
record("leak_with", leak["with_leak"])
record("leak_without", leak["without_leak"])
record("leak_gap_points", leak["gap_points"])

scaler = E.scaling_contamination()
record("scaler_contaminated", scaler["contaminated"])
record("scaler_correct", scaler["correct"])
record("scaler_optimism_points", scaler["optimism_points"])
record("scaler_trials", int(scaler["trials"]))

imputer = E.imputer_contamination()
record("imputer_contaminated", imputer["contaminated"])
record("imputer_correct", imputer["correct"])
record("imputer_optimism_points", imputer["optimism_points"])

encoding = E.target_encoding()
record("te_naive_all", encoding["naive_all_data"])
record("te_naive_train", encoding["naive_train_only"])
record("te_out_of_fold", encoding["out_of_fold"])
record("te_gap_points", encoding["gap_all_vs_oof_points"])

temporal = E.temporal_leakage()
record("time_random", temporal["random_split"])
record("time_ordered", temporal["time_ordered_split"])
record("time_gap_points", temporal["gap_points"])
record("time_majority_baseline", temporal["majority_rate_in_ordered_test"])
record("time_unseen_batches", int(temporal["test_batches_unseen_by_ordered_train"]))

cyc = E.cyclical_distances()
record("cyc_raw_23_0", cyc["raw_23_to_0"])
record("cyc_circle_23_0", cyc["cyclical_23_to_0"])
record("cyc_circle_3_4", cyc["cyclical_3_to_4"])
record("cyc_spread_below_1e12", cyc["cyclical_adjacent_spread"] < 1e-12)
record("cyc_expected", cyc["expected_adjacent"])

colours = E.ordinal_versus_one_hot()
record("ordinal_monotone", bool(colours["ordinal_is_monotone"]))
record("one_hot_monotone", bool(colours["one_hot_is_monotone"]))
record("ordinal_max_error", colours["ordinal_max_error"])
record("one_hot_max_error", colours["one_hot_max_error"])
record("ordinal_accuracy", colours["ordinal_accuracy"])
record("one_hot_accuracy", colours["one_hot_accuracy"])

inter = E.interaction()
record("income_only", inter["income_only"])
record("spend_only", inter["spend_only"])
record("ratio_only", inter["ratio_only"])
record("income_and_spend", inter["income_and_spend"])

vocab = E.vocabulary_contamination()
record("vocab_all_data", vocab["fitted_on_all_data"])
record("vocab_train_only", vocab["fitted_on_train_only"])
record("vocab_gap_points", vocab["gap_points"])
record("vocab_unseen_words", int(vocab["unseen_test_words"]))
record("vocab_columns", int(vocab["test_matrix_columns"]))

audit = E.audit_result()
record("audit_flagged", ",".join(audit["flagged"]))
record("audit_rules", ",".join(audit["rules"][c] for c in audit["flagged"]))
honest = ["visits", "minutes_on_site", "discount_pct", "channel"]
record("audit_honest_clean", all(c not in audit["flagged"] for c in honest))

frame = E.audit_table()
y = frame["converted"].to_numpy(dtype=float)
leak_column = frame["days_to_first_invoice"].to_numpy(dtype=float)
record("audit_leak_correlation", abs(float(np.corrcoef(leak_column, y)[0, 1])))
strict = F.leakage_audit(frame, "converted", corr_threshold=1.01)
record("audit_strict_flagged", ",".join(f.column for f in strict))

binning = E.binning_decision()
record("bin_width_top_rows", binning["equal_width_top_bin_rows"])
record("bin_count_top_rows", binning["equal_count_top_bin_rows"])
record("bin_width_top_rate", binning["equal_width_top_bin_rate"])
record("bin_count_top_rate", binning["equal_count_top_bin_rate"])

# Two determinism checks: the same generator twice, and the same
# experiment twice, must agree to the last bit.
record("data_is_deterministic", data.signups().equals(data.signups()))
record("experiment_is_deterministic", E.target_leakage() == leak)

for key, value in out.items():
    print(f"{key}={value}")
PY
)"
measured_status=$?
echo "${measured}"
echo

value_of() { echo "${measured}" | grep "^$1=" | cut -d= -f2-; }
at_least() { "${python_bin}" -c "import sys; sys.exit(0 if float('$1') >= float('$2') else 1)" && echo yes || echo no; }
below() { "${python_bin}" -c "import sys; sys.exit(0 if float('$1') < float('$2') else 1)" && echo yes || echo no; }

check "every experiment ran without error" "$( [ ${measured_status} -eq 0 ] && echo yes || echo no )"

echo
echo "  -- 1. target leakage"
check "the leaking feature scores 1.0000" "$( [ "$(value_of leak_with)" = "1.0000" ] && echo yes || echo no )"
check "removing it drops the score into the honest band 0.55-0.80" \
  "$( [ "$(at_least "$(value_of leak_without)" 0.55)" = yes ] && [ "$(below "$(value_of leak_without)" 0.80)" = yes ] && echo yes || echo no )"
check "the gap is at least 25 points" "$(at_least "$(value_of leak_gap_points)" 25)"

echo "  -- 2. a statistic fitted before the split"
check "a contaminated scaler is worth less than 1 point either way" \
  "$( "${python_bin}" -c "import sys; sys.exit(0 if abs(float('$(value_of scaler_optimism_points)')) < 1.0 else 1)" && echo yes || echo no )"
check "the scaler comparison averaged 200 splits" "$( [ "$(value_of scaler_trials)" = "200" ] && echo yes || echo no )"
check "a contaminated group-mean imputer is worth at least 5 points" "$(at_least "$(value_of imputer_optimism_points)" 5)"
check "the contaminated imputer scores above the correct one" \
  "$(at_least "$(value_of imputer_contaminated)" "$(value_of imputer_correct)")"

echo "  -- 3. target encoding"
check "the naive all-data encoding beats out-of-fold by at least 4 points" "$(at_least "$(value_of te_gap_points)" 4)"
check "out-of-fold is at least as good as naive-on-training-rows" \
  "$(at_least "$(value_of te_out_of_fold)" "$(value_of te_naive_train)")"

echo "  -- 4. temporal leakage"
check "the random split scores at least 0.80" "$(at_least "$(value_of time_random)" 0.80)"
check "the time-ordered split scores at most 0.20" "$(below "$(value_of time_ordered)" 0.20)"
check "the time-ordered score is below the majority-class baseline" \
  "$(below "$(value_of time_ordered)" "$(value_of time_majority_baseline)")"
check "exactly one test batch was unseen by the time-ordered training rows" \
  "$( [ "$(value_of time_unseen_batches)" = "1" ] && echo yes || echo no )"

echo "  -- 5. cyclical encoding"
check "raw hours put 23 and 0 exactly 23 apart" "$( [ "$(value_of cyc_raw_23_0)" = "23.0000" ] && echo yes || echo no )"
check "on the circle 23-to-0 equals 3-to-4" \
  "$( [ "$(value_of cyc_circle_23_0)" = "$(value_of cyc_circle_3_4)" ] && echo yes || echo no )"
check "and both equal 2*sin(pi/24)" \
  "$( [ "$(value_of cyc_circle_23_0)" = "$(value_of cyc_expected)" ] && echo yes || echo no )"
check "all 24 adjacent pairs agree to within 1e-12" "$( [ "$(value_of cyc_spread_below_1e12)" = yes ] && echo yes || echo no )"

echo "  -- 6. ordinal versus one-hot"
check "the ordinal model's predictions are monotone in the code" "$( [ "$(value_of ordinal_monotone)" = yes ] && echo yes || echo no )"
check "the one-hot model's predictions are not" "$( [ "$(value_of one_hot_monotone)" = no ] && echo yes || echo no )"
check "one-hot reproduces the observed rates to within 1e-5" "$(below "$(value_of one_hot_max_error)" 0.00001)"
check "the ordinal model is out by more than 0.30 somewhere" "$(at_least "$(value_of ordinal_max_error)" 0.30)"

echo "  -- 7. an interaction"
check "the ratio separates the classes perfectly" "$( [ "$(value_of ratio_only)" = "1.0000" ] && echo yes || echo no )"
check "income alone does not (under 0.60)" "$(below "$(value_of income_only)" 0.60)"
check "spend alone does not (under 0.75)" "$(below "$(value_of spend_only)" 0.75)"

echo "  -- 8. vocabulary"
check "a vocabulary chosen on all documents beats one chosen on training documents" \
  "$(at_least "$(value_of vocab_gap_points)" 1.5)"
check "test documents contain words the training vocabulary never saw" \
  "$(at_least "$(value_of vocab_unseen_words)" 1)"
check "the test matrix keeps the training vocabulary's width" \
  "$( [ "$(value_of vocab_columns)" = "30" ] && echo yes || echo no )"

echo "  -- 9. the audit"
check "both planted leaks are flagged, and only those" \
  "$( [ "$(value_of audit_flagged)" = "days_to_first_invoice,email_template" ] && echo yes || echo no )"
check "each is flagged by the expected rule" \
  "$( [ "$(value_of audit_rules)" = "separable,pure_category" ] && echo yes || echo no )"
check "no honest column is flagged" "$( [ "$(value_of audit_honest_clean)" = yes ] && echo yes || echo no )"
check "the numeric leak's correlation is UNDER the 0.90 threshold" "$(below "$(value_of audit_leak_correlation)" 0.90)"
check "disabling the correlation rule entirely still catches both leaks" \
  "$( [ "$(value_of audit_strict_flagged)" = "days_to_first_invoice,email_template" ] && echo yes || echo no )"

echo "  -- extra: a bin boundary is a decision"
check "equal-width and equal-count binning disagree about the top bin's size" \
  "$( [ "$(value_of bin_width_top_rows)" != "$(value_of bin_count_top_rows)" ] && echo yes || echo no )"
check "and about the rate you would quote for it" \
  "$( [ "$(value_of bin_width_top_rate)" != "$(value_of bin_count_top_rate)" ] && echo yes || echo no )"

echo "  -- determinism"
check "the generators return identical frames on a second call" "$( [ "$(value_of data_is_deterministic)" = yes ] && echo yes || echo no )"
check "the experiments return identical numbers on a second call" "$( [ "$(value_of experiment_is_deterministic)" = yes ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "3. Reference suite -- examples/ must pass in full"
# --------------------------------------------------------------------------

examples_output="$(cd "${lab_dir}" && "${pytest_bin}" examples -q 2>&1)"
examples_status=$?
echo "${examples_output}" | tail -3
check "examples/ exits 0" "$( [ ${examples_status} -eq 0 ] && echo yes || echo no )"
check "examples/ reports 9 passed, 0 failed" \
  "$( echo "${examples_output}" | grep -qE '^9 passed' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "4. Exercise suite -- starter/ is all-skip on an untouched checkout"
# --------------------------------------------------------------------------

starter_output="$(cd "${lab_dir}" && "${pytest_bin}" starter -q 2>&1)"
starter_status=$?
echo "${starter_output}" | tail -3
check "starter/ (untouched) exits 0" "$( [ ${starter_status} -eq 0 ] && echo yes || echo no )"
check "starter/ (untouched) reports 9 skipped, 0 failed" \
  "$( echo "${starter_output}" | grep -qE '^9 skipped' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "5. Never run 'pytest examples starter' in one invocation -- both"
echo "   directories define a module named test_features.py, and pytest"
echo "   collects by dotted module name. Documented, and run as two commands."
# --------------------------------------------------------------------------

combined_output="$(cd "${lab_dir}" && "${pytest_bin}" examples starter -q 2>&1)"
combined_status=$?
check "'pytest examples starter' aborts rather than silently passing" \
  "$( [ ${combined_status} -ne 0 ] && echo yes || echo no )"
check "the collision is reported as an import file mismatch" \
  "$( echo "${combined_output}" | grep -qi 'import file mismatch' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "6. Prove the suite can genuinely FAIL: solve every exercise in a"
echo "   scratch copy, confirm green, break one assertion on purpose,"
echo "   confirm a non-zero exit and a printed failure, then restore."
# --------------------------------------------------------------------------

scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/d137-scratch.XXXXXX")"
cleanup_scratch() { rm -rf "${scratch_dir}"; }
trap cleanup_scratch EXIT

for module in test_features.py experiments.py features.py models.py data.py conftest.py; do
  cp "${lab_dir}/examples/${module}" "${scratch_dir}/${module}"
done

solved_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
solved_status=$?
check "scratch copy of the solved suite exits 0" "$( [ ${solved_status} -eq 0 ] && echo yes || echo no )"
check "scratch copy reports 9 passed" "$( echo "${solved_output}" | grep -qE '^9 passed' && echo yes || echo no )"

# Break exercise 1's leaking-score assertion on purpose.
sed -i.bak 's/assert leakage\["with_leak"\] == 1.0/assert leakage["with_leak"] == 0.5/' \
  "${scratch_dir}/test_features.py"

broken_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
broken_status=$?
check "broken scratch copy exits non-zero" "$( [ ${broken_status} -ne 0 ] && echo yes || echo no )"
check "broken scratch copy prints a failure" \
  "$( echo "${broken_output}" | grep -qiE 'failed|assert' && echo yes || echo no )"

mv "${scratch_dir}/test_features.py.bak" "${scratch_dir}/test_features.py"
restored_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
restored_status=$?
check "restored scratch copy exits 0 again" "$( [ ${restored_status} -eq 0 ] && echo yes || echo no )"
check "restored scratch copy reports 9 passed again" \
  "$( echo "${restored_output}" | grep -qE '^9 passed' && echo yes || echo no )"

cleanup_scratch
trap - EXIT
echo

# --------------------------------------------------------------------------
echo "7. Offline, and nothing left behind"
# --------------------------------------------------------------------------

url_hits="$(grep -rEl 'https?://|ftp://' "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null || true)"
check "no URLs inside examples/ or starter/" "$( [ -z "${url_hits}" ] && echo yes || echo no )"

network_hits="$(grep -rElE '\b(requests|urllib|socket|httpx)\b' "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null || true)"
check "no networking module is imported anywhere in the lab" "$( [ -z "${network_hits}" ] && echo yes || echo no )"

find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

stray="$(find "${lab_dir}" -name '.venv' -prune -o \( -type d -name '__pycache__' -print -o -type d -name '.pytest_cache' -print \) 2>/dev/null || true)"
check "no __pycache__ or .pytest_cache left behind" "$( [ -z "${stray}" ] && echo yes || echo no )"

leftover_tmp="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'd137-*' -print 2>/dev/null || true)"
check "no d137 temporary directory left in the system temp directory" "$( [ -z "${leftover_tmp}" ] && echo yes || echo no )"
echo

echo "-------------------------------------------------------------"
echo "${checks} checks, ${failures} failure(s)"
if [ "${failures}" -gt 0 ]; then
  exit 1
fi
exit 0
