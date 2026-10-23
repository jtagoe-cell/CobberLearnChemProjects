import pandas as pd
from sklearn.datasets import fetch_california_housing


# Step 1: Load the California Housing dataset
housing = fetch_california_housing(as_frame=True)

# Convert the dataset into a pandas DataFrame
df = housing.frame.copy()


# Step 2: Display dataset information
print("=" * 60)
print("CALIFORNIA HOUSING DATASET EXPLORATION")
print("=" * 60)

print("\n1. DATASET SIZE")
print(f"Number of rows: {df.shape[0]:,}")
print(f"Number of columns: {df.shape[1]}")


# Step 3: Explain the features
print("\n2. FEATURE DESCRIPTIONS")

descriptions = {
    "MedInc": "Median income in the block group, in tens of thousands of dollars.",
    "HouseAge": "Median house age in the block group, in years.",
    "AveRooms": "Average number of rooms per household.",
    "AveBedrms": "Average number of bedrooms per household.",
    "Population": "Total population of the block group.",
    "AveOccup": "Average number of household members per household.",
    "Latitude": "Geographic latitude of the block group.",
    "Longitude": "Geographic longitude of the block group.",
    "MedHouseVal": "Median house value, measured in units of $100,000."
}

for feature, description in descriptions.items():
    print(f"{feature}: {description}")


# Step 4: Display the first five rows
print("\n3. FIRST FIVE ROWS")
print(df.head())


# Step 5: Display a random sample
print("\n4. RANDOM SAMPLE OF FIVE ROWS")
print(df.sample(n=5, random_state=42))


# Step 6: Calculate basic statistics
print("\n5. SUMMARY STATISTICS")
print(df.describe().round(3))


# Step 7: Check data types
print("\n6. DATA TYPES")
print(df.dtypes)


# Step 8: Check for missing values
print("\n7. MISSING VALUES")
print(df.isnull().sum())


# Step 9: Separate input features and target
X = df.drop(columns=["MedHouseVal"])
y = df["MedHouseVal"]

print("\n8. INPUT AND TARGET VARIABLES")
print("X shape:", X.shape)
print("y shape:", y.shape)
print("Input features:", list(X.columns))
print("Target variable: MedHouseVal")

print("\nDataset exploration complete!")
"""
CALIFORNIA HOUSING: REGRESSION MODELS AND DATA VISUALIZATION

Models:
1. Linear Regression
2. Decision Tree Regressor
3. Random Forest Regressor
4. Support Vector Regressor (SVR)

Outputs:
- housing_model_r2_scores.csv
- california_housing_histograms.png
- california_housing_correlation_heatmap.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


# ============================================================
# STEP 1: LOAD THE DATASET
# ============================================================

print("=" * 65)
print("CALIFORNIA HOUSING: MODEL TRAINING AND DATA VISUALIZATION")
print("=" * 65)

housing = fetch_california_housing(as_frame=True)
df = housing.frame.copy()

print("\nDataset loaded successfully.")
print(f"Number of rows: {df.shape[0]:,}")
print(f"Number of columns: {df.shape[1]}")

# Separate input features (X) and target (y).
# MedHouseVal is the median house value in units of $100,000.
X = df.drop(columns=["MedHouseVal"])
y = df["MedHouseVal"]

print("\nInput features:", list(X.columns))
print("Target variable: MedHouseVal")


# ============================================================
# STEP 2: SPLIT THE DATA INTO TRAINING AND TESTING SETS
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTRAINING AND TESTING DATA")
print("-" * 40)
print(f"Training observations: {len(X_train):,}")
print(f"Testing observations: {len(X_test):,}")


# ============================================================
# STEP 3: DEFINE THE FOUR REGRESSION MODELS
# ============================================================

models = {
    "Linear Regression": LinearRegression(),

    "Decision Tree Regressor": DecisionTreeRegressor(
        random_state=42
    ),

    "Random Forest Regressor": RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    ),

    # Scaling is important for Support Vector Regression.
    "Support Vector Regressor": make_pipeline(
        StandardScaler(),
        SVR(kernel="rbf", C=1.0, epsilon=0.1)
    )
}


# ============================================================
# STEP 4: TRAIN, TEST, AND COMPARE THE MODELS
# ============================================================

results = []

print("\nMODEL PERFORMANCE")
print("=" * 65)

for model_name, model in models.items():

    print(f"\nTraining {model_name}...")

    # Train the model.
    model.fit(X_train, y_train)

    # Predict house values for the test set.
    y_pred = model.predict(X_test)

    # Calculate R-squared.
    score = r2_score(y_test, y_pred)

    results.append({
        "Model": model_name,
        "R2 Score": score
    })

    print(f"{model_name} R² score: {score:.4f}")


# Convert the results into a DataFrame.
results_df = pd.DataFrame(results)

# Sort from highest to lowest R².
results_df = results_df.sort_values(
    by="R2 Score",
    ascending=False
).reset_index(drop=True)

print("\n" + "=" * 65)
print("FINAL MODEL COMPARISON")
print("=" * 65)

print(results_df.to_string(index=False, formatters={
    "R2 Score": "{:.4f}".format
}))

# Identify the best-performing model.
best_model = results_df.iloc[0]

print("\nBEST-PERFORMING MODEL")
print("-" * 40)
print(f"Model: {best_model['Model']}")
print(f"R² score: {best_model['R2 Score']:.4f}")

# Save the scores to a CSV file.
results_df.to_csv(
    "housing_model_r2_scores.csv",
    index=False
)

print("\nModel scores saved to housing_model_r2_scores.csv")


# ============================================================
# STEP 5: VISUALIZE THE DISTRIBUTIONS OF ALL FEATURES
# ============================================================

print("\nCreating feature distribution histograms...")

# Include all eight input features and the target variable.
columns_to_plot = df.columns.tolist()

# Arrange the nine histograms in a 3 x 3 grid.
fig, axes = plt.subplots(3, 3, figsize=(15, 12))

axes = axes.flatten()

for i, column in enumerate(columns_to_plot):

    axes[i].hist(
        df[column].dropna(),
        bins=40,
        edgecolor="black"
    )

    axes[i].set_title(column)
    axes[i].set_xlabel(column)
    axes[i].set_ylabel("Frequency")

plt.suptitle(
    "California Housing Dataset: Feature Distributions",
    fontsize=16
)

plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig(
    "california_housing_histograms.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Histograms saved to california_housing_histograms.png")


# ============================================================
# STEP 6: CREATE A CORRELATION HEATMAP
# ============================================================

print("\nCreating correlation heatmap...")

# Calculate correlations between all numerical columns.
correlation_matrix = df.corr(numeric_only=True)

plt.figure(figsize=(12, 9))

sns.heatmap(
    correlation_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    vmin=-1,
    vmax=1,
    square=True
)

plt.title(
    "California Housing Dataset: Correlation Heatmap",
    fontsize=15
)

plt.tight_layout()

plt.savefig(
    "california_housing_correlation_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Correlation heatmap saved to "
      "california_housing_correlation_heatmap.png")


# ============================================================
# STEP 7: DISPLAY CORRELATIONS WITH HOUSING PRICES
# ============================================================

print("\nFEATURE CORRELATIONS WITH MEDIAN HOUSE VALUE")
print("=" * 65)

price_correlations = (
    correlation_matrix["MedHouseVal"]
    .drop("MedHouseVal")
    .sort_values(ascending=False)
)

print(price_correlations.to_string())

print("\nAnalysis complete!")
print("Check your project folder for the saved CSV and PNG files.")
# ============================================================
# STEP 8: PREDICT PRICES FOR NEW, MADE-UP HOUSES
# ============================================================

print("\n" + "=" * 65)
print("PREDICTING PRICES FOR NEW, MADE-UP HOUSES")
print("=" * 65)

# Use the top-performing model from the previous comparison.
# This example uses Random Forest.
best_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

# Train the model on the training data.
best_model.fit(X_train, y_train)

# Create hypothetical houses.
# Feature values should be in the same units as the original dataset.
new_houses = pd.DataFrame([
    {
        "MedInc": 3.0,
        "HouseAge": 20.0,
        "AveRooms": 5.0,
        "AveBedrms": 1.0,
        "Population": 1000.0,
        "AveOccup": 3.0,
        "Latitude": 34.05,
        "Longitude": -118.25
    },
    {
        "MedInc": 5.0,
        "HouseAge": 30.0,
        "AveRooms": 6.0,
        "AveBedrms": 1.2,
        "Population": 800.0,
        "AveOccup": 2.5,
        "Latitude": 37.77,
        "Longitude": -122.42
    },
    {
        "MedInc": 8.0,
        "HouseAge": 15.0,
        "AveRooms": 7.0,
        "AveBedrms": 1.1,
        "Population": 600.0,
        "AveOccup": 2.0,
        "Latitude": 37.33,
        "Longitude": -121.89
    },
    {
        "MedInc": 2.0,
        "HouseAge": 40.0,
        "AveRooms": 4.0,
        "AveBedrms": 1.0,
        "Population": 1500.0,
        "AveOccup": 4.0,
        "Latitude": 36.74,
        "Longitude": -119.78
    },
    {
        "MedInc": 6.5,
        "HouseAge": 10.0,
        "AveRooms": 8.0,
        "AveBedrms": 1.3,
        "Population": 500.0,
        "AveOccup": 2.2,
        "Latitude": 32.72,
        "Longitude": -117.16
    }
])

# Predict median house values.
predictions = best_model.predict(new_houses)

# Add predictions to the table.
new_houses["PredictedValue_100000s"] = predictions
new_houses["PredictedPrice_USD"] = predictions * 100000

# Display selected information.
print("\nPREDICTION RESULTS")
print("-" * 65)

for i, row in new_houses.iterrows():
    print(f"\nHouse {i + 1}")
    print(f"  Median income feature: {row['MedInc']:.1f}")
    print(f"  House age: {row['HouseAge']:.0f} years")
    print(
        f"  Location: latitude {row['Latitude']:.2f}, "
        f"longitude {row['Longitude']:.2f}"
    )
    print(f"  Predicted median value: ${row['PredictedPrice_USD']:,.0f}")

# Save predictions.
new_houses.to_csv(
    "made_up_house_price_predictions.csv",
    index=False
)

print("\nPredictions saved to made_up_house_price_predictions.csv")# ============================================================
# STEP 9: INTERACTIVE CHART FOR CUSTOM HOUSING INPUTS
# ============================================================
# Paste this at the END of your script. It reuses `df`, `X`, `pd`, `plt`,
# and the trained `best_model` from earlier steps.
#
# Move the sliders and the charts update live:
#   - Left chart:  where your predicted price falls among all California
#                  block groups (histogram of house values).
#   - Right chart: how each of your inputs ranks vs. the dataset (percentile).
#
# Note: this needs an interactive matplotlib window (running locally,
# or a Jupyter notebook with `%matplotlib widget` / `%matplotlib qt`).

from matplotlib.widgets import Slider, Button

print("\n" + "=" * 65)
print("INTERACTIVE CUSTOM HOUSE PRICE CHART")
print("=" * 65)
print("Close the chart window to finish.")

# Single-row predictions are faster without parallel overhead.
best_model.set_params(n_jobs=1)

# (label, column, slider min, slider max, step)
slider_spec = [
    ("Median income ($10k)",    "MedInc",      0.5,    15.0,    0.1),
    ("House age (years)",       "HouseAge",    1.0,    52.0,    1.0),
    ("Avg rooms",               "AveRooms",    1.0,    12.0,    0.1),
    ("Avg bedrooms",            "AveBedrms",   0.5,    3.0,     0.05),
    ("Population",              "Population",  3.0,    10000.0, 50.0),
    ("Avg occupants",           "AveOccup",    0.5,    10.0,    0.1),
    ("Latitude",                "Latitude",    32.5,   42.0,    0.05),
    ("Longitude",               "Longitude",  -124.4, -114.3,   0.05),
]

defaults = X.median()
all_prices = df["MedHouseVal"] * 100000

# ---------- Figure layout ----------
fig = plt.figure(figsize=(14, 9))
fig.suptitle("Custom House Price Predictor", fontsize=16, fontweight="bold")

ax_hist = fig.add_axes([0.07, 0.55, 0.50, 0.35])
ax_pct = fig.add_axes([0.70, 0.55, 0.26, 0.35])

# ---------- Sliders ----------
sliders = {}
top, gap = 0.44, 0.045
for i, (label, col, lo, hi, step) in enumerate(slider_spec):
    ax = fig.add_axes([0.20, top - i * gap, 0.60, 0.025])
    sliders[col] = Slider(
        ax, label, lo, hi,
        valinit=float(min(max(defaults[col], lo), hi)),
        valstep=step,
    )

ax_reset = fig.add_axes([0.82, 0.05, 0.10, 0.04])
reset_button = Button(ax_reset, "Reset")


# ---------- Chart update ----------
def current_house():
    values = {col: s.val for col, s in sliders.items()}
    return pd.DataFrame([values], columns=X.columns)


def update(_=None):
    house = current_house()
    price = best_model.predict(house)[0] * 100000

    # Left: histogram of all house values + the prediction.
    ax_hist.clear()
    ax_hist.hist(all_prices, bins=40, color="#9ecae1", edgecolor="white")
    ax_hist.axvline(price, color="crimson", linewidth=2.5,
                    label=f"Your house: ${price:,.0f}")
    pct_price = (all_prices < price).mean() * 100
    ax_hist.set_title(
        f"Predicted value: ${price:,.0f}  "
        f"(higher than {pct_price:.0f}% of block groups)"
    )
    ax_hist.set_xlabel("Median house value (USD)")
    ax_hist.set_ylabel("Number of block groups")
    ax_hist.legend(loc="upper right")

    # Right: percentile of each input vs. the dataset.
    percentiles = [(X[col] < house[col].iloc[0]).mean() * 100 for col in X.columns]
    ax_pct.clear()
    ax_pct.barh(list(X.columns), percentiles, color="#6baed6")
    ax_pct.axvline(50, color="gray", linestyle="--", linewidth=1)
    ax_pct.set_xlim(0, 100)
    ax_pct.set_xlabel("Percentile in dataset")
    ax_pct.set_title("Your inputs vs. all California data")
    ax_pct.invert_yaxis()

    fig.canvas.draw_idle()


def reset(_):
    for s in sliders.values():
        s.reset()


for s in sliders.values():
    s.on_changed(update)
reset_button.on_clicked(reset)

update()
plt.show()
# ============================================================
# STEP 10: 5-FOLD CROSS-VALIDATION
# ============================================================
# Paste this at the END of your California Housing script.
# It reuses `models`, `X`, `y`, `pd`, and `plt` from the earlier steps.
#
# Why cross-validation? A single train/test split can be lucky or unlucky.
# 5-fold CV splits the data into 5 parts, trains on 4 and tests on the 1
# left out, and repeats so every part is used as the test set once.
# The average score is a more reliable measure of model performance.

import numpy as np
from sklearn.model_selection import KFold, cross_validate

print("\n" + "=" * 65)
print("5-FOLD CROSS-VALIDATION")
print("=" * 65)

# shuffle=True mixes the rows first; random_state makes it repeatable.
kfold = KFold(n_splits=5, shuffle=True, random_state=42)

cv_summary = []
fold_scores = {}  # model name -> list of 5 R² scores (used for the chart)

for model_name, model in models.items():

    print(f"\nRunning 5-fold CV for {model_name}...")

    # cross_validate clones the model for each fold, so the models
    # you trained earlier are not changed.
    cv = cross_validate(
        model,
        X,
        y,
        cv=kfold,
        scoring=("r2", "neg_root_mean_squared_error"),
        n_jobs=1
    )

    r2_scores = cv["test_r2"]
    rmse_scores = -cv["test_neg_root_mean_squared_error"]  # flip sign back

    fold_scores[model_name] = r2_scores

    # Show the score for each individual fold.
    for fold_number, score in enumerate(r2_scores, start=1):
        print(f"  Fold {fold_number}: R² = {score:.4f}")

    print(f"  Mean R²:  {r2_scores.mean():.4f}  (± {r2_scores.std():.4f})")
    print(f"  Mean RMSE: {rmse_scores.mean():.4f}  (in $100,000s)")

    cv_summary.append({
        "Model": model_name,
        "Mean R2": r2_scores.mean(),
        "Std R2": r2_scores.std(),
        "Min R2": r2_scores.min(),
        "Max R2": r2_scores.max(),
        "Mean RMSE ($100k)": rmse_scores.mean()
    })

# ---------- Summary table ----------
cv_df = (
    pd.DataFrame(cv_summary)
    .sort_values(by="Mean R2", ascending=False)
    .reset_index(drop=True)
)

print("\n" + "=" * 65)
print("CROSS-VALIDATION SUMMARY (sorted by mean R²)")
print("=" * 65)
print(cv_df.round(4).to_string(index=False))

best_cv = cv_df.iloc[0]
print(f"\nBest model by cross-validation: {best_cv['Model']} "
      f"(mean R² = {best_cv['Mean R2']:.4f})")

cv_df.to_csv("housing_cross_validation_results.csv", index=False)
print("\nResults saved to housing_cross_validation_results.csv")

order = cv_df["Model"].tolist()  # best model first

plt.figure(figsize=(10, 6))
plt.boxplot(
    [fold_scores[name] for name in order],
    showmeans=True
)
plt.xticks(range(1, len(order) + 1), order, rotation=15)
plt.title("5-Fold Cross-Validation: R² Score by Model")
plt.ylabel("R² Score")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig("housing_cross_validation_boxplot.png", dpi=300, bbox_inches="tight")
plt.show()