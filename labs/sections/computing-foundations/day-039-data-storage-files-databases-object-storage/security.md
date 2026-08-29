# Security notes — Day 039 lab

- **What the scripts do:** create a small CSV file, a SQLite database, a
  "bucket" directory, and a cache directory — all inside a private temporary
  directory made with `mktemp` and removed on exit. They make **no network
  connections**, need **no elevated privileges**, and write nothing outside
  that temp directory.

- **Temp dir only.** Because everything lives under a per-run temp directory,
  nothing you create here persists or leaks into the rest of your system. If
  you adapt the scripts to keep data, write it somewhere you control and clean
  up deliberately.

- **Never store secrets unencrypted.** This lab stores only harmless sample
  data. In real systems, never keep passwords, API keys, or personal data as
  plaintext in a file or database. Sensitive data should be encrypted at rest,
  and secrets belong in a dedicated secrets manager, never in a committed file.

- **SQL injection (conceptual).** The demo builds SQL with fixed, trusted
  values only. In real applications, never paste untrusted input (a form
  field, a URL parameter) directly into a SQL string — an attacker can craft
  input that rewrites your query. The fix is *parameterized queries*, where
  the database treats supplied values strictly as data and never as commands.
  Keep this rule in mind the moment your queries include anything a user typed.

- **Read before running.** Both scripts are short and commented — read them
  first. Running unread shell scripts is a common way to get compromised; the
  course's rule is that every lab script is small enough to read and
  understand before executing.
