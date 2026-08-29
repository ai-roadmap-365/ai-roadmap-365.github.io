# Security notes — Day 005 lab

- **What the scripts do:** read the three committed sample files with
  `file`, `wc`, and `xxd`, copy two of them into a throwaway temp
  directory (removed at the end of the run), and print text. They make
  **no network connections**, modify **no files outside `mktemp -d`
  scratch space**, and change **no settings**.
- **Privileges:** everything runs as your normal user; nothing needs
  `sudo`.
- **Why this lab is itself a security lesson:** file *extensions* are a
  naming convention, not a property of the data — the rename experiment
  proves a `.txt` can be a PNG and vice versa. Attackers exploit exactly
  this gap (a "document" that is really an executable, an upload that
  lies about its type). Tools that check **magic bytes**, like `file`,
  judge content instead of names. Inspecting bytes with `xxd` is
  read-only and always safe; *opening* an unknown file with an
  application is what carries risk, because parsers of complex formats
  have historically been a rich source of vulnerabilities.
- **Privacy:** the committed samples contain no personal data, and the
  walkthrough prints bare file names, not your local paths. If you
  inspect your *own* files while experimenting, remember a hex dump
  reveals everything in the file — including metadata you may not see in
  a normal viewer — so think before pasting dumps of personal files into
  a class forum.
