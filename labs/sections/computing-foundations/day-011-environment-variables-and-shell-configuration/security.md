# Security notes — Day 011 lab

Environment variables are the correct place to hold secrets — and therefore a
place to handle with care. This lab is built so you can practice safely.

- **The scripts hold no real secrets.** Everything is read-only inspection of
  your own environment. The only "secret" anywhere is in `examples/sample.env`,
  and it is an obviously **fake** placeholder (`sk-example-not-a-real-key`),
  present purely to show the dotenv shape.
- **Never commit a real `.env`.** A file holding real keys or passwords must be
  listed in `.gitignore` so it is never added to version control. The single
  most common way developers leak credentials is committing a `.env` (or
  pasting one into an issue or chat). Treat any leaked key as compromised and
  rotate it — generate a new one and revoke the old.
- **The subshell keeps experiments contained.** The variable and PATH demos run
  inside `( ... )`, a child shell. Nothing they set can change your real
  environment, so you can run the lab repeatedly with no lasting effect.
- **No elevated privileges, no network.** Nothing here needs `sudo` or touches
  the network. If any tutorial ever asks you to `sudo` a script you have not
  read, stop and read it first.
- **A dumped environment is mildly identifying.** `printenv` reveals your
  username, home path, locale, and installed tooling. Redact before sharing a
  full environment dump, and never share one that contains a real secret.
