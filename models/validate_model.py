import tensorflow as tf

# ✅ Define custom objects (register 'mse')
custom_objects = {"mse": tf.keras.losses.MeanSquaredError()}

# ✅ Load trained LSTM model with custom loss function
model_path = "C:/Users/91882/Desktop/College Projects/Ai driven Algorithm trading projext and paper/project/models/lstm_trained_model.h5"
model = tf.keras.models.load_model(model_path, custom_objects=custom_objects)

# ✅ Display model summary
model.summary()

print("✅ Model loaded successfully and is ready for trading!")
