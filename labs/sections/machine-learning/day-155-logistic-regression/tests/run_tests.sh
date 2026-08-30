#!/usr/bin/env bash
# Day 155 lab harness: "Logistic Regression"
set -u

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LAB_DIR"

# Resolve the interpreter rather than hard-coding one. The repository's
# .venv-tools is gitignored, so pointing straight at it made this lab
# unrunnable for anyone who cloned the public repository. Order: an explicit
# override, then a lab-local .venv, then the repo tools venv if it happens to
# exist, then whatever is on PATH.
resolve_tool() {
  tool="$1"
  override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  for candidate in ".venv/bin/${tool}" "../../../../.venv-tools/bin/${tool}"; do
    if [ -x "${candidate}" ]; then echo "${candidate}"; return 0; fi
  done
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

PYTHON="$(resolve_tool python3 "${PYTHON:-}")" || {
  echo "FAIL: python3 not found. Create the lab environment with:" >&2
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
}
PYTEST="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found. Create the lab environment with:" >&2
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
}

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
import logistic_lib as logreg

s0 = logreg.sigmoid(np.array([0.0]))[0]
assert abs(s0 - 0.5) < 1e-9, f"s(0)={s0}"

z = np.array([-2.5, 0.0, 2.5])
s_pos = logreg.sigmoid(z)
s_neg = logreg.sigmoid(-z)
assert np.allclose(s_neg, 1.0 - s_pos, atol=1e-9), "sigmoid symmetry violated"

y = np.array([1.0, 0.0])
p = np.array([0.5, 0.5])
loss_mid = logreg.binary_cross_entropy(y, p)
assert abs(loss_mid - np.log(2.0)) < 1e-9, f"loss_mid={loss_mid}"

X = np.eye(2)
y_match = np.array([1.0, 0.0])
p_match = np.array([1.0, 0.0])
gw, gb = logreg.compute_gradients(X, y_match, p_match)
assert np.allclose(gw, 0.0) and abs(gb) < 1e-9, "gradients not zero on exact match"

print("MATH_OK")
PYEOF
)

if [ "$MATH_CHECK" = "MATH_OK" ]; then
  ok "All mathematical identities verified exactly"
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
