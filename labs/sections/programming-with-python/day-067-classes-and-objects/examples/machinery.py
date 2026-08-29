"""Open the hood: type(), vars(), __dict__, dir(), and bound methods.

Nothing here is magic. A class is an object holding functions; an instance
is an object holding its own attribute dict; attribute lookup checks the
instance first and the class second. Run it:

    python3 examples/machinery.py

Note: this script never prints id() values or a default repr, because those
contain a memory address that changes on every run. It prints comparisons
instead, so the output is identical every time.
"""

from account import Account


class Card:
    """A tiny class showing the two encapsulation conventions side by side."""

    def __init__(self, holder, pin):
        self._holder = holder   # single underscore: "internal, please leave alone"
        self.__pin = pin        # double underscore: renamed by the compiler

    def check(self, guess):
        return guess == self.__pin


def main():
    ada = Account("ada", 100)
    bob = Account("bob", 100)

    print("--- two instances, one class ---")
    print("type(ada):", type(ada).__name__)
    print("type(Account):", type(Account).__name__)
    print("ada is bob:", ada is bob)
    print("id(ada) == id(bob):", id(ada) == id(bob))
    print("type(ada) is type(bob):", type(ada) is type(bob))
    print("ada == bob (no __eq__ defined, so identity is used):", ada == bob)

    print()
    print("--- state lives on the instance ---")
    ada.deposit(50)
    print("vars(ada):", vars(ada))
    print("vars(bob):", vars(bob))
    print("ada.__dict__ is vars(ada):", ada.__dict__ is vars(ada))
    print("'history' in ada.__dict__:", "history" in ada.__dict__)
    print("'deposit' in ada.__dict__:", "deposit" in ada.__dict__)

    print()
    print("--- behaviour lives on the class ---")
    print("class attributes and methods:")
    for name in sorted(vars(Account)):
        if not name.startswith("__"):
            print("   ", name, "->", type(vars(Account)[name]).__name__)
    print("Account.currency:", Account.currency)
    print("ada.currency (found on the class):", ada.currency)
    print("'currency' in ada.__dict__:", "currency" in ada.__dict__)

    print()
    print("--- a method call is a function call with self supplied ---")
    print("type(Account.deposit):", type(Account.deposit).__name__)
    print("type(ada.deposit):", type(ada.deposit).__name__)
    print("ada.deposit.__self__ is ada:", ada.deposit.__self__ is ada)
    print("ada.deposit.__func__ is Account.deposit:",
          ada.deposit.__func__ is Account.deposit)
    before = ada.balance
    Account.deposit(ada, 10)          # the unsugared form
    print(f"Account.deposit(ada, 10) moved the balance {before:.2f} -> {ada.balance:.2f}")

    print()
    print("--- name mangling and the property ---")
    print("'_balance' in ada.__dict__:", "_balance" in ada.__dict__)
    print("type(Account.balance):", type(Account.balance).__name__)
    print("Account.__dict__['is_valid_amount'] type:",
          type(Account.__dict__["is_valid_amount"]).__name__)
    print("Account.__dict__['from_csv_row'] type:",
          type(Account.__dict__["from_csv_row"]).__name__)
    card = Card("ada", "1234")
    print("vars(card):", vars(card))
    print("card.check('1234'):", card.check("1234"))
    print("hasattr(card, '__pin'):", hasattr(card, "__pin"))
    print("hasattr(card, '_Card__pin'):", hasattr(card, "_Card__pin"))

    print()
    print("--- the alternative constructor ---")
    cleo = Account.from_csv_row("cleo, 250.00")
    print("from_csv_row ->", repr(cleo))
    print("built by the same class:", type(cleo) is Account)


if __name__ == "__main__":
    main()
