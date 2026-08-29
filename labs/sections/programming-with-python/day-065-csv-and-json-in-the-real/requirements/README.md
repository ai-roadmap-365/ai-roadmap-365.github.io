# Dependencies — Day 065 lab

**Python 3 only. No third-party packages, no network, no API key.**

- `python3` (3.8 or newer; tested on 3.14.0). You set this up on Day 43.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only: `csv`, `json`, and `pathlib` in the lab files,
  plus `io` in the from-scratch parser so it can hand a string to
  `csv.reader`. There is deliberately no `requirements.txt`.

That last point is the lesson in miniature. CSV and JSON are so central to
data work that Python ships a reader, a writer, an encoder, and a decoder
for them in the box. You will meet `pandas` later, and it is excellent —
but reaching for a 30 MB dependency to read a five-row file is a habit
worth resisting, and you cannot debug what `pandas.read_csv` did to your
quoting unless you understand what the `csv` module does first.

Check your Python is present and new enough:

```bash
python3 --version
```

If that prints `Python 3.8` or higher, you are ready.

Windows users: run the commands inside WSL, or use `python` in place of
`python3` if that is how Python is exposed on your system. One genuine
difference matters on Windows and is covered in `troubleshooting.md`: if
you forget `newline=''` when opening a file for the `csv` module, Windows
translates the `\n` the writer emits into `\r\n`, and you get a blank line
between every record. The lab files all pass `newline=''`, so they behave
identically everywhere.
