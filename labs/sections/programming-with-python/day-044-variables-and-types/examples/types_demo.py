#!/usr/bin/env python3
"""Day 044 lab — a working tour of Python's core data model.

Run it with:  python3 examples/types_demo.py

It demonstrates, in order:
  1. A value of each core built-in type, printed with its type().
  2. Dynamic typing: one name re-bound to a different type.
  3. Mutability: a list mutated in place (id unchanged) versus a string
     "modified" (id changes because a new object is made).
  4. Safe type conversion with try/except so bad input is handled, not fatal.

Nothing here needs the network or any third-party package — only the
standard Python 3 interpreter you installed on Day 43.
"""


def show_core_types():
    """Assign one value of each core type and print each with its type()."""
    print("--- Core types ---")
    count = 42          # int   — a whole number
    price = 19.99       # float — a number with a fractional part
    is_open = True      # bool  — a truth value
    label = "widget"    # str   — text
    missing = None      # NoneType — the deliberate "no value" object

    # type(x).__name__ gives the short type name, e.g. 'int' instead of
    # "<class 'int'>", which reads more cleanly in a report.
    for name, value in [
        ("count", count),
        ("price", price),
        ("is_open", is_open),
        ("label", label),
        ("missing", missing),
    ]:
        print(f"{name:<10} = {str(value):<13} type = {type(value).__name__}")


def show_dynamic_typing():
    """Re-bind one name to a value of a different type — legal in Python."""
    print("\n--- Dynamic typing ---")
    thing = 100                       # thing points at an int
    print(f"thing = {thing} ({type(thing).__name__})")
    thing = "hello"                   # now it points at a str
    print(f"thing = {thing} ({type(thing).__name__})   <- same name, different type")


def show_mutability():
    """Show a list mutating in place (same id) vs a string making a new object."""
    print("\n--- Mutability ---")

    numbers = [1, 2, 3]
    id_before = id(numbers)
    numbers.append(4)                 # mutate the SAME list object in place
    print(f"list before: [1, 2, 3]  id unchanged after append: {id(numbers) == id_before}")

    text = "cat"
    id_before = id(text)
    text = text + "s"                 # builds a NEW string; text is re-bound
    print(f"str  before: cat        id changed after '+': {id(text) != id_before}")


def safe_int(raw):
    """Convert a string to an int, returning None instead of crashing on bad input."""
    try:
        return int(raw)
    except ValueError:
        return None


def show_safe_conversion():
    """Demonstrate safe type conversion with try/except ValueError."""
    print("\n--- Safe conversion ---")
    for raw in ["30", "oops"]:
        converted = safe_int(raw)
        if converted is None:
            print(f"{raw!r} -> could not convert (ValueError handled)")
        else:
            print(f"{raw!r}  -> {converted} ({type(converted).__name__})")


def main():
    show_core_types()
    show_dynamic_typing()
    show_mutability()
    show_safe_conversion()


if __name__ == "__main__":
    main()
