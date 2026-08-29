# Security notes — Day 032 lab

- **What the scripts do:** create Git repositories inside a fresh temporary
  directory (`mktemp -d`), commit a couple of tiny text files, and push/pull
  between them. They make **no network connections**, need **no elevated
  privileges**, and write **nothing outside the temporary workspace**, which
  is removed automatically on exit by a `trap`.
- **Temp dirs only:** all work happens under your system temp directory. The
  scripts never touch your real projects, your global Git config, or your
  home directory. The demo sets its Git identity with per-command `-c
  user.name=...` flags, so it does not change any saved configuration.
- **For real remotes, authenticate safely.** When you move from the local
  folder to a real hosting platform, prove your identity with an **SSH key**
  or a **personal access token** — never your account password, and **never**
  put a secret in the remote URL (for example `https://user:token@...`). A
  secret in a URL leaks into your shell history and `.git/config` in plain
  text.
- **Never commit secrets.** Anything committed to history is effectively
  published the moment you push, and stays in history even after you delete
  the file. Keep API keys and tokens in ignored configuration or environment
  variables, not in the repository. Making a repo public — even briefly —
  should be treated as "assume its contents were copied."
- **Read before you run.** Both scripts are short and commented; read them
  first. Running unread shell scripts is one of the most common ways
  developers get compromised.
