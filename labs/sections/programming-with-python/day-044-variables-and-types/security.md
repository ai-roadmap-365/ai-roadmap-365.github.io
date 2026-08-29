# Security notes — Day 044 lab

- **What the programs do:** they create a few values, print their types and
  identities, and demonstrate a safe conversion. They make **no network
  connections**, write **no files**, read **no input from you**, and change
  **no settings**. They run entirely as your normal user; nothing here needs
  `sudo`.

- **Never use `eval()` (or `exec()`) to convert untrusted input.** It is
  tempting to turn a string into a value with `eval("42")`, but `eval` runs
  *any* Python code the string contains — a string like
  `__import__("os").system("...")` would execute a real command. To turn text
  into a number, use the type constructors this lesson teaches — `int()`,
  `float()` — which parse a value and nothing else, and wrap them in
  `try`/`except ValueError` to reject bad input safely. The lab does exactly
  this and never calls `eval`.

- **Treat all external input as untrusted text.** Keyboard input, file
  contents, and network responses arrive as strings of unknown shape. Convert
  them to the exact type you expect, inside a `try`/`except`, and reject
  anything that does not fit, rather than assuming a value is already the type
  you want. Type confusion at these boundaries is a common root cause of real
  security bugs.

- **Reading before running:** both programs are short and commented — read
  them before running. Running unread code is one of the most common ways
  developers get compromised; every script in this course is small enough to
  read and understand first.
