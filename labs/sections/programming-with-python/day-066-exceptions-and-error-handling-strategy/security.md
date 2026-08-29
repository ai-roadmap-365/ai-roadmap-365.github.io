# Security notes — Day 066 lab

- **What the lab does:** reads small JSON-lines files you already have on
  disk, prints a summary, and writes one log file (`triage.log` by default,
  or the path you name as the second argument). It makes **no network
  connections**, needs **no privileges**, and installs nothing. The
  simulated "ward system" is a local function that raises `ConnectionError`
  on a counter — there is no socket anywhere in this lab.

- **Swallowed exceptions are a security bug, not just a tidiness problem.**
  `examples/swallowing.py` catches everything and exits 0. Run it against a
  missing file and it reports success. In a real system that pattern hides
  the exact events you most need to see: a permission denial, a failed
  integrity check, a rejected authentication, a truncated download. An
  attacker who can make an operation fail quietly has been handed a way to
  operate unobserved. **Fail loudly, or at minimum log loudly.**

- **Catch narrowly so you cannot catch what you did not mean to.** A bare
  `except:` catches `BaseException`, which includes `KeyboardInterrupt` and
  `SystemExit` — so it can trap Ctrl-C and defeat a deliberate shutdown. It
  also catches `MemoryError` and every bug in your own code. Name the
  exceptions you actually expect.

- **Do not put attacker-controlled detail into your user-facing message.**
  This lab's messages name the line number and the field, which is safe and
  useful. Be careful in real systems: an error message that echoes a raw
  path, a query, a stack trace, or a configuration value to an untrusted
  user leaks information about your system. The rule that works is: a short,
  safe message to the user; the full traceback to the log.

- **And be careful what the log itself holds.** `logging.exception` writes
  the complete traceback, and tracebacks can carry the values that were in
  flight. If a record contains personal data or an API key, that value can
  land in the log file. Log identifiers (line numbers, record ids), not
  payloads, when the payload may be sensitive — and treat log files as
  data that needs the same protection as the records they describe.

- **`assert` is not a security check.** Python's `assert` statements are
  removed entirely when the interpreter runs with `-O`. Anything you assert
  as a *validation* — "this token is authorised", "this index is in range" —
  silently disappears in that mode. Use `if ...: raise ...` for checks that
  must always run; keep `assert` for internal sanity checks that document
  what you believe to be impossible.

- **Retries can become an attack on someone else.** A retry loop with no cap
  and no backoff turns a struggling service into a service under load from
  you. This lab's helper caps attempts at 3 and doubles the delay each time
  for exactly that reason. Never retry a request that has already had an
  effect (a payment, a message send) unless it is safe to repeat.

- **Reading before running:** every file here is short and commented. Read
  `examples/triage.py`, `examples/swallowing.py`, and `tests/run_tests.sh`
  before running them. Running unread scripts is one of the most common ways
  developers get compromised.
