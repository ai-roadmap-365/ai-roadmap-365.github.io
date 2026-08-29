# API worksheet — Day 022

Call the three public APIs (from the examples or your completed starter) and
record what YOU got back. Some values are fixed; the ISS position is live, so
yours will differ from anyone else's — that is the point.

## 1. JSONPlaceholder — a to-do item

- Command: `curl -s https://jsonplaceholder.typicode.com/todos/1 | python3 -m json.tool`
- The `title` of to-do #1: `____________________________________`
- Is it `completed`?  (true / false): `______`

## 2. JSONPlaceholder — a user

- Command: `curl -s https://jsonplaceholder.typicode.com/users/1 | python3 -m json.tool`
- Pick ONE field and record it:
  - Field name: `____________`  Value: `____________________________`

## 3. httpbin — echo your request

- Command: `curl -s "https://httpbin.org/get?course=365-days-of-ai&day=22" | python3 -m json.tool`
- What appeared inside the `"args"` object? `____________________________`

## 4. Open Notify — live ISS position

- Command: `curl -s http://api.open-notify.org/iss-now.json | python3 -m json.tool`
- Latitude right now: `____________`   Longitude right now: `____________`
- Roughly what time did you run it? `____________`

## 5. One short paragraph

Using the restaurant analogy, name the menu, the order, and the plate that came
back for one of these calls. Then say which of the three responses was **live
data** and how you could tell.

> _your answer here_
