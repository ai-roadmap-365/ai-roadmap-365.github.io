# Request Journey Worksheet — Day 015

Pick a website you use often and trace its request journey with the three
tools. Fill in every field below with your real numbers.

**Site chosen (host name):** _______________________________________

## 1. DNS lookup — name to IP address

Command: `dig +short <host>`

- Resolved IP address(es): _______________________________________
- How many addresses came back? ________

## 2. Round-trip time — ping

Command: `ping -c 2 <host>`

- Round-trip time, packet 1: ________ ms
- Round-trip time, packet 2: ________ ms
- Were any packets lost, or was ping blocked? ________________________
  (Remember: a blocked ping does NOT mean the site is down.)

## 3. Connection stages — curl timings

Command:

```
curl -sS -o /dev/null \
  -w "dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s total=%{time_total}s\n" \
  https://<host>
```

Record each timestamp (elapsed time from the start at which the stage finished):

| Field | Value (seconds) |
| --- | --- |
| `time_namelookup` (DNS done) | |
| `time_connect` (TCP open) | |
| `time_appconnect` (TLS done) | |
| `time_total` (full response) | |

## 4. Read the timeline

Subtract consecutive values to get each stop's cost:

- DNS cost = `time_namelookup` = ________ s
- TCP handshake cost = `time_connect` − `time_namelookup` = ________ s
- TLS handshake cost = `time_appconnect` − `time_connect` = ________ s
- Server + transfer cost = `time_total` − `time_appconnect` = ________ s
- **Which stop cost the most?** _______________________________________

## 5. Narrate the journey (5–8 sentences)

Using your real numbers, tell the story of your site's request journey.
Which stop cost the most? Given your round-trip time from step 2, roughly
how many round trips does the setup imply? Did the site feel latency-bound
(far away, high RTT) or fast and nearby?

_____________________________________________________________________

_____________________________________________________________________

_____________________________________________________________________

_____________________________________________________________________
