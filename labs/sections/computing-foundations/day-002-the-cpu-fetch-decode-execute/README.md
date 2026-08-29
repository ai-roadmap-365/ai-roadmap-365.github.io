# Day 002 lab — Trace the Machine: a Toy CPU in Your Terminal

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The CPU: Fetch, Decode, Execute
- **Day number:** 2 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-002-the-cpu-fetch-decode-execute
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-002-the-cpu-fetch-decode-execute` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 2's lesson dissects the CPU: registers, the ALU, the control unit, the program counter, and the fetch-decode-execute cycle they perform together. This lab makes the cycle visible. You run a working toy CPU — a bash script that interprets a four-instruction assembly language — and watch it fetch, decode, and execute one instruction at a time, printing the PC and every register after each step. Then you become the CPU yourself: you hand-trace three programs on a worksheet *before* running them, and finally you write your own program for the machine.

## Learning objectives

- Read a short assembly-style program and predict exactly what a CPU will do with it, step by step.
- Follow the program counter through a run: where it points, when it advances, and how `HALT` stops the loop.
- Trace register state by hand through `LOAD`, `ADD`, and `PRINT` instructions, including the tricky case where a register is both source and destination.
- Explain the difference between the fetch, decode, and execute steps by pointing at the corresponding lines of the simulator's output.
- Write and run your own program in a four-instruction instruction set, and verify it with an automated test suite.

## Prerequisites

- The Day 2 lesson (it introduces every part of the machine this lab simulates) and the Day 1 lab (basic comfort running commands in a terminal).
- A terminal with `bash`: Terminal.app (macOS), any terminal (Linux), or WSL (Windows).
- No programming experience needed — the whole instruction set is four opcodes.

## Supported operating systems

- **macOS** — fully supported; the scripts run on the preinstalled bash 3.2.
- **Linux** — fully supported on any distribution with bash.
- **Windows** — run everything unmodified inside WSL; native PowerShell is not supported for this lab because the simulator is a bash script.

## Hardware requirements

Any computer that can open a terminal. The simulator is a few kilobytes of shell script; it needs no minimum RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard utilities used by the scripts: `tr`, `grep`, `sed`, `mktemp` — all part of the base system.

## Free and open-source options

Everything in this lab is free: bash and every utility used ship with your operating system. No account, API key, download, or purchase is needed.

## Installation

None. From the repository root:

```bash
cd labs/sections/computing-foundations/day-002-the-cpu-fetch-decode-execute
```

## File structure

```text
day-002-the-cpu-fetch-decode-execute/
├── README.md                        ← you are here
├── metadata.yml                     ← machine-readable lab metadata
├── starter/
│   ├── trace-worksheet.md           ← YOUR worksheet: predict before you run
│   └── my_program.txt               ← YOUR program (ships working; extend it)
├── examples/
│   ├── toy_cpu.sh                   ← the toy CPU simulator (read it!)
│   └── programs/
│       ├── add-two-numbers.txt      ← the demo program from the lesson
│       ├── trace-01.txt             ← worksheet program 1
│       ├── trace-02.txt             ← worksheet program 2
│       └── trace-03.txt             ← worksheet program 3
├── tests/
│   └── run_tests.sh                 ← automated checks (27 checks)
├── expected-output/
│   ├── add-two-numbers-run.txt      ← real captured run
│   ├── trace-01-run.txt             ← real captured run
│   ├── trace-02-run.txt             ← real captured run
│   ├── trace-03-run.txt             ← real captured run
│   └── my-program-starter-run.txt   ← real captured run of the unmodified starter
├── requirements/
│   └── README.md                    ← dependency statement (none beyond bash)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory, in this order:

```bash
# 1. Watch the machine run the lesson's demo program
bash examples/toy_cpu.sh examples/programs/add-two-numbers.txt

# 2. STOP. Open starter/trace-worksheet.md and hand-trace all three
#    programs — fill in every cell BEFORE running them.

# 3. Check your predictions against the real machine
bash examples/toy_cpu.sh examples/programs/trace-01.txt
bash examples/toy_cpu.sh examples/programs/trace-02.txt
bash examples/toy_cpu.sh examples/programs/trace-03.txt

# 4. Run, then extend, your own program
bash examples/toy_cpu.sh starter/my_program.txt

# 5. Check everything
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/toy_cpu.sh <program-file>` — starts the simulator: it loads the program file into an array (its "memory", one instruction per cell), sets registers R1–R4 to 0 and the PC to 0, then loops. Each iteration prints a `FETCH` line (the PC and the raw instruction), advances the PC, prints a `DECODE` line (the opcode and operands it recognized), an `EXECUTE` line (the effect), and a `REGS` line (all four registers). `PRINT` emits an `OUTPUT:` line; `HALT` stops the loop and prints the instruction count and final registers. Bad opcodes, bad register names, and programs without `HALT` end the run with a non-zero exit code.
- The instruction set the simulator accepts (uppercase opcodes, one instruction per line, `#` starts a comment): `LOAD Rn,value`, `ADD Ra,Rb->Rc`, `PRINT Rn`, `HALT`.
- `bash tests/run_tests.sh` — runs all four example programs and checks their exact outputs, step counts, and final register states; runs your `starter/my_program.txt` and checks it reaches `HALT` and prints at least one `OUTPUT:` line; and feeds the simulator deliberately broken programs to confirm they are rejected.

## Expected output

See [`expected-output/add-two-numbers-run.txt`](expected-output/add-two-numbers-run.txt) — a real captured run:

```text
=== Toy CPU ===
Program: examples/programs/add-two-numbers.txt (5 instructions in memory)
Registers start at: R1=0 R2=0 R3=0 R4=0

PC=0  FETCH    LOAD R1,5
      DECODE   opcode=LOAD  dest=R1  value=5
      EXECUTE  R1 <- 5
      REGS     R1=5 R2=0 R3=0 R4=0

PC=1  FETCH    LOAD R2,3
      DECODE   opcode=LOAD  dest=R2  value=3
      EXECUTE  R2 <- 3
      REGS     R1=5 R2=3 R3=0 R4=0

PC=2  FETCH    ADD R1,R2->R3
      DECODE   opcode=ADD  src1=R1  src2=R2  dest=R3
      EXECUTE  R3 <- R1 + R2 = 5 + 3 = 8
      REGS     R1=5 R2=3 R3=8 R4=0

PC=3  FETCH    PRINT R3
      DECODE   opcode=PRINT  reg=R3
      EXECUTE  send R3 to the output
OUTPUT: 8
      REGS     R1=5 R2=3 R3=8 R4=0

PC=4  FETCH    HALT
      DECODE   opcode=HALT
      EXECUTE  stop the clock

HALT reached after 5 instructions.
Final registers: R1=5 R2=3 R3=8 R4=0
```

Captured runs of all three worksheet programs and of the unmodified starter program are in [`expected-output/`](expected-output/) — but do not read the worksheet ones until your predictions are on paper.

## Validation steps

1. Run the demo program (step 1 above) and match it line-for-line against the expected output block here.
2. Complete `starter/trace-worksheet.md` fully — every cell, every predicted `OUTPUT:` line, every final-register prediction — then run the three trace programs and mark each prediction right or wrong.
3. For every wrong cell, write the one-sentence "why" the worksheet asks for.
4. Extend `starter/my_program.txt` so it uses at least one `ADD` and prints at least two values, then run it — it must reach `HALT reached after N instructions.` with no errors.
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `27 checks, 0 failure(s).` The suite checks exact `OUTPUT:` values, fetched-instruction counts, and final register states for all four example programs, structural success for your program, and non-zero exits for four kinds of broken program. The command exits 0 on success and non-zero on any failure, so it can run in CI. (The checks on `my_program.txt` only require it to run, print, and halt — your extensions cannot break the suite as long as the program stays valid.)

## Cleanup

Nothing to clean up: the simulator writes no files (the tests create theirs in a temporary directory that is removed on exit). To reset your work: `git checkout -- starter/my_program.txt starter/trace-worksheet.md`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (unknown opcode errors, register-name errors, the missing-HALT message, Windows notes).

## Security notes

See [security.md](security.md). Short version: a small, readable shell script that interprets text files you control — no network, no privileges, no files written. Read it before running it; that habit is the real security lesson.

## Extension exercises

1. Compute 5 × 6 using only the four instructions (hint: multiplication is repeated addition — chain `ADD`s through a register). Predict the instruction count first.
2. The simulator's PC advances immediately after fetch, *before* execute. Find the two lines in `examples/toy_cpu.sh` where this happens, and write one sentence on what a `JUMP` instruction would have to change for loops to become possible.
3. Add a `SUB Ra,Rb->Rc` instruction to a copy of `toy_cpu.sh` (model it on the `ADD` case), write a program that uses it, and extend a copy of the test suite to cover it.

## Navigation

- **Previous day:** [Day 1 — How a Computer Works: From Transistors to Programs](../day-001-how-a-computer-works-from-transistors/)
- **Next day:** Day 3 — Memory Hierarchy: Registers, RAM, and Storage (`../day-003-memory-hierarchy-registers-ram-and-storage/`, to be written).
