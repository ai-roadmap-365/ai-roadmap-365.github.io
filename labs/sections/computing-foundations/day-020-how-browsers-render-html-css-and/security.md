# Security notes — Day 020 lab

- **The HTML page is static and safe.** `examples/page/index.html` is a single
  self-contained file with no external references — no remote scripts, images,
  fonts, or trackers. Its `<script>` only edits its own DOM (it changes one
  paragraph's text on a button click) and its `console.log`; it makes **no
  network requests** and reads nothing about your machine.
- **The inspector reads, it does not execute.** `inspect_page.sh` and the
  starter perform a static text scan of the HTML with `grep`/`sed`/`wc`. They
  never run the page's JavaScript, open a network connection, or write files
  outside their own console output.
- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. If any tutorial ever tells you to `sudo` a script you haven't read,
  that is your cue to stop and read it first.
- **Open local files, not untrusted ones.** Opening *this* page is safe because
  you can read every line of it. Treat HTML from unknown sources with care: a
  web page is a live, scriptable program, and opening a malicious one runs its
  JavaScript in your browser. The habit this lab builds — inspect before you
  trust — is the same one that keeps you safe on the wider web.
