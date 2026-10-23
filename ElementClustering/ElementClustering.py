
import pandas as pd
from pathlib import Path

# Group 1 elements
data = {
    "Element Name": [
        "Hydrogen",
        "Lithium",
        "Sodium",
        "Potassium",
        "Rubidium",
        "Cesium",
        "Francium"
    ],
    "Symbol": ["H", "Li", "Na", "K", "Rb", "Cs", "Fr"],
    "Atomic Number": [1, 3, 11, 19, 37, 55, 87],
    "Atomic Radius (pm)": [53, 167, 190, 243, 265, 298, 348],
    "First Ionization Energy (kJ/mol)": [
        1312.0, 520.2, 495.8, 418.8, 403.0, 375.7, 380.0
    ]
}

# Create a pandas DataFrame
df = pd.DataFrame(data)

# Save the CSV in the same directory as this Python script
output_path = Path(__file__).resolve().parent / "group1_elements.csv"
df.to_csv(output_path, index=False)

# Display the data and confirm the saved location
print("GROUP 1 ELEMENTS")
print("================")
print(df.to_string(index=False))

print("\nCSV file created successfully!")
print(f"Saved to: {output_path}")

import matplotlib.pyplot as plt
from pathlib import Path

# Create the scatter plot
plt.figure(figsize=(10, 6))

plt.scatter(
    df["Atomic Radius (pm)"],
    df["First Ionization Energy (kJ/mol)"],
    color="teal",
    edgecolor="black",
    s=100,
    alpha=0.85
)

# Label each point with its element symbol
for _, row in df.iterrows():
    plt.annotate(
        row["Symbol"],
        (row["Atomic Radius (pm)"],
         row["First Ionization Energy (kJ/mol)"]),
        xytext=(5, 5),
        textcoords="offset points"
    )

# Label the axes and add a title
plt.xlabel("Atomic Radius (pm)", fontsize=12)
plt.ylabel("First Ionization Energy (kJ/mol)", fontsize=12)
plt.title("Atomic Radius vs. First Ionization Energy: Group 1 Elements",
          fontsize=14)

# Improve readability
plt.grid(True, linestyle="--", alpha=0.3)
plt.tight_layout()

# Save the plot in the same directory as the Python script
output_path = (
    Path(__file__).resolve().parent
    / "group1_scatter_plot.png"
)

plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()
plt.close()

print(f"Scatter plot saved to: {output_path}")
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Select the features for clustering
X = df[[
    "Atomic Radius (pm)",
    "First Ionization Energy (kJ/mol)"
]]

# Standardize the features so they contribute comparably
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Select features for clustering
X = df[[
    "Atomic Radius (pm)",
    "First Ionization Energy (kJ/mol)"
]]

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Interactive loop: rerun clustering with different k values
while True:
    try:
        k = int(input(
            "\nEnter the number of clusters (k), from 1 to "
            f"{len(df)}, or 0 to stop: "
        ))

        if k == 0:
            print("Clustering program stopped.")
            break

        if k < 1 or k > len(df):
            print(f"Please enter a number between 1 and {len(df)}.")
            continue

        # Create and train the KMeans model
        kmeans = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        df["Cluster"] = kmeans.fit_predict(X_scaled)

        # Convert cluster centers back to the original units
        centers = scaler.inverse_transform(kmeans.cluster_centers_)

        # Create the scatter plot
        plt.figure(figsize=(10, 6))

        colors = plt.cm.tab10.colors

        for cluster in sorted(df["Cluster"].unique()):
            cluster_data = df[df["Cluster"] == cluster]

            plt.scatter(
                cluster_data["Atomic Radius (pm)"],
                cluster_data["First Ionization Energy (kJ/mol)"],
                color=colors[cluster % len(colors)],
                edgecolor="black",
                s=110,
                label=f"Cluster {cluster}"
            )

        # Label each element
        for _, row in df.iterrows():
            plt.annotate(
                row["Symbol"],
                (row["Atomic Radius (pm)"],
                 row["First Ionization Energy (kJ/mol)"]),
                xytext=(5, 5),
                textcoords="offset points"
            )

        # Display cluster centers as large black X markers
        plt.scatter(
            centers[:, 0],
            centers[:, 1],
            marker="X",
            s=300,
            color="black",
            edgecolor="white",
            linewidth=1.2,
            label="Cluster Centers",
            zorder=5
        )

        # Add labels and formatting
        plt.xlabel("Atomic Radius (pm)")
        plt.ylabel("First Ionization Energy (kJ/mol)")
        plt.title(f"KMeans Clustering of Group 1 Elements (k={k})")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()

        # Save each plot with its k value in the filename
        output_path = (
            Path(__file__).resolve().parent
            / f"group1_kmeans_k{k}.png"
        )

        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.show()
        plt.close()

        # Display cluster assignments
        print("\nCLUSTER ASSIGNMENTS")
        print("===================")
        print(df[["Element Name", "Symbol", "Cluster"]].to_string(index=False))

        print("\nCLUSTER CENTERS")
        print("===============")
        for i, center in enumerate(centers):
            print(
                f"Cluster {i}: "
                f"Atomic radius = {center[0]:.2f} pm, "
                f"Ionization energy = {center[1]:.2f} kJ/mol"
            )

        print(f"\nPlot saved to: {output_path}")

    except ValueError:
        print("Invalid input. Enter a whole number, such as 2 or 3.")


