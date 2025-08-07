import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# ✅ Load trained LSTM model
model = tf.keras.models.load_model("models/lstm_model.h5", custom_objects={"mse": tf.keras.losses.MeanSquaredError()})

# ✅ Load historical stock data
df = pd.read_csv("data/TSLA_data_with_indicators.csv", index_col="Date", parse_dates=True)

# ✅ Select features and target
features = ["Close", "SMA_50", "SMA_200", "RSI", "MACD", "MACD_Signal", "BB_High", "BB_Low"]
target = "Close"

# ✅ Normalize data
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df[features])

# ✅ Convert data into sequences for LSTM
def create_sequences(data, seq_length=50):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])  # Predicting 'Close' price
    return np.array(X), np.array(y)

seq_length = 50
X_test, y_test = create_sequences(df_scaled, seq_length)

# ✅ Make predictions
y_pred_scaled = model.predict(X_test)

# ✅ Convert predictions back to original scale
y_pred = scaler.inverse_transform(
    np.hstack([y_pred_scaled, np.zeros((len(y_pred_scaled), len(features) - 1))])
)[:, 0]

# ✅ Convert y_test back to original scale
y_test = scaler.inverse_transform(
    np.hstack([y_test.reshape(-1, 1), np.zeros((len(y_test), len(features) - 1))])
)[:, 0]

# ✅ Plot actual vs. predicted prices
plt.figure(figsize=(12, 6))
plt.plot(df.index[seq_length:], y_test, label="Actual Price", color="blue")
plt.plot(df.index[seq_length:], y_pred, label="Predicted Price", color="red", linestyle="dashed")
plt.legend()
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.title("Backtesting AI Predictions vs. Actual Prices")
plt.show()

# ✅ Calculate Mean Squared Error (MSE)
mse = np.mean((y_test - y_pred) ** 2)
print(f"📊 Model Backtest MSE: {mse:.2f}")
