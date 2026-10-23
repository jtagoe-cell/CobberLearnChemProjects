
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Create x-axis values from 0 to 10
np.random.seed(42)  # Make the results reproducible
x = np.linspace(0, 10, 50)

# 2. Define the true line: y = 2x + 5
y_true = 2 * x + 5

# 3. Add random noise to simulate real-world data
noise = np.random.normal(loc=0, scale=2, size=len(x))
y_noisy = y_true + noise

# 4. Create the scatter plot of noisy data
plt.figure(figsize=(10, 6))

plt.scatter(
    x,
    y_noisy,
    color="royalblue",
    edgecolor="black",
    alpha=0.75,
    label="Noisy data"
)

# 5. Plot the true line
plt.plot(
    x,
    y_true,
    color="red",
    linewidth=2,
    label="True line: y = 2x + 5"
)

# 6. Label the axes and title
plt.xlabel("X values", fontsize=12)
plt.ylabel("Y values", fontsize=12)
plt.title("Noisy Dataset and True Line", fontsize=14)

plt.legend()
plt.grid(True, linestyle="--", alpha=0.3)
plt.tight_layout()

# 7. Save the plot beside this Python script
output_path = (
    Path(__file__).resolve().parent
    / "noisy_data_true_line.png"
)

plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()
plt.close()

print("Noisy dataset created successfully!")
print(f"Number of data points: {len(x)}")
print(f"Plot saved to: {output_path}")
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression

# 1. Create x values from 0 to 10
np.random.seed(42)
x = np.linspace(0, 10, 50)

# 2. Define the true line: y = 2x + 5
y_true = 2 * x + 5

# 3. Add random noise
noise = np.random.normal(0, 2, size=len(x))
y_noisy = y_true + noise

# 4. Reshape x for scikit-learn
X = x.reshape(-1, 1)

# 5. Create and train the linear regression model
model = LinearRegression()
model.fit(X, y_noisy)

# 6. Predict outputs using the trained model
y_predicted = model.predict(X)

# Print the learned equation
print("LINEAR REGRESSION RESULTS")
print("=========================")
print(f"True slope: 2")
print(f"True intercept: 5")
print(f"Learned slope: {model.coef_[0]:.4f}")
print(f"Learned intercept: {model.intercept_:.4f}")
print(
    f"Learned equation: y = "
    f"{model.coef_[0]:.4f}x + {model.intercept_:.4f}"
)

# 7. Create the plot
plt.figure(figsize=(10, 6))

# Noisy observations
plt.scatter(
    x, y_noisy,
    color="royalblue",
    edgecolor="black",
    alpha=0.75,
    label="Noisy data"
)

# Original true line
plt.plot(
    x, y_true,
    color="red",
    linewidth=2,
    label="True line: y = 2x + 5"
)

# Learned best-fit line
plt.plot(
    x, y_predicted,
    color="green",
    linestyle="--",
    linewidth=2,
    label="Linear regression best-fit line"
)

# 8. Format the plot
plt.xlabel("X values", fontsize=12)
plt.ylabel("Y values", fontsize=12)
plt.title("True Line vs. Linear Regression Best-Fit Line", fontsize=14)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.3)
plt.tight_layout()

# 9. Save the image in the script directory
output_path = (
    Path(__file__).resolve().parent
    / "linear_regression_best_fit.png"
)

plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()
plt.close()

print(f"\nPlot saved to: {output_path}")
def calculate_mse(slope, intercept, x, y):
    """
    Calculate and print mean squared error for a line.
    """
    y_predicted = slope * x + intercept
    mse = np.mean((y - y_predicted) ** 2)

    print(f"\nSlope: {slope:.4f}")
    print(f"Intercept: {intercept:.4f}")
    print(f"Mean Squared Error (MSE): {mse:.4f}")

    return mse


# Let the user enter a slope and intercept
try:
    slope = float(input("Enter a slope: "))
    intercept = float(input("Enter an intercept: "))

    mse = calculate_mse(slope, intercept, x, y_noisy)

except ValueError:
    print("Please enter valid numerical values.")
# Create ranges of possible slopes and intercepts
slopes = np.linspace(-1, 5, 100)
intercepts = np.linspace(-5, 15, 100)

# Create a 2D grid of parameter combinations
M, B = np.meshgrid(slopes, intercepts)

# Calculate MSE for every slope/intercept combination
loss = np.zeros_like(M)

for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        y_predicted = M[i, j] * x + B[i, j]
        loss[i, j] = np.mean((y_noisy - y_predicted) ** 2)

# Plot the loss landscape
plt.figure(figsize=(10, 7))

contour = plt.contourf(
    M,
    B,
    loss,
    levels=40,
    cmap="viridis"
)

plt.colorbar(contour, label="Mean Squared Error (MSE)")

plt.xlabel("Slope", fontsize=12)
plt.ylabel("Intercept", fontsize=12)
plt.title("Linear Regression Loss Landscape", fontsize=14)

# Mark the true parameters
plt.scatter(
    2, 5,
    color="red",
    marker="x",
    s=150,
    linewidths=3,
    label="True line (slope=2, intercept=5)"
)

# Mark the best-fit parameters learned by linear regression
plt.scatter(
    model.coef_[0],
    model.intercept_,
    color="white",
    edgecolor="black",
    marker="*",
    s=250,
    label="Learned best-fit line"
)

plt.legend()
plt.tight_layout()

# Save the loss landscape beside your Python script
output_path = (
    Path(__file__).resolve().parent
    / "linear_regression_loss_landscape.png"
)

plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()
plt.close()

print(f"Loss landscape saved to: {output_path}")
