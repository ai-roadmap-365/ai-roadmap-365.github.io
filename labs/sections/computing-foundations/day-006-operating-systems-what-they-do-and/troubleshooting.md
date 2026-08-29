# Troubleshooting — Day 006 lab

## `ps: illegal option` or strange `ps` output

You are probably in PowerShell or Command Prompt on Windows — those are not
Unix shells. Open a WSL terminal (`wsl` from PowerShell after
`wsl --install`) and run the lab there. `ps aux` works on macOS, Linux, and
WSL.

## `Login shell:` prints nothing (or the tests flag it)

Use the exact form `login_shell="${SHELL}"` in the script (or
`echo "$SHELL"` at the prompt). The dollar sign asks the shell to expand
the variable; without quotes and the `$`, you print a literal word or
nothing. In rare minimal environments `SHELL` may be unset — run
`echo $0` to see what shell you are actually in.

## The script dies partway with no message

If you experimented with `set -euo pipefail`, note the deliberate comment
at the top of both scripts: `ps aux | sort | head` ends with `head` closing
the pipe early, which `pipefail` treats as a failure. The shipped scripts
use `set -eu` for exactly this reason — restore that line.

## `df -h` shows a forest of rows and the mount count looks huge

Normal. macOS splits the system across several APFS volumes, and Linux
mounts many virtual filesystems (`tmpfs`, `proc`, `sysfs`, snap loops).
For this lab, only the row whose last column is `/` matters.

## `No /boot/vmlinuz* image visible from this environment.` on Linux

On WSL and inside containers this is the correct, honest answer: the
running kernel is supplied from outside the filesystem you can see (by
Windows in WSL's case). The tests accept this output. On a regular Linux
install, if `/boot` is empty you may need `sudo ls /boot` to check whether
it is a permissions issue — but do not `sudo` the lab script itself; it
never needs it.

## The top-memory list shows the same app five times

Also normal, and worth noticing: browsers and chat apps run each tab or
view as a separate isolated process on purpose. The lesson's security
section explains why that isolation is a feature.

## `%MEM` values don't add up to 100%

They never will: shared memory is counted in several processes at once,
and the kernel's own memory belongs to no process row. Treat `%MEM` as a
ranking, not an audit.

## Tests fail with `no field is left 'unknown'`

That check is telling you an exercise is still unfinished — search the
starter for `"unknown"` and complete the remaining assignments.

## Windows: `bash` is not recognized

Install WSL: open PowerShell as administrator, run `wsl --install`,
reboot, open the Ubuntu app, and run the lab from there. From Week 2
onward the course assumes a Unix-style shell, so this setup pays off
immediately.
