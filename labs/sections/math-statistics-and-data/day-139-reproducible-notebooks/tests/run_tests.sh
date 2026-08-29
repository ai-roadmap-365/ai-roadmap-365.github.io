#!/usr/bin/env bash
# Day 139 lab harness: "Notebooks That Reproduce"
#
# Prints "N checks, M failure(s)" and exits 0 only when M is zero.
set -u

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LAB_DIR"

PYTHON="${PYTHON:-.venv/bin/python3}"
PYTEST="${PYTEST:-.venv/bin/pytest}"

CHECKS=0
FAILURES=0

ok() {
  CHECKS=$((CHECKS + 1))
  echo "  ok: $1"
}

fail() {
  CHECKS=$((CHECKS + 1))
  FAILURES=$((FAILURES + 1))
  echo "  FAIL: $1"
}

if [ ! -x "$PYTHON" ]; then
  echo "No lab .venv found at $PYTHON."
  echo "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements/requirements.txt"
  exit 2
fi

echo "1. Installed versions match requirements/requirements.txt"
VERSION_CHECK=$("$PYTHON" - <<'PYEOF'
import nbformat, nbclient, nbconvert, pytest, ipykernel
print("nbformat", nbformat.__version__)
print("nbclient", nbclient.__version__)
print("nbconvert", nbconvert.__version__)
print("ipykernel", ipykernel.__version__)
print("pytest", pytest.__version__)
PYEOF
)
echo "$VERSION_CHECK" | sed 's/^/    /'
while read -r pkg pin; do
  pin_version="${pin#*==}"
  installed=$(echo "$VERSION_CHECK" | awk -v p="$pkg" '$1==p {print $2}')
  if [ "$installed" = "$pin_version" ]; then
    ok "$pkg $installed matches the pin"
  else
    fail "$pkg installed=$installed pinned=$pin_version"
  fi
done < <(sed 's/==/ ==/' requirements/requirements.txt)

echo ""
echo "2. The library, driven directly (outside pytest)"
DIRECT_CHECK=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import nb_lib
import nbformat as nbf

errors = []

# Exercise 1/2: out-of-order changes the answer, execution_count is not monotonic
nb = nb_lib.analyst_notebook()
clean = nb_lib.execute_clean(nb)
scrambled = nb_lib.execute_in_order(nb, [0, 2, 1])
clean_answer = nb_lib.final_value(clean, 2)
scrambled_answer = nb_lib.final_value(scrambled, 2)
if clean_answer != "30.0":
    errors.append(f"clean answer expected 30.0, got {clean_answer}")
if scrambled_answer != "50.0":
    errors.append(f"scrambled answer expected 50.0, got {scrambled_answer}")
if nb_lib.is_monotonic(nb_lib.execution_counts(scrambled)):
    errors.append("scrambled execution_count unexpectedly monotonic")
if not nb_lib.is_monotonic(nb_lib.execution_counts(clean)):
    errors.append("clean execution_count unexpectedly non-monotonic")

# Exercise 3: hidden state
cell_defining, cell_using = nb_lib.hidden_state_pair()
dirty = nb_lib.run_in_dirty_kernel_after_deletion(cell_defining, cell_using)
if len(dirty.cells) != 1:
    errors.append("hidden-state notebook should have exactly one cell left")
try:
    nb_lib.run_fresh_kernel(dirty)
    errors.append("fresh kernel unexpectedly succeeded on hidden-state notebook")
except nb_lib.CellExecutionError as e:
    if e.ename != "NameError":
        errors.append(f"expected NameError, got {e.ename}")

# Exercise 4: execution as a test
try:
    nb_lib.execute_clean(nb_lib.failing_notebook())
    errors.append("failing_notebook unexpectedly executed without error")
except nb_lib.CellExecutionError as e:
    if e.ename != "ValueError" or "In[2]" not in str(e):
        errors.append("failing cell not correctly named in the exception")

# Exercise 5: stripping
run_a = nb_lib.execute_clean(nb_lib.analyst_notebook())
run_b = nb_lib.execute_clean(nb_lib.analyst_notebook())
if nbf.writes(run_a) == nbf.writes(run_b):
    errors.append("two independent runs were unexpectedly byte-identical unstripped")
if nbf.writes(nb_lib.strip_outputs(run_a)) != nbf.writes(nb_lib.strip_outputs(run_b)):
    errors.append("stripped runs were not byte-identical")

# Exercise 6: parameterisation
strict = nb_lib.execute_clean(nb_lib.parameters_notebook(threshold=10))
loose = nb_lib.execute_clean(nb_lib.parameters_notebook(threshold=5))
if nb_lib.final_value(strict, 3) == nb_lib.final_value(loose, 3):
    errors.append("parameterised variants unexpectedly produced the same output")
if strict.cells[2].source != loose.cells[2].source:
    errors.append("unrelated analysis cell text changed between variants")

# Exercise 7: conversion
nb7 = nbf.v4.new_notebook()
nb7.cells = [
    nbf.v4.new_markdown_cell("A prose sentence with a claim in it."),
    nbf.v4.new_code_cell("21 * 2"),
]
executed7 = nb_lib.execute_clean(nb7)
md = nb_lib.to_markdown(executed7)
if "A prose sentence with a claim in it." not in md or "42" not in md:
    errors.append("nbconvert Markdown output missing prose or computed value")

# Exercise 8: module vs cell
from calc import clean_mean
if clean_mean([1, None, 3]) != 2.0:
    errors.append("calc.clean_mean gave the wrong answer")

# Exercise 9: environment record
env_nb = nb_lib.execute_clean(nb_lib.environment_cell_notebook())
recorded = nb_lib.final_value(env_nb, 0)
live = nb_lib.record_environment()
for key, value in live.items():
    if repr(value) not in recorded and value not in recorded:
        errors.append(f"environment record missing {key}={value}")

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-9 reproduced directly against nb_lib, no pytest involved"
else
  fail "direct library checks failed"
  echo "$DIRECT_CHECK" | sed 's/^/    /'
fi

echo ""
echo "3. examples/ passes in full"
EXAMPLES_OUT=$("$PYTEST" examples -q 2>&1)
if echo "$EXAMPLES_OUT" | tail -1 | grep -qE "^12 passed"; then
  ok "pytest examples -q -> 12 passed"
else
  fail "pytest examples -q did not report 12 passed"
  echo "$EXAMPLES_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "4. starter/ is an untouched skeleton"
STARTER_OUT=$("$PYTEST" starter -q 2>&1)
if echo "$STARTER_OUT" | tail -1 | grep -qE "3 passed, 9 skipped"; then
  ok "pytest starter -q -> 3 passed, 9 skipped (calc.py solved; the 9 notebook exercises are stubs)"
else
  fail "pytest starter -q did not report 3 passed, 9 skipped"
  echo "$STARTER_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "5. pytest examples starter (one invocation) aborts on the module-name collision"
COMBINED_OUT=$("$PYTEST" examples starter 2>&1)
if echo "$COMBINED_OUT" | grep -q "import file mismatch"; then
  ok "combined invocation reports import file mismatch, as documented -- never run starter and examples together"
else
  fail "combined invocation did not fail with import file mismatch as expected"
fi

echo ""
echo "6. Proof the harness can fail"
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d139-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^12 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
python3 - "$SCRATCH/test_notebooks.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = 'assert clean_answer == "30.0"'
replacement = 'assert clean_answer == "999.0"'
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_01_out_of_order_changes_the_answer"; then
  ok "breaking exercise 1's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "7. Offline, and nothing left behind"
if ! grep -rInE "https?://" examples/*.py starter/*.py > /dev/null 2>&1; then
  ok "no URLs inside examples/ or starter/ source"
else
  fail "found a URL inside examples/ or starter/"
fi
if [ -z "$(find . -path ./.venv -prune -o -iname '*.ipynb' -print 2>/dev/null)" ]; then
  ok "no .ipynb file anywhere inside the lab -- every notebook in this lab exists only in memory"
else
  fail "found a stray .ipynb file"
fi
if [ -z "$(find . -path ./.venv -prune -o -type d -iname '.ipynb_checkpoints' -print 2>/dev/null)" ]; then
  ok "no .ipynb_checkpoints directory anywhere inside the lab"
else
  fail "found a stray .ipynb_checkpoints directory"
fi
if [ -z "$(find . -path ./.venv -prune -o -type d -name '__pycache__' -print 2>/dev/null)" ]; then
  ok "no __pycache__ left behind"
else
  find . -path ./.venv -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
  ok "no __pycache__ left behind (cleaned during this run)"
fi
if [ ! -d .pytest_cache ]; then
  ok "no .pytest_cache left behind"
else
  rm -rf .pytest_cache
  ok "no .pytest_cache left behind (cleaned during this run)"
fi

echo ""
echo "---------------------------------------------------------------"
echo "$CHECKS checks, $FAILURES failure(s)"
if [ "$FAILURES" -ne 0 ]; then
  exit 1
fi
exit 0
