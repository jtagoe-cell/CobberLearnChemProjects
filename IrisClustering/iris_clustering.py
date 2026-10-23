import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Step 1: Load the Iris dataset.
iris = load_iris(as_frame=True)
df = iris.frame.copy()
df["species"] = df["target"].map(dict(enumerate(iris.target_names)))

X = iris.data  # the four measurements (original units: cm)

# Step 2: Normalize (scale) the features BEFORE clustering.
# KMeans uses distances, so features with larger numeric ranges can
# dominate. StandardScaler rescales each feature to mean 0 and
# standard deviation 1 so all four count equally.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Optional: confirm the scaling worked (means ~0, std ~1).
scaled_check = pd.DataFrame(X_scaled, columns=iris.feature_names)
print("Scaled feature means:\n", scaled_check.mean().round(3))
print("\nScaled feature std devs:\n", scaled_check.std().round(3))

# Step 3: Cluster the SCALED data.
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(X_scaled)

print("\nFlowers per cluster:")
print(df["cluster"].value_counts().sort_index())

print("\nClusters vs. actual species:")
print(pd.crosstab(df["species"], df["cluster"]))

# Step 4: Convert the cluster centers back to original units (cm)
# so they can be drawn on a plot of the original measurements.
centers_cm = scaler.inverse_transform(kmeans.cluster_centers_)

# Step 5: Plot petal length vs. petal width using the ORIGINAL values,
# colored by the clusters found on the scaled data.
x_col = "petal length (cm)"
y_col = "petal width (cm)"
colors = ["tab:blue", "tab:orange", "tab:green"]

plt.figure(figsize=(8, 6))

for cluster_number in range(3):
    members = df[df["cluster"] == cluster_number]
    plt.scatter(
        members[x_col],
        members[y_col],
        color=colors[cluster_number],
        label=f"Cluster {cluster_number}",
        s=60,
        edgecolor="black",
        alpha=0.8
    )

plt.scatter(
    centers_cm[:, 2],
    centers_cm[:, 3],
    color="red",
    marker="X",
    s=200,
    edgecolor="black",
    label="Cluster centers"
)

plt.xlabel("Petal Length (cm)")
plt.ylabel("Petal Width (cm)")
plt.title("Iris Flowers: Petal Length vs. Petal Width\n(KMeans on Standardized Features, k = 3)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("iris_cluster_scatter_scaled.png", dpi=300, bbox_inches="tight")
plt.show()

print("\nPlot saved to iris_cluster_scatter_scaled.png")