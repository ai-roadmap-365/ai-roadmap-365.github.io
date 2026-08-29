# Security notes — Day 041 lab

- **What the scripts do:** create a git repository in a fresh temporary directory
  (`mktemp -d`), install a hook, make commits, run a pipeline, and delete the
  temporary directory on exit. They make **no network connections**, need **no
  elevated privileges**, and write **nothing outside their own temp directory**.

- **Temp dir only:** every script confines its work to a temporary directory it
  owns and removes. Your real repositories, your global git config, and your home
  directory are untouched. The scripts set a *local* git identity
  (`git config user.email ...` without `--global`) so they never alter your
  global git settings.

- **Hooks run code — review before installing untrusted hooks.** A git hook is a
  program git executes automatically on your machine. Installing a hook (or a
  CI action, or a pre-commit config) from an untrusted source means running a
  stranger's code with your permissions, on every commit. **Read any hook before
  you install it.** The hooks in this lab are short and commented for exactly
  that reason; read `examples/pre-commit` before trusting it.

- **`--no-verify` is a foot-gun, not a feature to lean on.** Bypassing hooks
  routinely defeats the safety they provide. Use it only in a real emergency, and
  rely on CI as the backstop that cannot be individually skipped.

- **Secrets:** this lab uses none, which is the point — automation that needs a
  password, key, or token must read it from the environment or a secret store,
  never hard-code it in a script or commit it to a repository, because git
  history is permanent and copied to every clone.
