# Required output landmarks (all platforms)

`sample-run.txt` in this directory is a real captured run of
`examples/pr_flow.sh` (macOS, bash, 2026-07-12). **Commit hashes and the
temporary directory path change on every run** — that is normal, because Git
computes each commit hash from its content, author, and timestamp. What must
appear on every platform, in this order, is:

1. `Working in throwaway repo: <a temp path>`
2. `== main starts here ==` followed by an `Initial notes` commit.
3. `== Step 1: create a feature branch ==`
4. `== Step 3: the PR ...` showing a `git diff main..feature` that adds the
   line about a pull request being a proposal to merge a branch, then a
   `git log main..feature` listing the `Add greeting line to notes` commit.
5. `== Step 4: ...` where the PR now lists **two** commits: the original plus
   `Address review: clarify wording`.
6. `== Step 5: merge the PR with a merge commit (--no-ff) ==` whose
   `git log --graph --oneline` shows a two-parent **merge commit**
   (`Merge branch 'feature'`) with the `|\` / `|/` branch lines.
7. `== Step 6: contrast the SQUASH strategy ==` where a second branch with two
   `wip` commits lands on `main` as a **single** `Add feature2 note (squashed)`
   commit — the two `wip` commits do **not** appear in `main`'s history.

## Platform differences

- **macOS vs Linux:** identical output. The script uses only portable Git
  commands; the one `sed -i` in-place edit is written with a `.bak` backup so
  it works on both the BSD `sed` (macOS) and GNU `sed` (Linux).
- **Older Git (< 2.23):** `git switch` is unavailable; the script falls back to
  `git checkout -b` / `git checkout` automatically, so the output is the same.
- **Git graph glyphs:** some terminals render the `git log --graph` connector
  lines with slightly different spacing; the two-parent merge structure is the
  invariant, not the exact characters.
