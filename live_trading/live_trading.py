import numpy as np
import pandas as pd
import tensorflow as tf
import alpaca_trade_api as tradeapi
from sklearn.preprocessing import MinMaxScaler
import ta  # Ensure you installed this with `pip install ta`
import sys
import os
import requests
from datetime import datetime

# ✅ Get the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# ✅ Import API keys from config
from utils.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL

# ✅ Load the trained LSTM model
model = tf.keras.models.load_model(
    "C:/Users/91882/Desktop/College Projects/Ai driven Algorithm trading projext and paper/project/models/lstm_trained_model.h5",
    custom_objects={"mse": tf.keras.losses.MeanSquaredError()}
)

# ✅ Initialize Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)

# ✅ Check if market is open
clock = api.get_clock()
if not clock.is_open:
    print("❌ ERROR: Market is currently closed. Try again during market hours.")
    exit()

# ✅ Define stock symbol and sequence length
symbol = "TSLA"
seq_length = 50  # Last 50 days of data needed for prediction

# ✅ Fetch the last 50 days of stock data from Alpaca
bars = api.get_bars(symbol, "1Day", limit=seq_length, feed="iex").df

# ✅ Check if DataFrame is empty BEFORE processing
if bars.empty:
    print("❌ ERROR: No stock data returned from Alpaca. API may not be providing recent data.")
    exit()

# ✅ Print first 5 rows of data for debugging
print("📊 Sample Data from Alpaca API:\n", bars.head())

# ✅ Verify required columns exist before processing
required_columns = ["close", "volume"]
if not all(col in bars.columns for col in required_columns):
    print(f"❌ ERROR: Missing required columns. Available columns: {list(bars.columns)}")
    exit()

# ✅ Compute technical indicators manually (Handle NaN values)
bars["SMA_50"] = ta.trend.sma_indicator(bars["close"], window=50).fillna(0)
bars["RSI"] = ta.momentum.rsi(bars["close"], window=14).fillna(0)
bars["MACD"] = ta.trend.macd(bars["close"]).fillna(0)
bars["MACD_Signal"] = ta.trend.macd_signal(bars["close"]).fillna(0)
bars["OBV"] = ta.volume.on_balance_volume(bars["close"], bars["volume"]).fillna(0)

# ✅ Print DataFrame with Indicators for Debugging
print("📊 Data with Indicators:\n", bars.tail())

# ✅ Select relevant features
features = ["close", "SMA_50", "RSI", "MACD", "MACD_Signal", "OBV"]

# ✅ Normalize data
scaler = MinMaxScaler()
if bars.shape[0] > 0:  # ✅ Ensure DataFrame has rows before scaling
    bars_scaled = scaler.fit_transform(bars[features])
else:
    print("⚠️ ERROR: No valid stock data to process. Exiting.")
    exit()

# ✅ Prepare input sequence for prediction
X_input = np.array([bars_scaled[-seq_length:]])  # Use last 50 days

# ✅ Predict next day's closing price
predicted_price = model.predict(X_input)
predicted_price = scaler.inverse_transform(
    np.hstack([predicted_price, np.zeros((1, len(features) - 1))])
)[0][0]

# ✅ Get current market price
current_price = float(api.get_latest_quote(symbol).ask_price)

# ✅ Define risk management: Stop-Loss & Take-Profit
stop_loss_percentage = 0.03  # 3% below buy price
take_profit_percentage = 0.05  # 5% above buy price

# ✅ Print results
print(f"📈 Predicted Next Closing Price: ${predicted_price:.2f}")
print(f"💹 Current TSLA Price: ${current_price:.2f}")

# ✅ Function to send Telegram Alert
def send_telegram_alert(message):
    TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace with your Bot Token
    TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"  # Replace with your Chat ID
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
    requests.get(url)

# ✅ Define trade decision logic
if predicted_price > current_price:
    print("📊 AI suggests **BUY** signal! Placing order...")

    buy_price = current_price
    stop_loss = buy_price * (1 - stop_loss_percentage)
    take_profit = buy_price * (1 + take_profit_percentage)

    api.submit_order(
        symbol=symbol,
        qty=1,  # Number of shares
        side="buy",
        type="market",
        time_in_force="gtc"
    )
    print(f"✅ Order placed! Stop-Loss: ${stop_loss:.2f}, Take-Profit: ${take_profit:.2f}")

    # ✅ Log the trade
    with open("trade_log.txt", "a") as log:
        log.write(f"{datetime.now()} - BUY at ${buy_price:.2f}, Stop-Loss: ${stop_loss:.2f}, Take-Profit: ${take_profit:.2f}\n")

    # ✅ Send Telegram Alert
    send_telegram_alert(f"📢 AI Trading Alert: TSLA BUY at ${buy_price:.2f}\nStop-Loss: ${stop_loss:.2f}\nTake-Profit: ${take_profit:.2f}")

elif predicted_price < current_price:
    print("📊 AI suggests **SELL** signal! Placing order...")

    sell_price = current_price

    api.submit_order(
        symbol=symbol,
        qty=1,
        side="sell",
        type="market",
        time_in_force="gtc"
    )
    print("✅ Order placed successfully!")

    # ✅ Log the trade
    with open("trade_log.txt", "a") as log:
        log.write(f"{datetime.now()} - SELL at ${sell_price:.2f}\n")

    # ✅ Send Telegram Alert
    send_telegram_alert(f"📢 AI Trading Alert: TSLA SELL at ${sell_price:.2f}")

else:
    print("⏳ AI suggests **HOLD** strategy. No trade executed.")
