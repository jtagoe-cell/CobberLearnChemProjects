import matplotlib.pyplot as plt
import os

carbons = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

boiling_points = [-161.5, -88.6, -42.1, -0.5, 36.1, 68.7, 98.4, 125.6, 150.8, 174.1]

plt.scatter(carbons, boiling_points)

plt.title("Boiling Point vs. Number of Carbon Atoms")
plt.xlabel("Number of Carbon Atoms")
plt.ylabel("Boiling Point (°C)")

# Create the directory if it does not already exist
os.makedirs("AlkaneBoilingPoints", exist_ok=True)

# Save the plot in the directory
plt.savefig("AlkaneBoilingPoints/alkane_boiling_points.png")

# Display the plot
plt.show()
