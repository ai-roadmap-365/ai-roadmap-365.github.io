#!/usr/bin/env bash
# Day 005 lab — YOUR working file: X-ray the sample files with xxd and file.
#
# The skeleton below runs as-is, but each of the four exercises prints a
# placeholder line. Your job: replace each placeholder `echo` line with the
# exact command named in the comment above it, then re-run the script.
# The finished version is in examples/inspect_bytes.sh — try it yourself
# before peeking.
#
# Run from anywhere:  bash starter/inspect_bytes.sh
set -euo pipefail

samples="$(cd "$(dirname "${BASH_SOURCE[0]}")/../examples" && pwd)/samples"

echo "=== Byte detective: my own run ==="

echo
echo "--- Exercise 1: dump plain ASCII text ---"
# Replace the placeholder line below with exactly:
#   xxd "${samples}/hello.txt"
# Then answer on the worksheet: which hex byte is the capital H? Which
# byte is the invisible newline at the end?
echo "exercise 1 not completed yet"

echo
echo "--- Exercise 2: find multi-byte UTF-8 characters ---"
# Replace the placeholder line below with exactly:
#   xxd "${samples}/unicode.txt"
# Then find the two bytes of e-acute (c3 a9), the three bytes of the euro
# sign (e2 82 ac), and the four bytes of the emoji (f0 9f 8e 89).
echo "exercise 2 not completed yet"

echo
echo "--- Exercise 3: read the PNG magic bytes ---"
# Replace the placeholder line below with exactly:
#   xxd -l 8 "${samples}/tiny.png"
# The -l 8 flag limits the dump to the first 8 bytes — the PNG signature.
# On the worksheet, write down the first four bytes in hex.
echo "exercise 3 not completed yet"

echo
echo "--- Exercise 4: prove that extensions lie ---"
# Replace the placeholder line below with exactly:
#   cp "${samples}/hello.txt" "${workdir}/hello.png" && file "${workdir}/hello.png"
# The copy has a .png name but text content. Which one does `file` trust?
workdir="$(mktemp -d)"
echo "exercise 4 not completed yet"
rm -rf "${workdir}"

echo
echo "=== End of my run ==="
