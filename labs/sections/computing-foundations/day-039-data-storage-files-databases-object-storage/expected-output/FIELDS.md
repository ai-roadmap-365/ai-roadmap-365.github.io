# Expected output — required fields and platform notes

`sample-macos.txt` is a real captured run of `examples/storage_demo.sh` on
macOS (Apple Silicon). `sample-tests.txt` is a real captured run of
`tests/run_tests.sh`. Your own runs must contain the same load-bearing lines,
listed below; a few values legitimately vary.

## Lines that must appear (all platforms)

From `examples/storage_demo.sh`:

- `[1/4] FILE (structured CSV)` and the four CSV data rows.
- `[2/4] DATABASE (SQLite)` followed by the aggregated rows `ada|180.0` and
  `grace|90.0` — the total revenue per Ohio customer.
- `[3/4] OBJECT STORAGE (bucket + content key)` with a `PUT object under key:`
  line and the retrieved blob text `quarterly report: revenue up, storage bill down`.
- `[4/4] CACHE (key -> value with timestamp)` with `First call:  MISS` then
  `Second call: HIT`.

From `tests/run_tests.sh`: the final line `7 checks, 0 failure(s).` and exit
code 0.

## Values that legitimately differ

- **The object key** (`a185ba75...`) is the SHA-256 hash of the blob. It is
  identical on every machine for identical bytes — that is the point of
  content addressing — but if you edit the blob text, the key changes.
- **The cache timestamp** (`at 23:22:13`) is the wall-clock time of your run.
- **The work-dir path** printed on the second line is a temporary directory;
  the captured sample uses a fixed path only for readability. Real runs use a
  `mktemp` path under your system temp directory and clean it up on exit.

## Linux differences

The scripts are POSIX-portable and behave identically on Linux, using
`sha256sum` if `shasum` is absent (both produce the same SHA-256 key). The
only visible difference is the temp-dir path style (`/tmp/...`).
