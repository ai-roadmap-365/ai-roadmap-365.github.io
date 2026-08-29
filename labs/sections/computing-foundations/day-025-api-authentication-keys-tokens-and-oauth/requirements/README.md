# Dependencies — Day 025 lab

**Only `curl`.** This lab has no installable dependencies beyond a POSIX
shell and the `curl` command:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- `curl` (preinstalled on macOS and most Linux; on Debian/Ubuntu install with
  `sudo apt install curl`, on Fedora with `sudo dnf install curl`)

Check that curl is present:

```bash
curl --version
```

There is deliberately no `requirements.txt` or `package.json` here. The lab
talks to a public test server (`httpbin.org`) whose authentication endpoints
accept **any** credentials, so **no API key and no account are required**.
The lab needs network access to reach that server; with no network, the
scripts and tests degrade gracefully (they announce the skip and exit 0).
