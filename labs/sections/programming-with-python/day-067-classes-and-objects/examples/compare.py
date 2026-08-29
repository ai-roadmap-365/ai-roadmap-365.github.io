"""Prove the class version behaves exactly like the dict version.

Refactoring is only safe when you can show the behaviour did not change.
This script drives account_dict.py and account.py through the same script of
moves and compares what each produced -- then loads a whole CSV file through
the classmethod constructor. Run it:

    python3 examples/compare.py
"""

import os

import account_dict as old
from account import Account

MOVES = [("deposit", 50), ("withdraw", 30), ("deposit", 12.5), ("withdraw", 2.5)]
HERE = os.path.dirname(os.path.abspath(__file__))


def run_dict_version():
    """Drive the dict + functions version and return (description, history)."""
    acct = old.make_account("ada", 100)
    for move, amount in MOVES:
        if move == "deposit":
            old.deposit(acct, amount)
        else:
            old.withdraw(acct, amount)
    return old.describe(acct), acct["history"]


def run_class_version():
    """Drive the class version through the identical script of moves."""
    acct = Account("ada", 100)
    for move, amount in MOVES:
        getattr(acct, move)(amount)
    return acct.describe(), acct.history


def main():
    dict_text, dict_history = run_dict_version()
    class_text, class_history = run_class_version()

    print("--- same behaviour, two designs ---")
    print("dict version :", dict_text)
    print("class version:", class_text)
    print("descriptions identical:", dict_text == class_text)
    print("histories identical:   ", dict_history == class_history)

    print()
    print("--- what changed is what happens when a rule is broken ---")
    broken = old.make_account("bob", 10)
    broken["balance"] = -500
    print("dict version accepted a negative balance:", broken["balance"])
    guarded = Account("bob", 10)
    try:
        guarded.balance = -500
    except ValueError as err:
        print("class version refused it:", err)
    print("class balance unchanged:", guarded.balance)

    print()
    print("--- loading a CSV file through the alternative constructor ---")
    path = os.path.join(HERE, "accounts.csv")
    with open(path, "r", encoding="utf-8") as handle:
        accounts = [Account.from_csv_row(line) for line in handle if line.strip()]
    for acct in accounts:
        print("  ", repr(acct))
    total = sum(acct.balance for acct in accounts)
    print(f"loaded {len(accounts)} accounts, total {total:.2f} {Account.currency}")


if __name__ == "__main__":
    main()
