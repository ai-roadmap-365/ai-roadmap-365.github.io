# Security notes — Day 042 lab

- **What the scripts do:** read-only inspection. They check whether tools are
  present (`command -v`), print each tool's *version*, and run three tiny
  self-contained skill checks. They make **no network connections**, need
  **no elevated privileges**, and change **nothing** on your real files.
- **The only writes are throwaway and temporary.** The git skill check
  creates a disposable repository under a `mktemp -d` temporary directory and
  deletes it immediately; the SQLite check uses an in-memory database
  (`:memory:`) that never touches disk. Nothing is written to your working
  directory or your home folder.
- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. As the course has stressed since Day 1, if any tutorial ever asks
  you to `sudo` a script you have not read, stop and read it first — these
  scripts are short and commented for exactly that reason.
- **Privacy:** the report lists tool versions, your shell path, and your
  OS kernel. This is mildly identifying (it reveals patch levels), so treat a
  pasted readiness report the way you would a machine profile: fine for a
  class forum, but do not post reports for employer-managed machines. The
  lab deliberately collects no serial numbers, hostnames, or user identifiers.
- **No secrets are touched.** The git commit uses a placeholder identity
  supplied on the command line, not your real git config, and no API keys,
  tokens, or credentials are read or displayed anywhere.
