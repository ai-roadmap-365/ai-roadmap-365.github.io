# Expected output — what must match and what may differ

Both files in this directory were captured from real runs on macOS
(Apple Silicon).

## Files

- `inspect-bytes-macos.txt` — full output of `bash examples/inspect_bytes.sh`.
- `test-run-macos.txt` — full output of `bash tests/run_tests.sh`
  (final line: `18 checks, 0 failure(s).` with the starter untouched).

## Must be identical on every platform

The **bytes** never change — they are the whole point of the lab:

- `hello.txt` dump: `4865 6c6c 6f2c 2077 6f72 6c64 210a` (14 bytes).
- `unicode.txt` dump: contains `c3 a9` (é), `e2 82 ac` (€), and
  `f0 9f 8e 89` (party-popper emoji); 32 bytes, 24 characters.
- `tiny.png` first 8 bytes: `8950 4e47 0d0a 1a0a`; 145 bytes total.

## May differ slightly by platform

- The wording of `file` output: e.g. Linux may print `Unicode text, UTF-8
  text` as just `UTF-8 text`, or append `, with no line terminators` for
  some files. The tests only require the substrings `ASCII text`, `UTF-8`,
  and `PNG image data`.
- `wc -m` requires a UTF-8 locale to count 24 characters; in a `C`/POSIX
  locale it counts bytes (32). See `troubleshooting.md`.
- Temporary-directory paths in section 4 of the walkthrough are hidden
  because the script prints bare file names.
- Once you complete all four starter exercises, the test count rises from
  18 to 20 checks (the strict checks replace the structure-only check).
