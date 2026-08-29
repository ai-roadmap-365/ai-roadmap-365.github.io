# Security notes — Day 031 lab

- **Everything happens in a temporary directory.** Each script calls
  `mktemp -d` to create a fresh, private workspace and deletes it on exit via
  `trap cleanup EXIT`. The lab never writes into your real projects, your home
  directory, or any existing git repository.
- **No network, ever.** There is no `git clone`, `git push`, `git pull`, or
  any other remote operation. `metadata.yml` records `requires_network: false`.
  The lab runs identically on a fully offline machine.
- **A local-only git identity.** The scripts set `user.name` and `user.email`
  with `git config --local`, so the throwaway identity
  (`learner@example.invalid`) applies **only** to the temporary repository and
  never edits your global `~/.gitconfig`. The `.invalid` address is a reserved
  non-routable domain, so nothing could ever be sent to it.
- **No elevated privileges.** Nothing here needs `sudo`. If a tutorial ever
  tells you to `sudo` a git command you have not read, stop and read it first.
- **Read before you run.** Both scripts are short and commented — read them
  before executing, a habit worth keeping for every script you download.
