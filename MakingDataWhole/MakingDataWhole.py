
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix


# --------------------------------------------------
# 1. Load the Titanic dataset
# --------------------------------------------------

url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"

titanic = pd.read_csv(url)


# --------------------------------------------------
# 2. Calculate mean age and fill missing ages
# --------------------------------------------------

mean_age = titanic["Age"].mean()

print("Mean age:", round(mean_age, 2))

titanic["Age"] = titanic["Age"].fillna(mean_age)


# --------------------------------------------------
# 3. Print the first 10 rows
# --------------------------------------------------

print("\nFirst 10 rows:")
print(titanic.head(10))


# --------------------------------------------------
# 4. Create plots directory
# --------------------------------------------------

plot_directory = Path("plots")
plot_directory.mkdir(exist_ok=True)


# --------------------------------------------------
# 5. Generate correlation matrix
# --------------------------------------------------

correlation_matrix = titanic.corr(numeric_only=True)

print("\nCorrelation matrix:")
print(correlation_matrix)

plt.figure(figsize=(10, 8))

sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("Titanic Correlation Matrix")
plt.tight_layout()

plot_path = plot_directory / "titanic_correlation_matrix.png"
plt.savefig(plot_path, dpi=300)

print(f"\nCorrelation plot saved to: {plot_path}")

plt.show()


# --------------------------------------------------
# 6. Prepare data for KNN
# --------------------------------------------------

# Select the features we want the model to use
X = titanic[["Pclass", "Sex", "Age", "Fare"]]

# The value we want the model to predict
y = titanic["Survived"]


# Convert Sex from text into numbers
X = pd.get_dummies(X, columns=["Sex"], drop_first=True)

print("\nFeatures used by the KNN model:")
print(X.head())


# --------------------------------------------------
# 7. Split data into training and testing sets
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# 8. Scale the data
# --------------------------------------------------

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# --------------------------------------------------
# 9. Create and train the KNN model
# --------------------------------------------------

model = KNeighborsClassifier(n_neighbors=5)

model.fit(X_train, y_train)


# --------------------------------------------------
# 10. Make predictions
# --------------------------------------------------

predictions = model.predict(X_test)


# --------------------------------------------------
# 11. Calculate accuracy
# --------------------------------------------------

accuracy = accuracy_score(y_test, predictions)

print("\nKNN Model Accuracy:", round(accuracy, 3))


# --------------------------------------------------
# 12. Create confusion matrix
# --------------------------------------------------

cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6, 5))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Did not survive", "Survived"],
    yticklabels=["Did not survive", "Survived"]
)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("KNN Confusion Matrix")
plt.tight_layout()


# --------------------------------------------------
# 13. Save confusion matrix
# --------------------------------------------------

confusion_path = plot_directory / "knn_confusion_matrix.png"

plt.savefig(confusion_path, dpi=300)

print(f"Confusion matrix saved to: {confusion_path}")

plt.show()

from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# --------------------------------------------------
# KNN model to predict Age
# --------------------------------------------------

# Use passengers with known ages for training
age_data = titanic.dropna(subset=["Age"]).copy()

# Features used to predict Age
X_age = age_data[["Pclass", "Sex", "Fare", "SibSp", "Parch"]]

# Convert Sex into numbers
X_age = pd.get_dummies(X_age, columns=["Sex"], drop_first=True)

# Target variable
y_age = age_data["Age"]


# Split the known-age data into training and testing sets
X_age_train, X_age_test, y_age_train, y_age_test = train_test_split(
    X_age,
    y_age,
    test_size=0.2,
    random_state=42
)


# Scale the features
age_scaler = StandardScaler()

X_age_train = age_scaler.fit_transform(X_age_train)
X_age_test = age_scaler.transform(X_age_test)


# Create KNN regression model
age_model = KNeighborsRegressor(n_neighbors=5)

# Train the model
age_model.fit(X_age_train, y_age_train)


# Predict ages for the test data
age_predictions = age_model.predict(X_age_test)


# Calculate prediction errors
mae = mean_absolute_error(y_age_test, age_predictions)
r2 = r2_score(y_age_test, age_predictions)

print("\nKNN Age Prediction")
print("Mean Absolute Error:", round(mae, 2))
print("R² Score:", round(r2, 2))


# --------------------------------------------------
# Plot actual vs predicted ages
# --------------------------------------------------

plt.figure(figsize=(8, 6))

plt.scatter(
    y_age_test,
    age_predictions,
    alpha=0.6
)

# Perfect prediction line
min_age = min(y_age_test.min(), age_predictions.min())
max_age = max(y_age_test.max(), age_predictions.max())

plt.plot(
    [min_age, max_age],
    [min_age, max_age],
    color="red",
    linestyle="--",
    label="Perfect prediction"
)

plt.xlabel("Actual Age")
plt.ylabel("KNN Predicted Age")
plt.title("Actual Age vs KNN Predicted Age")
plt.legend()

plt.tight_layout()


# Save the plot
age_plot_path = plot_directory / "knn_actual_vs_predicted_age.png"

plt.savefig(age_plot_path, dpi=300)

print(f"Age prediction plot saved to: {age_plot_path}")

plt.show()
# --------------------------------------------------
# Log-linear regression: Fare vs log(Age)
# --------------------------------------------------

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Use rows with valid Age and Fare values
regression_data = titanic[
    (titanic["Age"] > 0) &
    (titanic["Fare"].notna())
].copy()

# Create log(Age)
regression_data["Log_Age"] = np.log(regression_data["Age"])

# Independent variable
X_log = regression_data[["Log_Age"]]

# Dependent variable
y_log = regression_data["Fare"]

# Create regression model
log_model = LinearRegression()

# Fit the model
log_model.fit(X_log, y_log)

# Make predictions
fare_predictions = log_model.predict(X_log)

# Calculate R²
r2 = r2_score(y_log, fare_predictions)

print("\nLog-Linear Regression")
print("---------------------")
print("Intercept:", round(log_model.intercept_, 3))
print("Log(Age) coefficient:", round(log_model.coef_[0], 3))
print("R²:", round(r2, 3))


# --------------------------------------------------
# Plot actual data and regression line
# --------------------------------------------------

plt.figure(figsize=(8, 6))

plt.scatter(
    regression_data["Age"],
    y_log,
    alpha=0.4,
    label="Actual data"
)

# Sort ages so the regression line displays correctly
sort_index = np.argsort(regression_data["Age"])

plt.plot(
    regression_data["Age"].iloc[sort_index],
    fare_predictions[sort_index],
    color="red",
    linewidth=2,
    label="Log-linear regression"
)

plt.xlabel("Age")
plt.ylabel("Fare")
plt.title("Log-Linear Regression: Fare vs Age")
plt.legend()

plt.tight_layout()


# --------------------------------------------------
# Save plot
# --------------------------------------------------

log_plot_path = plot_directory / "log_linear_fare_age.png"

plt.savefig(log_plot_path, dpi=300)

print(f"Log-linear regression plot saved to: {log_plot_path}")

plt.show()
from sklearn.metrics import mean_absolute_error

# Calculate Mean Absolute Error
mae = mean_absolute_error(y_log, fare_predictions)

print("Mean Absolute Error:", round(mae, 2))

