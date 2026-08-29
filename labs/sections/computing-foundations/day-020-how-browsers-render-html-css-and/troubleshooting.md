# Troubleshooting — Day 020 lab

## The button does nothing when I click it

You almost certainly opened the file in a text editor, not a browser. The
button's behavior lives in the page's `<script>`, which only runs inside a
browser. Open `examples/page/index.html` in Chrome, Edge, Firefox, or Safari —
the address bar should show a `file://` path ending in `index.html`.

## `bash: examples/inspect_page.sh: No such file or directory`

You are not in the lab directory. Change into it first, then rerun:

```bash
cd labs/sections/computing-foundations/day-020-how-browsers-render-html-css-and
bash examples/inspect_page.sh examples/page/index.html
```

## `Permission denied` when running a script

You don't need to make it executable — run it through bash explicitly:
`bash examples/inspect_page.sh`. If you prefer `./examples/inspect_page.sh`,
first run `chmod +x examples/inspect_page.sh`.

## The element count is not 10

If you edited `examples/page/index.html`, the count reflects your edits — that
is expected and correct. To restore the shipped page, run
`git checkout -- examples/page/index.html`. If you did not edit the page and
still see a different number, confirm you passed the right file path.

## DevTools won't open in my browser

- Chrome/Edge/Firefox: press F12, or right-click an element and choose
  **Inspect**.
- Safari: enable the Develop menu first (Settings → Advanced → "Show features
  for web developers"), then use Develop → Show Web Inspector.

## The browser Console prints a different number than the script

On this simple page they should both be 10. On real-world pages the live DOM
count (Console) often differs from the static tag count, because scripts add
and remove nodes after load — that difference is exactly the source-versus-DOM
distinction the lesson teaches, not an error.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu) or Git Bash to run the shell
scripts, and open the HTML file in any installed browser.
