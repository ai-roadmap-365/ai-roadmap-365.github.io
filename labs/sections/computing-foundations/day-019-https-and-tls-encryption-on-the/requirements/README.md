# Dependencies — Day 019 lab

**Two standard tools, both preinstalled on macOS and Linux:**

- `openssl` — the TLS/certificate toolkit. Ships with macOS (as LibreSSL) and
  every mainstream Linux distribution; Homebrew's `openssl@3` is a fine
  alternative. Used here only to *read* a public certificate.
- `curl` — the HTTP(S) client. Preinstalled on macOS and Linux; used with
  `-v` to show the TLS handshake.

**Network access is required.** Unlike most labs in this course, this one
opens a real HTTPS connection to a public host (`example.com` by default) to
read its certificate. It reads only the public certificate a server presents
to every visitor and sends no data of its own. With no network, every script
here degrades gracefully: it prints an "offline" message and exits cleanly.

There is deliberately no `requirements.txt` / `package.json`: the lab must
run on a stock machine with nothing installed.

## Windows

Use WSL (`wsl --install`, then follow the Linux path) or Git Bash, which
bundles both `openssl` and `curl`.
