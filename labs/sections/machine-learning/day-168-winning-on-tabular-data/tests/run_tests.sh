#!/usr/bin/env bash
# Day 168 lab harness: "Winning on Tabular Data"
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
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import tabular_lib as tab

cancer = load_breast_cancer()
X, y = cancer.data[:60], cancer.target[:60]
models = [LogisticRegression(max_iter=200), RandomForestClassifier(n_estimators=10, random_state=42)]
oof = tab.generate_out_of_fold_predictions(models, X, y, cv=3)
assert oof.shape == (60, 2), f"OOF shape {oof.shape} invalid"
assert np.all((oof >= 0.0) & (oof <= 1.0)), "OOF probabilities out of bounds"

print("MATH_OK")
PYEOF
)

if [ "$MATH_CHECK" = "MATH_OK" ]; then
  ok "Out-of-fold matrix generation and stacking invariants verified"
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
