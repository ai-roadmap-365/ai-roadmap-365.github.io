# Required profile fields (all platforms)

A correct run of `inspect_my_computer.sh` prints, in order:

1. `=== My Machine Profile ===`
2. `Generated on: YYYY-MM-DD`
3. `Operating system kernel: Darwin` (macOS) or `Linux`
4. `CPU model: <non-empty string>`
5. `CPU cores: <positive integer>`
6. `RAM: <n> GiB (<bytes> bytes)`
7. `Free disk on /: <value with unit, e.g. 436Gi or 89G>`
8. `OS version: <non-empty string>` (macOS product version, or PRETTY_NAME from /etc/os-release)
9. `=== End of profile ===`

`sample-macos.txt` in this directory is a real captured run (macOS, Apple
Silicon, 2026-07-12). Linux output has the same shape; only the kernel line
and the OS version wording differ. No field may read `unknown` in a
completed solution.
