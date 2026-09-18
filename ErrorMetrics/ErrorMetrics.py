
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

actual = np.array([2, 4, 5, 4, 5, 7, 9])

predicted = np.array([2.5, 3.5, 4, 5, 6, 8, 8])

# Calculate residuals
residuals = predicted - actual

print("Actual:", actual)
print("Predicted:", predicted)
print("Residuals:", residuals)

# Calculate error metrics
mae = mean_absolute_error(actual, predicted)
mse = mean_squared_error(actual, predicted)
r2 = r2_score(actual, predicted)

print("Mean Absolute Error:", mae)
print("Mean Squared Error:", mse)
print("R²:", r2)

import matplotlib.pyplot as plt

# Create scatterplot
plt.figure(figsize=(8, 6))

plt.scatter(actual, predicted, color="blue")

# Perfect prediction line
plt.plot(
    [actual.min(), actual.max()],
    [actual.min(), actual.max()],
    color="red",
    linestyle="--",
    label="Perfect prediction"
)

plt.xlabel("Actual Values")
plt.ylabel("Predicted Values")
plt.title("Actual vs Predicted Values")
plt.legend()
plt.grid(True)

# Save the graph
plt.savefig("actual_vs_predicted.png", dpi=300, bbox_inches="tight")

print("Graph saved as actual_vs_predicted.png")

# Display the graph
plt.show()

