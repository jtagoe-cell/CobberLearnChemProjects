
# Import required libraries
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import (
    VGG16,
    preprocess_input,
    decode_predictions
)

# ==========================================
# A. SELECT AN IMAGE FROM DOWNLOADS
# ==========================================

root = tk.Tk()
root.withdraw()

img_path = filedialog.askopenfilename(
    initialdir="/Users/janicetagoe/Downloads",
    title="Select an Image",
    filetypes=[
        ("Image files", "*.jpg *.jpeg *.png"),
        ("All files", "*.*")
    ]
)

if not img_path:
    print("No image selected. Program stopped.")
    root.destroy()
    exit()

root.destroy()

print("Selected image:", img_path)

# ==========================================
# B. LOAD AND RESIZE IMAGE
# ==========================================

img = image.load_img(img_path, target_size=(224, 224))

# Display selected image
plt.imshow(img)
plt.title("Selected Image")
plt.axis("off")
plt.show()

# ==========================================
# C. CONVERT IMAGE TO NUMPY ARRAY
# ==========================================

img_array = image.img_to_array(img)

print("Image array shape:", img_array.shape)

# ==========================================
# D. EXPAND DIMENSIONS TO CREATE A BATCH
# ==========================================

img_array = np.expand_dims(img_array, axis=0)

print("Batch shape:", img_array.shape)

# ==========================================
# E. PREPROCESS IMAGE FOR VGG16
# ==========================================

img_array = preprocess_input(img_array)

print("Image preprocessing completed!")

# ==========================================
# F. LOAD PRETRAINED VGG16 MODEL
# ==========================================

model = VGG16(weights="imagenet")

# ==========================================
# G. MAKE A PREDICTION
# ==========================================

predictions = model.predict(img_array)

# ==========================================
# H. DECODE THE TOP 5 PREDICTIONS
# ==========================================

decoded_predictions = decode_predictions(
    predictions,
    top=5
)

print("\nTOP 5 PREDICTIONS")
print("==============================")

for i, (class_id, label, confidence) in enumerate(
    decoded_predictions[0], start=1
):
    print(
        f"{i}. {label}: {confidence * 100:.2f}% confidence"
    )


# ==========================================
# I. SET MINIMUM CONFIDENCE THRESHOLD
# ==========================================

confidence_threshold = 0.70  # 70%

# Get the highest prediction
top_prediction = decoded_predictions[0][0]

predicted_label = top_prediction[1]
confidence = top_prediction[2]

print("\nCONFIDENCE THRESHOLD ANALYSIS")
print("==============================")

print("Predicted class:", predicted_label)
print(f"Confidence score: {confidence * 100:.2f}%")
print(f"Minimum threshold: {confidence_threshold * 100:.0f}%")

# Check whether prediction meets the threshold
if confidence >= confidence_threshold:

    print("\nACCEPTED")
    print("Prediction meets the minimum confidence requirement.")

else:

    print("\nREJECTED")
    print("Prediction is below the minimum confidence threshold.")
    print("The image classification is uncertain.")

# ==========================================
# J. DISPLAY TOP 5 PREDICTIONS
# ==========================================

print("\nTOP 5 PREDICTIONS")
print("==============================")

for i, (class_id, label, score) in enumerate(
    decoded_predictions[0], start=1
):
    print(f"{i}. {label.replace('_', ' ')}: {score * 100:.2f}%")
