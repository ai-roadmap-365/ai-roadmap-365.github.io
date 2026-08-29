#!/usr/bin/env bash
# Tests for the Day 075 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# These checks are the argument of the lesson, made mechanical:
#
#   * the pytest suite passes on the BUGGY starter code — proving that a
#     green suite is not proof of correctness;
#   * mypy exits non-zero on the same file and names specific error CODES;
#   * every assertion greps for the bracketed code, never the prose, so the
#     suite survives a wording change in a future mypy release;
#   * the fixed reference in examples/ is clean under --strict, and clean
#     again when driven by the real [tool.mypy] table in examples/pyproject.toml;
#   * adding Any to one signature makes a caught error vanish while the code
#     stays exactly as broken — the Any warning, proved rather than asserted;
#   * a `type: ignore` carrying the wrong error code does not suppress
#     anything, which is why you always write the code.
#
# No network at test time. mypy writes its cache into a temporary directory
# that is removed on exit, so nothing appears in the lab.
# Exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${lab_dir}" || exit 1

failures=0
checks=0

work_dir="$(mktemp -d)"
cache_dir="${work_dir}/cache"
cleanup() { rm -rf "${work_dir}"; }
trap cleanup EXIT

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

# Resolve a tool: an explicit override, then this lab's .venv, then whatever
# is on PATH. Fails loudly with instructions rather than silently skipping.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

install_hint() {
  local tool="$1"
  echo "  Install it with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing ${tool}: ${2}=/path/to/${tool} bash tests/run_tests.sh" >&2
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  install_hint pytest PYTEST
  exit 1
}

mypy_bin="$(resolve_tool mypy "${MYPY:-}")" || {
  echo "FAIL: mypy not found." >&2
  install_hint mypy MYPY
  exit 1
}

echo "Day 075 lab tests"
echo "================="
echo "pytest: $("${pytest_bin}" --version 2>&1 | head -1)"
echo "mypy:   $("${mypy_bin}" --version 2>&1 | head -1)"
echo

# run_mypy <output-file> <extra args...>
# Runs mypy with colour and the cache pinned so output is stable and nothing
# is written into the lab. Records the exit status in mypy_status.
mypy_status=0
run_mypy() {
  local out="$1"
  shift
  "${mypy_bin}" --no-color-output --no-error-summary --cache-dir "${cache_dir}" "$@" >"${out}" 2>&1
  mypy_status=$?
}

# ---------------------------------------------------------------------------
echo "1. The tests pass on the buggy code (this is the whole point)"
# ---------------------------------------------------------------------------

pytest_out="${work_dir}/pytest-starter.txt"
if PYTHONPATH="${lab_dir}/starter" "${pytest_bin}" -q -p no:cacheprovider \
    starter/test_catalog.py >"${pytest_out}" 2>&1; then
  check "pytest exits 0 on the buggy starter/catalog.py" "yes"
else
  check "pytest exits 0 on the buggy starter/catalog.py" "no"
  sed -n '$p' "${pytest_out}"
fi

if grep -q "8 passed" "${pytest_out}"; then
  check "all 8 starter tests pass — a green suite over a broken module" "yes"
else
  check "all 8 starter tests pass — a green suite over a broken module" "no"
fi

# ---------------------------------------------------------------------------
echo
echo "2. mypy finds what the tests missed, and names the codes"
# ---------------------------------------------------------------------------

mypy_starter="${work_dir}/mypy-starter.txt"
run_mypy "${mypy_starter}" starter/catalog.py
if [ "${mypy_status}" -ne 0 ]; then
  check "mypy exits non-zero on starter/catalog.py" "yes"
else
  check "mypy exits non-zero on starter/catalog.py" "no"
fi

# Grep for the bracketed CODE, not the prose. Messages get reworded between
# releases; the codes are the stable interface.
for code in union-attr arg-type; do
  if grep -q "\[${code}\]" "${mypy_starter}"; then
    check "default mypy reports [${code}] on starter/catalog.py" "yes"
  else
    check "default mypy reports [${code}] on starter/catalog.py" "no"
  fi
done

if grep -q "^starter/catalog.py:63: error:.*\[union-attr\]" "${mypy_starter}"; then
  check "[union-attr] is reported on line 63 — the unguarded lookup in describe()" "yes"
else
  check "[union-attr] is reported on line 63 — the unguarded lookup in describe()" "no"
fi

# ---------------------------------------------------------------------------
echo
echo "3. Strict mode adds the errors default settings let through"
# ---------------------------------------------------------------------------

mypy_strict="${work_dir}/mypy-starter-strict.txt"
run_mypy "${mypy_strict}" --strict starter/catalog.py
if [ "${mypy_status}" -ne 0 ]; then
  check "mypy --strict exits non-zero on starter/catalog.py" "yes"
else
  check "mypy --strict exits non-zero on starter/catalog.py" "no"
fi

for code in no-untyped-def no-untyped-call no-any-return; do
  if grep -q "\[${code}\]" "${mypy_strict}"; then
    check "strict mode reports [${code}]" "yes"
  else
    check "strict mode reports [${code}]" "no"
  fi
  if grep -q "\[${code}\]" "${mypy_starter}"; then
    check "default settings do NOT report [${code}]" "no"
  else
    check "default settings do NOT report [${code}]" "yes"
  fi
done

# A file with no annotations at all: mypy's silence means "nothing to check",
# not "nothing wrong". Strict mode says so out loud.
mypy_untyped="${work_dir}/mypy-untyped.txt"
run_mypy "${mypy_untyped}" starter/untyped_first_run.py
if [ "${mypy_status}" -eq 0 ]; then
  check "default mypy is SILENT on a fully unannotated file" "yes"
else
  check "default mypy is SILENT on a fully unannotated file" "no"
fi

run_mypy "${mypy_untyped}" --strict starter/untyped_first_run.py
if [ "${mypy_status}" -ne 0 ] && grep -q "\[no-untyped-def\]" "${mypy_untyped}"; then
  check "--strict on the same file reports [no-untyped-def]" "yes"
else
  check "--strict on the same file reports [no-untyped-def]" "no"
fi

# ---------------------------------------------------------------------------
echo
echo "4. The fixed reference is clean, and the behaviour really was broken"
# ---------------------------------------------------------------------------

mypy_examples="${work_dir}/mypy-examples.txt"
run_mypy "${mypy_examples}" --strict \
  examples/catalog.py examples/typing_tour.py examples/demo.py examples/test_catalog.py
if [ "${mypy_status}" -eq 0 ]; then
  check "mypy --strict exits 0 on every file in examples/" "yes"
else
  check "mypy --strict exits 0 on every file in examples/" "no"
  cat "${mypy_examples}"
fi

mypy_config="${work_dir}/mypy-config.txt"
run_mypy "${mypy_config}" --config-file examples/pyproject.toml examples/catalog.py
if [ "${mypy_status}" -eq 0 ]; then
  check "the real [tool.mypy] table in examples/pyproject.toml also passes" "yes"
else
  check "the real [tool.mypy] table in examples/pyproject.toml also passes" "no"
  cat "${mypy_config}"
fi

pytest_examples="${work_dir}/pytest-examples.txt"
if PYTHONPATH="${lab_dir}/examples" "${pytest_bin}" -q -p no:cacheprovider \
    examples/test_catalog.py >"${pytest_examples}" 2>&1 && grep -q "9 passed" "${pytest_examples}"; then
  check "the fixed module passes all 9 tests, including the new None case" "yes"
else
  check "the fixed module passes all 9 tests, including the new None case" "no"
  sed -n '$p' "${pytest_examples}"
fi

# The type error was a real bug, not a bookkeeping complaint: prove it.
if PYTHONPATH="${lab_dir}/starter" python3 -c \
    "import catalog; catalog.describe('enormous')" >/dev/null 2>&1; then
  check "buggy describe('enormous') raises at runtime" "no"
else
  check "buggy describe('enormous') raises at runtime" "yes"
fi

fixed_describe="$(PYTHONPATH="${lab_dir}/examples" python3 -c \
  "import catalog; print(catalog.describe('enormous'))" 2>&1)"
if [ "${fixed_describe}" = "enormous: unknown model" ]; then
  check "fixed describe('enormous') returns a sensible string" "yes"
else
  check "fixed describe('enormous') returns a sensible string" "no"
  echo "    got: ${fixed_describe}"
fi

# ---------------------------------------------------------------------------
echo
echo "5. Any switches the checker off — proved, not asserted"
# ---------------------------------------------------------------------------

any_dir="${work_dir}/any"
mkdir -p "${any_dir}"
cp starter/any_demo.py "${any_dir}/before.py"
sed 's/-> str | None:/-> Any:/' "${any_dir}/before.py" >"${any_dir}/after.py"

if ! cmp -s "${any_dir}/before.py" "${any_dir}/after.py"; then
  check "the Any edit changed exactly one annotation" "yes"
else
  check "the Any edit changed exactly one annotation" "no"
fi

any_before="${work_dir}/any-before.txt"
run_mypy "${any_before}" "${any_dir}/before.py"
if [ "${mypy_status}" -ne 0 ] && grep -q "\[union-attr\]" "${any_before}"; then
  check "before: mypy reports [union-attr] on the unguarded call" "yes"
else
  check "before: mypy reports [union-attr] on the unguarded call" "no"
fi

any_after="${work_dir}/any-after.txt"
run_mypy "${any_after}" "${any_dir}/after.py"
if [ "${mypy_status}" -eq 0 ]; then
  check "after: the same code with Any reports NOTHING and exits 0" "yes"
else
  check "after: the same code with Any reports NOTHING and exits 0" "no"
  cat "${any_after}"
fi

# The code is exactly as broken as it was. Only the checking changed.
if PYTHONPATH="${any_dir}" python3 -c \
    "import after; after.shout('zzz')" >/dev/null 2>&1; then
  check "the Any version still crashes at runtime — nothing got safer" "no"
else
  check "the Any version still crashes at runtime — nothing got safer" "yes"
fi

# ---------------------------------------------------------------------------
echo
echo "6. A type: ignore with the wrong code suppresses nothing"
# ---------------------------------------------------------------------------

ignore_dir="${work_dir}/ignore"
mkdir -p "${ignore_dir}"
sed 's|return lookup(name).upper()|return lookup(name).upper()  # type: ignore[arg-type]|' \
  "${any_dir}/before.py" >"${ignore_dir}/wrong_code.py"
sed 's|return lookup(name).upper()|return lookup(name).upper()  # type: ignore[union-attr]|' \
  "${any_dir}/before.py" >"${ignore_dir}/right_code.py"

ignore_wrong="${work_dir}/ignore-wrong.txt"
run_mypy "${ignore_wrong}" "${ignore_dir}/wrong_code.py"
if [ "${mypy_status}" -ne 0 ] && grep -q "\[union-attr\]" "${ignore_wrong}"; then
  check "ignore[arg-type] does NOT suppress a [union-attr] error" "yes"
else
  check "ignore[arg-type] does NOT suppress a [union-attr] error" "no"
fi

ignore_right="${work_dir}/ignore-right.txt"
run_mypy "${ignore_right}" "${ignore_dir}/right_code.py"
if [ "${mypy_status}" -eq 0 ]; then
  check "ignore[union-attr] suppresses exactly that error and nothing else" "yes"
else
  check "ignore[union-attr] suppresses exactly that error and nothing else" "no"
  cat "${ignore_right}"
fi

# warn_unused_ignores turns a stale ignore into an error of its own.
cp examples/catalog.py "${ignore_dir}/stale.py"
printf '\n\nSTALE: int = 1  # type: ignore[assignment]\n' >>"${ignore_dir}/stale.py"
ignore_stale="${work_dir}/ignore-stale.txt"
run_mypy "${ignore_stale}" --strict "${ignore_dir}/stale.py"
if [ "${mypy_status}" -ne 0 ] && grep -q "\[unused-ignore\]" "${ignore_stale}"; then
  check "warn_unused_ignores reports a stale ignore as [unused-ignore]" "yes"
else
  check "warn_unused_ignores reports a stale ignore as [unused-ignore]" "no"
  cat "${ignore_stale}"
fi

# ---------------------------------------------------------------------------
echo
echo "7. The reference scripts run and produce their documented output"
# ---------------------------------------------------------------------------

demo_out="${work_dir}/demo.txt"
if PYTHONPATH="${lab_dir}/examples" python3 examples/demo.py >"${demo_out}" 2>&1; then
  check "python3 examples/demo.py exits 0" "yes"
else
  check "python3 examples/demo.py exits 0" "no"
fi

if grep -q "describe('enormous'): enormous: unknown model" "${demo_out}"; then
  check "demo shows the None path handled" "yes"
else
  check "demo shows the None path handled" "no"
fi

tour_out="${work_dir}/tour.txt"
if PYTHONPATH="${lab_dir}/examples" python3 examples/typing_tour.py >"${tour_out}" 2>&1; then
  check "python3 examples/typing_tour.py exits 0" "yes"
else
  check "python3 examples/typing_tour.py exits 0" "no"
fi

for expected in "first_word(None): (nothing)" "structural typing works" "first_or([], 'fallback'): fallback"; do
  if grep -qF "${expected}" "${tour_out}"; then
    check "typing tour prints: ${expected}" "yes"
  else
    check "typing tour prints: ${expected}" "no"
  fi
done

# ---------------------------------------------------------------------------
echo
echo "-----------------------------------------------------------"
echo "${checks} checks, ${failures} failure(s)."
if [ "${failures}" -ne 0 ]; then
  exit 1
fi
exit 0
