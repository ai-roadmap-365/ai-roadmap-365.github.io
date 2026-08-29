# Troubleshooting — Day 014 lab

## `error: give one existing directory to organize`

You ran the script without a target folder, or the folder does not exist.
Create it first and pass its path: `mkdir -p ~/organize-demo` then
`bash examples/organize_files.sh --dry-run ~/organize-demo`.

## The dry run seems to move files

It must not — a dry run only prints. If files actually moved, you left off the
`--dry-run` flag or put it after the folder in a way your shell mis-parsed.
The flag can go before or after the folder, but check it is spelled exactly
`--dry-run` and is passed as its own argument.

## A file with no extension (like `readme`) was not sorted

That is by design. Files with no dot in the name, and dotfiles such as
`.gitkeep`, are skipped so the script never invents a folder for them. Give
the file an extension if you want it sorted, or extend the script (see the
lesson's extension challenge).

## `photo.JPG` and `photo.jpg` ended up in the same folder

Also by design: the script lowercases extensions, so both land in `jpg/`.
This keeps you from ending up with separate `JPG/` and `jpg/` folders.

## A second run says `0 file(s) organized` — did it fail?

No — that is the script being **idempotent**. After the first run the files
already live in their subfolders, which the top-level scan does not descend
into, so there is nothing left to move. Zero moves on a second run is the
correct, safe result.

## `Permission denied` when running the script

Run it through bash explicitly: `bash examples/organize_files.sh ...`. You do
not need to `chmod +x` it. You never need `sudo` for this lab; if a tutorial
ever tells you to `sudo` a script you have not read, stop and read it first.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and follow the Linux path). The
script and tests run unchanged inside WSL.

## I want to actually schedule it, and cron does nothing

Scheduling is intentionally outside this lab, but the usual cause is a relative
path: cron runs with a bare environment and an unpredictable working directory.
Always use absolute paths for both the script and the target folder in a
crontab line, and redirect output to a log (`>> file 2>&1`) so you can see what
happened. See `examples/schedule-examples.md`.
