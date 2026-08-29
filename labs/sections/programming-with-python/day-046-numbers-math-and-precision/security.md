# Security notes — Day 046 lab

- **What the program does:** pure arithmetic on numbers written into the
  source. It makes **no network connections**, reads **no files**, writes
  **no files**, and needs **no elevated privileges**. Read it first (it is
  short and commented), as you should with any script.

- **`random` is not cryptographically secure.** The lesson introduces
  Python's `random` module for simulations, samples, and shuffles. It uses a
  Mersenne Twister generator that is fast and statistically good but
  **predictable**: given enough outputs, an attacker can reconstruct its
  internal state and predict every future value. **Never use `random` for
  anything that must be unguessable** — passwords, session tokens, API keys,
  password-reset links, one-time codes, or nonces.

- **Use the `secrets` module instead for security.** The standard library's
  `secrets` module draws from the operating system's cryptographically secure
  random source. Reach for it whenever unpredictability protects something:

  ```python
  import secrets
  token = secrets.token_urlsafe(32)   # a safe URL-friendly token
  code = secrets.randbelow(1_000_000)  # a safe 0-999999 one-time code
  ```

  Rule of thumb: `random` for games, tests, and data sampling; `secrets` for
  anything a stranger should not be able to guess.

- **Money math is a correctness-and-trust issue.** Silent float rounding
  errors in financial code are a real-world source of reconciliation bugs and
  disputes. Using `Decimal` (or integer cents) for currency is not just tidy —
  it prevents a class of defects that erode user trust and can have legal and
  audit consequences.
