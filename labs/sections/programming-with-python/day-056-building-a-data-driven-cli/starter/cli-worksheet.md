# CLI design worksheet

Fill this in *before* writing code for the practice assignment. Designing a
CLI on paper first — its subcommands, arguments, data shape, and exit codes —
is exactly the discipline the lesson teaches. One row per subcommand.

## The tool

- **Name of the tool:**
- **One job it does:**
- **Where the data lives (JSON file path/default):**
- **Shape of one record (the dict keys and their types):**

## Subcommands

| Subcommand | Positional args | Options / flags | What it mutates | Prints (stdout) | Exit code(s) |
| ---------- | --------------- | --------------- | --------------- | --------------- | ------------ |
| add        |                 |                 |                 |                 |              |
| list       |                 |                 |                 |                 |              |
| find       |                 |                 |                 |                 |              |
| delete     |                 |                 |                 |                 |              |

## Validation and errors

List at least three bad inputs the tool must reject, and for each: the
message it prints (to **stderr**) and the exit code it returns.

1.
2.
3.

## Idempotence check

For each subcommand, write whether running it twice with the same arguments
leaves the store in the same state as running it once (idempotent) or not,
and why.

- add:
- list:
- find:
- delete:

## Recorded behaviour (fill in after you build it)

- One good run (command and its output):
- One bad run (command, stderr message, and `echo $?`):
