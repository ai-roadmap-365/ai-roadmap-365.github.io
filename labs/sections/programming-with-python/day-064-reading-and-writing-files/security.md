# Security notes — Day 064 lab

- **What the lab does:** creates a `workspace/` directory beneath the lab
  directory, writes text files and one 8.2 MB generated log into it, reads
  them back, and removes nothing until you run `rm -rf workspace`. It makes
  **no network connections**, needs **no privileges**, and touches nothing
  outside `workspace/`. The test runner does its work in a throwaway
  directory created with `mktemp -d` and removes it on exit.

- **Never build a path from untrusted input by concatenation.** This is the
  central file-handling vulnerability, and it is called path traversal. A
  filename that arrived from a user, a request, or a dataset may contain
  `../`, so `open(base + "/" + name)` can be steered anywhere on the
  filesystem — `../../.ssh/id_rsa` turns "read a file from my data
  directory" into "read the user's private key". Resolve the candidate path
  and confirm it really is inside the directory you meant before opening it:

  ```python
  from pathlib import Path

  def safe_open(base, name):
      base = Path(base).resolve()
      candidate = (base / name).resolve()
      if base not in candidate.parents:
          raise ValueError(f"path escapes {base}: {name!r}")
      return open(candidate, "r", encoding="utf-8")
  ```

- **Treat file *contents* as untrusted data.** Parse them with safe
  converters — `int()`, `float()`, and from Day 65 the `csv` and `json`
  modules. Never reach for `eval()` or `exec()` to "read" a value out of a
  file; those execute the text as Python, so anyone who can write to the
  file can run code as you. This lab uses only safe conversions.

- **Mode `x` is a security tool.** Exclusive creation refuses to open a file
  that already exists, which is what you want for lock files, first-run
  markers, and outputs that must not be silently overwritten. Where mode `w`
  destroys without asking, mode `x` fails loudly.

- **The atomic write is an availability property.** Overwriting a file in
  place means a crash, a full disk, or a killed process can leave you with a
  fragment and no original. Writing beside the target and renaming over it
  means there is no instant at which a reader can observe a partial file.
  For anything whose loss would cost real work — a checkpoint, a
  configuration, a record store — that is the difference between an
  inconvenience and an incident.

- **Temporary files inherit their directory's permissions.** The
  atomic-write temp file deliberately lives beside its target rather than in
  a shared temporary directory. That is required for the rename to be
  atomic, and it also avoids writing your data into a world-readable
  location. When you do need scratch space, `tempfile` creates it with
  restrictive permissions — use it rather than inventing predictable names in
  `/tmp`, which are vulnerable to symlink attacks.

- **Files are where personal data comes to rest.** Anything you write
  persists after your program forgets it, including into backups you did not
  think about. Write only what you need, keep personal data where you can
  find and delete it again, and remember that deleting a file removes the
  name far more reliably than it removes the bytes.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/fileio_toolkit.py`, `examples/demo.py`, and
  `tests/run_tests.sh` before running them. Running unread scripts is one of
  the most common ways developers get compromised; the course's rule is that
  every lab script is small enough to read and understand first. Note in
  particular that `tests/run_tests.sh` runs `rm -rf` on a directory it
  created itself with `mktemp -d` — read that line and satisfy yourself it
  can only remove its own scratch directory.
