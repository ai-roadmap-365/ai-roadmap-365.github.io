# Expected output — what to look for (all platforms)

This directory holds real captured runs from the authoring machine
(macOS, Apple Silicon, 2026-07-12, **shellcheck not installed**).

## `quality-check-no-shellcheck.txt`

A real run of `bash examples/quality_check.sh examples/samples/buggy.sh` on a
machine **without** shellcheck. A correct run always shows, in order:

1. `=== Quality check: examples/samples/buggy.sh ===`
2. `[1/3] Syntax check (bash -n)...` → `ok: script is syntactically valid.`
3. `[2/3] Lint check (shellcheck)...` → either
   - `SKIP: shellcheck is not installed on this machine.` (as captured here), or
   - shellcheck's real findings (SC2086, SC2034, and the test warning) if it *is* installed.
4. `[3/3] Formatting check ...` → two `FAIL` lines: one trailing-whitespace
   line (line 13 of the sample) and one tab-indentation line (line 14).
5. `Summary: syntax OK; lint skipped (shellcheck absent); formatting issues found.`

The script **always exits 0** — it is a report, not a gate.

## `tests.txt`

A real run of `bash tests/run_tests.sh`. The final line must read
`9 checks, 0 failure(s).` and the command must exit 0.

## Platform differences (not fabricated — described)

- **With shellcheck installed** (any OS): step [2/3] prints shellcheck's real
  findings instead of the SKIP block, and the summary's lint field reads
  `findings` (or `clean`) instead of `skipped (shellcheck absent)`. The test
  suite's check 6 adapts automatically: it verifies shellcheck ran rather than
  that it was skipped. Every other line is identical.
- **Linux**: output is byte-for-byte the same shape; only the absence/presence
  of shellcheck changes step [2/3].
- **Windows**: run under WSL or Git Bash; behaviour matches Linux.
