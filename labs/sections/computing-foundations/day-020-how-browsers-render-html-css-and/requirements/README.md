# Dependencies — Day 020 lab

**None beyond a shell and a web browser.** This lab has zero installable
dependencies:

- **To view the page:** any modern web browser (Chrome, Edge, Firefox, or
  Safari) — all include the developer tools the exercise uses, for free.
- **To run the inspector and tests:** `bash` ≥ 3.2 (preinstalled on macOS and
  every mainstream Linux distribution) plus the standard POSIX text tools
  `grep`, `sed`, `sort`, `uniq`, and `wc` — all part of the base system.

The inspector needs only `grep` and `wc` at minimum; it performs a static read
of the committed HTML file and makes **no network connections**. There is
deliberately no `requirements.txt`/`package.json` here — the page is a single
self-contained file you open directly from disk.

Windows: run the shell parts under WSL (Ubuntu) or Git Bash, and open the HTML
file in any installed browser.
