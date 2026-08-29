# Dependencies — Day 013 lab

**None beyond a POSIX shell.** This lab intentionally has zero installable
dependencies — fitting, since its whole subject is installing software:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- Standard OS utilities: `command`, `uname`, `date`, `sed`, `grep`, `head` —
  all part of the base system.

The lab only *detects and inspects* the package managers you already have; it
installs nothing and needs no network connection. If a manager the script looks
for (brew, apt, apt-get, winget, pip, pip3, npm) is absent, that is simply
reported and is a valid result — you do not need to install anything to
complete the lab.

There is deliberately no `requirements.txt`/`package.json` here.
