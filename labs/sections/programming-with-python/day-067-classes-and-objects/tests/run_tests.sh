#!/usr/bin/env bash
# Tests for the Day 067 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# These checks exercise real behaviour, not file existence: a class is
# built, its invariant is attacked, its property rejects a bad value, its
# __repr__ is compared to an exact string, and its classmethod builds an
# instance from a CSV row. The dict version and the class version are then
# driven through the same moves and their results compared, which is what
# "the refactor changed nothing" actually means.
#
# Nothing here prints a default object repr, because that contains a memory
# address which differs on every run; the suite compares custom reprs and
# boolean facts instead, so the output is deterministic.
#
# No network, no pip, no sudo, non-interactive. Exits 0 only if every check
# passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

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

# check_py <label> <import_dir> <python-body>
# Runs an assertion body with `account` importable from import_dir.
# A clean exit (every assert holds) is a pass.
check_py() {
  local label="$1" import_dir="$2" body="$3"
  if PYTHONPATH="${import_dir}:${lab_dir}/examples" python3 -c "
import sys
sys.path.insert(0, '${import_dir}')
from account import Account
${body}
" 2>/dev/null; then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
}

# check_script <label> <script> <needle>
check_script() {
  local label="$1" script="$2" needle="$3"
  local out code
  out="$(cd "${lab_dir}" && python3 "${script}" 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ] && printf '%s' "${out}" | grep -qF "${needle}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (exit ${code}; output: ${out})"
  fi
}

run_class_checks() {
  local import_dir="$1"
  echo "Testing the Account class in ${import_dir} ..."

  check_py "two instances hold separate state" "${import_dir}" \
    "a = Account('ada', 100)
b = Account('bob', 100)
a.deposit(50)
assert a is not b
assert type(a) is type(b)
assert a.balance == 150.0 and b.balance == 100.0"

  check_py "history is per instance, not shared on the class" "${import_dir}" \
    "a = Account('ada', 100)
b = Account('bob', 100)
a.deposit(50)
assert a.history is not b.history
assert b.history == [], f'shared list bug: {b.history}'
assert a.history == [('deposit', 50.0)]"

  check_py "deposit and withdraw maintain the balance" "${import_dir}" \
    "a = Account('ada', 100)
assert a.deposit(50) == 150.0
assert a.withdraw(30) == 120.0
assert a.describe() == 'ada: 120.00 (2 entries)'"

  check_py "the invariant is defended: overdraft is refused" "${import_dir}" \
    "a = Account('ada', 100)
try:
    a.withdraw(1000)
    raise SystemExit(1)
except ValueError as err:
    assert 'insufficient funds' in str(err)
assert a.balance == 100.0"

  check_py "the property rejects a negative balance" "${import_dir}" \
    "a = Account('ada', 100)
try:
    a.balance = -500
    raise SystemExit(1)
except ValueError as err:
    assert 'negative' in str(err)
assert a.balance == 100.0"

  check_py "balance is a property on the class, backed by _balance" "${import_dir}" \
    "a = Account('ada', 100)
assert isinstance(Account.__dict__['balance'], property)
assert '_balance' in vars(a)
assert 'balance' not in vars(a)"

  check_py "__repr__ is custom and shows the state" "${import_dir}" \
    "a = Account('ada', 120)
assert repr(a) == \"Account(owner='ada', balance=120.00)\", repr(a)
assert 'object at 0x' not in repr(a)"

  check_py "from_csv_row is a classmethod that builds an instance" "${import_dir}" \
    "a = Account.from_csv_row('cleo, 250.00')
assert type(a) is Account
assert a.owner == 'cleo' and a.balance == 250.0
assert isinstance(Account.__dict__['from_csv_row'], classmethod)
try:
    Account.from_csv_row('nonsense')
    raise SystemExit(1)
except ValueError:
    pass"

  check_py "is_valid_amount is a staticmethod" "${import_dir}" \
    "assert isinstance(Account.__dict__['is_valid_amount'], staticmethod)
assert Account.is_valid_amount(5) is True
assert Account.is_valid_amount(-5) is False
assert Account.is_valid_amount('5') is False"

  check_py "a method call is Class.method(instance, ...)" "${import_dir}" \
    "a = Account('ada', 100)
assert a.deposit.__self__ is a
assert a.deposit.__func__ is Account.deposit
Account.deposit(a, 10)
assert a.balance == 110.0"

  check_py "currency is a class attribute seen by every instance" "${import_dir}" \
    "a = Account('ada', 100)
assert 'currency' not in vars(a)
assert a.currency == Account.currency == 'USD'"

  check_py "the class reproduces the dict version's behaviour exactly" "${import_dir}" \
    "import account_dict as old
moves = [('deposit', 50), ('withdraw', 30), ('deposit', 12.5), ('withdraw', 2.5)]
d = old.make_account('ada', 100)
c = Account('ada', 100)
for move, amount in moves:
    (old.deposit if move == 'deposit' else old.withdraw)(d, amount)
    getattr(c, move)(amount)
assert old.describe(d) == c.describe()
assert d['history'] == c.history"
}

# --- Reference implementation: always tested strictly ---
run_class_checks "${lab_dir}/examples"

echo "Testing the supporting example scripts ..."
check_script "account_dict.py runs and shows the unguarded edit" \
  "examples/account_dict.py" "after a direct edit: ada: -500.00"
check_script "account.py runs and refuses the same edit" \
  "examples/account.py" "after the refused edit: ada: 120.00"
check_script "shared_bug.py reproduces the shared list" \
  "examples/shared_bug.py" "same list object? True"
check_script "shared_bug.py shows the per-instance fix" \
  "examples/shared_bug.py" "cleo.history: [('cleo', 10)]"
check_script "compare.py proves the two versions agree" \
  "examples/compare.py" "descriptions identical: True"
check_script "compare.py loads accounts.csv through the classmethod" \
  "examples/compare.py" "loaded 4 accounts, total 2225.75 USD"
check_script "closure_object.py builds an object without the class keyword" \
  "examples/closure_object.py" "outputs identical: True"
check_script "machinery.py shows the bound-method mechanism" \
  "examples/machinery.py" "ada.deposit.__self__ is ada: True"
check_script "machinery.py shows name mangling" \
  "examples/machinery.py" "hasattr(card, '_Card__pin'): True"

# --- Learner starter ---
echo "Testing starter/account.py ..."
starter_file="${lab_dir}/starter/account.py"
if python3 -c "compile(open('${starter_file}').read(), '${starter_file}', 'exec')" 2>/dev/null; then
  check "starter is valid Python" "yes"
else
  check "starter is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter_file}"; then
  echo "Note: starter/account.py still has unfinished exercises — testing structure only."
  grep -q 'class Account' "${starter_file}" && check "starter defines class Account" "yes" || check "starter defines class Account" "no"
  grep -q 'def __init__' "${starter_file}" && check "starter defines __init__" "yes" || check "starter defines __init__" "no"
  grep -q 'def deposit' "${starter_file}" && check "starter defines deposit" "yes" || check "starter defines deposit" "no"
  grep -q 'def withdraw' "${starter_file}" && check "starter defines withdraw" "yes" || check "starter defines withdraw" "no"
  grep -q 'def __repr__' "${starter_file}" && check "starter defines __repr__" "yes" || check "starter defines __repr__" "no"
  grep -q 'def from_csv_row' "${starter_file}" && check "starter defines from_csv_row" "yes" || check "starter defines from_csv_row" "no"
else
  run_class_checks "${lab_dir}/starter"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
