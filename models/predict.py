import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

import tensorflow.keras.losses

# Register the MSE loss function before loading the model
custom_objects = {"mse": tensorflow.keras.losses.MeanSquaredError()}
model = tf.keras.models.load_model("models/lstm_model.h5", custom_objects=custom_objects)


# Load dataset
df = pd.read_csv("data/TSLA_data_with_indicators.csv", index_col="Date", parse_dates=True)

# Select features
features = ["Close", "SMA_50", "SMA_200", "RSI", "MACD", "MACD_Signal", "BB_High", "BB_Low"]
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df[features])

# Prepare last sequence for prediction
seq_length = 50
X_input = np.array([df_scaled[-seq_length:]])  # Last 50 days data

# Predict next day's stock price
predicted_price = model.predict(X_input)
predicted_price = scaler.inverse_transform(
    np.hstack([predicted_price, np.zeros((1, len(features) - 1))])
)[0][0]

print(f"📈 Predicted Next Closing Price: ${predicted_price:.2f}")
