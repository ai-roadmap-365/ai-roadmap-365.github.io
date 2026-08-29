# Expected output — what is stable and what varies

`sample-run.txt` in this directory is a real captured run of
`examples/editorconfig_demo.sh` (macOS, bash, 2026-07-12). A correct run on
any platform prints, in order:

1. `=== EditorConfig demo ===`
2. `Created sample project in: <path>` — the `<path>` is a temporary
   directory created by `mktemp`, so it **differs on every run and machine**
   (for example `/tmp/editorconfig-demo.XXXXXX` on Linux, or a
   `/var/folders/.../T/...` path on macOS). Only the path varies; the label
   is fixed.
3. `Wrote .editorconfig with 6 rules.`
4. `Checking files against .editorconfig ...`
5. `  clean.py ............ OK`
6. `  tabs.py ............. VIOLATION: uses tabs (indent_style = space)`
7. `  trailing.py ......... VIOLATION: trailing whitespace on 2 line(s)`
8. `  no_newline.py ....... VIOLATION: missing final newline`
9. `3 file(s) with violations, 1 clean.`
10. `Cleaning up temporary project.`

Lines 3–10 are identical on macOS and Linux — the checker uses only POSIX
`awk`, `grep`, `printf`, `tail`, and `mktemp`, which behave the same on both.
The only line that changes between runs is the temporary path on line 2.

The `tests/run_tests.sh` run for this lab ends with the line
`12 checks, 0 failure(s).` and exits 0.
