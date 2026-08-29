# Dependencies — Day 040 lab

**Two tools, both preinstalled on macOS and Linux:**

- `bash` ≥ 3.2 — the shell that runs the pipeline (preinstalled on macOS and
  every mainstream Linux distribution).
- `python3` — used only for the percentile computation (the p95/p50) and to
  parse the JSON span lines when reconstructing the trace. It ships with macOS
  and nearly every Linux distribution. Check with `python3 --version`.

The lab also uses the standard text utilities `grep`, `sed`, `awk`, `head`,
`seq`, and `mktemp`, all part of the base system on macOS and Linux.

There is deliberately no `requirements.txt` or `package.json`: the lab installs
nothing and reaches no network. If `python3` is somehow missing, install it
from your package manager (for example `sudo apt install python3` on
Debian/Ubuntu); everything else is already present.
