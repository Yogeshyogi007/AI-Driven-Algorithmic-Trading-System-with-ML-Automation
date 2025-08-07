import tensorflow as tf

# ✅ Load the original model
model = tf.keras.models.load_model(
    "C:/Users/91882/Desktop/College Projects/Ai driven Algorithm trading projext and paper/project/models/lstm_trained_model.h5",
    custom_objects={"mse": tf.keras.losses.MeanSquaredError()}
)

# ✅ Create a new Sequential model to remove batch_shape
new_model = tf.keras.Sequential()
for layer in model.layers:
    new_model.add(layer)

# ✅ Compile the model
new_model.compile(optimizer="adam", loss="mse")

# ✅ Save the model in a compatible format
new_model.save("C:/Users/91882/Desktop/College Projects/Ai driven Algorithm trading projext and paper/project/models/lstm_fixed.h5")

print("✅ Model re-saved successfully as lstm_fixed.h5!")
