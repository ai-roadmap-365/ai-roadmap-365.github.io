#!/usr/bin/env bash
# Tests for the Day 046 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Runs the reference program and confirms the numeric facts it demonstrates:
# the Decimal cart total is exact, math.isclose treats 0.1+0.2 as 0.3, and
# floor division / modulo give the expected whole numbers. No network access.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

# --- 1. The reference program runs cleanly and prints its sections. --------
echo "Running examples/precision_demo.py ..."
if output="$(python3 "${lab_dir}/examples/precision_demo.py" 2>&1)"; then
  check "program exits successfully" "yes"
else
  check "program exits successfully" "no"
  echo "${output}" | sed 's/^/    /'
fi

echo "${output}" | grep -q "0.30000000000000004" \
  && check "shows the exact float result of 0.1 + 0.2" "yes" \
  || check "shows the exact float result of 0.1 + 0.2" "no"

echo "${output}" | grep -q "Charge the customer: \$28.78" \
  && check "charges the exact Decimal total of \$28.78" "yes" \
  || check "charges the exact Decimal total of \$28.78" "no"

echo "${output}" | grep -q "7 x dollar" \
  && check "making change gives 7 whole dollars" "yes" \
  || check "making change gives 7 whole dollars" "no"

# --- 2. Direct numeric assertions with python3 -c. -------------------------
echo "Checking numeric facts directly ..."

python3 -c "assert (0.1 + 0.2) != 0.3, 'expected float error'" \
  && check "0.1 + 0.2 != 0.3 in float (the trap is real)" "yes" \
  || check "0.1 + 0.2 != 0.3 in float (the trap is real)" "no"

python3 -c "import math; assert math.isclose(0.1 + 0.2, 0.3), 'isclose should be True'" \
  && check "math.isclose(0.1 + 0.2, 0.3) is True" "yes" \
  || check "math.isclose(0.1 + 0.2, 0.3) is True" "no"

python3 -c "from decimal import Decimal; prices=['19.99','5.99','2.50','0.10','0.20']; assert sum(Decimal(p) for p in prices) == Decimal('28.78'), 'Decimal total must be exact'" \
  && check "Decimal cart total is exactly 28.78" "yes" \
  || check "Decimal cart total is exactly 28.78" "no"

python3 -c "assert 725 // 100 == 7, 'floor division wrong'; assert 725 % 100 == 25, 'modulo wrong'" \
  && check "725 // 100 == 7 and 725 % 100 == 25" "yes" \
  || check "725 // 100 == 7 and 725 % 100 == 25" "no"

python3 -c "from decimal import Decimal; assert Decimal('0.1') + Decimal('0.2') == Decimal('0.3'), 'Decimal from strings must be exact'" \
  && check "Decimal('0.1') + Decimal('0.2') == Decimal('0.3')" "yes" \
  || check "Decimal('0.1') + Decimal('0.2') == Decimal('0.3')" "no"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
