# Security notes — Day 045 lab

- **What the program does:** reads one local file, `examples/sample.txt`,
  which sits next to the script, and prints a report to your terminal. It
  makes **no network connections**, writes **no files**, and needs **no
  arguments** or environment variables.
- **File access:** the path is built with `Path(__file__).resolve().parent`,
  so the program always reads the sample shipped with the lab and never a file
  you pass in. It opens that file read-only.
- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`; if a tutorial ever tells you to run a script as root without reading
  it, stop and read it first — a habit this course keeps reinforcing.
- **Reading before running:** both Python files are short and commented. Read
  them before you run them. Running unread code — especially anything that
  reads files or reaches the network — is one of the most common ways
  developers get compromised.
- **Your own text:** if you later point the program at your own documents,
  remember that text can contain private information. This lab deliberately
  ships a harmless sample so nothing sensitive is ever printed or committed.
