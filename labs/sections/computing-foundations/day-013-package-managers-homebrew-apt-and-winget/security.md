# Security notes — Day 013 lab

- **What the scripts do:** detect which package managers exist
  (`command -v ...`) and run read-only queries (`--version`, `brew list`,
  `apt-cache policy`). They make **no network connections**, **install nothing**,
  remove nothing, upgrade nothing, write no files outside their own console
  output, and never use `sudo`. The test suite statically enforces this.
- **Real installs need care — and sometimes sudo.** Outside this lab, installing
  software *does* change your system, and on Linux (apt) the changing commands
  require administrator rights via `sudo`. Treat `sudo` as a deliberate act:
  never `sudo` a command you have not read and understood, and prefer official
  repositories over third-party ones.
- **Trust the source.** A package manager verifies that a download matches what
  the repository published, but it cannot vouch for software you point it at
  from an untrusted repository. Read package names carefully — a name that is a
  near-miss of a popular tool ("typosquatting") is a known trick — and prefer
  your operating system's official repository.
- **Privacy:** installing packages tells the repository's servers which
  software a machine requested. The set of packages you have installed is mildly
  revealing; this lab only lists it locally and sends nothing anywhere.
- **Reading before running:** both scripts are short and commented — read them
  first. Running unread shell scripts is one of the most common ways developers
  get compromised; every script in this course is small enough to read before
  you run it.
