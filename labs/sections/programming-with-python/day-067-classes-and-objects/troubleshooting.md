# Troubleshooting — Day 067 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the five numbered exercises in
`starter/account.py`. Each unfinished method raises `NotImplementedError` on
purpose so you cannot mistake an empty method for a working one. Replace
each `raise NotImplementedError(...)` line with the body described in the
docstring above it. Once all of them are done, the test suite stops checking
structure and holds your class to the same standard as the reference.

## `TypeError: __init__() takes 2 positional arguments but 3 were given`

You wrote `def __init__(self, owner)` but called `Account('ada', 100)`, or
you forgot `self` entirely. Every method defined inside a class takes the
instance as its first parameter, conventionally named `self`, and Python
supplies it for you. `Account('ada', 100)` calls
`Account.__init__(new_object, 'ada', 100)` — three arguments, so the
signature needs three parameters.

## `NameError: name 'self' is not defined`

`self` only exists inside a method body, because it is that method's first
parameter. If you are seeing this at class level (between the methods), you
have written code that runs when the class is *defined*, not when an
instance is created. Move it inside `__init__`.

## `AttributeError: 'Account' object has no attribute 'history'`

You referenced `self.history` before anything assigned it. Instance
attributes come into existence when they are assigned, which is what
`__init__` is for: `self.history = []`. If you deleted the class-level
`history = []` (exercise 2) without adding the line in `__init__`, this is
exactly the error you get.

## `RecursionError: maximum recursion depth exceeded` after adding the property

Inside a property getter or setter, never touch the property's own name. This
loops forever, because the assignment calls the setter again:

```python
@balance.setter
def balance(self, value):
    self.balance = value        # calls this same setter, forever
```

Store the value under a different, underscore-prefixed name, and have the
getter return that:

```python
@balance.setter
def balance(self, value):
    self._balance = value       # correct: a plain instance attribute
```

## My property setter never runs

Two common causes. First, the `@property` getter must be defined *before*
the `@name.setter` block, and the setter must be decorated with the
property's own name (`@balance.setter`, not `@property`). Second, if you
assign to `self._balance` inside `__init__` instead of `self.balance`, you
bypass the setter and its validation — assign to the public name so the
validation runs at construction time too.

## One account's deposit shows up in another account's history

That is the shared mutable class attribute bug, and finding it is exercise 2.
A list written at class level (`history = []` between the methods) is created
once, when the class is defined, and every instance reaches the same object.
Run `python3 examples/shared_bug.py` to see it isolated, then create the list
inside `__init__` (`self.history = []`) so each instance gets its own.

## `ModuleNotFoundError: No module named 'account'`

The one-line commands in the starter and in `starter/inspection-notes.md`
begin with `sys.path.insert(0, 'starter')`, which only works when you run
them **from the lab directory** (the one containing `starter/` and
`examples/`). Check with `pwd`. Running a script by its path
(`python3 examples/machinery.py`) works from here too, because Python adds
the script's own directory to the import path automatically.

## Printing an object shows `<account.Account object at 0x104f3a2d0>`

That is Python's default representation, and the hex number is a memory
address that changes on every run. It means the class has no `__repr__` yet —
which is exercise 3. Add one that shows the state you actually care about,
and the same object prints as `Account(owner='ada', balance=120.00)`.

## `TypeError: from_csv_row() missing 1 required positional argument`

You defined `from_csv_row` with `@staticmethod` instead of `@classmethod`,
or you wrote `def from_csv_row(row)` without `cls`. A classmethod receives
the class itself as its first argument, named `cls` by convention, and calls
`cls(...)` to build the instance.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows: `bash tests/run_tests.sh`.
You do not need to `chmod +x` anything.
