# Required inspection fields (all platforms)

A correct run of `inspect_page.sh` on the shipped `examples/page/index.html`
prints, in order:

1. `=== Static page inspection: <path> ===`
2. `Title: Tiny Web Page: Structure, Style, and Behavior`
3. `HTML elements (opening and void tags): 10`
4. `Distinct element types used:` followed by ten `  <n> <name>` lines, sorted
   alphabetically: `body`, `button`, `h1`, `head`, `html`, `meta`, `p`,
   `script`, `style`, `title` — each with a count of 1
5. `Has <style> block (CSS / presentation): yes`
6. `Has <script> block (JavaScript / behavior): yes`
7. `=== End of inspection ===`

`inspect_page.txt` in this directory is a real captured run (macOS, bash,
2026-07-12). `test-run.txt` is the captured output of `bash tests/run_tests.sh`.

Platform notes: the tools used (`grep`, `sed`, `sort`, `uniq`, `wc`) are POSIX
and behave identically on macOS and Linux for this page, so the output is the
same on both. The element count (10) equals the number the browser's Console
reports for `document.querySelectorAll('*').length`, because each element has
exactly one opening (or void) tag. If you edit the page, every number moves
with your edits — that is the intended lesson.
