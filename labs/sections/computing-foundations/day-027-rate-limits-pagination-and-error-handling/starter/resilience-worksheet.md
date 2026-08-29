# Resilience worksheet — Day 027

Fill this in from a real run of your completed `starter/resilient_client.sh`
(or the reference `examples/resilient_client.sh`). The point is to prove your
client is genuinely resilient — that it terminates, classifies, and paginates —
not merely optimistic.

## 1. Backoff terminates (it does NOT loop forever)

- Retry cap you set (`MAX_ATTEMPTS`): ______
- Base delay you set (`BASE_DELAY`, seconds): ______
- How many **retries** did the backoff function make before giving up? ______
  (Read the `made N retries before giving up` line.)
- Status code the `/status/429` endpoint returned on your attempts: ______
  (It may show `503`/`504` if the shared test server's gateway was busy — the
  client treats those the same as `429`. Note whichever you saw.)

## 2. Classify: retry vs do not retry

- `/status/500` was classified as: ______________________  (retry? yes / no)
- `/status/404` was classified as: ______________________  (retry? yes / no)
- In one sentence, why is the 404 decision different from the 500 decision?

  ________________________________________________________________________

## 3. Pagination

- Items on page 1: ______
- Items on page 2: ______
- **Total posts collected across the 2 pages:** ______

## 4. Short reflection (4–6 sentences)

Explain, in your own words, why your backoff loop is **guaranteed to
terminate**, and what would go wrong if you removed the `MAX_ATTEMPTS` cap.
Mention what role jitter plays when many clients hit the same limit at once.

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________
