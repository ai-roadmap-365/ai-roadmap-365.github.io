# Troubleshooting

Symptom-by-symptom fixes for this lab. Every error message below is one you
can produce deliberately, and most of them are worth producing once on
purpose so you recognise them later.

## `AttributeError: 'X' object has no attribute 'name'` — raised in a method, not in `__init__`

**Cause.** The subclass defined its own `__init__` and never called
`super().__init__(...)`. Defining `__init__` in a subclass *replaces* the
parent's; it does not add to it. The object was constructed perfectly
happily — it is simply missing the attributes the parent's constructor would
have set, and the failure waits until something actually reads one.

**Fix.** Call the parent constructor, conventionally as the first line:

```python
def __init__(self, name, watts, capacity_litres):
    super().__init__(name, watts)      # <- the missing line
    self.capacity_litres = capacity_litres
```

**Why it is confusing.** The traceback names the method where the attribute
was read, not the constructor that failed to set it. When you see this error,
look at the constructor first, not at the line that raised.

## `TypeError: __init__() takes 3 positional arguments but 4 were given`

**Cause.** You forwarded the child's whole argument list to the parent
unchanged. The parent declares fewer parameters than the child does.

**Fix.** Pass only the arguments the parent actually declares, and keep the
child-specific ones for the child:

```python
def __init__(self, name, watts, max_celsius, capacity_litres):
    super().__init__(name, watts, max_celsius)   # not capacity_litres
    self.capacity_litres = capacity_litres
```

## `TypeError: Cannot create a consistent method resolution order (MRO) for bases ...`

**Cause.** You listed base classes in an order C3 linearization cannot
satisfy — almost always a parent listed before its own child, as in
`class X(Appliance, Heater)` where `Heater` already inherits from
`Appliance`. C3 requires that a class precede its parents, and you asked for
the opposite.

**Fix.** Reorder the bases so the more specific class comes first:
`class X(Heater, Appliance)` — or, better, ask whether you need both at all.

**Note.** Python raises this when the *class is defined*, not when an
instance is created. That is a feature: an impossible hierarchy never gets
built. `examples/02_mro_diamond.py` triggers it on purpose so you see it once.

## `TypeError: unhashable type: 'Menu'` (or `cannot use 'Menu' as a set element`)

**Cause.** You defined `__eq__`. Python then set `__hash__` to `None`,
because objects that compare equal must hash equal and the interpreter will
not guess which fields to use. Your class became unhashable the moment you
added equality, and the crash appears later, in a `set` or `dict`, far from
the class you edited.

**Fix.** Define `__hash__` over the same fields `__eq__` compares:

```python
def __hash__(self):
    return hash(tuple(self.dishes))
```

If the object is genuinely mutable and should *not* live in a set, leaving it
unhashable is a legitimate choice — but make it a decision, not an accident.

## `TypeError: '<' not supported between instances of 'Menu' and 'Menu'`

**Cause.** `sorted()`, `min()` and `max()` order things with `<`, which means
`__lt__`. You have not defined it.

**Fix.** Define `__lt__`, or pass a `key=` function to sort by something else
entirely (`sorted(menus, key=len)` needs no `__lt__` on `Menu` at all,
because it compares the integers `len` returns).

## `>=` raises `TypeError` even though `__lt__` works

**Cause.** `@total_ordering` is missing, or it is applied but `__eq__` is not
defined. The decorator derives `<=`, `>` and `>=` from `__lt__` **plus**
`__eq__` — it needs both.

**Fix.** Decorate the class with `@total_ordering` and make sure `__eq__` is
defined alongside `__lt__`.

## `RecursionError: maximum recursion depth exceeded` inside `__contains__`

**Cause.** Your `__contains__` used the `in` operator on the object itself —
`return item in self` — which calls `__contains__` again, forever.

**Fix.** Search the underlying data, not the wrapper:

```python
return any(dish.name == name for dish in self.dishes)   # not "in self"
```

The same trap catches `__len__` written as `return len(self)` and `__iter__`
written as `return iter(self)`.

## A second `for` loop over the same object finds nothing

**Cause.** `__iter__` returned an *iterator that had already been consumed*,
or returned `self` on a class that also defines `__next__` with exhausted
state. An iterator can only be walked once.

**Fix.** Return a fresh iterator every time. Delegating to the underlying
list does this correctly, because `iter(list)` builds a new iterator on each
call:

```python
def __iter__(self):
    return iter(self.dishes)
```

## `TypeError: iter() returned non-iterator of type 'list'`

**Cause.** `__iter__` returned `self.dishes` — the list itself — rather than
an iterator over it. A list is *iterable* but is not an *iterator*: it has no
`__next__`.

**Fix.** Wrap it: `return iter(self.dishes)`. The test suite checks this
specifically, with `assert iter(it) is it`.

## Comparing to an unrelated type gives a confidently wrong answer

**Cause.** Your `__eq__` returns `False` for types it does not recognise.
That looks harmless, but it stops Python from asking the other operand,
which may well know how to do the comparison.

**Fix.** Return `NotImplemented` instead. Python then tries the reflected
call on the right-hand operand, and only falls back to identity comparison
(giving `False`) if that also declines:

```python
def __eq__(self, other):
    if not isinstance(other, Menu):
        return NotImplemented       # not False
    return self.dishes == other.dishes
```

## `TypeError: Can't instantiate abstract class ...` when you did not expect it

**Cause.** The class has an outstanding `@abstractmethod`. This is the ABC
working as designed.

**Fix.** Implement the method it names. To see exactly what is outstanding:

```python
print(PastryStation.__abstractmethods__)
```

If the wording of the message on your machine differs from the capture in
`expected-output/`, that is a Python version difference and nothing is wrong
— see `requirements/README.md`.

## An abstract method is *not* enforced

**Cause.** The class does not actually inherit from `ABC` (or its metaclass
is not `ABCMeta`). `@abstractmethod` on a plain class is only documentation —
it enforces nothing on its own.

**Fix.** `class Station(ABC):`, importing `ABC` from `abc`.

## `ModuleNotFoundError: No module named 'kitchen'` from step 5

**Cause.** You ran `examples/05_context_manager.py` from a directory other
than the lab root, or copied it somewhere away from `examples/kitchen.py`.

**Fix.** Run every command from the lab directory, as the README shows:

```bash
cd labs/sections/programming-with-python/day-068-inheritance-composition-and-dunder-methods
python3 examples/05_context_manager.py
```

## `bash: tests/run_tests.sh: No such file or directory`

**Cause.** You are not in the lab directory.

**Fix.** `cd` to it first. The suite itself is location-independent once
started — it resolves the lab root from its own path — but the command has to
find it.

## The test suite says "testing structure only"

**Not a problem.** That message means `starter/kitchen.py` still contains
`NotImplementedError`, so the suite checked that the six methods exist rather
than that they behave. Complete the exercises and the full protocol checks
run against your version too, taking the suite from 36 checks to 39.

## `__exit__` runs but the exception disappears

**Cause.** `__exit__` returned a truthy value. Returning `True` tells Python
the exception has been handled, and it is swallowed silently.

**Fix.** Return `False` (or nothing at all, since `None` is falsy) unless you
genuinely intend to suppress the error. `Menu.__exit__` returns `False`
explicitly to make the choice visible.
