# Day 020 lab — Build and Inspect a Tiny Web Page

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** How Browsers Render: HTML, CSS, and JavaScript
- **Day number:** 20 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-020-how-browsers-render-html-css-and
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-020-how-browsers-render-html-css-and` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 20's lesson explains what the browser does after it receives a page: parse
HTML into the DOM, parse CSS into the CSSOM, build the render tree, lay it out,
and paint it. This lab makes that concrete. You open a tiny, self-contained web
page that shows all three web languages at once — structure (HTML), style
(CSS), and behavior (JavaScript) — inspect its live DOM in your browser, and
run a static inspector that reads the same file from the command line. Seeing
the page from both sides — the built DOM and the raw source — is the core
skill of debugging any web interface.

## Learning objectives

- Open a local HTML file in a browser and inspect its live DOM with developer tools.
- Watch JavaScript edit the DOM in real time by clicking a button.
- Read a page's structure statically with `grep`/`wc` — no browser needed.
- Extract a page's `<title>`, count its elements, and list its tags from the shell.
- Explain why the static tag count and the live DOM count describe the same page from two directions.

## Prerequisites

- The Day 20 lesson (read it first — it explains the DOM, CSSOM, render tree, layout, and paint).
- A terminal: Terminal.app (macOS), any terminal (Linux), or WSL/Git Bash (Windows).
- Any modern web browser with developer tools (all of them have these, free).
- No programming experience required; every command is given and explained.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution with `bash`, `grep`, `sed`, `sort`, `uniq`, `wc`).
- **Windows** — run the shell scripts under WSL or Git Bash; open the HTML file in any installed browser.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only reads a small text
file and opens a page in a browser; it needs no special RAM, disk, or GPU.

## Required software

- A web browser (Chrome, Edge, Firefox, or Safari) — for viewing and inspecting the page.
- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard text utilities: `grep`, `sed`, `sort`, `uniq`, `wc` — all preinstalled.

## Free and open-source options

Everything in this lab is free. Every browser ships professional developer
tools (Elements, Console, Network, Performance, and Lighthouse) at no cost, and
every shell tool used is open-source or part of your OS. No account, API key,
or purchase is needed.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-020-how-browsers-render-html-css-and
```

## File structure

```text
day-020-how-browsers-render-html-css-and/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── inspect_page.sh             ← YOUR working file (4 exercises)
│   └── render-worksheet.md         ← worksheet for the practice assignment
├── examples/
│   ├── page/
│   │   └── index.html              ← the tiny page you open and inspect
│   └── inspect_page.sh             ← completed reference inspector
├── tests/
│   └── run_tests.sh                ← automated checks
├── expected-output/
│   ├── inspect_page.txt            ← real captured inspector run
│   ├── test-run.txt                ← real captured test run
│   └── FIELDS.md                   ← required fields on every platform
├── requirements/
│   └── README.md                   ← dependency statement (browser + shell)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. Open the page in your browser (macOS shown; see notes for Linux/Windows)
open examples/page/index.html          # Linux: xdg-open examples/page/index.html

# 2. Inspect the same file statically from the command line
bash examples/inspect_page.sh examples/page/index.html

# 3. Your task: complete the four exercises in the starter, then run it
bash starter/inspect_page.sh examples/page/index.html

# 4. Check your work
bash tests/run_tests.sh
```

In the browser, press F12 (or right-click → Inspect) to open developer tools.
Look at the **Elements** panel (the live DOM), switch to the **Console** and
run `document.querySelectorAll('*').length`, then click the page's button and
watch the paragraph's text change in the Elements panel.

## What the commands do

- `open examples/page/index.html` — opens the committed page in your default
  browser so you can view and inspect it. On Linux use `xdg-open`; on Windows,
  drag the file onto a browser window.
- `bash examples/inspect_page.sh examples/page/index.html` — the reference
  static inspector: it uses `sed` to pull the `<title>`, `grep -oE` to list
  every opening tag, `sort | uniq -c` to tally element types, `wc -l` to count
  them, and `grep -q` to confirm the `<style>` and `<script>` blocks. No
  browser, no network.
- `bash starter/inspect_page.sh examples/page/index.html` — the same skeleton
  with four values set to `unknown`; each exercise comment names the exact
  command to use. Edit the file and replace each `unknown`.
- `bash tests/run_tests.sh` — checks that the committed page has the required
  structural tags and that the inspector extracts the right title and counts
  exactly 10 elements; exits 0 on success, non-zero on any failure.

## Expected output

See [`expected-output/inspect_page.txt`](expected-output/inspect_page.txt) — a
real captured run:

```text
=== Static page inspection: examples/page/index.html ===
Title: Tiny Web Page: Structure, Style, and Behavior
HTML elements (opening and void tags): 10
Distinct element types used:
     1 body
     1 button
     1 h1
     1 head
     1 html
     1 meta
     1 p
     1 script
     1 style
     1 title
Has <style> block (CSS / presentation): yes
Has <script> block (JavaScript / behavior): yes
=== End of inspection ===
```

The count of 10 matches what the browser Console reports for
`document.querySelectorAll('*').length` — each element has exactly one opening
tag. [`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the fields
that must appear on every platform.

## Validation steps

1. Open `examples/page/index.html` in a browser and confirm you see a heading, a navy paragraph, and a button.
2. Click the button and confirm the paragraph text changes to "Changed by JavaScript!".
3. Run `bash examples/inspect_page.sh examples/page/index.html` and confirm the title and the count of 10.
4. Complete `starter/inspect_page.sh` (replace every `unknown`) and confirm it prints the same values.
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `21 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. It uses no browser and no
network. A captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

Nothing to clean up: the scripts only read a local file and print to the
console, and the page writes nothing. To reset any edits, restore the files
from git: `git checkout -- examples/page/index.html starter/inspect_page.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (button not
reacting, wrong directory, DevTools not opening, count differences, Windows
notes).

## Security notes

See [security.md](security.md). Short version: the page is static and
self-contained, its script only edits its own DOM and makes no network calls,
the inspector only reads text, and nothing needs elevated privileges — but the
habit to keep is to open local files you can read, not untrusted HTML.

## Extension exercises

1. Add a second CSS rule to the `<style>` block (for example, style the `<h1>`)
   and re-run the inspector — note that the element count is unchanged because
   CSS never adds DOM nodes.
2. Add a second paragraph in the HTML and confirm the element count rises by
   one in both the inspector and the browser Console.
3. Use the browser's **Lighthouse** panel to audit the page (served locally or
   any public page) and connect one flagged issue back to a stage of the
   critical rendering path.
4. In the **Performance** panel, record a page load and find the layout and
   paint events in the timeline.

## Navigation

- **Previous day:** Day 19 — HTTPS and TLS: Encryption on the Wire (`labs/sections/computing-foundations/day-019-https-and-tls-encryption-on-the/`, to be written).
- **Next day:** Day 21 — Inspecting Traffic with curl and Developer Tools (`labs/sections/computing-foundations/day-021-inspecting-traffic-with-curl-and-developer/`, to be written).
