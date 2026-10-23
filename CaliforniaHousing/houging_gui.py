
import tkinter as tk
from tkinter import messagebox

import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# ============================================================
# STEP 1: LOAD DATA AND TRAIN THE MODEL (runs once at startup)
# ============================================================
print("Loading data and training the model... (this takes a few seconds)")

housing = fetch_california_housing(as_frame=True)
df = housing.frame.copy()

X = df.drop(columns=["MedHouseVal"])
y = df["MedHouseVal"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

print("Model ready. Opening the window...")

# The exact column order the model was trained on.
FEATURE_ORDER = list(X.columns)

# ============================================================
# STEP 2: BUILD THE WINDOW
# ============================================================
root = tk.Tk()
root.title("California Housing Price Predictor")
root.geometry("500x620")
root.resizable(False, False)

tk.Label(
    root,
    text="California Housing Price Predictor",
    font=("Arial", 16, "bold")
).pack(pady=(20, 5))

tk.Label(
    root,
    text="Enter the housing details below:",
    font=("Arial", 11)
).pack(pady=(0, 15))

# (label shown to the user, feature name, default value)
fields = [
    ("Median Income ($10,000s)", "MedInc",      "3.0"),
    ("House Age (years)",        "HouseAge",    "20"),
    ("Average Rooms",            "AveRooms",    "5.0"),
    ("Average Bedrooms",         "AveBedrms",   "1.0"),
    ("Population",               "Population",  "1000"),
    ("Average Occupancy",        "AveOccup",    "3.0"),
    ("Latitude",                 "Latitude",    "34.05"),
    ("Longitude",                "Longitude",   "-118.25"),
]

form_frame = tk.Frame(root)
form_frame.pack(pady=5)

entries = {}  # feature name -> Entry widget

for row, (label_text, feature, default) in enumerate(fields):
    tk.Label(
        form_frame,
        text=label_text + ":",
        font=("Arial", 11),
        anchor="e",
        width=24
    ).grid(row=row, column=0, padx=(10, 5), pady=6, sticky="e")

    entry = tk.Entry(form_frame, width=15, font=("Arial", 11))
    entry.insert(0, default)
    entry.grid(row=row, column=1, padx=(5, 10), pady=6)

    entries[feature] = entry


# ============================================================
# STEP 3: COLLECT AND CONVERT THE INPUTS
# ============================================================
def get_inputs():
    """Read every entry box and convert the text to a float.
    Returns a dict of feature -> float, or None if any value is invalid."""
    values = {}
    for label_text, feature, _ in fields:
        text = entries[feature].get().strip()

        if text == "":
            messagebox.showerror("Missing input", f"Please enter a value for '{label_text}'.")
            entries[feature].focus_set()
            return None

        try:
            values[feature] = float(text)
        except ValueError:
            messagebox.showerror("Invalid input", f"'{text}' is not a valid number for '{label_text}'.")
            entries[feature].focus_set()
            return None

    return values


# ============================================================
# STEP 4: PREDICT WHEN THE BUTTON IS CLICKED
# ============================================================
def predict_price():
    values = get_inputs()
    if values is None:
        result_label.config(text="Predicted price: --", fg="black")
        return

    # Convert to a one-row DataFrame with columns in the same order the
    # model was trained on.
    house = pd.DataFrame([values], columns=FEATURE_ORDER)

    # The model predicts in units of $100,000, so multiply to get dollars.
    prediction = model.predict(house)[0]
    price_usd = prediction * 100000

    result_label.config(text=f"Predicted price: ${price_usd:,.0f}", fg="#0a7d2c")


predict_button = tk.Button(
    root,
    text="Predict Price",
    font=("Arial", 13, "bold"),
    command=predict_price,
    padx=15,
    pady=5
)
predict_button.pack(pady=(20, 10))

result_label = tk.Label(
    root,
    text="Predicted price: --",
    font=("Arial", 16, "bold")
)
result_label.pack(pady=10)

# Pressing Enter in any box also triggers the prediction.
root.bind("<Return>", lambda event: predict_price())

root.mainloop()