#!/usr/bin/env bash
# Day 005 lab — completed reference walkthrough: X-ray the three sample
# files with `file`, `wc`, and `xxd` and point at what the bytes mean.
#
# Run from anywhere:  bash examples/inspect_bytes.sh
set -euo pipefail

samples="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/samples"
cd "${samples}"   # so every tool prints short, machine-neutral file names

section() {
  echo
  echo "=== $1 ==="
}

section "1. hello.txt — plain ASCII, one byte per character"
file hello.txt
echo "size in bytes:      $(wc -c < hello.txt | tr -d ' ')"
echo "size in characters: $(wc -m < hello.txt | tr -d ' ')"
xxd hello.txt
echo "Note: 13 visible characters + 1 newline (0a) = 14 bytes."
echo "Note: 'H' = 48 hex = 72 decimal, exactly its ASCII code."

section "2. unicode.txt — UTF-8 with 1-, 2-, 3-, and 4-byte characters"
file unicode.txt
echo "size in bytes:      $(wc -c < unicode.txt | tr -d ' ')"
echo "size in characters: $(wc -m < unicode.txt | tr -d ' ')"
xxd unicode.txt
echo "Note: bytes and characters differ because some characters need"
echo "several bytes. Look for these multi-byte UTF-8 sequences above:"
echo "  c3 a9        = e-acute      (U+00E9, 2 bytes)"
echo "  e2 82 ac     = euro sign    (U+20AC, 3 bytes)"
echo "  f0 9f 8e 89  = party emoji  (U+1F389, 4 bytes)"
echo "xxd prints a dot in the right-hand column for every byte that is"
echo "not printable ASCII — that is why the accents look like dots."

section "3. tiny.png — a real binary file with magic bytes"
file tiny.png
echo "size in bytes:      $(wc -c < tiny.png | tr -d ' ')"
echo "first 8 bytes (the PNG signature):"
xxd -l 8 tiny.png
echo "89 50 4e 47 0d 0a 1a 0a — bytes 2-4 spell 'PNG' in ASCII."
echo "full dump (note the readable chunk names IHDR, tEXt, IDAT, IEND):"
xxd tiny.png

section "4. Extensions lie; magic bytes do not"
workdir="$(mktemp -d)"
cp "${samples}/hello.txt" "${workdir}/hello.png"
cp "${samples}/tiny.png" "${workdir}/tiny.txt"
echo "Renamed hello.txt -> hello.png. What does 'file' say?"
(cd "${workdir}" && file hello.png)
echo "Renamed tiny.png -> tiny.txt. What does 'file' say?"
(cd "${workdir}" && file tiny.txt)
echo "'file' reads the CONTENT (magic bytes), not the name: the fake"
echo ".png is still ASCII text, and the fake .txt is still PNG image data."
rm -rf "${workdir}"

echo
echo "=== End of byte walkthrough ==="
