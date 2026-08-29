"""Step 1: break inheritance on purpose, then fix it.

A subclass that defines __init__ REPLACES the parent's __init__. If it does
not call super().__init__(...), the parent's setup never runs. The object is
still created — it is just incomplete, and the failure surfaces later in some
unrelated method, blaming a missing attribute instead of the constructor that
never ran. That displacement is the whole point of this script.

Run it:  python3 examples/01_inheritance_super.py
"""

import traceback


class Appliance:
    """The base class. It owns `name` and `watts`."""

    def __init__(self, name, watts):
        self.name = name
        self.watts = watts

    def describe(self):
        return f"{self.name} ({self.watts}W)"


class BrokenOven(Appliance):
    """A two-level hierarchy with the super() call deliberately missing."""

    def __init__(self, name, watts, capacity_litres):
        # BUG ON PURPOSE: no super().__init__(name, watts) here, so `name`
        # and `watts` are never set on this instance.
        self.capacity_litres = capacity_litres

    def describe(self):
        # Extending: override, but still call the parent through super().
        return f"{super().describe()}, {self.capacity_litres}L"


class FixedOven(Appliance):
    """The same class with the one missing line restored."""

    def __init__(self, name, watts, capacity_litres):
        super().__init__(name, watts)  # THE FIX: run the parent's setup first
        self.capacity_litres = capacity_litres

    def describe(self):
        return f"{super().describe()}, {self.capacity_litres}L"


def main():
    print("-- broken: subclass __init__ never calls super().__init__() --")
    oven = BrokenOven("Deck oven", 3200, 60)
    # Note that construction SUCCEEDED. Nothing raised yet.
    print(f"constructed fine: {type(oven).__name__}, capacity_litres = "
          f"{oven.capacity_litres}")
    try:
        oven.describe()
    except AttributeError as err:
        # Print only the final line, so the output is stable across machines.
        print(f"AttributeError: {err}")
        print("    ^ raised inside describe(), NOT inside __init__ —")
        print("      the constructor left the object incomplete and moved on.")
        # The full traceback shows both frames; kept short on purpose.
        frames = traceback.format_exc().strip().splitlines()
        print(f"    (traceback frames: {sum(1 for f in frames if 'File ' in f)})")

    print()
    print("-- fixed: super().__init__(name, watts) restores the parent's setup --")
    fixed = FixedOven("Deck oven", 3200, 60)
    print(fixed.describe())
    print(f"attributes now present: name={fixed.name!r}, watts={fixed.watts}")
    print(f"MRO: {' -> '.join(c.__name__ for c in FixedOven.__mro__)}")


if __name__ == "__main__":
    main()
