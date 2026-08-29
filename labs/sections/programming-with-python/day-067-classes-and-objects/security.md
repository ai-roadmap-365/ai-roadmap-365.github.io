# Security notes — Day 067 lab

- **What this lab does:** defines a few small classes, runs them in memory,
  and reads one small CSV file (`examples/accounts.csv`) that ships with the
  lab. It makes **no network connections**, needs **no privileges**,
  installs **nothing**, and writes **no files**. The test runner creates no
  temporary files either.

- **A class is an enforcement point, and that is a security property.** The
  dict version in `examples/account_dict.py` lets any caller write
  `account["balance"] = -500` and walk straight past every rule the
  functions were meant to enforce. The class version routes that same
  assignment through a `@property` setter that refuses it. When the rules
  that keep your data valid live *with* the data, there is one place to
  audit them and no way around them — instead of a rule scattered across
  every function that happens to remember it.

- **Encapsulation in Python is a convention, not a wall.** A single leading
  underscore (`self._balance`) means "internal, please leave this alone" and
  nothing more; a double leading underscore (`self.__pin`) is *name
  mangled* to `self._Card__pin`, which prevents accidental collisions, not
  determined access — `examples/machinery.py` shows `_Card__pin` sitting in
  plain sight in `vars(card)`. Never treat a double underscore as a secret
  store. Real secrets do not belong in object attributes you print, log, or
  serialize; keep them out of `__repr__` in particular, because a repr is
  exactly what ends up in log files and tracebacks.

- **`__repr__` is a disclosure surface.** A helpful repr is a debugging
  gift, but whatever you put in it will be printed by tracebacks, loggers,
  and debuggers. The reference `Account.__repr__` shows an owner and a
  balance because this is a teaching lab; in a real system, think before
  putting an API key, a token, a password, or personal data in a repr.

- **Validate at the boundary, and fail loudly.** Values entering the class
  from outside — a CSV row in `from_csv_row`, an amount in `deposit` — are
  converted with `float()` and checked before they touch the state. `float()`
  can only produce a number or raise `ValueError`; never reach for `eval()`
  to "read" a number from a file or an input, because `eval()` executes the
  text as Python and would run whatever an attacker wrote there. Every
  rejection in this lab raises an exception rather than quietly clamping the
  value, so a wrong input is noticed instead of silently absorbed.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/account.py`, `examples/machinery.py`, and
  `tests/run_tests.sh` before running them. Running unread scripts is one of
  the most common ways developers get compromised; the course's rule is that
  every lab script is small enough to read and understand first.
