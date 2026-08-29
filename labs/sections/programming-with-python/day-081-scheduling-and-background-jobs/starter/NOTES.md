# Your notes — exercises 5 and 6

Write your answers underneath each heading, in sentences. These are the
questions that separate "I scheduled a job" from "I operate a job", and they
are worth more than the code above.

## Exercise 5 — write the schedule files, install nothing

Run the generator against a directory of your own:

```bash
python3 examples/gen_schedules.py --out starter/schedules \
    --hour 2 --minute 30 --project-dir /opt/reports --timezone UTC
```

Open all four files it wrote. Then answer:

### 5a. What does cron give your job, and what does it not?

_(List at least four things about a cron job's environment that differ from
your interactive terminal, and say which line of the generated `.cron` file
compensates for each one.)_

### 5b. What is the install command for each of the three schedulers, and why have you not run it?

_(Quote the three commands from the generator's output. Then say, in one
sentence each, what would change on this machine if you ran them.)_

### 5c. Which of the three would you choose for a job on a laptop, and which for a job on a server that must not miss a run?

_(Name the specific feature that decides it.)_

## Exercise 6 — the operational questions

### 6a. Your job takes 40 seconds and runs every 5 minutes. One day the upstream feed is slow and it takes 6 minutes. Describe exactly what happens, minute by minute, with and without the lock.

_(Your answer here.)_

### 6b. The machine was off from Friday evening until Monday morning. Should the three missed daily runs be made up, one made up, or none? Justify the answer for a report job, and then for a job that sends an email to a customer.

_(Your answer here.)_

### 6c. Your job has run successfully every day for six months. Today somebody edits the crontab and drops the line. How long until anybody notices, and what single mechanism would have caught it the next morning?

_(Your answer here.)_

### 6d. Which of the properties you built today would you add first to a job you inherited, and why that one?

_(Your answer here.)_
