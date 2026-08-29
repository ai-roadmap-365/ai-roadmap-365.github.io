# REST worksheet — Day 023

Run the commands (from the examples or your completed starter) against
JSONPlaceholder (`https://jsonplaceholder.typicode.com`) and record what the
server returned. The status codes are real even though the writes are faked.

## 1. Read — status code for a GET

- Command: `curl -s -o /dev/null -w '%{http_code}\n' https://jsonplaceholder.typicode.com/posts/1`
- Status code returned: `____`  (expect 200)

## 2. Create — status code and assigned id for a POST

- Command:
  `curl -s -w '\nHTTP %{http_code}\n' -X POST -H "Content-Type: application/json" -d '{"title":"my post","body":"hello","userId":1}' https://jsonplaceholder.typicode.com/posts`
- Status code returned: `____`  (expect 201)
- The `id` JSONPlaceholder assigned to your new post: `____`

## 3. Delete — status code for a DELETE

- Command: `curl -s -o /dev/null -w '%{http_code}\n' -X DELETE https://jsonplaceholder.typicode.com/posts/1`
- Status code returned: `____`  (expect 200)

## 4. Collection vs item

- Which of your four requests targeted the **collection** (`/posts`)? `____`
- Which targeted an **item** (`/posts/1`)? `____`

## 5. One paragraph

Explain, in your own words (4–6 sentences), why you can safely retry a failed
`GET` or `DELETE` but must be careful retrying a failed `POST`. Name the
property that makes the difference.

> _your answer here_
