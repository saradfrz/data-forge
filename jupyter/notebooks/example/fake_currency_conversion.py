import csv
import datetime
import random

# Configuration
CURRENCIES = ["USD", "EUR"]  # List of currencies to convert from BRL
YEARS = [2023, 2024]
OUTPUT_FILE = "jupyter/notebooks/example/fake_currency_conversion_from_brl.csv"

# Reference exchange rates (1,000 units in BRL)
REFERENCE_RATES = {
    "USD": 5759 / 1000,  # 1 USD = 5.759 BRL
    "EUR": 6216 / 1000,  # 1 EUR = 6.216 BRL
}

# Allowable variation range (+/- 20%)
VARIATION = 0.2

def generate_fake_exchange_rate(base_rate):
    """Generates a random fake exchange rate within the specified variation range."""
    min_rate = base_rate * (1 - VARIATION)
    max_rate = base_rate * (1 + VARIATION)
    return round(random.uniform(min_rate, max_rate), 4)

def generate_conversion_csv():
    """Generates a CSV file with fake conversion rates from BRL to other currencies for each day in 2023 and 2024."""
    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Currency", "Exchange Rate (BRL to Currency)"])

        for year in YEARS:
            for month in range(1, 13):
                for day in range(1, 32):
                    try:
                        date = datetime.date(year, month, day).strftime("%Y-%m-%d")
                        for currency, base_rate in REFERENCE_RATES.items():
                            rate = generate_fake_exchange_rate(base_rate)
                            writer.writerow([date, currency, rate])
                    except ValueError:
                        continue  # Skips invalid dates like Feb 30

    print(f"CSV file '{OUTPUT_FILE}' generated successfully.")

if __name__ == "__main__":
    generate_conversion_csv()
