# Dependencies — Day 064 lab

**Python 3 only. No third-party packages, no network, no privileges.**

- `python3` (3.8 or newer; tested on 3.14.0). Preinstalled on most Linux
  distributions and installable on macOS; you set this up on Day 43.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Only the Python standard library is used: `os`, `pathlib`, `tracemalloc`,
  and `sys`. There is deliberately no `requirements.txt` — reading and
  writing files is a built-in capability, and the point of this lab is that
  the tools you need for it ship with Python.

Check your Python is present and new enough:

```bash
python3 --version
```

If that prints `Python 3.8` or higher, you are ready.

## Disk space

The lab generates a `workspace/` directory containing an 8.2 MB log file
(200,000 lines) so the memory comparison has something real to measure. Allow
about 10 MB of free space. Everything the lab creates lives inside
`workspace/`, and `rm -rf workspace` removes all of it.

## Platform notes

- **macOS and Linux:** every command runs as written.
- **Windows:** run the commands inside WSL. The Python code is portable —
  `pathlib` handles separators and the code passes `newline="\n"` explicitly
  where line endings matter — but the test runner is a bash script.
- `os.fsync` is available on macOS, Linux, and Windows. On network
  filesystems some devices acknowledge a sync before the bytes are truly on
  physical media; that is a property of the hardware, not of Python, and it
  does not affect anything this lab measures.
