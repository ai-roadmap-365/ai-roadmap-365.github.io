"""The classic mutable-class-attribute bug, reproduced and then fixed.

A list written at class level belongs to the CLASS, not to any instance, so
every instance mutates the same list. Run it:

    python3 examples/shared_bug.py
"""


class BuggyAccount:
    """BUG ON PURPOSE: history is created once, at class-definition time."""

    history = []  # one list, shared by every instance ever created

    def __init__(self, owner):
        self.owner = owner

    def deposit(self, amount):
        # self.history finds no instance attribute, so it falls back to the
        # CLASS attribute -- and .append() mutates that one shared list.
        self.history.append((self.owner, amount))


class FixedAccount:
    """FIXED: the list is created inside __init__, once per instance."""

    def __init__(self, owner):
        self.owner = owner
        self.history = []  # a fresh list, bound to THIS instance

    def deposit(self, amount):
        self.history.append((self.owner, amount))


def main():
    print("--- buggy: one list shared by every instance ---")
    ada = BuggyAccount("ada")
    bob = BuggyAccount("bob")
    ada.deposit(10)
    bob.deposit(20)
    print("ada.history:", ada.history)
    print("bob.history:", bob.history)
    print("same list object?", ada.history is bob.history)
    print("it lives on the class:", BuggyAccount.history)
    print("instance __dict__ of ada:", vars(ada))

    print()
    print("--- fixed: one list per instance ---")
    cleo = FixedAccount("cleo")
    dev = FixedAccount("dev")
    cleo.deposit(10)
    dev.deposit(20)
    print("cleo.history:", cleo.history)
    print("dev.history:", dev.history)
    print("same list object?", cleo.history is dev.history)
    print("instance __dict__ of cleo:", vars(cleo))


if __name__ == "__main__":
    main()
