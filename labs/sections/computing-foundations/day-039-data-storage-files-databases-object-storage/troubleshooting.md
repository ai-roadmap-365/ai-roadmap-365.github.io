# Troubleshooting — Day 039 lab

- **`sqlite3: command not found`.** The database step needs the `sqlite3`
  tool. It ships on macOS; on Debian/Ubuntu run `sudo apt install sqlite3`, on
  Fedora `sudo dnf install sqlite`. Confirm with `sqlite3 --version`.

- **The query returns nothing.** Check that your `WHERE` clause matches the
  data exactly — the state code is `'OH'`, not `'Ohio'` — and that the
  `CREATE TABLE`/`INSERT` ran before the `SELECT`. In the starter, that means
  finishing Exercise 1 before Exercise 2.

- **`Error: no such table: orders`.** The inserts did not run, usually because
  Exercise 1 is still a placeholder or the heredoc was mistyped. Copy the
  `CREATE TABLE ... INSERT ...` block from `examples/storage_demo.sh` and
  compare.

- **The cache always prints `MISS`.** Two common causes: the cache filename
  changes between calls (it must be stable for a given key), or the result is
  saved *after* the existence check instead of only on a miss. The correct
  order is: check for the file first; if present, print a HIT; otherwise
  compute, save, and print a MISS.

- **`database is locked`.** Another process still holds `storage_demo.db`.
  Close any other `sqlite3` session on that file. Because the scripts use a
  fresh temp directory each run, simply rerunning usually clears it.

- **`shasum`/`sha256sum` not found.** Rare, but if neither is present the
  scripts stop with a clear message. Install coreutils (Linux:
  `sudo apt install coreutils`) or Perl's `shasum` (usually already present).

- **`unbound variable` errors when editing.** The scripts run with
  `set -euo pipefail`, so referencing an unset variable stops the run
  immediately. Declare each `local` variable on its own line and set every
  variable before you use it.

- **Windows.** Native PowerShell is not supported. Install WSL, open a Linux
  shell, and run the commands exactly as on Linux.
