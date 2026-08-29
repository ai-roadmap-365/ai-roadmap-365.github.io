# Security notes — Day 003 lab

- **What the scripts do:** read cache/RAM sizes from the OS, then write one
  ~200 MB temporary file (`read-speed-testfile.bin`) **inside this lab
  directory**, time reading it twice, and delete it on exit via a `trap`.
  Nothing is written outside the lab directory; there is no network access.
- **Privileges:** everything runs as your normal user. No `sudo` is
  required. The optional Linux "drop caches" tip in the troubleshooting
  file *does* need sudo — it is clearly marked optional and you can skip it.
- **Disk:** the temporary file is the only footprint and is removed
  automatically. If a hard kill interrupts the script, delete the file
  manually.
- **Privacy:** cache and RAM sizes are generic hardware facts, safe to
  share. As with Day 1, avoid posting full profiles of employer-managed
  machines.
- **Read before running:** the scripts are short and commented — read them
  first, as with every lab in this course.
