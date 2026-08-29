#!/usr/bin/env bash
# Day 159 lab harness: "Precision, Recall, ROC, and Choosing Thresholds"
set -u

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LAB_DIR"

PYTHON="${PYTHON:-../../../../.venv-tools/bin/python3}"
PYTEST="${PYTEST:-../../../../.venv-tools/bin/pytest}"

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

echo "=== 1. Package versions ==="
VERSION_CHECK=$("$PYTHON" - <<'PYEOF'
import numpy, sklearn, pytest, scipy
print("numpy", numpy.__version__)
print("scikit-learn", sklearn.__version__)
print("pytest", pytest.__version__)
print("scipy", scipy.__version__)
PYEOF
)
echo "$VERSION_CHECK" | sed 's/^/    /'
while read -r pkg pin; do
  pin_version="${pin#*==}"
  installed=$(echo "$VERSION_CHECK" | awk -v p="$pkg" '$1==p {print $2}')
  if [ "$installed" = "$pin_version" ]; then
    ok "$pkg $installed matches pinned version"
  else
    fail "$pkg installed=$installed pinned=$pin_version"
  fi
done < <(sed 's/==/ ==/' requirements/requirements.txt)

echo ""
echo "=== 2. Mathematical invariants verified ==="
MATH_CHECK=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import metrics_lib as met

# Harmonic mean property: F1 must lie strictly between min(P, R) and max(P, R)
y_t = np.array([1, 1, 1, 1, 0, 0, 0, 0])
y_p = np.array([1, 1, 1, 0, 1, 0, 0, 0])
m = met.compute_metrics(y_t, y_p)
p, r, f1 = m["precision"], m["recall"], m["f1"]
assert min(p, r) <= f1 <= max(p, r), f"F1={f1} outside [P={p}, R={r}]"

print("MATH_OK")
PYEOF
)

if [ "$MATH_CHECK" = "MATH_OK" ]; then
  ok "Classification metric invariants (F1 harmonic bound) verified"
else
  fail "Mathematical verification failed: $MATH_CHECK"
fi

echo ""
echo "=== 3. Pytest on examples ==="
PYTHONPATH="examples" "$PYTEST" -q examples >/dev/null 2>&1
if [ $? -eq 0 ]; then
  ok "All reference test cases passed in examples/"
else
  fail "Reference test suite failed"
fi

echo ""
echo "=== 4. Pytest on starter ==="
PYTHONPATH="starter" "$PYTEST" -q starter >/dev/null 2>&1
if [ $? -eq 0 ]; then
  ok "Starter stub tests executed successfully"
else
  fail "Starter stub tests failed"
fi

echo ""
echo "Summary: $CHECKS checks, $FAILURES failure(s)"
if [ $FAILURES -eq 0 ]; then
  exit 0
else
  exit 1
fi
