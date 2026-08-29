# Security notes

## What this lab does

It draws charts, saves them to a temporary directory, reads state back off
the returned Figure and Axes objects, and deletes the temporary directory
when each test finishes. It opens no network connection after the
one-time `pip install`, needs no credentials, no `sudo` and no elevated
permissions, and touches nothing outside its own directory and the
system's temporary-file area. All plotted data is invented and is written
out directly in each script.

Section 6 of `tests/run_tests.sh` greps every source file in `examples/`
and `starter/` for `urlopen`, `requests.`, `socket.`, `http://` and
`https://`, and fails if any of them appears. It also checks that no
`.png`, `.svg` or `.pdf` file is left anywhere under the lab directory
after a full run — every image this lab produces lives in a
`tempfile.TemporaryDirectory()` that is deleted automatically when its
`with` block exits, matching the lesson's own claim that the lab writes no
generated image files to disk.

## The virtual environment

`python3 -m venv .venv` creates the environment inside the lab directory,
so nothing installed here can affect the rest of your machine, and
`rm -rf .venv` is a complete undo. The three packages are pinned to exact
versions in `requirements/requirements.txt`, and section 1 of the harness
reads the installed version back and compares it against that file rather
than trusting that the install did what it said.

## The one thing worth carrying away from this particular day

**A plotting helper that draws into "whichever figure is current" is a
shared-mutable-state bug wearing a data-visualization costume.** Exercise
1's `draw_line_pyplot_style` function is not contrived — it is the natural
shape of code written against `plt.plot`/`plt.xlabel`/`plt.title`, and it
silently overlays whatever was drawn last onto whatever gets drawn next
unless something remembers to call `plt.figure()` first. In a training
loop or an evaluation script, that "something" is easy to forget under
deadline pressure, and the failure mode is not a crash — it is a report
where two experiments' curves sit on the same axes with nobody having
asked for that, and nothing in the output flags it as wrong. The object
API's `fig, ax = plt.subplots()` removes the failure mode structurally: a
function that returns its own `fig` and `ax` cannot silently draw into
someone else's, because there is no "someone else's" it could reach
without being handed the object explicitly.

## What this lab deliberately does not claim

`seaborn` is genuinely installed in this authoring environment but is not
imported anywhere in this lab — Day 129 owns statistical plotting with
seaborn, and this lab's tests, scripts and lesson text do not reproduce
any seaborn output. `plotnine` and `plotly` are not installed anywhere in
this authoring environment; both are described from their public
documentation in the lesson's Tools section, explicitly marked as not run
here, and no output attributed to either appears anywhere in this lab or
its lesson.
