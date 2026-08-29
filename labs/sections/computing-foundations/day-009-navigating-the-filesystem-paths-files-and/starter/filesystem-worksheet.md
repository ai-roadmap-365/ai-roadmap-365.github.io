# Filesystem worksheet — Day 009

Fill in every value from your own machine using the commands from the
lesson. Keep this file — Week 2's shell-scripting lessons build on these
skills.

## 1. Your home directory

Run `cd ~` then `pwd`.

| Question | Your answer | Command you used |
| -------- | ----------- | ---------------- |
| Absolute path of your home directory |            | `cd ~ ; pwd`     |

## 2. The same file, two ways

Create a file (for example, `~/day9/hello.txt` via `mkdir -p ~/day9 && touch ~/day9/hello.txt`).
Then write its location two ways and confirm both reach the same file.

| Question | Your answer |
| -------- | ----------- |
| Absolute path to the file (starts with `/`) |            |
| Relative path to the file from one directory above it |            |
| Command you ran to confirm both point at the same file (e.g. `ls -l <path>`) |            |

## 3. A permission you set

Make a file executable: `chmod 754 ~/day9/hello.txt` (or your own file), then
`ls -l` it.

| Question | Your answer |
| -------- | ----------- |
| Full permission string from `ls -l` (e.g. `-rwxr-xr--`) |            |
| Octal number for that string |            |
| Owner triad → octal (show the arithmetic, e.g. r+w+x = 4+2+1 = 7) |            |
| Group triad → octal (show the arithmetic) |            |
| Other triad → octal (show the arithmetic) |            |

## 4. In your own words

In two or three sentences, explain why the execute (`x`) bit is what
separates a plain data file from a runnable script.

_Your answer:_
