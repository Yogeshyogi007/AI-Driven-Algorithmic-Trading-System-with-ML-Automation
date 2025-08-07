from alpaca_trade_api.rest import REST, TimeFrame
import pandas as pd
import datetime

# Replace with your actual API keys
API_KEY = "PK6TUU8PQAY50QN5MSF5"
API_SECRET = "CEmeaYj0k25JHtqGwodggjb9HEvx5tr371XEnVBJ"
BASE_URL = "https://paper-api.alpaca.markets"  # Use live URL if trading real

# Initialize API
api = REST(API_KEY, API_SECRET, base_url=BASE_URL)


symbol = "TSLA"
timeframe = "1Day"

# Define date range (last 90 trading days)
end_date = datetime.datetime.today().date()
start_date = end_date - datetime.timedelta(days=120)  # 90 trading days ≈ 120 calendar days

# Fetch data with explicit date range
bars = api.get_bars(symbol, timeframe, start=start_date, end=end_date, feed="iex").df


# Save to CSV
bars.to_csv("data/tsla_90_days.csv")
print("✅ Data successfully saved with specified date range!")