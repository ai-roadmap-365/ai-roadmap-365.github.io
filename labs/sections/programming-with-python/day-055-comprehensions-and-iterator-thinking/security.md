# Security notes — Day 055 lab

- **What the program does:** transforms a small in-memory list of records
  with comprehensions and streams it through a lazy generator pipeline,
  printing results. It makes **no network connections**, reads and writes
  **no files**, and changes **no settings**. The test runner is equally
  self-contained and non-interactive.

- **A comprehension runs real code for every item.** The output expression of
  a comprehension is evaluated once per kept item, so never build one whose
  expression executes untrusted text. Keep the output a plain transform
  (`r["name"].upper()`, `int(x)`), never a call that runs a string a user
  supplied. There is no `eval()` here, and there must never be one — the same
  rule you learned for input handling applies inside comprehensions.

- **Laziness delays errors — validate where you consume.** Because a
  generator computes on demand, an exception inside it surfaces when you pull
  on it, not when you create it. Validate inputs at the point they are read
  (inside the reader generator), and do not let a half-consumed generator
  swallow errors silently.

- **Streaming minimizes data held in memory.** A generator pipeline touches
  each record once and forgets it, so a filter that drops fields early means
  sensitive data never accumulates. Building a giant list first does the
  opposite. Prefer streaming with an early filter when records could contain
  anything private.

- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. As always in this course, if a script ever asks you to run it with
  elevated privileges, stop and read it first.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/pipeline.py` and `tests/run_tests.sh` before running them.
  Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
