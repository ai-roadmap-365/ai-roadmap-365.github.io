#!/usr/bin/env bash
# Day 004 lab — binary toolkit (YOUR working file).
#
# This skeleton already runs: two converters (dec2hex, hex2dec) are complete
# so you can see the pattern. Your job is the four numbered exercises below —
# each comment names the exact printf/bc incantation to use. Replace each
# `echo "unknown"` line with that incantation. The finished reference is in
# examples/binary_toolkit.sh — try each exercise yourself before peeking.
#
# Usage (identical to the reference):
#   bash binary_toolkit.sh              # demo
#   bash binary_toolkit.sh d2b 42      # decimal     -> binary
#   bash binary_toolkit.sh b2d 101010  # binary      -> decimal
#   bash binary_toolkit.sh d2h 255    # decimal     -> hexadecimal
#   bash binary_toolkit.sh h2d FF     # hexadecimal -> decimal
#   bash binary_toolkit.sh h2b 2F     # hexadecimal -> binary
#   bash binary_toolkit.sh byte A     # inspect one character's ASCII byte
set -euo pipefail

# ---- Already implemented (study these two before starting) ----------------

# Decimal -> hexadecimal: printf's %X renders a value in uppercase hex.
dec2hex() {
  printf '%X\n' "$1"
}

# Hexadecimal -> decimal: printf understands 0x-prefixed input with %d.
hex2dec() {
  printf '%d\n' "0x${1#0x}"
}

# ---- Your four exercises ---------------------------------------------------

# Exercise 1: decimal -> binary.
# Use bc with an output base:      echo "obase=2; $1" | bc
dec2bin() {
  echo "unknown"
}

# Exercise 2: binary -> decimal.
# Use bc with an input base:       echo "ibase=2; $1" | bc
bin2dec() {
  echo "unknown"
}

# Exercise 3: hexadecimal -> binary.
# Use bc with BOTH bases — obase must come first, hex digits UPPERCASE:
#                                  echo "obase=2; ibase=16; $1" | bc
# (You may pass the digits through: tr '[:lower:]' '[:upper:]')
hex2bin() {
  echo "unknown"
}

# Exercise 4: byte inspector — a character's ASCII code and its bits.
# Get the code with printf's apostrophe trick:   printf '%d' "'$1"
# Then convert the code with bc as in Exercise 1, and pad the result to a
# full byte with:                                printf '%08d\n' <bits>
inspect_byte() {
  echo "unknown"
}

# ---- Command dispatch (no changes needed below this line) ------------------

demo() {
  echo "=== Binary toolkit demo ==="
  echo "dec2bin 42        -> $(dec2bin 42)"
  echo "bin2dec 101010    -> $(bin2dec 101010)"
  echo "dec2hex 255       -> $(dec2hex 255)"
  echo "hex2dec 0xFF      -> $(hex2dec 0xFF)"
  echo "hex2bin 2F        -> $(hex2bin 2F)"
  echo "byte inspector    -> $(inspect_byte A)"
  echo "=== End of demo ==="
}

cmd="${1:-demo}"
case "${cmd}" in
  d2b)  dec2bin "$2" ;;
  b2d)  bin2dec "$2" ;;
  d2h)  dec2hex "$2" ;;
  h2d)  hex2dec "$2" ;;
  h2b)  hex2bin "$2" ;;
  byte) inspect_byte "$2" ;;
  demo) demo ;;
  *)
    echo "unrecognized command: ${cmd}" >&2
    echo "usage: bash binary_toolkit.sh [d2b|b2d|d2h|h2d|h2b|byte] <value>" >&2
    exit 1
    ;;
esac
