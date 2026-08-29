# Security notes — Day 058 lab

- **What the module does:** defines pure functions and closures and prints a
  short demo. It makes **no network connections**, needs **no privileges**,
  reads **no files**, and writes **no files**. The tests import the module in
  separate `python3 -c` processes and assert return values; nothing is
  persisted.

- **Forward `**kwargs` deliberately, not blindly.** `build_request` shows the
  real-world pattern: a function gathers arbitrary keyword arguments and
  merges or forwards them. In production code this is a genuine risk — a
  function that passes user-supplied `**kwargs` straight into a database call,
  a model call, or an object constructor can let a caller set options that
  were never meant to be exposed (a "mass assignment" bug). The safe habit is
  to validate or allow-list the keys you accept and forward, rather than
  trusting the whole `kwargs` dict.

- **Closures keep captured state private — and alive.** A variable captured by
  a closure is reachable only through the inner function, which is good for
  encapsulation (a counter's state cannot be reached in and corrupted). The
  flip side: a closure keeps its captured variables alive for as long as the
  closure exists, so a closure that captured a large object holds that object
  in memory. Be mindful of what long-lived closures capture.

- **Prefer arguments and return values over globals.** The module changes no
  global state; `DEFAULTS` is read but never mutated (the merge builds a new
  dict). Mutating module-level globals from many functions makes behaviour
  depend on call order and hides data flow — avoid it except for deliberate,
  declared cases with the `global` keyword.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/flexible.py` and `tests/run_tests.sh` before running them.
  Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
