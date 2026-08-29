# Trace worksheet — be the CPU before you run the CPU

Work through all three programs **by hand, on this sheet, before running
anything**. That order matters: predicting first and checking second is how
you find out whether your mental model of fetch-decode-execute is right.
The programs live in `../examples/programs/`.

Rules of the machine (same as the lesson):

- Four registers — R1, R2, R3, R4 — all start at 0.
- The PC starts at 0 and moves to the next line after each fetch.
- `LOAD Rn,value` puts a number in a register. `ADD Ra,Rb->Rc` adds two
  registers into a third (which may be one of the sources). `PRINT Rn`
  emits `OUTPUT: <value>`. `HALT` stops the machine.

Fill every empty cell. The first row of program 1 is done for you.

## Program 1 — `trace-01.txt`

```text
LOAD R1,4
LOAD R2,7
ADD R1,R2->R3
PRINT R3
HALT
```

| PC | Instruction | What the execute step does | R1 | R2 | R3 | R4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | `LOAD R1,4` | R1 gets the value 4 | 4 | 0 | 0 | 0 |
| 1 | `LOAD R2,7` |  |  |  |  |  |
| 2 | `ADD R1,R2->R3` |  |  |  |  |  |
| 3 | `PRINT R3` |  |  |  |  |  |
| 4 | `HALT` |  |  |  |  |  |

- Predicted `OUTPUT:` line(s): `OUTPUT: ____`
- Predicted final line: `Final registers: R1=__ R2=__ R3=__ R4=__`
- Predicted instruction count in `HALT reached after __ instructions.`

## Program 2 — `trace-02.txt`

```text
LOAD R1,10
ADD R1,R1->R2
ADD R2,R2->R2
PRINT R2
HALT
```

Watch the third line closely: R2 is both a source and the destination. The
ALU reads the old value, computes, and only then does the write-back
replace it.

| PC | Instruction | What the execute step does | R1 | R2 | R3 | R4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | `LOAD R1,10` |  |  |  |  |  |
| 1 | `ADD R1,R1->R2` |  |  |  |  |  |
| 2 | `ADD R2,R2->R2` |  |  |  |  |  |
| 3 | `PRINT R2` |  |  |  |  |  |
| 4 | `HALT` |  |  |  |  |  |

- Predicted `OUTPUT:` line(s): `OUTPUT: ____`
- Predicted final line: `Final registers: R1=__ R2=__ R3=__ R4=__`
- Predicted instruction count in `HALT reached after __ instructions.`

## Program 3 — `trace-03.txt`

```text
LOAD R1,6
LOAD R2,2
ADD R1,R2->R1
PRINT R1
ADD R1,R2->R1
PRINT R1
HALT
```

Two `PRINT`s: each one emits the register's value *at that moment*, so the
two output lines will differ.

| PC | Instruction | What the execute step does | R1 | R2 | R3 | R4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | `LOAD R1,6` |  |  |  |  |  |
| 1 | `LOAD R2,2` |  |  |  |  |  |
| 2 | `ADD R1,R2->R1` |  |  |  |  |  |
| 3 | `PRINT R1` |  |  |  |  |  |
| 4 | `ADD R1,R2->R1` |  |  |  |  |  |
| 5 | `PRINT R1` |  |  |  |  |  |
| 6 | `HALT` |  |  |  |  |  |

- Predicted `OUTPUT:` line(s): `OUTPUT: ____` and `OUTPUT: ____`
- Predicted final line: `Final registers: R1=__ R2=__ R3=__ R4=__`
- Predicted instruction count in `HALT reached after __ instructions.`

## Check yourself

Only now, run each program and compare every prediction:

```bash
bash ../examples/toy_cpu.sh ../examples/programs/trace-01.txt
bash ../examples/toy_cpu.sh ../examples/programs/trace-02.txt
bash ../examples/toy_cpu.sh ../examples/programs/trace-03.txt
```

For any cell you got wrong, write one sentence below it about *why* — the
mistake is more valuable than the correction. The most common ones: using
a register's new value one step too early (program 2), and forgetting that
`PRINT` reports the value at that instant, not the final value (program 3).
