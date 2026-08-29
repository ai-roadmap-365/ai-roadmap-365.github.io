"""The 'before' version: a dict of state plus a pile of loose functions.

This is how you have modelled a bank account with everything you knew up to
Day 66. It works, but notice the friction:

* every function must be handed the same dict as its first argument;
* the rules ("balance is never negative", "every movement is recorded")
  live in the functions, not with the data, so nothing stops a caller from
  writing account["balance"] = -500 and breaking them;
* the state and the behaviour are only related by convention and by you
  remembering which functions belong to which dict.

Day 67 turns exactly this file into a class. Run it directly to see it work:

    python3 examples/account_dict.py
"""


def make_account(owner, balance=0.0):
    """owner, starting balance -> a new account dict with its own history."""
    if float(balance) < 0:
        raise ValueError("balance cannot be negative")
    return {"owner": owner, "balance": float(balance), "history": []}


def deposit(account, amount):
    """Add a positive amount, record it, and return the new balance."""
    if amount <= 0:
        raise ValueError("deposit amount must be positive")
    account["balance"] += float(amount)
    account["history"].append(("deposit", float(amount)))
    return account["balance"]


def withdraw(account, amount):
    """Remove a positive amount that the balance can cover."""
    if amount <= 0:
        raise ValueError("withdrawal amount must be positive")
    if amount > account["balance"]:
        raise ValueError("insufficient funds")
    account["balance"] -= float(amount)
    account["history"].append(("withdraw", float(amount)))
    return account["balance"]


def describe(account):
    """A one-line human summary of the account dict."""
    return (
        f"{account['owner']}: {account['balance']:.2f} "
        f"({len(account['history'])} entries)"
    )


def main():
    ada = make_account("ada", 100)
    deposit(ada, 50)
    withdraw(ada, 30)
    print(describe(ada))
    try:
        withdraw(ada, 1000)
    except ValueError as err:
        print(f"rejected: {err}")
    # Nothing protects the invariant when a caller edits the dict directly.
    ada["balance"] = -500
    print("after a direct edit:", describe(ada))


if __name__ == "__main__":
    main()
