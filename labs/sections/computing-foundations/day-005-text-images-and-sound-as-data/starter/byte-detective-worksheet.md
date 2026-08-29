# Byte-detective worksheet — Day 005

Answer every question by **running a command and reading real bytes**, not
from memory. The commands you need are named in `starter/inspect_bytes.sh`
and demonstrated in `examples/inspect_bytes.sh`. Work from the lab
directory. Write your answers directly into this file.

## Part 1 — hello.txt (plain ASCII)

Run `xxd examples/samples/hello.txt` and `wc -c examples/samples/hello.txt`.

1. How many bytes is `hello.txt`, and how many characters do you *see* in
   the text? Explain why the two numbers relate the way they do (remember
   the invisible newline).

   Answer:

2. What is the hex value of the first byte, and which character is it?
   (Check it against the ASCII column on the right of the xxd output.)

   Answer:

3. What is the very last byte of the file in hex, and what character is
   it? Why does xxd print a dot for it in the right-hand column?

   Answer:

## Part 2 — unicode.txt (UTF-8)

Run `xxd examples/samples/unicode.txt`, then `wc -c` and `wc -m` on it.

4. Which two bytes (hex) encode the character é? How many times does that
   two-byte sequence appear in the file, and which words do they belong to?

   Answer:

5. `wc -c` and `wc -m` report different numbers for this file. Write both
   numbers and account for the difference exactly: which characters take
   2, 3, and 4 bytes?

   Answer:

6. Which four bytes (hex) encode the party-popper emoji? What do the first
   few bits of the leading byte tell a UTF-8 decoder?

   Answer:

## Part 3 — tiny.png (binary with magic bytes)

Run `xxd -l 8 examples/samples/tiny.png`, then the full
`xxd examples/samples/tiny.png`, and `file examples/samples/tiny.png`.

7. What are the first 4 bytes of the PNG in hex? Which three ASCII letters
   hide inside bytes 2–4?

   Answer:

8. `file` reports the image is "2 x 2". Find the readable chunk names in
   the full dump (IHDR, tEXt, IDAT, IEND). What human-readable sentence is
   stored inside the tEXt chunk?

   Answer:

## Part 4 — extensions versus content

Copy the samples under wrong names (use a scratch directory, e.g.
`cp examples/samples/hello.txt /tmp/hello.png`), then run `file` on the
copies.

9. When you rename `hello.txt` to `hello.png`, what does `file` say about
   it — and what does that prove about where a file's "type" really lives?

   Answer:

10. When you rename `tiny.png` to `tiny.txt` and double-click it or `cat`
    it, things look broken — yet `file` still knows what it is. Explain
    the difference between what your operating system's file manager uses
    (the extension) and what `file` uses (the magic bytes).

    Answer:
