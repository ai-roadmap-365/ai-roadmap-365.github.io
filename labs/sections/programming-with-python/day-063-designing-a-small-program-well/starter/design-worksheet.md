# Design worksheet — design it first

Use this for the practice assignment: design a *second* small program on
paper before writing any code, the same way this lab's `summary` tool was
designed. Filling this in first — spec, then modules and signatures, then
which parts are pure — is the whole discipline the lesson teaches. Do not
write a function body until every row below is filled.

## 1. Spec and examples (before any code)

- **One sentence: what does the program do?**
- **Input (what comes in, and from where — argv, a file, stdin):**
- **Output (what goes out, and to where — stdout, exit code):**
- **Three concrete examples** (input → output), including one bad input:
  1. input: … → output: …
  2. input: … → output: …
  3. bad input: … → error message (stderr) and exit code:

## 2. Decompose into functions (signatures before bodies)

One row per function. Mark each **pure** (values in, values out, no I/O)
or **shell** (does I/O). Aim for a pure core and a thin shell.

| Function (name + params) | What it returns | Pure or shell? | One responsibility (one sentence) |
| ------------------------ | --------------- | -------------- | --------------------------------- |
|                          |                 |                |                                   |
|                          |                 |                |                                   |
|                          |                 |                |                                   |
|                          |                 |                |                                   |

## 3. The functional core / imperative shell split

- **Which functions form the pure core (no I/O)?**
- **Which functions form the shell (all the I/O)?**
- **How will you test the core without any files or captured output?**

## 4. Incremental plan (make it work on the simplest case first)

Order the steps you will build and test, smallest working slice first:

1.
2.
3.

## 5. YAGNI check (what you are deliberately NOT building)

List at least two features you could add but will not, because the spec
does not ask for them yet:

- 
- 

## 6. Recorded behaviour (fill in after you build it)

- One good run (command and its output):
- One bad run (command, stderr message, and `echo $?`):
