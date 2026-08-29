#!/usr/bin/env bash
# Day 004 lab — binary toolkit (completed reference implementation).
#
# A set of base converters built from exactly two preinstalled tools:
#   printf — formats numbers between decimal and hexadecimal
#   bc     — an arbitrary-precision calculator that speaks bases 2..16
#
# Usage:
#   bash binary_toolkit.sh              # run the demo (all converters)
#   bash binary_toolkit.sh d2b 42      # decimal     -> binary
#   bash binary_toolkit.sh b2d 101010  # binary      -> decimal
#   bash binary_toolkit.sh d2h 255    # decimal     -> hexadecimal
#   bash binary_toolkit.sh h2d FF     # hexadecimal -> decimal (0x prefix ok)
#   bash binary_toolkit.sh h2b 2F     # hexadecimal -> binary, 4 bits per digit
#   bash binary_toolkit.sh byte A     # inspect one character's ASCII byte
set -euo pipefail

# Decimal -> binary. bc's obase sets the output base.
dec2bin() {
  echo "obase=2; $1" | bc
}

# Binary -> decimal. bc's ibase sets the input base.
bin2dec() {
  echo "ibase=2; $1" | bc
}

# Decimal -> hexadecimal. printf's %X renders a value in uppercase hex.
dec2hex() {
  printf '%X\n' "$1"
}

# Hexadecimal -> decimal. printf understands 0x-prefixed input with %d.
hex2dec() {
  printf '%d\n' "0x${1#0x}"
}

# Hexadecimal -> binary, padded to 4 bits per hex digit.
# Order matters in bc: set obase BEFORE ibase, and use UPPERCASE hex digits.
hex2bin() {
  local hex bits width
  hex="$(printf '%s' "${1#0x}" | tr '[:lower:]' '[:upper:]')"
  bits="$(echo "obase=2; ibase=16; ${hex}" | bc)"
  width=$(( ${#hex} * 4 ))                # each hex digit is exactly 4 bits
  printf "%0${width}d\n" "${bits}"        # re-pad the leading zeros bc drops
}

# Byte inspector: one character -> its ASCII code, hex form, and 8-bit pattern.
# printf "'X" is the POSIX trick that yields a character's code number.
inspect_byte() {
  local char code hex bits
  char="$1"
  code="$(printf '%d' "'${char}")"
  hex="$(printf '%02X' "${code}")"
  bits="$(printf '%08d' "$(echo "obase=2; ${code}" | bc)")"
  echo "character '${char}'  ->  decimal ${code}  =  hex 0x${hex}  =  bits ${bits}"
}

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
