# Dependencies — Day 37 lab

**Required: a POSIX shell only.** The lab runs on tools that ship with your OS:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- Standard utilities: `grep`, `sed`, `printf`, `mktemp` — all part of the base system

There is deliberately no `requirements.txt` / `package.json`: the quality
check must run on a factory-fresh machine.

## Optional (recommended): ShellCheck

[ShellCheck](https://www.shellcheck.net/) is a free, open-source linter for
shell scripts. The lab **works without it** — the quality check detects its
absence and reports what it would have caught — but installing it turns the
lint step on and lets you see real findings. It is free and worth having.

Install (all free):

- **macOS (Homebrew):** `brew install shellcheck`
- **Debian / Ubuntu:** `sudo apt install shellcheck`
- **Fedora:** `sudo dnf install ShellCheck`
- **Windows:** install under WSL with the Ubuntu instructions, or use `scoop install shellcheck`

Verify with `shellcheck --version`. After installing, re-run
`bash examples/quality_check.sh examples/samples/buggy.sh` and step [2/3] will
show real SC-code findings instead of the SKIP block.

No account, API key, or network access is required for any part of this lab
(installing ShellCheck is the only step that uses the network, and it is
optional).
