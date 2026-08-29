"""Driver for the Safe File I/O Toolkit — provided complete; do not edit it.

It imports `fileio_toolkit` from the directory next to it, so this copy
drives YOUR toolkit in `starter/fileio_toolkit.py`. Run it from the lab
directory:

    python3 starter/demo.py              # workspace defaults to ./workspace
    python3 starter/demo.py my-scratch   # or name your own workspace directory

Until you finish an exercise, the part that needs it stops with
`NotImplementedError` — that is the expected behaviour, not a bug.

Everything it creates lives inside the workspace directory, so cleanup is a
single `rm -rf workspace`. It makes no network calls and needs no
privileges.
"""

import sys
from pathlib import Path

import fileio_toolkit as toolkit

LINE_COUNT = 200_000
LONG_LINE_AT = 100_000


def mib(byte_count):
    """Bytes as a human-readable MiB string (1 MiB = 1024 * 1024 bytes)."""
    return f"{byte_count / (1024 * 1024):.2f} MiB"


def part_1_round_trip(workspace):
    print("[1] text round-trip with an explicit encoding")
    notes = workspace / "notes.txt"
    text = "Day 64: reading and writing files\ncafé, naïve, 日本語\nthird line\n"
    size = toolkit.write_text_file(notes, text)
    back = toolkit.read_text_file(notes)
    print(f"    wrote {notes.name}: {size} bytes on disk, {len(text)} characters in memory")
    print(f"    lines read back: {len(back.splitlines())}")
    print(f"    round-trip identical: {back == text}")
    print(f"    note: {size} bytes > {len(text)} characters — non-ASCII characters")
    print("          take more than one byte each in UTF-8")
    print()


def part_2_memory(workspace):
    print("[2] whole-file read vs line-by-line streaming")
    big = workspace / "big.log"
    size = toolkit.make_big_file(big, LINE_COUNT, long_line_at=LONG_LINE_AT)
    print(f"    generated {big.name}: {LINE_COUNT} lines, {size} bytes ({mib(size)})")

    whole_len, whole_peak = toolkit.longest_line_whole_file(big)
    stream_len, stream_peak = toolkit.longest_line_streaming(big)

    print(f"    read() + splitlines()  -> longest line {whole_len} chars, "
          f"peak memory {mib(whole_peak)}")
    print(f"    for line in handle     -> longest line {stream_len} chars, "
          f"peak memory {mib(stream_peak)}")
    print(f"    same answer: {whole_len == stream_len}")
    print(f"    streaming used {whole_peak / max(stream_peak, 1):.0f}x less memory")
    print()


def part_3_decoding(workspace):
    print("[3] decoding trouble and how to survive it")
    broken = workspace / "broken.log"
    # Written as RAW BYTES so we control exactly what lands on disk. 0xE9 is
    # "é" in latin-1, but on its own it is not valid UTF-8.
    broken.write_bytes(b"caf\xe9 was logged by a latin-1 program\n")
    print(f"    wrote {broken.name} as raw bytes: {broken.read_bytes()!r}")

    try:
        toolkit.read_text_file(broken)
        print("    strict utf-8 read: no error (unexpected)")
    except UnicodeDecodeError as err:
        print(f"    strict utf-8 read raised UnicodeDecodeError: {err}")

    text, recovered = toolkit.read_text_surviving_bad_bytes(broken)
    print(f"    errors='replace' read: {text.strip()!r}")
    print(f"    recovered: {recovered}; U+FFFD present: {chr(0xFFFD) in text}")
    print()


def part_4_atomic(workspace):
    print("[4] atomic write — proved by looking at the directory mid-operation")
    box = workspace / "config"
    box.mkdir(exist_ok=True)
    config = box / "config.txt"
    toolkit.write_text_file(config, "version = 1\n")
    print(f"    before: {sorted(p.name for p in box.iterdir())} "
          f"content={toolkit.read_text_file(config).strip()!r}")

    def peek(temp_path):
        during = sorted(p.name for p in box.iterdir())
        still_old = toolkit.read_text_file(config).strip()
        print(f"    during: {during} content={still_old!r}")
        print(f"            the new bytes are all in {temp_path.name}; readers of "
              f"{config.name} still get the OLD file, whole")

    toolkit.atomic_write_text(config, "version = 2\n", after_temp=peek)
    print(f"    after : {sorted(p.name for p in box.iterdir())} "
          f"content={toolkit.read_text_file(config).strip()!r}")

    # The contrast: the naive write, caught in the act.
    unsafe = box / "unsafe.txt"
    toolkit.write_text_file(unsafe, "version = 1\n")

    seen = {}

    def peek_unsafe(path):
        seen["mid"] = toolkit.read_text_file(path)

    toolkit.unsafe_write_text(unsafe, "version = 2 with more content\n", after_open=peek_unsafe)
    print(f"    contrast: mode 'w' straight onto the real file was caught mid-write "
          f"holding {seen['mid']!r}")
    print("              — a crash there destroys the old file and leaves that fragment")
    print()


def part_5_pathlib(workspace):
    print("[5] walking a directory tree with pathlib")
    tree = workspace / "tree"
    (tree / "sub" / "deeper").mkdir(parents=True, exist_ok=True)
    toolkit.write_text_file(tree / "a.txt", "a\n")
    toolkit.write_text_file(tree / "sub" / "b.txt", "b\n")
    toolkit.write_text_file(tree / "sub" / "deeper" / "c.txt", "c\n")

    found = toolkit.list_tree(tree)
    for relative in found:
        print(f"    {relative}")
    print(f"    {len(found)} file(s) found by Path.rglob")
    print(f"    tree exists: {tree.exists()}; is a directory: {tree.is_dir()}")
    print()


def main(argv):
    workspace = Path(argv[1] if len(argv) > 1 else "workspace")
    workspace.mkdir(parents=True, exist_ok=True)
    print(f"Safe File I/O Toolkit — workspace: {workspace}")
    print()
    part_1_round_trip(workspace)
    part_2_memory(workspace)
    part_3_decoding(workspace)
    part_4_atomic(workspace)
    part_5_pathlib(workspace)
    print(f"Done. Remove everything with: rm -rf {workspace}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
