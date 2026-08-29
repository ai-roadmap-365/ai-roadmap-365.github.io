# Security notes — Day 056 lab

- **What the tool does:** reads command-line arguments, reads and writes one
  JSON file you name with `--store`, and prints results. It makes **no
  network connections**, needs **no privileges**, and touches **no file**
  except the store you point it at. The test runner uses a throwaway store
  created with `mktemp` and removes it on exit.

- **Validate input; never execute it.** Records enter through argparse and
  are checked (`validate_new` rejects an empty name and an email with no
  `@`) before anything is saved. Data is read with `json.load`, which parses
  text into plain Python values — it can **never** run code. Do **not** reach
  for `eval()`/`exec()` to "parse" a record or a query; those execute the
  string as Python, so a malicious value could delete files or open a
  network connection. Parsing with `json` and validating at the boundary is
  the safe pattern, and it is exactly what this tool does.

- **Treat the store as untrusted on read.** A JSON file can be edited by
  anyone with access to it, so the tool does not assume it is well-formed:
  a corrupt file becomes a clear error and exit code 1, not a crash. When
  you build the Week 8 project, keep this habit — never trust that the file
  you load is the file you last wrote.

- **Watch what you write to a shared file.** Because each mutation rewrites
  the whole file, two programs writing at once can lose data (a "race"). It
  is harmless for this single-user lab, but it is why production tools use a
  database or file locking. Do not point `--store` at a file another program
  is also writing.

- **Fail loudly, not silently.** Every error path prints a message to
  standard error and returns a non-zero exit code, so a person or a script
  notices. Silent failure — saving nothing, or saving something wrong, while
  reporting success — is worse than a crash.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/records.py` and `tests/run_tests.sh` before running them.
  Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
