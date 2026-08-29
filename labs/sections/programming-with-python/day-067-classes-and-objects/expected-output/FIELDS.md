# Expected output — Day 067 lab

These are real captured runs from the authoring machine (macOS on Apple
Silicon, Python 3.14.0, bash 3.2, 2026-07-19). Everything in this lab is
deterministic: given the same input it produces the same output and the same
exit code on every platform Python 3 runs on.

## A note about memory addresses

An object printed without a custom `__repr__` shows something like
`<account.Account object at 0x104f3a2d0>`. That hex number is the object's
address in memory, and it is **different on every run and every machine**.
Nothing in this lab's captured output or its tests depends on it:

- every class you build here defines its own `__repr__`, so the tested
  representation is `Account(owner='ada', balance=120.00)`;
- where identity matters, the scripts print comparisons (`a is b`,
  `id(a) == id(b)`) rather than the addresses themselves.

If you print a default repr yourself while exploring, expect the hex digits
to differ from any example — that is correct, not a failure.

## Files

- `sample-run.txt` — every example script driven in order:
  `account_dict.py` (the dict version, including the direct edit that breaks
  its rules), `account.py` (the class version refusing the same edit),
  `shared_bug.py` (the shared mutable class attribute and its fix),
  `compare.py` (the two versions proved equivalent, plus a CSV file loaded
  through the classmethod), `closure_object.py` (an object built by hand
  from dicts and closures next to the same thing written with `class`), and
  `machinery.py` (`type`, `vars`, `__dict__`, bound methods, name mangling).
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished: 28 checks, 0 failures, exit 0. The lab directory path is
  shown as `<lab>`; on your machine it is your real path.

## Required behaviour on every platform

The reference class (`examples/account.py`) must satisfy exactly:

| Call | Result |
| --- | --- |
| `Account('ada', 100).deposit(50)` | `150.0` |
| `Account('ada', 100).describe()` after `deposit(50)`, `withdraw(30)` | `'ada: 120.00 (2 entries)'` |
| `repr(Account('ada', 120))` | `"Account(owner='ada', balance=120.00)"` |
| `Account('ada', 100).withdraw(1000)` | raises `ValueError` mentioning `insufficient funds` |
| `acct.balance = -500` | raises `ValueError` mentioning `negative`; the balance is unchanged |
| `Account.from_csv_row('cleo, 250.00')` | an `Account` with `owner == 'cleo'` and `balance == 250.0` |
| `Account.from_csv_row('nonsense')` | raises `ValueError` |
| `Account.is_valid_amount(5)` / `(-5)` / `('5')` | `True` / `False` / `False` |
| `a.history is b.history` for two accounts | `False` (each instance owns its list) |
| `a.deposit.__self__ is a` | `True` |
| `a.deposit.__func__ is Account.deposit` | `True` |
| `'currency' in vars(a)` | `False` — it is found on the class |
| `isinstance(Account.__dict__['balance'], property)` | `True` |

The buggy demonstration class (`examples/shared_bug.py`) must satisfy:

| Call | Result |
| --- | --- |
| `BuggyAccount('ada').history is BuggyAccount('bob').history` | `True` — the bug |
| `FixedAccount('cleo').history is FixedAccount('dev').history` | `False` — the fix |

The equivalence proof (`examples/compare.py`) must print
`descriptions identical: True`, `histories identical:    True`, and
`loaded 4 accounts, total 2225.75 USD`.

## Platform notes

- The only visible difference between platforms is the shell prompt (`$`)
  shown before each command in `sample-run.txt`; the programs' own output is
  identical.
- Dictionary display order in `vars(...)` output follows insertion order,
  which is guaranteed by the language since Python 3.7, so those lines match
  everywhere.
- Balances are formatted with `:.2f`, which rounds to two decimals
  identically across platforms.
- The test runner prints its own lab directory path in the first line; that
  path is your machine's, and is shown as `<lab>` in the captured file.
