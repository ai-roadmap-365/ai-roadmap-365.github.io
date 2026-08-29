# lookup_capital.py — looks up a country's capital city.
capitals = {"France": "Paris", "Japan": "Tokyo", "Kenya": "Nairobi"}

country = "Germany"  # BUG: "Germany" is not a key in the dictionary

print(f"The capital of {country} is {capitals[country]}.")
