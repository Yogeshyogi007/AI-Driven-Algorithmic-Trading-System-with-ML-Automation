import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler

# ✅ Load the processed dataset
df = pd.read_csv("C:/Users/91882/Desktop/College Projects/Ai driven Algorithm trading projext and paper/project/data/tsla_90_days_with_indicators.csv")

# ✅ Remove SMA_200 (not enough data)
df.drop(columns=["SMA_200"], inplace=True, errors="ignore")

# ✅ Select features for training
features = ["close", "SMA_50", "RSI", "MACD", "MACD_Signal", "OBV"]
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df[features])

# ✅ Convert data into LSTM sequences
def create_sequences(data, seq_length=50):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])  # Predicting 'close' price
    return np.array(X), np.array(y)

seq_length = 50
X, y = create_sequences(df_scaled, seq_length)

# ✅ Split into training (80%) and validation (20%) sets
split = int(len(X) * 0.8)
X_train, X_val = X[:split], X[split:]
y_train, y_val = y[:split], y[split:]

# ✅ Define LSTM Model
model = Sequential([
    LSTM(128, return_sequences=True, input_shape=(seq_length, len(features))),
    Dropout(0.2),
    LSTM(64, return_sequences=False),
    Dropout(0.2),
    Dense(32, activation="relu"),
    Dense(1)  # Predicting 'close' price
])

# ✅ Compile the model
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss="mse")

# ✅ Train the model
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=8,
    verbose=1
)

# ✅ Save the trained model
model.save("C:/Users/91882/Desktop/College Projects/Ai driven Algorithm trading projext and paper/project/models/lstm_trained_model.h5", save_format="h5")

print("✅ Model training complete! Model saved at: models/lstm_trained_model.h5")

