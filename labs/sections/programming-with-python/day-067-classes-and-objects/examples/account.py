"""The 'after' version: one class binding the state to the behaviour.

Same program as account_dict.py, expressed as a class. The state (owner,
balance, history) and the rules that keep it valid now live in one named
thing, and the balance can no longer be set to a negative number by anyone,
inside the class or outside it.

Run it directly to see the same session as the dict version:

    python3 examples/account.py
"""


class Account:
    """A bank account: an owner, a balance, and a history of movements.

    Invariant (the rule this class exists to keep): the balance is never
    negative, and every movement is recorded in *this instance's own*
    history list.
    """

    currency = "USD"        # class attribute: one value shared by every account
    accounts_opened = 0     # class attribute: a counter, rebound (not mutated)

    def __init__(self, owner, balance=0.0):
        """Initialize an account that Python has already created for us."""
        self.owner = owner
        self.balance = balance      # goes through the property setter below
        self.history = []           # a FRESH list for every instance
        Account.accounts_opened += 1

    # --- the property: a computed, validated attribute -------------------
    @property
    def balance(self):
        """The current balance. Assigning a negative value is rejected."""
        return self._balance

    @balance.setter
    def balance(self, value):
        amount = float(value)
        if amount < 0:
            raise ValueError(f"balance cannot be negative (got {amount:.2f})")
        self._balance = amount

    # --- a staticmethod: a rule that needs neither instance nor class ----
    @staticmethod
    def is_valid_amount(amount):
        """True when amount is a positive number. Takes no self and no cls."""
        return isinstance(amount, (int, float)) and amount > 0

    # --- a classmethod: an alternative constructor -----------------------
    @classmethod
    def from_csv_row(cls, row):
        """Build an account from one CSV line: 'ada,120.50' (ties to Day 65)."""
        parts = [field.strip() for field in row.split(",")]
        if len(parts) != 2:
            raise ValueError(f"expected 'owner,balance', got {row!r}")
        owner, balance = parts
        return cls(owner, float(balance))

    # --- ordinary methods: behaviour that maintains the invariant --------
    def deposit(self, amount):
        """Add a positive amount, record it, and return the new balance."""
        if not self.is_valid_amount(amount):
            raise ValueError("deposit amount must be positive")
        self.balance = self.balance + amount
        self.history.append(("deposit", float(amount)))
        return self.balance

    def withdraw(self, amount):
        """Remove a positive amount the balance can cover."""
        if not self.is_valid_amount(amount):
            raise ValueError("withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance = self.balance - amount
        self.history.append(("withdraw", float(amount)))
        return self.balance

    def describe(self):
        """A one-line human summary, the same text the dict version prints."""
        return f"{self.owner}: {self.balance:.2f} ({len(self.history)} entries)"

    def __repr__(self):
        """What you see in the debugger and the REPL. Every class deserves one."""
        return f"Account(owner={self.owner!r}, balance={self.balance:.2f})"


def main():
    ada = Account("ada", 100)
    ada.deposit(50)
    ada.withdraw(30)
    print(ada.describe())
    try:
        ada.withdraw(1000)
    except ValueError as err:
        print(f"rejected: {err}")
    # The direct edit that broke the dict version is refused here.
    try:
        ada.balance = -500
    except ValueError as err:
        print(f"rejected: {err}")
    print("after the refused edit:", ada.describe())
    print("repr:", repr(ada))


if __name__ == "__main__":
    main()
