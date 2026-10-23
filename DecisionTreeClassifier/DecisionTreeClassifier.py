import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
# 1. Create the dataset
data = {
    "Molecule": [
        "Molecule 1", "Molecule 2", "Molecule 3", "Molecule 4",
        "Molecule 5", "Molecule 6", "Molecule 7", "Molecule 8",
        "Molecule 9", "Molecule 10", "Molecule 11", "Molecule 12"
    ],
    "Molecular Weight": [
        180, 250, 80, 300, 150, 400, 90, 200, 130, 275, 135, 220
    ],
    "Hydrogen Bond Donors": [
        5, 2, 1, 1, 4, 3, 0, 2, 3, 1, 1, 3
    ],
    "Hydrogen Bond Acceptors": [
        6, 3, 2, 2, 5, 4, 1, 3, 4, 2, 3, 2
    ],
    "Water Solubility": [
        1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1
    ]
}

# 2. Create the DataFrame
df = pd.DataFrame(data)

print("WATER SOLUBILITY DATASET")
print("========================")
print(df.to_string(index=False))

# 3. Separate input features (X) and target variable (y)
X = df[[
    "Molecular Weight",
    "Hydrogen Bond Donors",
    "Hydrogen Bond Acceptors"
]]

y = df["Water Solubility"]

print("\nINPUT FEATURES (X)")
print("==================")
print(X.to_string(index=False))

print("\nTARGET VARIABLE (y)")
print("===================")
print(y.to_string(index=False))

# 4. Create the decision tree model
model = DecisionTreeClassifier(random_state=42)

# 5. Train the model
model.fit(X, y)
# Generate and save a visualization of the decision tree

# Get the directory where this Python script is saved
output_directory = Path(__file__).resolve().parent

# Set the output image filename
image_path = output_directory / "water_solubility_decision_tree.png"

# Create the figure
plt.figure(figsize=(20, 10))

# Draw the decision tree
plot_tree(
    model,
    feature_names=list(X.columns),
    class_names=["Not Soluble (0)", "Soluble (1)"],
    filled=True,
    rounded=True,
    fontsize=10
)

# Add a title
plt.title("Decision Tree for Water Solubility Prediction", fontsize=16)

# Adjust the layout
plt.tight_layout()

# Save the image directly to the project directory
plt.savefig(image_path, dpi=300, bbox_inches="tight")

# Close the figure to free memory
plt.close()

# Confirm where the image was saved
print("\nDECISION TREE IMAGE")
print("===================")
print(f"Image saved successfully to:\n{image_path}")
print("\nMODEL TRAINING SUMMARY")
print("======================")
print("Model type:", type(model).__name__)
print("Training samples:", len(X))
print("Number of input features:", X.shape[1])
print("Target variable: Water Solubility")
print("Training completed successfully!")

# 6. Display the learned decision tree rules
tree_rules = export_text(model, feature_names=list(X.columns))

print("\nLEARNED DECISION TREE RULES")
print("===========================")
print(tree_rules)
