# Troubleshooting — Day 009 lab

## `Permission denied` when you run `./run.sh`

The execute bit is not set. Either run it through bash (`bash run.sh`) or make
it executable first: `chmod +x run.sh` (or `chmod 754 run.sh`), then check with
`ls -l run.sh` that an `x` now appears in the permission string.

## `No such file or directory`

You are using a relative path from the wrong place. Run `pwd` to see where you
are, then either `cd` to the right directory or use an absolute path. In the
starter, this also appears briefly if you run the script before completing
Exercise 2 (`mkdir -p project/data`) — the later `cd project` then has nothing
to enter. Completing the exercises removes the message.

## The starter prints `REPLACE-ME ...` lines

Those are the unfinished exercises. Open `starter/explore_files.sh` in a text
editor and replace each line that prints `REPLACE-ME` with the exact command
named in the comment beside it (`pwd`, `mkdir -p project/data`,
`touch data/notes.txt report.md`, `chmod 754 run.sh`, `mv report.md data/`).

## `ls` does not show a file whose name starts with a dot

Hidden files (dot-files) are skipped by plain `ls`. Use `ls -a` or `ls -la` to
reveal them.

## macOS shows an `@` after the permission string

On macOS, `ls -l` appends `@` to a file that carries extended attributes, e.g.
`-rw-r--r--@`. This is normal — the nine permission bits before the `@` are the
ones that matter, and the tests ignore the trailing `@`.

## `mktemp` behaves differently or fails

The scripts call `mktemp -d "${lab_dir}/tmp.explore.XXXXXX"`, which works on both
macOS and Linux. If you are on a minimal system without `mktemp`, install the
core utilities (`coreutils`) or run inside WSL.

## A `tmp.explore.*` directory is left behind

Normally the `trap ... EXIT` removes it. A leftover only appears if the script
was killed with an uncatchable signal (`kill -9`). Delete it manually after
checking it is a `tmp.explore.*` directory in this lab folder:
`rm -rf tmp.explore.*` (run from the lab directory, and read the path first).

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and run the commands there). Native
PowerShell does not run these bash scripts.
