# lookup_capital.py — FIXED: .get() returns a default instead of raising KeyError.
capitals = {"France": "Paris", "Japan": "Tokyo", "Kenya": "Nairobi"}

country = "Germany"  # still not in the dictionary — but now we handle that

# FIX: dict.get(key, default) returns the default when the key is missing
capital = capitals.get(country, "unknown")
print(f"The capital of {country} is {capital}.")
