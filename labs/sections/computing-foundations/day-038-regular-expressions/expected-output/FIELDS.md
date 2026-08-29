# Expected results (all platforms)

The committed sample `examples/regex_drills.sh` runs against
`examples/samples/data.txt`, which is fixed, so these counts are exact and the
same on macOS and Linux:

| Drill / pattern | Result |
| --- | --- |
| Email addresses extracted | **6** |
| Lines containing a `YYYY-MM-DD` date | **9** |
| IP-ish addresses extracted | **5** |
| Status codes pulled from log lines | **5** (200, 401, 200, 404, 500) |
| Non-comment lines (do not start with `#`) | **16** |
| `sed` reformat of `2026/07/12` | **`2026-07-12`** |

Files in this directory are real captures from the authoring machine
(macOS, BSD grep/sed, 2026-07-12):

- `drills-output.txt` — the full output of `bash examples/regex_drills.sh`.
- `test-output.txt` — the full output of `bash tests/run_tests.sh`, ending in
  `8 checks, 0 failure(s).`

## Platform note (macOS vs Linux)

The patterns in this lab deliberately use POSIX character classes (`[0-9]`,
`[[:alnum:]]`, `[[:alpha:]]`) and explicit `{n}` counts, and both `grep -E` and
`sed -E`. These behave identically under BSD tools (macOS) and GNU tools
(Linux), so the output above is byte-for-byte the same on both. The only
differences you would hit are with GNU-only shorthands like `\d` or `\+`, which
this lab avoids on purpose — see `troubleshooting.md`.
