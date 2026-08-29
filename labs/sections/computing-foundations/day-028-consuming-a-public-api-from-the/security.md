# Security notes — Day 028 lab

- **No key, no secret.** Open-Meteo is a free, no-key API, so this lab has no
  credential to protect. That is exactly why it is a safe place to learn the
  request-and-parse loop.
- **If you later use a key-based API, keep the key in an environment variable.**
  As on Day 25, reference it as `$API_KEY` and never paste it into the script or
  the URL. A key hard-coded in a file gets committed and shared with everyone
  who reads it; a key typed on the command line lands in your shell history and
  the process list. Prefer sending a key in a header (`-H "Authorization:
  Bearer $API_KEY"`) over the query string, because URLs are logged by servers
  and proxies along the way.
- **The client only sends a location.** Each request tells Open-Meteo the
  latitude and longitude you asked about and your IP address. Repeated lookups
  of your home coordinates are a small breadcrumb trail — be deliberate about
  what you send, and read a service's terms to know what it logs.
- **Always set a timeout.** The client uses `curl --max-time 15` so a hung or
  slow server cannot freeze your script. Do this for every API call you write.
- **Read a script before running it.** Both scripts here are short and
  commented; the course's habit is to read any shell script before executing
  it. Nothing in this lab needs `sudo`.
