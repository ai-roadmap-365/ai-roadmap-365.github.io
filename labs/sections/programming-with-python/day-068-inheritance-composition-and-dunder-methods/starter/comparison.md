# Worksheet — your written answers

Fill this in as you work. Steps 2 and 3 of the lab ask for written answers,
not code, and writing them down is the part that makes the distinction stick.
Replace each `Your answer:` line with what you actually observed.

## Step 2 — predict the MRO before you run it

`class ToasterOven(Heater, Timer)`, where `Heater` and `Timer` both inherit
from `Appliance`. Write your prediction here **before** running
`python3 examples/02_mro_diamond.py`.

- My predicted MRO: `Your answer:`
- What the program actually printed: `Your answer:`
- Did they match? `Your answer:`
- If not, which C3 rule did I miss — local precedence (a class comes before
  its own parents) or monotonicity (the order bases are listed is kept)?
  `Your answer:`

`Heater.power_on` calls `super().power_on()`. Which class does that call
reach, and does `Heater` inherit from it?

- `Your answer:`

Why does `Appliance` appear only once in the MRO, and what would go wrong if
it appeared twice?

- `Your answer:`

## Step 3 — the same domain, two ways

Run `python3 examples/03_composition.py` and then answer.

Which version would you keep for a kitchen-appliance product that ships for
years, and why?

- `Your answer:`

Name one change that would be **easier** in the inheritance version:

- `Your answer:`

Name one change that would be **easier** in the composition version:

- `Your answer:`

Describe one concrete edit to `Appliance` or `HeatingAppliance` that would
break `InheritedOven` but would leave `ComposedOven` untouched. (This is the
fragile base class problem, stated in your own words.)

- `Your answer:`

Say the relationship out loud in both directions. Which of these sounds true
and which makes you wince?

- "An `Oven` **is a** `HeatingAppliance`" — `Your answer:`
- "An `Oven` **is a** `Timer`" — `Your answer:`
- "An `Oven` **has a** `Timer`" — `Your answer:`

## Step 4 — what the protocols bought you

After completing `starter/kitchen.py`, list the builtins that now work on
your `Menu` class without any of them being modified:

- `Your answer:`

You wrote only `__lt__` for ordering. Which comparison operators did
`@total_ordering` derive for you, and what else did it need in order to do
that?

- `Your answer:`

`len({lunch, copy, dinner})` prints `2`, not `3`. Explain why in one
sentence, naming both dunder methods responsible.

- `Your answer:`

## Step 5 — the context manager guarantee

In the run whose body raises `ValueError`, does `[service closed]` print
before or after the `caught:` line, and what does that ordering prove about
when `__exit__` runs?

- `Your answer:`

What would change if `Menu.__exit__` returned `True` instead of `False`?

- `Your answer:`

## Step 6 — enforcement versus duck typing

`PastryStation` raised `TypeError` at construction. Why is failing there
better than failing later, inside a call to `announce`?

- `Your answer:`

`Ticket` inherits from nothing but `object`, yet `isinstance(t, Iterable)` is
`True`. What is `isinstance` actually checking in that case?

- `Your answer:`

When would you reach for `abc.ABC`, and when would you rely on duck typing
instead?

- `Your answer:`
