# Dependencies — Day 005 lab

**None beyond a POSIX shell and standard utilities.** Everything this lab
uses ships with macOS and mainstream Linux distributions:

- `bash` ≥ 3.2 (preinstalled on macOS and Linux)
- `xxd` — the hex-dump tool (ships with vim; preinstalled on macOS, and
  present on nearly every Linux distribution via the `vim`/`vim-common`
  or `xxd` package)
- `file` — identifies file types by magic bytes (preinstalled everywhere)
- `wc`, `cp`, `mktemp`, `printf` — POSIX basics
- `base64` — only needed if you re-run `examples/make_samples.sh`
- `hexdump` — optional alternative to `xxd` shown in the README

There is deliberately no `requirements.txt`/`package.json`: the sample
files are committed to the repository, so nothing needs to be downloaded
or installed. If `xxd` is missing on a minimal Linux container, install it
with your package manager (e.g. `sudo apt install xxd` on Debian/Ubuntu).
