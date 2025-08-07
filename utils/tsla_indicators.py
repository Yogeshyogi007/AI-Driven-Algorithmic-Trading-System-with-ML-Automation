import pandas as pd
import ta  # Ensure you've installed it with `pip install ta`

# ✅ Load TSLA dataset
file_path = "C:/Users/91882/Desktop/College Projects/Ai driven Algorithm trading projext and paper/project/data/tsla_90_days.csv"
df = pd.read_csv(file_path)

# ✅ Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])
df.set_index("timestamp", inplace=True)

# ✅ Ensure numerical columns are in correct data type
df[["close", "high", "low", "open", "volume", "vwap"]] = df[["close", "high", "low", "open", "volume", "vwap"]].apply(pd.to_numeric, errors='coerce')

# ✅ Calculate technical indicators
df["SMA_50"] = ta.trend.sma_indicator(df["close"], window=50)
df["SMA_200"] = ta.trend.sma_indicator(df["close"], window=200)
df["RSI"] = ta.momentum.rsi(df["close"], window=14)
df["MACD"] = ta.trend.macd(df["close"])
df["MACD_Signal"] = ta.trend.macd_signal(df["close"])
df["OBV"] = ta.volume.on_balance_volume(df["close"], df["volume"])

# ✅ Handle NaN values (fill instead of dropping all rows)
df.fillna(method="bfill", inplace=True)  # Backfill missing values

# ✅ Save processed data
output_path = "C:/Users/91882/Desktop/College Projects/Ai driven Algorithm trading projext and paper/project/data/tsla_90_days_with_indicators.csv"
df.to_csv(output_path)

print("✅ Data successfully processed with indicators!")
