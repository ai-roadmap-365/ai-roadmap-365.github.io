#!/usr/bin/env bash
# Day 005 lab — (re)build the three sample files in examples/samples/.
#
# The samples ship with the repository, so you normally never need to run
# this. It exists so you can see that every byte in the samples is
# deliberate: the text files are written byte by byte with printf escape
# sequences, and the PNG is decoded from base64 text back into its exact
# 145 binary bytes.
set -euo pipefail

samples_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/samples"
mkdir -p "${samples_dir}"

# 1. hello.txt — pure ASCII: every character is exactly one byte.
printf 'Hello, world!\n' > "${samples_dir}/hello.txt"

# 2. unicode.txt — UTF-8 with 1-, 2-, 3-, and 4-byte characters:
#      \xc3\xa9          = é (U+00E9, 2 bytes)
#      \xe2\x82\xac      = € (U+20AC, 3 bytes)
#      \xf0\x9f\x8e\x89  = party-popper emoji (U+1F389, 4 bytes)
printf 'caf\xc3\xa9 costs 3 \xe2\x82\xac\nr\xc3\xa9sum\xc3\xa9\n\xf0\x9f\x8e\x89\n' \
  > "${samples_dir}/unicode.txt"

# 3. tiny.png — a real, valid 145-byte PNG: a 2x2 image whose pixels are
#    red, green, blue, and white, plus a tEXt chunk holding a comment.
#    The binary bytes are stored here as base64 text and decoded back.
png_b64='iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAOnRFWHRDb21tZW50AERheSA1IHNhbXBsZTogMngyIHBpeGVscyAtIHJlZCwgZ3JlZW4sIGJsdWUsIHdoaXRllGR9ewAAABJJREFUeNpj+M/AwADCDP+BAAAf7gX78au6dwAAAABJRU5ErkJggg=='
if printf %s "${png_b64}" | base64 -d > "${samples_dir}/tiny.png" 2>/dev/null; then
  :  # GNU coreutils and modern macOS accept -d
else
  printf %s "${png_b64}" | base64 -D > "${samples_dir}/tiny.png"  # older macOS uses -D
fi

echo "Samples written to ${samples_dir}:"
file "${samples_dir}/hello.txt" "${samples_dir}/unicode.txt" "${samples_dir}/tiny.png"
