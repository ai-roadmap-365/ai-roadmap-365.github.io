# Automation worksheet — Day 041

Fill this in as you work through the lab and the lesson. Keep it: the Week 6
project reuses these decisions.

## 1. What does your pre-commit hook check?

List every check your `pre-commit` hook performs, and state exactly what makes a
commit fail each one.

- Check 1: _______________________________________________
  - A commit fails it when: ______________________________
- Check 2: _______________________________________________
  - A commit fails it when: ______________________________

Which single line in the hook actually causes git to abort the commit?

- Answer: ________________________________________________

## 2. One thing you WOULD automate in this course's workflow

Name a real, repeated task in how you work through this course (for example:
running the day's tests before committing, or reformatting your notes).

- Task: __________________________________________________
- Which rung of the ladder fits it (script / scheduled / hook / CI)? _________
- Why that rung, and not a higher or lower one? __________
  ________________________________________________________

## 3. One thing you would NOT automate

Name a task you have decided to leave manual, and justify it with the heuristic
from the lesson (rare? steps keep changing? needs human judgment? irreversible?).

- Task: __________________________________________________
- Why leave it manual: ___________________________________
  ________________________________________________________

## 4. Reflection (2–3 sentences)

Where would you draw the line between what your local hook checks and what a
shared CI pipeline checks, and why?

- Answer: ________________________________________________
  ________________________________________________________
  ________________________________________________________
