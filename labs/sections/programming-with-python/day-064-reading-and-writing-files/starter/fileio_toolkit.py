"""Safe file I/O toolkit — YOUR working file.

Five numbered exercises. Each unfinished function raises
`NotImplementedError` on purpose, so an empty function can never be
mistaken for a working one. Replace each `raise NotImplementedError(...)`
line with the real body described above it, keeping the docstring's promise
exactly — the docstring is the contract the tests check.

Work in order; run the driver after each exercise to see your progress:

    python3 starter/demo.py

and check your work at any time with:

    bash tests/run_tests.sh

The reference solution is in `examples/fileio_toolkit.py`. Use it when you
are stuck, not before — the point is the typing.
"""

import os
import tracemalloc
from pathlib import Path

# One padded record, so every generated line has the same length.
FILLER = "log line padding-padding-padding"


# --- Exercise 1 of 5: round-trip text with an EXPLICIT encoding -------------
#
# Fill in both functions.
#
# write_text_file: open `path` in mode "w" with `encoding=encoding` and
#   `newline="\n"`, inside a `with ... as handle:` block, and `handle.write`
#   the text. Then return `os.path.getsize(path)`.
#   Reminder: `write()` adds NO newline of its own — whatever you pass is
#   exactly what lands on disk.
#
# read_text_file: open `path` in mode "r" with `encoding=encoding`, inside a
#   `with` block, and return `handle.read()`.
#
# Both must name the encoding explicitly. Never rely on the platform default.

def write_text_file(path, text, encoding="utf-8"):
    """Write `text` to `path`, replacing anything already there.

    Returns the size of the finished file in bytes.
    """
    raise NotImplementedError("Exercise 1a: open in mode 'w' with an explicit encoding and write")


def read_text_file(path, encoding="utf-8"):
    """Read the whole of `path` back as one string, decoding with `encoding`."""
    raise NotImplementedError("Exercise 1b: open in mode 'r' with an explicit encoding and read")


# --- Provided complete: the file generator and the expensive reader ---------
# You do not edit these two. They exist so Exercise 2 has something big to
# read and something to be compared against.

def make_big_file(path, line_count, long_line_at=None):
    """Generate a large-ish log file: one numbered record per line.

    Every line has the same length except the one numbered `long_line_at`,
    which gets extra padding. Returns the size of the file in bytes.
    """
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for number in range(1, line_count + 1):
            extra = "!" * 20 if number == long_line_at else ""
            handle.write(f"{number:07d} {FILLER}{extra}\n")
    return os.path.getsize(path)


def longest_line_whole_file(path):
    """Length of the longest line, read the EXPENSIVE way.

    Returns (longest_length, peak_bytes) — peak memory measured with
    `tracemalloc`, Python's built-in allocation tracker.
    """
    tracemalloc.start()
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    lines = text.splitlines()
    longest = max((len(line) for line in lines), default=0)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return longest, peak


# --- Exercise 2 of 5: the same answer, one line at a time -------------------
#
# Give the SAME answer as longest_line_whole_file for a fraction of the
# memory. Between `tracemalloc.start()` and the peak reading:
#
#   1. set `longest = 0`
#   2. open `path` in mode "r" with `encoding="utf-8"` inside a `with` block
#   3. `for line in handle:` — iterating the file object hands you one line
#      at a time and lets the previous one be reclaimed
#   4. measure `len(line.rstrip("\n"))` and keep the largest
#
# Do NOT call `handle.read()` or `handle.readlines()` anywhere in here —
# both pull the whole file into memory and defeat the exercise.

def longest_line_streaming(path):
    """Length of the longest line, read the CHEAP way.

    Returns (longest_length, peak_bytes), the same answer as
    `longest_line_whole_file` for far less memory.
    """
    tracemalloc.start()
    raise NotImplementedError("Exercise 2: iterate the file object one line at a time")


# --- Exercise 3 of 5: survive bytes that are not valid UTF-8 ----------------
#
# 1. `try:` reading `path` strictly (a plain `with open(..., encoding=...)`
#    and `handle.read()`), and return `(text, False)` when it works.
# 2. `except UnicodeDecodeError:` open it again, this time adding
#    `errors="replace"`, read it, and return `(text, True)`.
#
# `errors="replace"` swaps each undecodable byte for the replacement
# character U+FFFD instead of raising. Strict-first is the right default:
# an error tells you the file is not what you assumed, and silence is worse.

def read_text_surviving_bad_bytes(path, encoding="utf-8"):
    """Read `path` as text, surviving bytes that are not valid `encoding`.

    Returns (text, recovered) where `recovered` is True when the
    `errors="replace"` fallback was needed.
    """
    raise NotImplementedError("Exercise 3: strict read first, then errors='replace' on failure")


# --- Exercise 4 of 5: the atomic write --------------------------------------
#
# Replace `path` with `text` so that no reader ever sees a half-written
# file. Four steps, in this order:
#
#   1. `path = Path(path)` and `temp = path.with_name(path.name + ".tmp")`
#      — the temp file must sit in the SAME directory, so the final rename
#      stays inside one filesystem and therefore stays atomic.
#   2. `with open(temp, "w", encoding=encoding, newline="\n") as handle:`
#      write the text, then `handle.flush()` (Python buffer -> operating
#      system) and `os.fsync(handle.fileno())` (operating system -> disk).
#   3. if `after_temp is not None:` call `after_temp(temp)` — that is the
#      moment the driver inspects the directory and finds both files.
#   4. `os.replace(temp, path)` — the atomic rename. Return `path`.

def atomic_write_text(path, text, encoding="utf-8", after_temp=None):
    """Replace `path` with `text` so no reader ever sees a half-written file.

    Returns the path that was written.
    """
    raise NotImplementedError("Exercise 4: temp file -> flush -> fsync -> os.replace")


def unsafe_write_text(path, text, encoding="utf-8", after_open=None):
    """The naive alternative, provided complete for contrast — do NOT copy it.

    Mode "w" truncates the real file immediately, so until the write
    finishes the file on disk is empty or partial. `after_open` is called
    while it is still incomplete, so the driver can look at the damage.
    """
    with open(path, "w", encoding=encoding, newline="\n") as handle:
        handle.write(text[: len(text) // 2])
        handle.flush()
        if after_open is not None:
            after_open(path)
        handle.write(text[len(text) // 2 :])
    return path


# --- Exercise 5 of 5: walk a tree with pathlib ------------------------------
#
# Return every FILE under `root` as sorted relative path strings.
#
#   1. `root = Path(root)`
#   2. `root.rglob("*")` yields every entry in the tree, recursively
#   3. keep only those where `p.is_file()` is true
#   4. turn each into `str(p.relative_to(root))`
#   5. wrap the whole thing in `sorted(...)`
#
# One generator expression inside `sorted(...)` does all of it.

def list_tree(root):
    """Every file under `root`, as sorted relative paths, using pathlib."""
    raise NotImplementedError("Exercise 5: sorted(str(p.relative_to(root)) for p in ...)")
