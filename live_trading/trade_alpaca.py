import numpy as np
import pandas as pd
import tensorflow as tf
import alpaca_trade_api as tradeapi
from sklearn.preprocessing import MinMaxScaler

import sys
import os

# Get the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the project root to sys.path
sys.path.insert(0, project_root)

# Now import the config file
from utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL



# ✅ Load trained LSTM model
model = tf.keras.models.load_model("models/lstm_model.h5", custom_objects={"mse": tf.keras.losses.MeanSquaredError()})

# ✅ Load stock data
df = pd.read_csv("data/TSLA_data_with_indicators.csv", index_col="Date", parse_dates=True)

# ✅ Feature selection
features = ["Close", "SMA_50", "SMA_200", "RSI", "MACD", "MACD_Signal", "BB_High", "BB_Low"]
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df[features])

# ✅ Prepare last sequence for prediction
seq_length = 50
X_input = np.array([df_scaled[-seq_length:]])  # Last 50 days data

# ✅ Predict next day's stock price
predicted_price = model.predict(X_input)
predicted_price = scaler.inverse_transform(
    np.hstack([predicted_price, np.zeros((1, len(features) - 1))])
)[0][0]

print(f"📈 Predicted Next Closing Price: ${predicted_price:.2f}")

# ✅ Connect to Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)

# ✅ Get current stock price
symbol = "TSLA"
current_price = float(api.get_latest_quote(symbol).ask_price)
print(f"💹 Current TSLA Price: ${current_price:.2f}")

# ✅ Define trade strategy
if predicted_price > current_price:
    print("📊 AI suggests **BUY** signal! Placing order...")
    api.submit_order(
        symbol=symbol,
        qty=1,  # Number of shares
        side="buy",
        type="market",
        time_in_force="gtc"
    )
    print("✅ Order placed successfully!")
elif predicted_price < current_price:
    print("📊 AI suggests **SELL** signal! Placing order...")
    api.submit_order(
        symbol=symbol,
        qty=1,
        side="sell",
        type="market",
        time_in_force="gtc"
    )
    print("✅ Order placed successfully!")
else:
    print("⏳ AI suggests **HOLD** strategy. No trade executed.")
