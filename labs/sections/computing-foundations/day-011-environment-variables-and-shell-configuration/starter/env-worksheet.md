# Environment worksheet — Day 011

Fill this in for **your own machine** using the commands from the lesson and lab.
Do **not** edit your real shell config file for this assignment — just identify
the correct one.

## 1. Your PATH

- Command used: `echo "$PATH" | tr ':' '\n' | grep -c .`
- **How many directories are in your PATH?** ______

- Look at the first three entries. Command: `echo "$PATH" | tr ':' '\n' | head -3`
  1. ______________________________________
  2. ______________________________________
  3. ______________________________________

## 2. Your shell and locale

- Command used: `printenv SHELL LANG`
- **Your SHELL:** ________________________  (e.g. `/bin/zsh` or `/bin/bash`)
- **Your LANG:** _________________________  (e.g. `en_US.UTF-8`)
- Which config file does this shell read for a new interactive terminal?
  (`~/.zshrc` for zsh, `~/.bashrc` for bash): ________________________

## 3. An alias you would add

- **Alias definition** (name and command):

  ```bash
  alias ______='______________________________'
  ```

- **Why would you use it?** (1–2 sentences: what does it save you?)

  ____________________________________________________________________

  ____________________________________________________________________

- **Which config file would you add it to, and why is that the right file
  for your shell?**

  ____________________________________________________________________
