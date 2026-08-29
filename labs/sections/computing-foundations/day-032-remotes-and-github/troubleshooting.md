# Troubleshooting — Day 032 lab

## The bare-repository trick (why the "remote" is just a folder)

A server-side remote is a **bare repository**: it stores Git history but has
no working directory of checked-out files. `git init --bare` makes exactly
that. Because a bare repo is what a real remote *is*, you can use a local
folder as a fully honest stand-in for a hosting platform — no network, no
account, no authentication. Everything you learn here transfers unchanged to
a real remote; only the address changes from a folder path to a web URL.

## `unknown switch 'b'` or `error: unknown option -b` on `git init`

Your Git predates 2.28 and lacks `git init -b main`. Use the fallback:

```bash
git init origin.git --bare
git init repo-a
cd repo-a
git symbolic-ref HEAD refs/heads/main   # name the default branch 'main'
```

Everything else in the lab works the same; the branch is simply named
explicitly instead of by the `-b` flag.

## `fatal: remote origin already exists`

You added `origin` twice. Either remove and re-add it, or update its URL:

```bash
git remote remove origin        # then git remote add origin <path>
# or, to change where it points:
git remote set-url origin <path>
```

## `error: failed to push some refs to ...`

The remote has commits your local branch does not. This is the safety
feature working: Git will not let you silently overwrite others' work.
Integrate first, then push:

```bash
git pull origin main   # or: git fetch origin && git merge origin/main
git push origin main
```

## `src refspec main does not match any`

You have not committed yet, so there is no `main` branch to push. Make at
least one commit first (`git add` then `git commit`), then push.

## A push "succeeds" but the change is not there

Push moves **commits**, not uncommitted edits. Run `git status`; if it shows
staged or unstaged changes, you have not committed them yet. Commit, then
push.

## Pointing at a real GitHub (or GitLab/Bitbucket) remote

When you graduate from the local folder to a real platform:

- **HTTPS:** clone/add a `https://...` address. When prompted, use a
  **personal access token** as the password (generate one in the platform's
  developer settings) — modern platforms reject your account password here.
- **SSH:** generate a key pair with `ssh-keygen`, add the **public** key to
  your account, then use a `git@...` address. After the one-time setup, no
  prompt appears.

If a push hangs on a restrictive network, the SSH port may be blocked — try
the HTTPS address instead.
