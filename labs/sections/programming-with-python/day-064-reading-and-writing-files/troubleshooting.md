# Troubleshooting — Day 064 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the five exercises in
`starter/fileio_toolkit.py`. Each unfinished function raises
`NotImplementedError` on purpose so you cannot mistake an empty function for
a working one. Replace each `raise NotImplementedError(...)` line with the
real body described in the comment above it. Once all five are done,
`python3 starter/demo.py` produces the same five-part report as the
reference.

## `FileNotFoundError` when opening a file for reading

The path is wrong, or it is relative to somewhere you did not expect. A
relative path is resolved from the directory you **launched the program
in**, not the directory the script lives in. Print `Path.cwd()` to see where
the process actually is. Every command in this lab is meant to be run from
the lab directory itself:

```bash
cd labs/sections/programming-with-python/day-064-reading-and-writing-files
```

## `ModuleNotFoundError: No module named 'fileio_toolkit'`

`demo.py` imports the toolkit that sits beside it. Run the driver by its
path (`python3 examples/demo.py` or `python3 starter/demo.py`) from the lab
directory rather than copying one file somewhere else, and the import
resolves.

## Part 2's memory numbers do not match the captured output

They will not match exactly, and they are not supposed to. Allocation peaks
vary by a few kilobytes between runs, Python versions, and platforms. What
must hold is the **shape** of the result: both strategies report the same
longest-line length, and the streaming peak is far below the whole-file peak
(roughly 0.14 MiB against roughly 25 MiB on the generated log). The test
suite checks that shape, never the exact digits.

## Part 2 is slow, or the machine starts swapping

The lab generates 200,000 lines (about 8.2 MB) so there is something real to
measure. Generation takes a second or two. If your machine is very
constrained, pass a smaller workspace and regenerate with fewer lines by
editing the `make_big_file(..., line_count=...)` call in `demo.py` — the
memory *ratio* is the lesson, and it survives a smaller file, though the
175x figure will shrink because the fixed overheads stay constant.

## `UnicodeDecodeError` where I did not expect one

That is the machinery working correctly — the file is not what you assumed.
Before reaching for `errors="replace"`, find out what encoding it really
uses. Look at the raw bytes:

```bash
python3 -c "print(open('workspace/broken.log','rb').read(40))"
```

Single high bytes such as `\xe9` suggest Latin-1; pairs such as `\xc3\xa9`
are UTF-8. Part 3 of the lab creates exactly such a file on purpose.

## `ValueError: I/O operation on closed file`

You used the file object outside its `with` block. Everything you do with
the handle must happen inside the block — take the *data* out, not the
handle.

## A second `read()` returns an empty string

The cursor is at the end of the file. Call `handle.seek(0)` before reading
again, or better, read once and keep the value in a variable.

## My file ended up as one enormous line

`write()` never adds a newline; only `print()` does. Every newline in the
file is one you typed, so write `"text\n"` rather than `"text"`.

## Part 4 leaves a `.tmp` file behind

That is the failure mode the pattern is designed around, and seeing it means
something interrupted the write between `fsync` and `os.replace`. The
original file is intact — that is the guarantee. Delete the stray `.tmp`
and re-run. Production code does this cleanup at startup, which is the
Extension Challenge in the lesson.

## `os.replace` fails with `OSError: [Errno 18] Invalid cross-device link`

The temp file and the target are on different filesystems, so the rename
cannot be atomic. Put the temp file in the **same directory** as the target
— never in `/tmp`. This is exactly why `atomic_write_text` derives the temp
name from the target path with `path.with_name(...)`.

## `PermissionError` when writing

You are running somewhere you cannot write, or the file is owned by another
user. Check with `ls -l` and confirm you are in the lab directory. Nothing
in this lab needs `sudo`; if you find yourself reaching for it, the working
directory is wrong.

## The test suite fails but the demo looks fine

Read the first failing `ok:`/`FAIL:` line — each check names the behaviour it
tested. The most common cause is a starter exercise that returns the right
value but with the wrong type (for example `list_tree` returning `Path`
objects rather than relative strings, or a function returning only the text
instead of the `(text, recovered)` pair that Part 3 expects).
