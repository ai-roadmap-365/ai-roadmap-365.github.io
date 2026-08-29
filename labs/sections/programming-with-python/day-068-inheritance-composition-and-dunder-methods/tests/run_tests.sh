#!/usr/bin/env bash
# Tests for the Day 068 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# These checks exercise real behaviour, not file existence: a subclass that
# skips super().__init__() is constructed and the resulting AttributeError is
# caught in the method where it actually surfaces, a real diamond is built and
# its __mro__ compared against the C3 answer, an inconsistent hierarchy is
# rejected by the interpreter, a collaborator is swapped at runtime, and the
# container class is driven through len(), indexing, slicing, iteration,
# membership, equality, hashing and sorted() using nothing but builtins.
# Every check runs in a throwaway temporary directory that is removed
# afterwards. No network, no privileges, non-interactive. Exits 0 only if
# every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0

scratch="$(mktemp -d -t day068-tests.XXXXXX)"
cleanup() { rm -rf "${scratch}"; }
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

# check_kitchen <label> <kitchen_dir> <python-body>
# Runs an assertion body against the kitchen module imported from kitchen_dir.
# A clean exit (every assert passed) is a pass.
check_kitchen() {
  local label="$1" kitchen_dir="$2" body="$3"
  local out
  if out="$(PYTHONPATH="${kitchen_dir}" python3 -c "
from kitchen import Dish, Menu, build_menus
lunch, dinner, copy = build_menus()
${body}" 2>&1)"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (${out##*$'\n'})"
  fi
}

# check_script <label> <script> <needle>
# Runs an example script and asserts it exits 0 and its output contains a
# literal string.
check_script() {
  local label="$1" script="$2" needle="$3"
  local out code
  out="$(cd "${lab_dir}" && python3 "${script}" 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ] && printf '%s' "${out}" | grep -qF "${needle}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (exit ${code}; wanted \"${needle}\")"
  fi
}

# --- 1. Inheritance and super() -----------------------------------------
echo "Testing inheritance, super(), and what breaks without it ..."

check_script "1. broken subclass raises AttributeError for the parent's attribute" \
  "examples/01_inheritance_super.py" \
  "AttributeError: 'BrokenOven' object has no attribute 'name'"

check_script "1b. the fixed subclass produces the extended description" \
  "examples/01_inheritance_super.py" "Deck oven (3200W), 60L"

# The failure must appear in describe(), NOT in __init__ — that displacement
# is the actual lesson, so assert on the frame, not just the message.
if out="$(cd "${lab_dir}" && PYTHONPATH="examples" python3 -c "
import importlib.util, traceback
spec = importlib.util.spec_from_file_location('m', 'examples/01_inheritance_super.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
oven = m.BrokenOven('Deck oven', 3200, 60)
assert oven.capacity_litres == 60, 'construction itself must succeed'
try:
    oven.describe()
except AttributeError:
    tb = traceback.format_exc()
    assert 'in describe' in tb, 'failure must surface in describe()'
    assert 'in __init__' not in tb, 'the constructor must NOT be in the traceback'
else:
    raise SystemExit('describe() should have raised')
" 2>&1)"; then
  check "1c. construction succeeds; the failure surfaces in describe(), not __init__" "yes"
else
  check "1c. construction succeeds; the failure surfaces in describe(), not __init__" "no"
  echo "    (${out##*$'\n'})"
fi

if out="$(cd "${lab_dir}" && python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('m', 'examples/01_inheritance_super.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
fixed = m.FixedOven('Deck oven', 3200, 60)
assert fixed.name == 'Deck oven' and fixed.watts == 3200, 'parent setup missing'
assert fixed.describe() == 'Deck oven (3200W), 60L', fixed.describe()
assert [c.__name__ for c in m.FixedOven.__mro__] == ['FixedOven', 'Appliance', 'object']
" 2>&1)"; then
  check "1d. super().__init__() restores name and watts and extends describe()" "yes"
else
  check "1d. super().__init__() restores name and watts and extends describe()" "no"
  echo "    (${out##*$'\n'})"
fi

# --- 2. The MRO and the diamond -----------------------------------------
echo "Testing the diamond hierarchy and C3 linearization ..."

check_script "2. the diamond MRO is ToasterOven -> Heater -> Timer -> Appliance -> object" \
  "examples/02_mro_diamond.py" \
  "ToasterOven -> Heater -> Timer -> Appliance -> object"

check_script "2b. cooperative super() chains through all four classes" \
  "examples/02_mro_diamond.py" \
  "ToasterOven: ready -> Heater: elements warming -> Timer: clock started -> Appliance: power on"

if out="$(cd "${lab_dir}" && python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('m', 'examples/02_mro_diamond.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
mro = [c.__name__ for c in m.ToasterOven.__mro__]
assert mro == ['ToasterOven', 'Heater', 'Timer', 'Appliance', 'object'], mro
assert mro.count('Appliance') == 1, 'C3 must list the shared base exactly once'
# super() in Heater reaches Timer, which Heater does not inherit from.
assert m.Timer not in m.Heater.__bases__, 'Heater must NOT inherit from Timer'
assert mro[mro.index('Heater') + 1] == 'Timer', 'super() should land on Timer'
" 2>&1)"; then
  check "2c. the shared base appears once, and Heater's super() lands on a non-parent" "yes"
else
  check "2c. the shared base appears once, and Heater's super() lands on a non-parent" "no"
  echo "    (${out##*$'\n'})"
fi

if out="$(cd "${lab_dir}" && python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('m', 'examples/02_mro_diamond.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
try:
    type('Impossible', (m.Appliance, m.Heater), {})
except TypeError as err:
    # Python wraps this message differently across versions, so normalise
    # whitespace before matching rather than depending on the line breaks.
    message = ' '.join(str(err).split())
    assert 'consistent method resolution order' in message, message
else:
    raise SystemExit('an inconsistent hierarchy should have been rejected')
" 2>&1)"; then
  check "2d. an inconsistent hierarchy is refused at class-definition time" "yes"
else
  check "2d. an inconsistent hierarchy is refused at class-definition time" "no"
  echo "    (${out##*$'\n'})"
fi

# --- 3. Composition -------------------------------------------------------
echo "Testing the composition rewrite of the same domain ..."

check_script "3. the composed oven delegates to its element and its timer" \
  "examples/03_composition.py" \
  "Deck oven: heating to 220C at 3200W; timer set to 35 min"

if out="$(cd "${lab_dir}" && python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('m', 'examples/03_composition.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
# Both designs must produce the same heating string for the same inputs.
inherited = m.InheritedOven('Deck oven', 3200, 260, 60).heat(220)
composed = m.ComposedOven('Deck oven', 3200).element.heat(220)
assert inherited == composed == 'heating to 220C at 3200W', (inherited, composed)
# The composed classes must genuinely inherit nothing.
assert m.ComposedOven.__bases__ == (object,), m.ComposedOven.__bases__
assert m.ComposedToaster.__bases__ == (object,), m.ComposedToaster.__bases__
# has-a, not is-a: the collaborators are attributes.
oven = m.ComposedOven('Deck oven', 3200)
assert isinstance(oven.element, m.HeatingElement) and isinstance(oven.timer, m.Timer)
assert not isinstance(oven, m.HeatingElement), 'an Oven is not a HeatingElement'
" 2>&1)"; then
  check "3b. both designs behave identically, but the composed one inherits nothing" "yes"
else
  check "3b. both designs behave identically, but the composed one inherits nothing" "no"
  echo "    (${out##*$'\n'})"
fi

if out="$(cd "${lab_dir}" && python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('m', 'examples/03_composition.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
oven = m.ComposedOven('Deck oven', 3200)
before = oven.bake(220, 35)
oven.element = m.FanAssistedElement(3200)   # swapped at RUNTIME
after = oven.bake(220, 35)
assert 'heating to' in before and 'fan-assisted to' in after, (before, after)
assert before != after, 'swapping the collaborator must change the behaviour'
" 2>&1)"; then
  check "3c. a collaborator can be swapped at runtime with no class edited" "yes"
else
  check "3c. a collaborator can be swapped at runtime with no class edited" "no"
  echo "    (${out##*$'\n'})"
fi

# --- 5. Context manager ---------------------------------------------------
echo "Testing the context manager's cleanup guarantee ..."

check_script "5. cleanup runs and the exception still reaches the caller" \
  "examples/05_context_manager.py" "caught: burnt the souffle | open = False"

# --- 6. Abstract base class -----------------------------------------------
echo "Testing the abstract base class and duck typing ..."

# Match on the class name only: the rest of this sentence was reworded
# between Python versions (see requirements/README.md). The method name is
# asserted separately in 6c via __abstractmethods__.
check_script "6. an incomplete subclass is refused at construction, by name" \
  "examples/06_abstract_base.py" \
  "TypeError: Can't instantiate abstract class PastryStation"

check_script "6b. the complete subclass works through the template method" \
  "examples/06_abstract_base.py" "Grill: grilling mackerel over charcoal"

if out="$(cd "${lab_dir}" && python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('m', 'examples/06_abstract_base.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
assert m.PastryStation.__abstractmethods__ == frozenset({'prepare'}), \
    m.PastryStation.__abstractmethods__
try:
    m.Station('any')
except TypeError:
    pass
else:
    raise SystemExit('the ABC itself must not be instantiable')
" 2>&1)"; then
  check "6c. the ABC itself is not instantiable and names its outstanding method" "yes"
else
  check "6c. the ABC itself is not instantiable and names its outstanding method" "no"
  echo "    (${out##*$'\n'})"
fi

# --- 4. The container class: the protocol checks -------------------------
run_kitchen_checks() {
  local dir="$1"
  echo "Testing the container class in ${dir} (builtins only, nothing patched) ..."

  check_kitchen "4. len(menu) calls __len__" "${dir}" "
assert len(lunch) == 3, len(lunch)
assert len(dinner) == 2, len(dinner)
assert len(Menu('Empty')) == 0
"

  check_kitchen "4b. menu[i] and menu[i:j] call __getitem__ (slicing comes free)" "${dir}" "
assert lunch[0] == Dish('Ramen', 12), lunch[0]
assert lunch[-1] == Dish('Salad', 4), lunch[-1]
assert lunch[1:3] == [Dish('Gyoza', 8), Dish('Salad', 4)], lunch[1:3]
try:
    lunch[99]
except IndexError:
    pass
else:
    raise SystemExit('an out-of-range index should raise IndexError')
"

  check_kitchen "4c. a for loop calls __iter__, and two loops both start over" "${dir}" "
names = [d.name for d in lunch]
assert names == ['Ramen', 'Gyoza', 'Salad'], names
assert [d.name for d in lunch] == names, 'a second loop must restart, not exhaust'
assert list(lunch) == lunch.dishes, 'list() must consume __iter__'
"

  check_kitchen "4d. 'x in menu' calls __contains__ for both names and Dishes" "${dir}" "
assert ('Ramen' in lunch) is True
assert ('Duck' in lunch) is False
assert (Dish('Gyoza', 8) in lunch) is True
assert ('Duck' in dinner) is True
"

  check_kitchen "4e. __eq__ compares contents and defers on unknown types" "${dir}" "
assert (lunch == copy) is True, 'equal dishes must compare equal'
assert lunch is not copy, 'they must be distinct objects'
assert (lunch == dinner) is False
assert (lunch == 'Lunch') is False, 'comparing to a str must be False, not an error'
assert Menu.__eq__(lunch, 'Lunch') is NotImplemented, \
    '__eq__ must return NotImplemented for unknown types, not False'
"

  check_kitchen "4f. __hash__ survives __eq__, so menus work in sets and dicts" "${dir}" "
assert Menu.__hash__ is not None, 'defining __eq__ without __hash__ breaks sets'
assert hash(lunch) == hash(copy), 'equal objects must hash equal'
assert len({lunch, copy, dinner}) == 2, 'the set must collapse the two equal menus'
assert {lunch: 'x'}[copy] == 'x', 'an equal menu must find the same dict entry'
"

  check_kitchen "4g. sorted() and max() work using only __lt__ and @total_ordering" "${dir}" "
assert lunch.total_minutes() == 24 and dinner.total_minutes() == 52
assert sorted([dinner, lunch]) == [lunch, dinner], 'sorted must use __lt__'
assert (dinner < lunch) is False and (lunch < dinner) is True
# total_ordering derives these three from __lt__ plus __eq__:
assert (dinner >= lunch) is True
assert (dinner > lunch) is True
assert (lunch <= dinner) is True
assert max([dinner, lunch]) is dinner, 'max must use the ordering'
assert max([dinner, lunch], key=len) is lunch, 'key=len must use __len__'
"

  check_kitchen "4h. iteration protocol feeds max(), sum() and comprehensions" "${dir}" "
assert max(lunch, key=lambda d: d.minutes) == Dish('Ramen', 12)
assert sum(d.minutes for d in lunch) == 24
assert sorted(d.name for d in lunch) == ['Gyoza', 'Ramen', 'Salad']
"

  check_kitchen "4i. the context manager opens, closes, and closes again on failure" "${dir}" "
m = Menu('Service', [Dish('Waffles', 9)])
with m as service:
    assert service is m, '__enter__ must return the object bound by as'
    assert m.open is True
assert m.open is False, '__exit__ must run after a normal exit'
try:
    with m:
        raise ValueError('kitchen fire')
except ValueError as err:
    assert str(err) == 'kitchen fire', 'returning False must not swallow it'
else:
    raise SystemExit('__exit__ returned True and swallowed the exception')
assert m.open is False, '__exit__ must run after a raising exit too'
"

  check_kitchen "4j. Dish equality and hashing behave as the pattern for Menu" "${dir}" "
assert Dish('Ramen', 12) == Dish('Ramen', 12)
assert Dish('Ramen', 12) != Dish('Ramen', 13)
assert hash(Dish('Ramen', 12)) == hash(Dish('Ramen', 12))
assert Dish.__eq__(Dish('Ramen', 12), 'Ramen') is NotImplemented
assert len({Dish('Ramen', 12), Dish('Ramen', 12)}) == 1
"
}

# --- Reference: always tested strictly ---
run_kitchen_checks "${lab_dir}/examples"

echo "Testing examples/kitchen.py end to end ..."
check_script "4k. the reference demo reports the collapsed set of menus" \
  "examples/kitchen.py" "set of menus: 2"

# --- Learner starter ---
echo "Testing starter/kitchen.py ..."
starter_kitchen="${lab_dir}/starter/kitchen.py"
if python3 -c "compile(open('${starter_kitchen}').read(), '${starter_kitchen}', 'exec')" 2>/dev/null; then
  check "starter kitchen.py is valid Python" "yes"
else
  check "starter kitchen.py is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter_kitchen}"; then
  echo "Note: starter/kitchen.py still has unfinished exercises — testing structure only."
  for name in __len__ __getitem__ __iter__ __contains__ __eq__ __hash__ __lt__ \
              __enter__ __exit__; do
    if grep -q "def ${name}" "${starter_kitchen}"; then
      check "starter defines ${name}" "yes"
    else
      check "starter defines ${name}" "no"
    fi
  done
else
  run_kitchen_checks "${lab_dir}/starter"
  check_script "starter demo reports the collapsed set of menus" \
    "starter/kitchen.py" "set of menus: 2"
  # A __contains__ that secretly rebuilds a list is not what was asked for,
  # but an __iter__ that returns the list itself is an outright bug: a list
  # is iterable, not an iterator, so nested loops would misbehave.
  if PYTHONPATH="${lab_dir}/starter" python3 -c "
from kitchen import Menu, Dish
m = Menu('x', [Dish('a', 1)])
it = iter(m)
assert iter(it) is it, '__iter__ must return an iterator, not the list'
" 2>/dev/null; then
    check "starter __iter__ returns a real iterator" "yes"
  else
    check "starter __iter__ returns a real iterator" "no"
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
