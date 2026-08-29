# Expected output — what a correct run shows (all platforms)

`sample-run.txt` and `tests-run.txt` in this directory are **real captured
runs** (macOS, Apple Silicon, 2026-07-12). Your temporary paths and commit
hashes will differ — that is expected, because each run uses a fresh
`mktemp` workspace and Git computes hashes from content and timestamps.

A correct run of `examples/remote_demo.sh` must show, in order:

1. A bare repository created to act as the remote.
2. `git remote -v` listing `origin` twice (once for fetch, once for push),
   pointing at a **local folder path** — never an `http(s)://` or `git@` URL.
3. The push reporting `* [new branch]      main -> main`.
4. `branch 'main' set up to track 'origin/main'.` (the upstream being set).
5. A clone whose file listing contains `README.md`.
6. A second push from the clone advancing the remote (`<old>..<new>  main -> main`).
7. `git branch -vv` in the first repo showing `[origin/main: behind 1]`
   after the fetch.
8. A pull reporting `Fast-forward` and `shared.txt | 1 +`.
9. `shared.txt present in repo-a: yes`.

A correct run of `tests/run_tests.sh` ends with `12 checks, 0 failure(s).`
and exits 0.

## Platform differences

- **Linux:** identical output and behaviour; only the temporary path prefix
  differs (`/tmp/...` instead of macOS's `/var/folders/...`).
- **Windows:** run under WSL (Windows Subsystem for Linux) and the output
  matches Linux exactly. Native Git Bash also works, but the temp path form
  differs.
- **Older Git (< 2.28):** `git init -b main` may be unsupported. The
  troubleshooting notes give the two-line fallback; the branch may be called
  `master` instead of `main`, which changes only the branch name in the
  output, not the behaviour.
