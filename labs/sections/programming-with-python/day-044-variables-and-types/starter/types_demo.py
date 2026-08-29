#!/usr/bin/env python3
"""Day 044 lab — YOUR working file. Complete the four numbered exercises.

Run it with:  python3 starter/types_demo.py

Each exercise names the exact function to use. Replace every `None` marked
with an "# exercise" comment with real code, then run the file. The finished
reference version is examples/types_demo.py — try to complete this yourself
first, then compare.
"""


def exercise_1_three_types():
    """Exercise 1: create variables of THREE different types and print each
    with its type name, using type(value).__name__.

    Pick three different types (for example an int, a str, and a bool).
    Replace the three `None` values below with values of your choice, then
    the loop will print each with its type.
    """
    print("--- Exercise 1: three types ---")
    value_a = None   # exercise 1a: assign an int, e.g. 7
    value_b = None   # exercise 1b: assign a str, e.g. "hello"
    value_c = None   # exercise 1c: assign a bool, e.g. True

    for name, value in [("value_a", value_a), ("value_b", value_b), ("value_c", value_c)]:
        print(f"{name} = {value!r}  type = {type(value).__name__}")


def exercise_2_safe_conversion():
    """Exercise 2: convert the string "42" to an int SAFELY.

    Use int(...) inside a try/except ValueError. Set `result` to the integer
    on success, or the string "conversion failed" if a ValueError is raised.
    Fill in the two exercise lines.
    """
    print("\n--- Exercise 2: safe conversion ---")
    raw = "42"
    result = None
    try:
        result = None   # exercise 2a: use int(raw) here
    except ValueError:
        result = None   # exercise 2b: set this to "conversion failed"
    print(f"{raw!r} converted to: {result!r}  type = {type(result).__name__}")


def exercise_3_list_is_mutable():
    """Exercise 3: show that a list is MUTABLE.

    Start from [1, 2, 3], record id() before, append the number 4, then print
    whether the id stayed the same (it should — a list mutates in place).
    Fill in the two exercise lines.
    """
    print("\n--- Exercise 3: a list is mutable ---")
    numbers = [1, 2, 3]
    id_before = id(numbers)
    # exercise 3a: append the number 4 to `numbers` using numbers.append(...)
    same_object = None   # exercise 3b: set to (id(numbers) == id_before)
    print(f"numbers is now {numbers}  same object after append: {same_object}")


def exercise_4_none_vs_zero():
    """Exercise 4: distinguish absent (None) from present-but-zero (0).

    Write a check that prints "absent" when value is None and "present"
    otherwise — even when the value is 0. Use `is not None` (NOT a plain
    truthiness test, which would wrongly call 0 absent). Fill in the exercise line.
    """
    print("\n--- Exercise 4: None vs zero ---")
    for value in [0, None, 5]:
        present = None   # exercise 4: set to (value is not None)
        label = "present" if present else "absent"
        print(f"value = {value!r}  -> {label}")


def main():
    exercise_1_three_types()
    exercise_2_safe_conversion()
    exercise_3_list_is_mutable()
    exercise_4_none_vs_zero()


if __name__ == "__main__":
    main()
