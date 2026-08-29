# Troubleshooting — Day 004 lab

## `bc: command not found` (Linux)

Some minimal Linux images omit `bc`. Install it with your package manager
(`sudo apt install bc`, `sudo dnf install bc`, etc.), or run the lab on
macOS/WSL where `bc` ships by default.

## `printf: 2F: invalid number` when converting hex

`printf '%d' 0x2F` needs the `0x` prefix to read hex; the toolkit adds it
for you in the `h2d`/`h2b` converters. If you call `printf` directly, write
`printf '%d\n' 0x2F`, not `printf '%d\n' 2F`.

## My binary result has no leading zeros

`bc` prints the minimal number of digits: 42 becomes `101010`, not
`00101010`. That is correct — a leading zero carries no value. When a byte
is expected (8 bits), pad it yourself; the worksheet notes where padding
matters.

## Two's-complement negation looks wrong

Remember the fixed width. In 8 bits, negating 5 means: invert `00000101`
to `11111010`, then add 1 to get `11111011` (which is -5). If you drop the
width you will get a different bit pattern — the instructor solution shows
the full working.

## The byte inspector prints a different code for my character

`byte A` reports 65 because 'A' is ASCII 65. Accented or non-ASCII
characters are multi-byte in UTF-8 (Day 5 covers this) — the single-byte
inspector is meant for plain ASCII characters.
