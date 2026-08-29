# Security notes — Day 065 lab

- **What the lab does:** reads two files that ship with it
  (`data/messy_orders.csv` and `data/config.json`), and writes three files
  into `out/` inside this lab directory. It makes **no network
  connections**, needs **no privileges**, and touches nothing outside the
  lab. The test runner writes its round-trip files into a throwaway
  directory made with `mktemp -d` and removes it on exit.

- **Parsed data is data, never code.** The single most important habit in
  this lab: a CSV field or a JSON value is *text you were handed*, not
  something to execute. Use `float(value)` and `int(value)` to turn text
  into numbers — they can only ever produce a number or raise
  `ValueError`. Never use `eval()` or `exec()` to "read" a value, and
  never use `ast.literal_eval` as a substitute for a real parser on
  untrusted input. Likewise, `json.loads` is safe by design; Python's
  `pickle` is not, and must never be pointed at a file you did not write
  yourself — unpickling runs code.

- **A separator is not sanitisation.** A field arriving from a CSV can
  contain a comma, a newline, a quote, a null byte, or a megabyte of text.
  If you paste those values into a SQL string, a shell command, or an HTML
  page without escaping, you have handed the file's author control of your
  program. Use the real interface at every boundary: parameterised SQL
  queries, `subprocess` argument lists rather than shell strings, and a
  templating layer that escapes HTML.

- **Spreadsheet formula injection is real.** A CSV field beginning with
  `=`, `+`, `-`, or `@` is treated as a formula by Excel, LibreOffice, and
  Google Sheets when the file is opened. If you export user-supplied text
  to CSV for other people to open, prefix such fields with a single quote
  or refuse them; a well-formed CSV can still be a hostile one.

- **Size and shape are attack surface too.** `json.load` on a hostile file
  will happily allocate everything it describes, and a deeply nested
  document can exhaust the recursion limit. When the file did not come
  from you, check its size before reading it, prefer JSON Lines so you can
  process one record at a time instead of holding the whole document in
  memory, and treat a failure to parse as an expected outcome rather than
  a crash.

- **Personal data lives in these files.** Order records, names, and notes
  are exactly the sort of content that turns a convenient CSV into a
  privacy incident when it is copied to a laptop, pasted into a chat, or
  committed to version control. Keep real data out of repositories, keep
  the generated `out/` directory local, and delete extracts when the job
  they were made for is finished.

- **Reading before running:** every file in this lab is short and
  commented. Read `examples/wrangle.py`, `examples/csv_field_parser.py`,
  and `tests/run_tests.sh` before running them. Running unread scripts is
  one of the most common ways developers get compromised; the course's
  rule is that every lab script is small enough to read and understand
  first.
