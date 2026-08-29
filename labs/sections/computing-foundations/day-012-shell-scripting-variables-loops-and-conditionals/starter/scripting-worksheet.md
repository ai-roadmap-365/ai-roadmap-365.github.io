# Scripting worksheet — predict, then run

The best way to know you understand a loop is to predict what it will do
*before* you run it. Do the prediction below by hand first; only then run the
script and compare. A wrong prediction you understand afterwards teaches more
than a lucky right one.

## The input directory

The lab ships a sample directory at `examples/sample-notes/`. It contains
exactly these files:

```text
sample-notes/
├── shopping.txt
├── ideas.txt
├── meeting.md
├── recipe.md
├── budget.csv
└── README
```

## Step 1 — Predict (fill this in before running anything)

Using your understanding of how `backup_notes.sh` counts files by extension,
predict its report for `examples/sample-notes/`:

- Total files: __________
- `txt`: __________
- `md`: __________
- `csv`: __________
- `(no extension)`: __________

Then predict the order the extensions will be printed in. (Hint: the script
pipes the extensions through `sort` before counting — so what determines the
order?)

Predicted order (top to bottom): ________________________________________

## Step 2 — Run and compare

From the lab directory, run your completed script against the sample:

```bash
bash examples/backup_notes.sh examples/sample-notes
```

(Use `examples/backup_notes.sh` to check against the reference, or
`starter/backup_notes.sh` once you have completed all five exercises — they
should produce identical output.)

Write down the actual result:

- Total files: __________
- `txt`: __________
- `md`: __________
- `csv`: __________
- `(no extension)`: __________

## Step 3 — Reconcile

- Did your totals match? If not, which file did you miscount, and why?
- Did the *order* match your prediction? Explain in one sentence what `sort`
  did to the extension list, and where `(no extension)` landed relative to the
  letters — and why.
- The `README` file has no dot in its name. Trace how the `extension_of`
  function decides it has "(no extension)": what does `"${name%.*}"` produce
  for `README`, and why does that equal `README` itself?

## Step 4 — A second prediction (harder)

Suppose you add two more files to the directory: `photo.JPG` (uppercase
extension) and `.gitignore` (a dotfile whose name begins with a dot). Predict:

- Will `photo.JPG` be counted under `JPG` or `jpg`? (The script does not change
  case — so which?)
- Will `.gitignore` be counted, and if so, under what extension? Think about
  what `"${name%.*}"` does to a name that starts with a dot, and check your
  answer by creating the files and re-running. Note anything that surprised
  you — this is exactly the kind of edge case real scripts must handle.
