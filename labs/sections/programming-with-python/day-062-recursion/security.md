# Security notes — Day 062 lab

- **What the tool does:** reads command-line arguments, computes recursive
  functions in memory, and prints results. It makes **no network
  connections**, needs **no privileges**, reads **no files**, and writes
  **no files**. There is nothing to clean up.

- **Parse data with `json`, never `eval()`.** The `flatten` and `treesum`
  subcommands take nested data as JSON on the command line and parse it with
  `json.loads`, which turns text into plain lists, dicts, numbers, and
  strings and can **never** run code. Do **not** be tempted to `eval()` a
  string to "turn it into a list" — `eval` executes its argument as Python,
  so a malicious value could delete files or open a network connection.
  Parsing with `json` is the safe pattern, and it is what this tool does.

- **Recursion depth is a resource limit, and that is a safety feature.**
  Python caps the call stack (about 1000 frames by default) so a runaway or
  maliciously deep input cannot exhaust all memory and take the machine down;
  instead it raises `RecursionError`, which this tool catches and turns into a
  clear message and exit code 1. If you ever raise the limit with
  `sys.setrecursionlimit`, do so deliberately and modestly — setting it far
  too high can crash the interpreter itself, because the real operating-system
  stack has a hard size.

- **A missing base case is the classic recursion bug.** A recursive function
  with no base case, or one whose calls do not move toward it, recurses
  forever and overflows the stack. That is a correctness *and* an availability
  problem: a service that can be pushed into unbounded recursion by crafted
  input can be knocked over. Always verify that every recursive call shrinks
  the problem.

- **Fail loudly, not silently.** Every error path prints a message to standard
  error and returns a non-zero exit code, so a person or a script notices.
  Silent failure — returning a wrong number while reporting success — is worse
  than a crash.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/recursion.py` and `tests/run_tests.sh` before running them.
  Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
