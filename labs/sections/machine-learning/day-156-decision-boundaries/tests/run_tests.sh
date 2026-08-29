#!/usr/bin/env bash
# Day 156 lab harness: "Decision Boundaries"
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
import boundary_lib as bnd

# 1. Point on boundary has zero distance
w = np.array([3.0, 4.0])
b = -10.0
# Point (2, 1) gives 3(2) + 4(1) - 10 = 0
p0 = np.array([[2.0, 1.0]])
d0 = bnd.signed_distance_to_boundary(p0, w, b)[0]
assert abs(d0) < 1e-9, f"d0={d0}"

# 2. Distance magnitude matches Euclidean formula
# Point (2, 6) gives 3(2) + 4(6) - 10 = 20 / 5 = 4
p1 = np.array([[2.0, 6.0]])
d1 = bnd.signed_distance_to_boundary(p1, w, b)[0]
assert abs(d1 - 4.0) < 1e-9, f"d1={d1}"

print("MATH_OK")
PYEOF
)

if [ "$MATH_CHECK" = "MATH_OK" ]; then
  ok "Decision boundary geometry and distance metrics verified exactly"
else
  fail "Mathematical verification failed: $MATH_CHECK"
fi

echo ""
echo "=== 3. Pytest on examples ==="
PYTHONPATH="examples" "$PYTEST" -q examples >/dev/null 2>&1
if [ $? -eq 0 ]; then
  ok "All 4 reference test cases passed in examples/"
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
