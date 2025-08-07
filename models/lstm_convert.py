import tensorflow as tf

# ✅ Define custom loss function explicitly
custom_objects = {"mse": tf.keras.losses.MeanSquaredError()}

# ✅ Load your original model with the correct custom_objects
model = tf.keras.models.load_model(
    "C:/Users/91882/Desktop/College Projects/Ai driven Algorithm trading projext and paper/project/models/lstm_trained_model.h5",
    custom_objects=custom_objects
)

# ✅ Re-save the model in a compatible format
model.save("C:/Users/91882/Desktop/College Projects/Ai driven Algorithm trading projext and paper/project/models/lstm_fixed.h5")

print("✅ Model re-saved successfully as lstm_fixed.h5!")
