# Ports worksheet — Day 017

Fill this in from your own machine using the commands in the lesson and the
lab (`lsof -nP -iTCP -sTCP:LISTEN` on macOS, `ss -tlnp` or `netstat -tln` on
Linux, and `nc -z -w 1 127.0.0.1 <port>` for the connection test). Everything
here is read-only and local — you never touch another machine.

## 1. Two ports your machine is listening on

| Port number | IANA class (well-known / registered / ephemeral) | Which service do you think it is, and why? |
| ----------- | ------------------------------------------------ | ------------------------------------------ |
|             |                                                  |                                            |
|             |                                                  |                                            |

Reminder of the ranges: **0–1023** well-known, **1024–49151** registered,
**49152–65535** ephemeral. Use the process name in the last column of your
listing (and the well-known-port table in the lesson) to make your guess.

## 2. Is port 80 open locally?

Run the loopback probe against the standard HTTP port:

```bash
nc -z -w 1 127.0.0.1 80
```

- Command's exit status (`echo $?` right after): __________
- Is anything listening on port 80 of this machine? (open / closed): __________
- If it is closed, what error would a browser-style client report when it
  tried to connect there? __________________________________________________

## 3. One sentence in your own words

Explain, in one sentence, the difference between a **port** and an **IP
address**, using the "building with an address, apartments with numbers"
analogy from the lesson:

_______________________________________________________________________________
