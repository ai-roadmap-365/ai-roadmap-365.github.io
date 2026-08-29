#!/usr/bin/env bash
# Tests for the Day 070 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# What this suite is really testing is a DESIGN, not just some functions:
#
#   * the value objects are immutable and compare by value;
#   * the entities compare by identity and enforce their invariants;
#   * every broken rule raises a domain error from the GymError family;
#   * the domain core imports nothing that does I/O — proved twice, once by
#     reading its imports and once by running it from an EMPTY directory;
#   * the repository round-trips the club through JSON without losing a fact.
#
# No network, non-interactive, deterministic. Exits 0 only if every check
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

# check_core <label> <core_dir> <python-body>
# Runs an assertion body with the domain core importable from core_dir, from
# an EMPTY working directory. If the body needs a file to exist, it fails —
# which is exactly the property we want to prove about a pure core.
check_core() {
  local label="$1" core_dir="$2" body="$3" empty_dir
  empty_dir="$(mktemp -d "${TMPDIR:-/tmp}/gym-core.XXXXXX")"
  if (cd "${empty_dir}" && PYTHONPATH="${core_dir}" python3 -c "
import gym_core as g
${body}
" >/dev/null 2>&1); then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
  rm -rf "${empty_dir}"
}

# check_repo <label> <core_dir> <python-body>
# Same, but the repository (which DOES do I/O) is importable too, and the
# working directory is a scratch dir the body may write into.
check_repo() {
  local label="$1" core_dir="$2" body="$3" work_dir
  work_dir="$(mktemp -d "${TMPDIR:-/tmp}/gym-repo.XXXXXX")"
  if (cd "${work_dir}" && PYTHONPATH="${core_dir}" python3 -c "
import gym_core as g
from gym_repository import JsonClubRepository
${body}
" >/dev/null 2>&1); then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
  rm -rf "${work_dir}"
}

check_purity() {
  # Parse the file and inspect what it REALLY imports and calls, rather than
  # grepping text (a docstring that says "no open()" is not a violation).
  local core_file="$1" label="$2"
  if python3 - "${core_file}" <<'PY' 2>/dev/null
import ast
import sys

BANNED_MODULES = {
    "json", "os", "sys", "io", "pathlib", "shutil", "subprocess",
    "socket", "urllib", "http", "sqlite3", "csv", "pickle", "logging",
}
BANNED_CALLS = {"open", "print", "input", "eval", "exec"}

with open(sys.argv[1], encoding="utf-8") as handle:
    tree = ast.parse(handle.read(), sys.argv[1])

violations = []
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name.split(".")[0] in BANNED_MODULES:
                violations.append(f"import {alias.name}")
    elif isinstance(node, ast.ImportFrom):
        if node.module and node.module.split(".")[0] in BANNED_MODULES:
            violations.append(f"from {node.module} import ...")
    elif isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id in BANNED_CALLS:
            violations.append(f"{func.id}()")

for v in violations:
    print(v, file=sys.stderr)
sys.exit(1 if violations else 0)
PY
  then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (the core reaches for the outside world — move that code to an adapter)"
  fi
}

run_model_checks() {
  local core_dir="$1"
  echo "Testing the domain core in ${core_dir} (no files, empty working directory) ..."

  check_core "MembershipNumber compares by value" "${core_dir}" \
    "assert g.MembershipNumber('GYM-0007') == g.MembershipNumber('GYM-0007')
assert g.MembershipNumber('GYM-0007') != g.MembershipNumber('GYM-0008')"

  check_core "MembershipNumber is immutable" "${core_dir}" \
    "import dataclasses
n = g.MembershipNumber('GYM-0007')
try:
    n.value = 'GYM-9999'
except dataclasses.FrozenInstanceError:
    pass
else:
    raise SystemExit(1)"

  check_core "MembershipNumber rejects a bad format" "${core_dir}" \
    "for bad in ['0007', 'GYM-7', 'gym-0007', 'GYM-00007', 7]:
    try:
        g.MembershipNumber(bad)
    except g.InvalidMembershipNumber:
        continue
    raise SystemExit(1)"

  check_core "Money compares by value and is immutable" "${core_dir}" \
    "import dataclasses
assert g.Money(2900, 'EUR') == g.Money(2900, 'EUR')
assert g.Money(2900, 'EUR') != g.Money(2900, 'USD')
try:
    g.Money(1, 'EUR').cents = 2
except dataclasses.FrozenInstanceError:
    pass
else:
    raise SystemExit(1)"

  check_core "Money rejects negatives, floats and bad currencies" "${core_dir}" \
    "for bad in [(-1, 'EUR'), (1.5, 'EUR'), (True, 'EUR'), (100, 'eur'), (100, 'EURO')]:
    try:
        g.Money(*bad)
    except g.InvalidMoney:
        continue
    raise SystemExit(1)"

  check_core "Money adds within a currency" "${core_dir}" \
    "assert g.Money(2900, 'EUR') + g.Money(4900, 'EUR') == g.Money(7800, 'EUR')
assert g.Money.zero('EUR') + g.Money(2900, 'EUR') == g.Money(2900, 'EUR')
assert str(g.Money(2900, 'EUR')) == '29.00 EUR'"

  check_core "Money refuses to add two currencies" "${core_dir}" \
    "try:
    g.Money(100, 'EUR') + g.Money(100, 'USD')
except g.CurrencyMismatch:
    pass
else:
    raise SystemExit(1)"

  check_core "DateRange rejects a backwards period and answers contains()" "${core_dir}" \
    "from datetime import date
period = g.DateRange(date(2026, 4, 1), date(2026, 4, 30))
assert period.contains(date(2026, 4, 1))
assert period.contains(date(2026, 4, 30))
assert not period.contains(date(2026, 5, 1))
try:
    g.DateRange(date(2026, 4, 30), date(2026, 4, 1))
except g.InvalidDateRange:
    pass
else:
    raise SystemExit(1)"

  check_core "PlanTier is a closed set" "${core_dir}" \
    "assert g.PlanTier('basic') is g.PlanTier.BASIC
try:
    g.PlanTier('pluss')
except ValueError:
    pass
else:
    raise SystemExit(1)"

  check_core "Member equality is identity, not values" "${core_dir}" \
    "from datetime import date
plan = g.Plan(g.PlanTier.BASIC, g.Money(2900, 'EUR'))
a = g.Member(g.MembershipNumber('GYM-0001'), 'Ada', date(2026, 1, 15), plan)
b = g.Member(g.MembershipNumber('GYM-0001'), 'Different Name', date(2026, 9, 9), plan)
c = g.Member(g.MembershipNumber('GYM-0002'), 'Ada', date(2026, 1, 15), plan)
assert a == b
assert a != c
assert len({a, b, c}) == 2"

  check_core "a Member stays the same member after every value changes" "${core_dir}" \
    "from datetime import date
basic = g.Plan(g.PlanTier.BASIC, g.Money(2900, 'EUR'))
plus = g.Plan(g.PlanTier.PLUS, g.Money(4900, 'EUR'))
m = g.Member(g.MembershipNumber('GYM-0001'), 'Ada', date(2026, 1, 15), basic)
before = hash(m)
m.name = 'Ada L.'
m.switch_plan(plus)
m.check_in(date(2026, 4, 2))
assert hash(m) == before
assert m.plan is plus
assert len(m.check_ins) == 1"

  check_core "a basic member gets 12 check-ins a month, not 13" "${core_dir}" \
    "from datetime import date
basic = g.Plan(g.PlanTier.BASIC, g.Money(2900, 'EUR'))
m = g.Member(g.MembershipNumber('GYM-0003'), 'Lin', date(2026, 1, 1), basic)
for day in range(1, 13):
    m.check_in(date(2026, 4, day))
assert m.check_ins_in_month(2026, 4) == 12
try:
    m.check_in(date(2026, 4, 13))
except g.CheckInLimitExceeded:
    pass
else:
    raise SystemExit(1)
m.check_in(date(2026, 5, 1))
assert m.check_ins_in_month(2026, 5) == 1"

  check_core "a plus member is unlimited" "${core_dir}" \
    "from datetime import date
plus = g.Plan(g.PlanTier.PLUS, g.Money(4900, 'EUR'))
m = g.Member(g.MembershipNumber('GYM-0002'), 'Grace', date(2026, 2, 1), plus)
for day in range(1, 29):
    m.check_in(date(2026, 4, day))
assert m.check_ins_in_month(2026, 4) == 28"

  check_core "a CheckIn is frozen history" "${core_dir}" \
    "import dataclasses
from datetime import date
visit = g.CheckIn(g.MembershipNumber('GYM-0001'), date(2026, 4, 3))
try:
    visit.day = date(2026, 4, 4)
except dataclasses.FrozenInstanceError:
    pass
else:
    raise SystemExit(1)"

  check_core "Club refuses duplicate numbers and unknown members" "${core_dir}" \
    "from datetime import date
basic = g.Plan(g.PlanTier.BASIC, g.Money(2900, 'EUR'))
club = g.Club('Northside Gym')
club.enroll(g.Member(g.MembershipNumber('GYM-0001'), 'Ada', date(2026, 1, 15), basic))
try:
    club.enroll(g.Member(g.MembershipNumber('GYM-0001'), 'Impostor', date(2026, 5, 1), basic))
except g.DuplicateMember:
    pass
else:
    raise SystemExit(1)
try:
    club.find(g.MembershipNumber('GYM-9999'))
except g.UnknownMember:
    pass
else:
    raise SystemExit(1)"

  check_core "Club sums monthly revenue into one Money" "${core_dir}" \
    "from datetime import date
basic = g.Plan(g.PlanTier.BASIC, g.Money(2900, 'EUR'))
plus = g.Plan(g.PlanTier.PLUS, g.Money(4900, 'EUR'))
club = g.Club('Northside Gym')
club.enroll(g.Member(g.MembershipNumber('GYM-0001'), 'Ada', date(2026, 1, 15), basic))
club.enroll(g.Member(g.MembershipNumber('GYM-0002'), 'Grace', date(2026, 2, 1), plus))
club.enroll(g.Member(g.MembershipNumber('GYM-0003'), 'Lin', date(2026, 3, 9), basic))
assert club.monthly_revenue() == g.Money(10700, 'EUR')
assert [m.number.value for m in club.roster()] == ['GYM-0001', 'GYM-0002', 'GYM-0003']"

  check_core "every refusal is a GymError the adapter can catch" "${core_dir}" \
    "for cls in [g.InvalidMembershipNumber, g.InvalidMoney, g.CurrencyMismatch,
            g.InvalidDateRange, g.DuplicateMember, g.UnknownMember,
            g.CheckInLimitExceeded]:
    assert issubclass(cls, g.GymError)"
}

run_repository_checks() {
  local core_dir="$1"
  echo "Testing the repository in ${core_dir} (JSON round trip) ..."

  check_repo "save then load returns an identical club" "${core_dir}" \
    "from datetime import date
basic = g.Plan(g.PlanTier.BASIC, g.Money(2900, 'EUR'))
plus = g.Plan(g.PlanTier.PLUS, g.Money(4900, 'EUR'))
club = g.Club('Northside Gym')
club.enroll(g.Member(g.MembershipNumber('GYM-0001'), 'Ada', date(2026, 1, 15), basic))
club.enroll(g.Member(g.MembershipNumber('GYM-0002'), 'Grace', date(2026, 2, 1), plus))
club.check_in(g.MembershipNumber('GYM-0001'), date(2026, 4, 3))
club.check_in(g.MembershipNumber('GYM-0001'), date(2026, 4, 5))
repo = JsonClubRepository('club.json')
repo.save(club)
back = repo.load()
assert back.name == club.name
assert back.roster() == club.roster()
assert back.monthly_revenue() == club.monthly_revenue()
ada = back.find(g.MembershipNumber('GYM-0001'))
assert ada.name == 'Ada' and ada.joined_on == date(2026, 1, 15)
assert ada.check_ins_in_month(2026, 4) == 2
assert ada.plan == basic"

  check_repo "loading validates: a hand-edited bad file is refused" "${core_dir}" \
    "import json
from datetime import date
basic = g.Plan(g.PlanTier.BASIC, g.Money(2900, 'EUR'))
club = g.Club('Northside Gym')
club.enroll(g.Member(g.MembershipNumber('GYM-0001'), 'Ada', date(2026, 1, 15), basic))
repo = JsonClubRepository('club.json')
repo.save(club)
raw = json.loads(open('club.json', encoding='utf-8').read())
raw['members'][0]['plan']['price_cents'] = -1
open('club.json', 'w', encoding='utf-8').write(json.dumps(raw))
try:
    repo.load()
except g.InvalidMoney:
    pass
else:
    raise SystemExit(1)"

  check_repo "the JSON on disk is plain, readable data" "${core_dir}" \
    "import json
from datetime import date
basic = g.Plan(g.PlanTier.BASIC, g.Money(2900, 'EUR'))
club = g.Club('Northside Gym')
club.enroll(g.Member(g.MembershipNumber('GYM-0001'), 'Ada', date(2026, 1, 15), basic))
JsonClubRepository('club.json').save(club)
raw = json.loads(open('club.json', encoding='utf-8').read())
assert raw['club'] == 'Northside Gym'
assert raw['members'][0]['number'] == 'GYM-0001'
assert raw['members'][0]['plan'] == {'tier': 'basic', 'price_cents': 2900, 'currency': 'EUR'}"
}

run_demo_check() {
  local demo="$1" label="$2" work_dir out code
  work_dir="$(mktemp -d "${TMPDIR:-/tmp}/gym-demo.XXXXXX")"
  out="$(cd "${work_dir}" && python3 "${demo}" club.json 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ] \
    && printf '%s' "${out}" | grep -qF 'monthly revenue: 107.00 EUR' \
    && printf '%s' "${out}" | grep -qF 'round trip intact: True' \
    && printf '%s' "${out}" | grep -qF 'CheckInLimitExceeded' \
    && ! printf '%s' "${out}" | grep -qF 'NOT REFUSED'; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (exit ${code}; output: ${out})"
  fi
  rm -rf "${work_dir}"
}

# --- Reference: always tested strictly -------------------------------------
run_model_checks "${lab_dir}/examples"
run_repository_checks "${lab_dir}/examples"

echo "Testing the boundary (the core must not be able to do I/O) ..."
check_purity "${lab_dir}/examples/gym_core.py" "examples/gym_core.py imports nothing that does I/O"
run_demo_check "${lab_dir}/examples/demo.py" "examples/demo.py runs end to end and exits 0"

# --- Learner starter --------------------------------------------------------
echo "Testing starter/ ..."
starter_core="${lab_dir}/starter/gym_core.py"
starter_repo="${lab_dir}/starter/gym_repository.py"

for f in "${starter_core}" "${starter_repo}"; do
  if python3 -c "compile(open('${f}').read(), '${f}', 'exec')" 2>/dev/null; then
    check "$(basename "${f}") is valid Python" "yes"
  else
    check "$(basename "${f}") is valid Python" "no"
  fi
done

check_purity "${starter_core}" "starter/gym_core.py imports nothing that does I/O"

if grep -q 'NotImplementedError' "${starter_core}" || grep -q 'NotImplementedError' "${starter_repo}"; then
  echo "Note: starter/ still has unfinished exercises — testing structure only."
  for name in MembershipNumber Money DateRange Plan CheckIn Member Club; do
    if grep -q "^class ${name}\|^class ${name}(" "${starter_core}"; then
      check "starter defines ${name}" "yes"
    else
      check "starter defines ${name}" "no"
    fi
  done
  if grep -q 'class JsonClubRepository' "${starter_repo}"; then
    check "starter defines JsonClubRepository" "yes"
  else
    check "starter defines JsonClubRepository" "no"
  fi
else
  run_model_checks "${lab_dir}/starter"
  run_repository_checks "${lab_dir}/starter"
  run_demo_check "${lab_dir}/starter/demo.py" "starter/demo.py runs end to end and exits 0"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
