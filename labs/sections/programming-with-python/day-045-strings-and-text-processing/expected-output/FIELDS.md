# Expected output — Day 045 lab

`sample-run.txt` in this directory is a real captured run of
`examples/text_report.py` on the committed `examples/sample.txt`
(Python 3.14, macOS, 2026-07-12). Because the program reads a fixed sample
file and does no I/O beyond printing, the output is **identical on every
platform and every modern Python 3** — there are no machine-specific values.

A correct run prints, in order:

1. A line of 44 `=` characters.
2. The title-cased heading, centred: `The River And The Reader`.
3. Another line of 44 `=` characters, then a blank line.
4. `Preview:  the river and the reader A river starts ...`
5. `Heading reversed:  redaeR ehT dnA reviR ehT`
6. `First / last body word:  'river' / 'you'`, then a blank line.
7. A statistics table:
   - header row `Statistic` / `Value`
   - a dashed rule
   - `Lines` = **9**
   - `Words` = **105**
   - `Characters` = **556**
   - `Unique words` = **66**
8. A blank line, then
   `Most common word:  "river" (11 times, 10.5% of words)`.

The centred heading and table rows contain trailing spaces from the f-string
width specs; that is expected. If your numbers differ, you edited the sample
file — restore it from git (`git checkout -- examples/sample.txt`).
