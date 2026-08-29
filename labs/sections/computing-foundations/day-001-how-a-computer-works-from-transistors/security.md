# Security notes — Day 001 lab

- **What the scripts do:** read system information (`sysctl`, `lscpu`, `df`, `/proc`, `/etc/os-release`) and print it. They make **no network connections**, write **no files**, and change **no settings**.
- **Privileges:** everything runs as your normal user. Nothing in this lab needs `sudo`; if any tutorial ever asks you to `sudo` a script you haven't read, that is your cue to stop and read it — a habit this course will reinforce.
- **Privacy:** a machine profile (CPU, RAM, OS version) is mildly identifying and reveals patch level. Sharing it in a class forum is normally fine; avoid posting profiles of employer-managed machines, and never share serial numbers or hardware UUIDs (this lab deliberately does not collect them).
- **Reading before running:** both scripts are short and commented — read them first. Running unread shell scripts from the internet is one of the most common ways developers get compromised; the course's rule is that every lab script is small enough to read and understand before executing.
