"""YOUR WORKING FILE — Day 67: turn a dict + functions into a class.

The 'before' version you are converting is `examples/account_dict.py`: a
dict holding owner/balance/history plus loose functions that all take that
dict as their first argument. Your job is to bind that state and that
behaviour into one named thing.

Work through the five numbered exercises below in order. Each one names the
exact command to run when you finish it. When every exercise is done, no
`NotImplementedError` remains and the test suite holds your class to the
same standard as the reference.

Run this file at any time to see how far you have got:

    python3 starter/account.py

Run the full suite when you think you are finished:

    bash tests/run_tests.sh
"""


class Account:
    """A bank account: an owner, a balance, and a history of movements.

    Invariant (the rule this class exists to keep): the balance is never
    negative, and every movement is recorded in this instance's own history.
    """

    currency = "USD"        # class attribute: one value shared by every account

    # ---------------------------------------------------------------
    # EXERCISE 2 (do this one AFTER exercise 1)
    #
    # The line below is a deliberate bug: a list written at class level is
    # created ONCE, at class-definition time, and every instance shares it.
    # First see the bug for yourself:
    #
    #     python3 examples/shared_bug.py
    #
    # Then prove it in your own class:
    #
    #     python3 -c "import sys; sys.path.insert(0, 'starter'); from account import Account; a = Account('ada', 10); b = Account('bob', 10); a.deposit(5); print(b.history)"
    #
    # If b.history is not empty, ada's deposit landed in bob's history.
    # FIX: delete the line below and create `self.history = []` inside
    # __init__ instead, so each instance gets a fresh list.
    # ---------------------------------------------------------------
    history = []

    def __init__(self, owner, balance=0.0):
        """EXERCISE 1 — initialize the object Python has already created.

        Set three attributes on `self`:
          * self.owner   -> the owner argument
          * self.balance -> the balance argument (this goes through the
                            property setter you write in exercise 4; until
                            then it just stores the value)
          * self.history -> a NEW empty list (this is also the fix for
                            exercise 2)

        Then run:  python3 starter/account.py
        """
        raise NotImplementedError("exercise 1: set owner, balance, and history on self")

    def deposit(self, amount):
        """EXERCISE 1 (continued) — add a positive amount and record it.

        Mirror examples/account_dict.py's deposit(): reject amounts that are
        not positive with ValueError("deposit amount must be positive"), add
        the amount to self.balance, append ("deposit", float(amount)) to
        self.history, and return the new balance.
        """
        raise NotImplementedError("exercise 1: implement deposit")

    def withdraw(self, amount):
        """EXERCISE 1 (continued) — remove an amount the balance can cover.

        Reject a non-positive amount with
        ValueError("withdrawal amount must be positive"), reject an amount
        larger than the balance with ValueError("insufficient funds"),
        otherwise subtract it, append ("withdraw", float(amount)) to
        self.history, and return the new balance.
        """
        raise NotImplementedError("exercise 1: implement withdraw")

    def describe(self):
        """A one-line summary — provided, so you can compare with the dict version.

        This must print exactly what examples/account_dict.py's describe()
        prints for the same moves. That is how you prove the conversion did
        not change the behaviour:

            python3 examples/compare.py
        """
        return f"{self.owner}: {self.balance:.2f} ({len(self.history)} entries)"

    def __repr__(self):
        """EXERCISE 3 — give the class a useful debugging representation.

        Return the string  Account(owner='ada', balance=120.00)  for an
        account owned by 'ada' holding 120. Use !r on the owner so the
        quotes appear, and :.2f on the balance.

        Before and after, compare what the REPL shows:

            python3 -c "import sys; sys.path.insert(0, 'starter'); from account import Account; print(repr(Account('ada', 120)))"

        Without a __repr__ you get a default like <account.Account object at
        0x...>, whose hex number is a memory address that changes every run
        and tells you nothing about the account.
        """
        raise NotImplementedError("exercise 3: return a useful repr string")

    # ---------------------------------------------------------------
    # EXERCISE 4 — a property that validates.
    #
    # Turn `balance` into a computed attribute backed by self._balance:
    #
    #   @property
    #   def balance(self):
    #       return self._balance
    #
    #   @balance.setter
    #   def balance(self, value):
    #       amount = float(value)
    #       if amount < 0:
    #           raise ValueError(f"balance cannot be negative (got {amount:.2f})")
    #       self._balance = amount
    #
    # Write those two blocks here (delete this comment when you do), then
    # confirm a bad value is refused and the exception is catchable:
    #
    #     python3 -c "import sys; sys.path.insert(0, 'starter'); from account import Account; a = Account('ada', 10)
    #     try:
    #         a.balance = -500
    #     except ValueError as err:
    #         print('rejected:', err)
    #     print('balance still', a.balance)"
    # ---------------------------------------------------------------

    @staticmethod
    def is_valid_amount(amount):
        """Provided: a rule that needs neither the instance nor the class."""
        return isinstance(amount, (int, float)) and amount > 0

    @classmethod
    def from_csv_row(cls, row):
        """EXERCISE 5 — an alternative constructor (ties to Day 65).

        Turn one CSV line, 'ada, 120.50', into an Account:
          * split the row on ',' and strip whitespace from each field;
          * if there are not exactly two fields, raise
            ValueError(f"expected 'owner,balance', got {row!r}");
          * otherwise return cls(owner, float(balance)).

        Use `cls(...)`, not `Account(...)` — that is what makes it an
        alternative constructor rather than a hard-coded factory.

        Then load a whole file with it:

            python3 -c "import sys; sys.path.insert(0, 'starter'); from account import Account; print([Account.from_csv_row(line) for line in open('examples/accounts.csv') if line.strip()])"
        """
        raise NotImplementedError("exercise 5: build an instance from a CSV row")


def main():
    """A short session you can run as you go: python3 starter/account.py"""
    ada = Account("ada", 100)
    ada.deposit(50)
    ada.withdraw(30)
    print(ada.describe())
    print("repr:", repr(ada))
    try:
        ada.balance = -500
    except ValueError as err:
        print("rejected:", err)
    print("from_csv_row:", repr(Account.from_csv_row("cleo, 250.00")))


if __name__ == "__main__":
    main()
