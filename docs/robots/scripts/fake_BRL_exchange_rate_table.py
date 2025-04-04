import pandas as pd

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exchange Rates</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .exchange-table {{ width: 100%; border-collapse: collapse; }}
        .exchange-table th, .exchange-table td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        .exchange-table th {{ background-color: #f4f4f4; }}
    </style>
</head>
<body>
    <h2>Exchange Rates (BRL to Other Currencies)</h2>
    <table class="exchange-table">
        <thead>
            <tr>
                <th class="date-header">Date</th>
                <th class="currency-header">Currency</th>
                <th class="rate-header">Exchange Rate</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>
"""

# Read data from CSV
df = pd.read_csv("docs/robots/scripts/fake_currency_conversion_from_brl.csv")

rows = "".join(f"<tr><td class='date-cell'>{row['Date']}</td><td class='currency-cell'>{row['Currency']}</td><td class='rate-cell'>{row['Exchange Rate (BRL to Currency)']}</td></tr>" for _, row in df.iterrows())

html_output = html_content.format(rows=rows)

with open("docs/robots/scripts/exchange_rates.html", "w", encoding="utf-8") as file:
    file.write(html_output)

print("HTML file generated: exchange_rates.html")