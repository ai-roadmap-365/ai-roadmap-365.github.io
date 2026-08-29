# Webhook worksheet — Day 026

Run the commands (from the examples or your completed starter) and record what
YOUR run produced. The signature is deterministic, so it will match everyone
else's for the same payload and secret — but the echo response and trace ID
are unique to your run.

Sample event used:
`{"event":"invoice.paid","id":"evt_28a7","data":{"amount":4200,"currency":"usd"}}`
Secret used: `whsec_demo_do_not_use_in_production`

## 1. The signature your payload + secret produces

- Command: `printf '%s' "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET"`
- Signature (paste the full value): `sha256=____`
- How many characters is the hex digest? `____`  (should be 64)

## 2. What the echo endpoint reported back

Paste the body the receiver received:

```
____
```

Paste at least one header the receiver saw (e.g. `X-Webhook-Event` or
`X-Webhook-Signature`):

```
____
```

## 3. One reason webhooks retry

- In your own words, one concrete reason a webhook sender retries a delivery:

> _your answer here_

- The problem retrying creates for a receiver, and the property that solves it
  (name it):

> _your answer here_

## 4. Tampering detection

Change one character of the payload (for example `4200` → `999999`), re-run the
signature step, and answer:

- How much of the signature changed? `____`
- Why does that make tampering detectable?

> _your answer here_
