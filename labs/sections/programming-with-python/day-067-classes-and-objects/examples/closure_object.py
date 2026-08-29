"""Build a minimal object system from scratch, with dicts and closures.

A class is not a new kind of thing in the language; it is state plus
functions-that-share-that-state, with syntax on top. Here is the same
account built twice: once by hand (a dict of closures over a captured
variable, using only Day 58 knowledge) and once with `class`.

Run it:

    python3 examples/closure_object.py
"""


def make_account(owner, balance=0.0):
    """Return a dict of closures that all share one hidden `state` dict.

    This IS an object: `state` is the instance's private attribute storage,
    and the returned dict is the method table. There is no `class` keyword
    anywhere, and no `self` -- the closure captures the state instead.
    """
    state = {"owner": owner, "balance": float(balance), "history": []}

    def deposit(amount):
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        state["balance"] += float(amount)
        state["history"].append(("deposit", float(amount)))
        return state["balance"]

    def withdraw(amount):
        if amount <= 0:
            raise ValueError("withdrawal amount must be positive")
        if amount > state["balance"]:
            raise ValueError("insufficient funds")
        state["balance"] -= float(amount)
        state["history"].append(("withdraw", float(amount)))
        return state["balance"]

    def describe():
        return f"{state['owner']}: {state['balance']:.2f} ({len(state['history'])} entries)"

    return {"deposit": deposit, "withdraw": withdraw, "describe": describe,
            "state": state}


class ClassAccount:
    """The same thing, with the language doing the wiring for you."""

    def __init__(self, owner, balance=0.0):
        self.owner = owner
        self.balance = float(balance)
        self.history = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        self.balance += float(amount)
        self.history.append(("deposit", float(amount)))
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= float(amount)
        self.history.append(("withdraw", float(amount)))
        return self.balance

    def describe(self):
        return f"{self.owner}: {self.balance:.2f} ({len(self.history)} entries)"


def main():
    print("--- hand-built object (dicts + closures, no class keyword) ---")
    hand = make_account("ada", 100)
    hand["deposit"](50)
    hand["withdraw"](30)
    print("describe():", hand["describe"]())
    print("method table keys:", sorted(hand))
    print("hidden state:", hand["state"])
    print("each call needs its dict:  hand['deposit'](50)")

    print()
    print("--- the same thing with `class` ---")
    sugar = ClassAccount("ada", 100)
    sugar.deposit(50)
    sugar.withdraw(30)
    print("describe():", sugar.describe())
    print("method table keys:",
          sorted(n for n in vars(ClassAccount) if not n.startswith("__")))
    print("hidden state:", vars(sugar))
    print("each call finds its object: sugar.deposit(50)")

    print()
    print("--- same answers, different amount of sugar ---")
    print("outputs identical:", hand["describe"]() == sugar.describe())
    print("hand-built keeps state in a captured dict; the class keeps it in "
          "the instance __dict__")
    print("hand-built copies every function per account; the class stores "
          "one function per method, shared")
    print("two hand-built accounts share no functions:",
          make_account('x')['deposit'] is make_account('y')['deposit'])
    print("two class instances share one function:",
          ClassAccount('x').deposit.__func__ is ClassAccount('y').deposit.__func__)


if __name__ == "__main__":
    main()
