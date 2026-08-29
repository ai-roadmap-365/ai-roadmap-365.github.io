# Security notes — Day 060 lab

- **What the tool does:** reads the directory you name with `--dir`,
  reads only file *names and metadata* (it never opens or reads file
  contents), and prints or writes a small JSON report. It makes **no network
  connections**, needs **no privileges**, and writes only the report file you
  name with `--out`. The test runner builds a throwaway directory with
  `mktemp -d` and removes it on exit.

- **Fewer dependencies is a security posture.** The lab's whole lesson is
  standard-library-first, and that habit is also a security habit: every
  third-party package you install is code from someone else that runs with
  your program's privileges, and the package supply chain has been attacked
  through malicious or hijacked releases. A tool that uses only the standard
  library has a far smaller attack surface — there is nothing extra to trust,
  update, or be compromised through.

- **Read data with `json`, never `eval()`.** When the tool reads a JSON
  report back, it uses `json.load`, which turns text into plain Python values
  and can **never** execute code. Do not reach for `eval()`/`exec()` to
  "parse" a report or any file contents; those run the string as Python, so a
  malicious value could delete files or open a network connection.

- **Treat directory input as untrusted.** The tool walks whatever path you
  give `--dir`. Point it at your own project folders, not at system
  directories you do not control. It only reads metadata, but it is good
  practice to know exactly what you are pointing a file-walking tool at.

- **Fail loudly, not silently.** Every command prints its result and returns
  an exit code, so a person or a script can tell whether it worked. When you
  build the extension challenge (a missing `--dir` printing to standard error
  and exiting non-zero), keep that discipline — a clear error beats a silent
  wrong answer.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/toolkit.py` and `tests/run_tests.sh` before running them.
  Running unread scripts is one of the most common ways developers get
  compromised; the course's rule is that every lab script is small enough to
  read and understand first.
