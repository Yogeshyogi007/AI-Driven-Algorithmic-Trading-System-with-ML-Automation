import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv("data/TSLA_data_with_indicators.csv", index_col="Date", parse_dates=True)

# Select features and target variable
features = ["Close", "SMA_50", "SMA_200", "RSI", "MACD", "MACD_Signal", "BB_High", "BB_Low"]
target = "Close"

# Normalize data
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df[features])

# Convert data into sequences for LSTM
def create_sequences(data, seq_length=50):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])  # Predicting 'Close' price
    return np.array(X), np.array(y)

# Prepare training and testing data
seq_length = 50
X, y = create_sequences(df_scaled, seq_length)

# Split into training (80%) and testing (20%)
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Build LSTM Model
model = Sequential([
    LSTM(100, return_sequences=True, input_shape=(seq_length, len(features))),
    Dropout(0.2),
    LSTM(100),
    Dropout(0.2),
    Dense(50, activation="relu"),
    Dense(1)  # Output layer: Predicting stock price
])

# Compile model
model.compile(optimizer="adam", loss="mse")

# Train the model
print("🚀 Training LSTM Model...")
history = model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

# Save the trained model
model.save("models/lstm_model.h5")
print("✅ Model saved successfully!")

# Plot training loss
plt.plot(history.history['loss'], label="Training Loss")
plt.plot(history.history['val_loss'], label="Validation Loss")
plt.legend()
plt.title("LSTM Model Training Loss")
plt.show()
