# Troubleshooting — Day 002 lab

## `ERROR at PC=N: unknown opcode 'load'`

Opcodes must be uppercase: `LOAD`, `ADD`, `PRINT`, `HALT`. The simulator is
deliberately strict, because real CPUs are stricter still — a single wrong
bit in an opcode is a different instruction or an illegal one. Fix the
case and rerun.

## `ERROR at PC=N: unknown register 'R5'` (or `R0`)

The machine has exactly four registers: `R1`, `R2`, `R3`, `R4`. There is
no R0 and no R5 — just as a real CPU has a fixed register set baked into
its silicon. Use one of the four valid names.

## `ERROR at PC=N: ADD needs the form: ADD Ra,Rb->Rc`

Check the punctuation: a comma between the two sources and an ASCII arrow
`->` before the destination, e.g. `ADD R1,R2->R3`. Spaces around the comma
and arrow are fine; a Unicode arrow (`→`) pasted from a document is not.

## `ERROR: the program ended without HALT …`

Every program must end by telling the machine to stop. The message is the
lesson: a real CPU never decides it is finished — it fetches whatever the
PC points at next, forever, even if that memory is garbage. Add `HALT` as
the last instruction.

## `error: program file not found: …`

Run the commands from the lab directory (the one containing `README.md`),
so relative paths like `examples/programs/trace-01.txt` resolve. If you
are inside `starter/`, the paths start with `../examples/` instead — the
worksheet uses that form.

## `Permission denied` when running the simulator

You do not need to make anything executable — invoke it through bash
explicitly: `bash examples/toy_cpu.sh <program>`. If you prefer
`./examples/toy_cpu.sh`, first run `chmod +x examples/toy_cpu.sh`.

## The tests fail on `my_program: …`

The suite requires your `starter/my_program.txt` to (a) run without
errors, (b) print at least one `OUTPUT:` line, and (c) end with `HALT`.
Run it directly — `bash examples/toy_cpu.sh starter/my_program.txt` — and
the simulator's own error message will point at the offending line.

## My edits to `my_program.txt` vanished after cleanup

`git checkout -- starter/my_program.txt` restores the shipped version —
that is what it is for. Copy your program elsewhere first if you want to
keep it.

## Windows: `bash` is not recognized

Install WSL (`wsl --install`, then open Ubuntu) and run the lab there
unchanged. The simulator is a bash script, so PowerShell alone cannot run
it; Git Bash generally works too, but WSL matches the environment the
whole course assumes.
