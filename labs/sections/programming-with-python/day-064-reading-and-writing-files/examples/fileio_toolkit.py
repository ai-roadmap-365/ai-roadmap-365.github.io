"""Safe file I/O toolkit — the reference implementation.

Nine small functions covering the five habits of reading and writing files
well:

  1. round-trip text with an EXPLICIT encoding             write_text_file / read_text_file
  2. compare whole-file reading with line-by-line reading  longest_line_whole_file /
                                                           longest_line_streaming
  3. survive undecodable bytes                             read_text_surviving_bad_bytes
  4. write without ever leaving a half-written file        atomic_write_text
  5. walk a directory tree with pathlib                    list_tree

Standard library only: os, tracemalloc, pathlib. Nothing here touches the
network, and every file this module opens is closed by a `with` block even
if an error is raised part-way through.
"""

import os
import tracemalloc
from pathlib import Path

# One padded record, so every generated line has the same length.
FILLER = "log line padding-padding-padding"


def write_text_file(path, text, encoding="utf-8"):
    """Write `text` to `path`, replacing anything already there.

    Mode "w" truncates the file to zero bytes before the first write, so
    this is a replace, not an append. The encoding is explicit on purpose:
    without it Python picks a locale-dependent default and the same code
    produces different bytes on different machines. `newline="\\n"` pins
    the line ending so the output is byte-identical everywhere.

    Returns the size of the finished file in bytes.
    """
    with open(path, "w", encoding=encoding, newline="\n") as handle:
        handle.write(text)
    return os.path.getsize(path)


def read_text_file(path, encoding="utf-8"):
    """Read the whole of `path` back as one string, decoding with `encoding`."""
    with open(path, "r", encoding=encoding) as handle:
        return handle.read()


def make_big_file(path, line_count, long_line_at=None):
    """Generate a large-ish log file: one numbered record per line.

    Every line has the same length except the one numbered `long_line_at`,
    which gets extra padding so the "longest line" question has a single
    correct answer. Returns the size of the file in bytes.
    """
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for number in range(1, line_count + 1):
            extra = "!" * 20 if number == long_line_at else ""
            handle.write(f"{number:07d} {FILLER}{extra}\n")
    return os.path.getsize(path)


def longest_line_whole_file(path):
    """Length of the longest line, read the EXPENSIVE way.

    `handle.read()` pulls the entire file into one string, and
    `.splitlines()` then builds a list holding every line at once. Peak
    memory therefore scales with the size of the file: a 2 GB log needs
    more than 2 GB of RAM before a single line is examined.

    Returns (longest_length, peak_bytes); the peak is measured by
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


def longest_line_streaming(path):
    """Length of the longest line, read the CHEAP way.

    Iterating the file object hands you one line at a time and lets the
    previous line be reclaimed, so peak memory is the size of the longest
    single line plus a read buffer — flat, no matter how big the file is.

    Returns (longest_length, peak_bytes), the same answer as
    `longest_line_whole_file` for far less memory.
    """
    tracemalloc.start()
    longest = 0
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            length = len(line.rstrip("\n"))
            if length > longest:
                longest = length
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return longest, peak


def read_text_surviving_bad_bytes(path, encoding="utf-8"):
    """Read `path` as text, surviving bytes that are not valid `encoding`.

    The first attempt decodes strictly, which is what you want by default:
    a `UnicodeDecodeError` tells you the file is not what you assumed, and
    silence would be worse. If it fails, the second attempt uses
    `errors="replace"`, which substitutes the replacement character U+FFFD
    (shown as an inverted question mark) for each undecodable byte instead
    of raising.

    Returns (text, recovered) where `recovered` is True when the fallback
    was needed.
    """
    try:
        with open(path, "r", encoding=encoding) as handle:
            return handle.read(), False
    except UnicodeDecodeError:
        with open(path, "r", encoding=encoding, errors="replace") as handle:
            return handle.read(), True


def atomic_write_text(path, text, encoding="utf-8", after_temp=None):
    """Replace `path` with `text` so no reader ever sees a half-written file.

    The pattern has four steps:

      1. write the new content to a temporary file IN THE SAME DIRECTORY
         (same directory so the final rename stays inside one filesystem),
      2. `flush()` so Python's buffer reaches the operating system,
      3. `os.fsync()` so the operating system writes it to the disk itself,
      4. `os.replace()` — an atomic rename: every reader sees either the
         complete old file or the complete new one, never a mixture.

    A crash before step 4 leaves the old file untouched and a stray `.tmp`
    beside it; a crash after step 4 leaves the complete new file.

    `after_temp`, if given, is called with the temporary path between steps
    3 and 4 — that is the moment the lab inspects, to show both files
    existing side by side.

    Returns the path that was written.
    """
    path = Path(path)
    temp = path.with_name(path.name + ".tmp")
    with open(temp, "w", encoding=encoding, newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    if after_temp is not None:
        after_temp(temp)
    os.replace(temp, path)
    return path


def unsafe_write_text(path, text, encoding="utf-8", after_open=None):
    """The naive alternative, kept for contrast — do NOT copy this.

    Opening the real file in mode "w" truncates it immediately, so from
    that instant until the write completes the file on disk is empty or
    partial. A crash in that window destroys the old content and leaves
    nothing usable behind. `after_open` is called while the file is open
    and still incomplete, so the lab can look at the damage.
    """
    with open(path, "w", encoding=encoding, newline="\n") as handle:
        handle.write(text[: len(text) // 2])
        handle.flush()
        if after_open is not None:
            after_open(path)
        handle.write(text[len(text) // 2 :])
    return path


def list_tree(root):
    """Every file under `root`, as sorted relative paths, using pathlib.

    `Path.rglob("*")` walks the whole tree recursively and yields `Path`
    objects; `is_file()` filters out the directories; `relative_to(root)`
    turns each absolute path back into a short readable one. The same job
    with `os.path` string juggling needs `os.walk` plus `os.path.join` plus
    `os.path.relpath` and a lot of care about separators.
    """
    root = Path(root)
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
