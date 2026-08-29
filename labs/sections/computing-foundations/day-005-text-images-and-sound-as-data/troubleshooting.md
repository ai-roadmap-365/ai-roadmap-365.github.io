# Troubleshooting — Day 005 lab

## `command not found: xxd`

`xxd` ships with vim and is preinstalled on macOS. On a minimal Linux
system install it (`sudo apt install xxd` on Debian/Ubuntu, `sudo dnf
install vim-common` on Fedora), or use `hexdump -C` instead — its output
is equivalent for this lab (bytes on the left, ASCII on the right), only
formatted slightly differently.

## `wc -m` prints 32 instead of 24 for unicode.txt

Character counting depends on your locale. In a `C`/POSIX locale, `wc -m`
counts bytes. Check with `locale`; if `LC_CTYPE` is not a UTF-8 locale,
run the command as `LC_ALL=en_US.UTF-8 wc -m examples/samples/unicode.txt`
(any UTF-8 locale works). The byte count from `wc -c` is locale-independent.

## The emoji or accents display as boxes or question marks

That is a **font/terminal** limitation, not a data problem — the bytes in
the file are correct (verify with `xxd`: the sequence `f0 9f 8e 89` is
there). Try a different terminal profile or font. This is a live
demonstration of the lesson's point that rendering and encoding are
separate layers.

## `file` output wording differs from the expected output

Different `file` versions phrase results differently (`UTF-8 text` versus
`Unicode text, UTF-8 text`; extra notes like `with no line terminators`).
The tests only look for the substrings `ASCII text`, `UTF-8`, and
`PNG image data`, which every current version prints.

## Tests fail with `tiny.png starts with the PNG magic bytes … FAIL`

The sample was probably corrupted by an editor or a checkout that
translated line endings (byte `0a` → `0d 0a` breaks binary files — that is
exactly why the PNG signature contains both). Regenerate all three samples:
`bash examples/make_samples.sh`, then re-run the tests.

## `base64: invalid option -- d` when running make_samples.sh

Older macOS `base64` uses `-D` (capital) to decode; the script tries `-d`
first and falls back automatically. If you see this message but the script
still ends with three `file` lines, everything worked.

## My own text file shows `ef bb bf` at the start

That is a UTF-8 byte-order mark (BOM) — three bytes some Windows editors
prepend. It is legal but often unwanted; many Unix tools choke on it. Save
without BOM, or note it as a finding: you just diagnosed a real encoding
issue from raw bytes.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and work from there — `xxd` and
`file` are available). PowerShell's `Format-Hex` can substitute for `xxd`
if you prefer to explore manually, but the scripts and tests assume a
Unix-style shell.
