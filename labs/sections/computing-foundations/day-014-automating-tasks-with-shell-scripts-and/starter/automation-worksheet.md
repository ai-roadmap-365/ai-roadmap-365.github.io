# Automation worksheet — Day 014

Fill this in as you work through the lesson and lab. It feeds directly into
the Week 2 project (a Personal Automation Script). Nothing here touches your
real crontab — you are writing and reading schedules on paper, not installing
them.

## Part 1 — Write two cron expressions

Using only the five-field definition (minute, hour, day-of-month, month,
day-of-week), write the crontab line for each schedule and explain every
field. The command to run in both cases is:

```text
/usr/bin/env bash /absolute/path/to/organize_files.sh "$HOME/Downloads"
```

### 1a. Every day at 8:00 p.m.

```text
Your cron expression:  ____  ____  ____  ____  ____   <command>
```

| Field | Your value | What it means |
| ----- | ---------- | ------------- |
| minute | | |
| hour | | |
| day of month | | |
| month | | |
| day of week | | |

### 1b. Every Monday at 6:00 a.m.

```text
Your cron expression:  ____  ____  ____  ____  ____   <command>
```

| Field | Your value | What it means |
| ----- | ---------- | ------------- |
| minute | | |
| hour | | |
| day of month | | |
| month | | |
| day of week | | |

## Part 2 — Predict the dry-run output

Suppose the target folder contains exactly these entries before you run the
script:

```text
budget.xlsx
photo1.JPG
photo2.jpg
readme
notes.txt
.gitkeep
organize.log
```

Predict the dry-run output **before running anything**. Answer these:

1. Which subfolders would the script create? (List the extension names.)
   Your answer: ______________________________________________

2. Which files would it report it "would move," and to which folder each?
   Your answer: ______________________________________________

3. Which entries would it skip entirely, and why?
   Your answer: ______________________________________________

4. How many files would the summary line report? ______

> Hints, from the script's rules: extensions are **lowercased** (so `photo1.JPG`
> sorts to `jpg/`, the same folder as `photo2.jpg`); files with **no dot** in
> the name are skipped; **dotfiles** (names starting with `.`) are skipped; and
> the script never sorts its own `organize.log`.

## Part 3 — Check your prediction

Create a scratch folder, recreate the listing above, and run the real script
in dry-run mode. Compare its output with your Part 2 answers.

```bash
mkdir -p ~/organize-demo && cd ~/organize-demo
touch budget.xlsx photo1.JPG photo2.jpg readme notes.txt .gitkeep organize.log
bash /path/to/lab/examples/organize_files.sh --dry-run ~/organize-demo
```

Note any difference between your prediction and the actual output here:

```text
Differences (if any): ______________________________________
```
