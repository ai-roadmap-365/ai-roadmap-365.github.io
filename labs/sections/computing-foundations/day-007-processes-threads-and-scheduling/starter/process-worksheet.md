# Process worksheet — Day 007

Fill this in from a real session in one terminal on your own machine.
Commands to use are shown with each field; record what *your* system printed.

## 1. The process population

- Command used: `ps -e | tail -n +2 | wc -l`
- Total processes right now: `____`
- Roughly how many cores does your machine have (from your Day 1 worksheet)? `____`
- One sentence: how can that many processes share that few cores?

  > _your answer here_

## 2. Your shell and its ancestors

- Your shell's PID (`echo $$`): `____`
- Your shell's parent (`ps -o pid,ppid,command -p $$` — the PPID column): `____`
- The parent's own row (`ps -o pid,ppid,command -p <that PPID>`):

  ```text
  (paste the line here)
  ```

- In words: what program spawned your shell (a terminal app? another shell? a login manager?)

  > _your answer here_

## 3. One background-job lifecycle, observed

Run each step and record the evidence:

| Step | Command | What your system printed |
| --- | --- | --- |
| Start | `sleep 300 &` | job number and PID: `____` |
| Capture | `echo $!` | `____` |
| Shell's view | `jobs -l` | `____` |
| System's view | `ps -o pid,ppid,stat,command -p <PID>` | `____` |
| Signal | `kill <PID>` | (usually silent) |
| Exit status | `wait <PID>; echo $?` | `____` |
| Verify | `ps -p <PID>` | `____` |

- The `stat` column showed: `____` — which lifecycle state is that?
- The PPID of your sleep matched: `____` (compare with your `$$` above)

## 4. Polite versus forced: kill versus kill -9

Start two fresh sleepers (`sleep 300 &` twice, capturing each PID from `$!`
right away). Terminate the first with `kill <PID1>` and the second with
`kill -9 <PID2>`, collecting each exit status with `wait <PID>; echo $?`.

- Exit status after plain `kill` (SIGTERM): `____`
- Exit status after `kill -9` (SIGKILL): `____`
- What the shell printed for each (e.g. `Terminated` vs `Killed`):

  ```text
  (paste both lines here)
  ```

- Two or three sentences: what is the difference between the two signals,
  why does the exit-status arithmetic (128 + signal number) explain your
  two numbers, and when is each signal appropriate?

  > _your answer here_
