# lookup_capital.py — YOUR COPY TO FIX.
# Run it, read the traceback bottom-up, then fix the program so it runs
# cleanly (one good fix: use capitals.get(country, "unknown")).
capitals = {"France": "Paris", "Japan": "Tokyo", "Kenya": "Nairobi"}

country = "Germany"  # BUG: this key is missing — decide how to handle that

print(f"The capital of {country} is {capitals[country]}.")
