import json

def load_hourly_rates():
    """Load technology hourly rates from JSON config."""
    with open("config/hourly_rates.json", "r") as file:
        rates = json.load(file)
    return rates  # ✅ Returns a dictionary
