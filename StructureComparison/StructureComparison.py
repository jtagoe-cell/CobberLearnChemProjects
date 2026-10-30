
"""
Protein Structure Analysis: Experimental vs AlphaFold

Calculates:
1. Basic protein structure statistics
2. C-alpha RMSD
3. Per-residue structural distances
4. AlphaFold pLDDT confidence scores
5. Confidence and structural difference visualizations
6. Correlation between pLDDT and structural distances
7. Aligned PDB files
8. CSV containing residue-level results
9. PyMOL visualization script
10. Browser-based NGL visualization
11. Analysis summary
"""

from Bio.PDB import PDBParser, PDBIO, Superimposer, is_aa
from tkinter import Tk, filedialog
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json


# --------------------------------------------------
# 1. CREATE ONE RESULTS DIRECTORY
# --------------------------------------------------

script_directory = Path(__file__).resolve().parent

output_directory = (
    script_directory / "structure_comparison_results"
)

output_directory.mkdir(parents=True, exist_ok=True)

print("All results will be saved in:")
print(output_directory)


# --------------------------------------------------
# 2. SELECT THE TWO PDB FILES
# --------------------------------------------------

root = Tk()
root.withdraw()

print("\nSelect the EXPERIMENTAL PDB file.")

experimental_file = filedialog.askopenfilename(
    title="Select Experimental PDB File",
    filetypes=[("PDB files", "*.pdb"), ("All files", "*.*")]
)

if not experimental_file:
    print("No experimental file selected.")
    root.destroy()
    raise SystemExit

print("\nSelect the ALPHAFOLD PDB file.")

alphafold_file = filedialog.askopenfilename(
    title="Select AlphaFold PDB File",
    filetypes=[("PDB files", "*.pdb"), ("All files", "*.*")]
)

if not alphafold_file:
    print("No AlphaFold file selected.")
    root.destroy()
    raise SystemExit

root.destroy()


# --------------------------------------------------
# 3. LOAD BOTH PROTEIN STRUCTURES
# --------------------------------------------------

parser = PDBParser(QUIET=True)

experimental_structure = parser.get_structure(
    "Experimental", experimental_file
)

alphafold_structure = parser.get_structure(
    "AlphaFold", alphafold_file
)

experimental_model = next(experimental_structure.get_models())
alphafold_model = next(alphafold_structure.get_models())


# --------------------------------------------------
# 4. CALCULATE BASIC STRUCTURE STATISTICS
# --------------------------------------------------

def analyze_structure(model, structure_name):

    chains = list(model.get_chains())

    total_atoms = 0
    total_residues = 0
    standard_residues = 0

    residue_counts = {}

    for chain in chains:

        for residue in chain:

            total_atoms += len(list(residue.get_atoms()))

            if is_aa(residue, standard=False):

                total_residues += 1

                if is_aa(residue, standard=True):
                    standard_residues += 1

                residue_name = residue.get_resname()

                residue_counts[residue_name] = (
                    residue_counts.get(residue_name, 0) + 1
                )

    return {
        "name": structure_name,
        "chains": len(chains),
        "residues": total_residues,
        "standard_residues": standard_residues,
        "atoms": total_atoms,
        "residue_counts": residue_counts
    }


def display_results(results):

    print("\n--------------------------------------")
    print(results["name"].upper())
    print("--------------------------------------")

    print("Number of chains:", results["chains"])
    print("Total amino acid residues:", results["residues"])
    print("Standard amino acid residues:",
          results["standard_residues"])
    print("Total atoms:", results["atoms"])

    print("\nResidue composition:")

    for residue, count in sorted(results["residue_counts"].items()):
        print(f"{residue}: {count}")


experimental_results = analyze_structure(
    experimental_model, "Experimental Structure"
)

alphafold_results = analyze_structure(
    alphafold_model, "AlphaFold Structure"
)

display_results(experimental_results)
display_results(alphafold_results)


# --------------------------------------------------
# 5. EXTRACT C-ALPHA ATOMS
# --------------------------------------------------

def get_ca_atoms(model):

    ca_atoms = {}

    for chain in model:

        for residue in chain:

            if is_aa(residue, standard=True) and "CA" in residue:

                key = (chain.id, residue.id)

                ca_atoms[key] = residue["CA"]

    return ca_atoms


experimental_ca = get_ca_atoms(experimental_model)
alphafold_ca = get_ca_atoms(alphafold_model)

# Match chain IDs and residue numbering
common_keys = sorted(
    set(experimental_ca.keys()) & set(alphafold_ca.keys()),
    key=lambda key: (key[0], key[1][1], key[1][2])
)

if len(common_keys) < 3:

    raise ValueError(
        "Fewer than three matching C-alpha atoms found. "
        "Check chain IDs and residue numbering."
    )

fixed_atoms = [
    experimental_ca[key] for key in common_keys
]

moving_atoms = [
    alphafold_ca[key] for key in common_keys
]

print("\nMatching C-alpha atoms:", len(common_keys))


# --------------------------------------------------
# 6. ALIGN ALPHAFOLD TO EXPERIMENTAL STRUCTURE
# --------------------------------------------------

superimposer = Superimposer()

superimposer.set_atoms(fixed_atoms, moving_atoms)

# Calculate RMSD before applying the transformation
overall_rmsd = superimposer.rms

# Transform all AlphaFold atoms into the experimental coordinate frame
superimposer.apply(list(alphafold_structure.get_atoms()))

print("\nOverall C-alpha RMSD:")
print(f"{overall_rmsd:.3f} Angstroms")


# --------------------------------------------------
# 7. CALCULATE PER-RESIDUE DISTANCES AND PLDDT
# --------------------------------------------------

residue_distances = []
plddt_scores = []
residue_numbers = []
residue_names = []
chain_ids = []

for key in common_keys:

    experimental_coordinate = experimental_ca[key].get_coord()
    alphafold_coordinate = alphafold_ca[key].get_coord()

    # Calculate distance after alignment
    distance = np.linalg.norm(
        experimental_coordinate - alphafold_coordinate
    )

    # AlphaFold stores pLDDT in the B-factor column
    confidence = alphafold_ca[key].get_bfactor()

    residue_distances.append(distance)
    plddt_scores.append(confidence)

    chain_id, residue_id = key

    residue_numbers.append(residue_id[1])
    chain_ids.append(chain_id)

    residue_names.append(
        alphafold_ca[key].get_parent().get_resname()
    )

residue_distances = np.array(residue_distances)
plddt_scores = np.array(plddt_scores)

positions = np.arange(1, len(common_keys) + 1)


# --------------------------------------------------
# 8. PRINT PLDDT STATISTICS
# --------------------------------------------------

print("\n--------------------------------------")
print("ALPHAFOLD CONFIDENCE ANALYSIS")
print("--------------------------------------")

print(f"Average pLDDT: {np.mean(plddt_scores):.2f}")
print(f"Highest pLDDT: {np.max(plddt_scores):.2f}")
print(f"Lowest pLDDT: {np.min(plddt_scores):.2f}")

print(
    "Very high confidence (90-100):",
    np.sum(plddt_scores >= 90)
)

print(
    "Confident predictions (70-90):",
    np.sum((plddt_scores >= 70) & (plddt_scores < 90))
)

print(
    "Low confidence (50-70):",
    np.sum((plddt_scores >= 50) & (plddt_scores < 70))
)

print(
    "Very low confidence (below 50):",
    np.sum(plddt_scores < 50)
)


# --------------------------------------------------
# 9. PLOT ALPHAFOLD CONFIDENCE
# --------------------------------------------------

plt.figure(figsize=(12, 6))

plt.plot(
    positions,
    plddt_scores,
    marker=".",
    linewidth=1,
    label="AlphaFold pLDDT"
)

plt.axhline(y=90, linestyle="--", label="90: Very high")
plt.axhline(y=70, linestyle="--", label="70: Confident")
plt.axhline(y=50, linestyle="--", label="50: Low confidence")

plt.xlabel("Matched Residue Position")
plt.ylabel("pLDDT Confidence Score")
plt.title("AlphaFold Confidence Along Protein Sequence")

plt.ylim(0, 105)
plt.grid(True)
plt.legend()
plt.tight_layout()

confidence_plot = output_directory / "alphafold_confidence.png"

plt.savefig(confidence_plot, dpi=300)
plt.show()
plt.close()


# --------------------------------------------------
# 10. PLOT PER-RESIDUE STRUCTURAL DISTANCES
# --------------------------------------------------

plt.figure(figsize=(12, 6))

plt.plot(
    positions,
    residue_distances,
    marker=".",
    linewidth=1
)

plt.xlabel("Matched Residue Position")
plt.ylabel("C-alpha Distance (Angstroms)")
plt.title("Per-Residue Structural Differences")

plt.grid(True)
plt.tight_layout()

distance_plot = output_directory / "per_residue_distances.png"

plt.savefig(distance_plot, dpi=300)
plt.show()
plt.close()


# --------------------------------------------------
# 11. PLOT CONFIDENCE VS STRUCTURAL DISTANCE
# --------------------------------------------------

plt.figure(figsize=(9, 6))

plt.scatter(
    plddt_scores,
    residue_distances,
    alpha=0.6
)

plt.xlabel("AlphaFold pLDDT Confidence")
plt.ylabel("C-alpha Distance (Angstroms)")
plt.title("AlphaFold Confidence vs Structural Differences")

plt.grid(True)
plt.tight_layout()

correlation_plot = (
    output_directory / "confidence_vs_distance.png"
)

plt.savefig(correlation_plot, dpi=300)
plt.show()
plt.close()


# --------------------------------------------------
# 12. CALCULATE PEARSON CORRELATION
# --------------------------------------------------

if (
    len(plddt_scores) > 1
    and np.std(plddt_scores) > 0
    and np.std(residue_distances) > 0
):

    correlation = np.corrcoef(
        plddt_scores,
        residue_distances
    )[0, 1]

    print("\nPearson correlation:", f"{correlation:.3f}")

else:

    correlation = np.nan

    print("\nCorrelation could not be calculated.")


# --------------------------------------------------
# 13. IDENTIFY REGIONS TO INVESTIGATE
# --------------------------------------------------

low_confidence = plddt_scores < 70
large_difference = residue_distances > 3.0

problem_regions = low_confidence & large_difference

print("\n--------------------------------------")
print("REGIONS TO INVESTIGATE")
print("--------------------------------------")

print(
    "Low-confidence residues with distances above 3 Å:",
    np.sum(problem_regions)
)

for i in np.where(problem_regions)[0]:

    print(
        f"Chain {chain_ids[i]}, "
        f"Residue {residue_numbers[i]} "
        f"({residue_names[i]}): "
        f"pLDDT = {plddt_scores[i]:.2f}, "
        f"Distance = {residue_distances[i]:.2f} Å"
    )


# --------------------------------------------------
# 14. SAVE RESIDUE-LEVEL CSV
# --------------------------------------------------

results_df = pd.DataFrame({

    "Chain": chain_ids,
    "Residue_Number": residue_numbers,
    "Residue_Name": residue_names,
    "pLDDT": plddt_scores,
    "CA_Distance_Angstroms": residue_distances,
    "Low_Confidence": low_confidence,
    "Large_Structural_Difference": large_difference,
    "Low_Confidence_and_Large_Difference": problem_regions

})

csv_file = output_directory / "protein_comparison_results.csv"

results_df.to_csv(csv_file, index=False)


# --------------------------------------------------
# 15. SAVE ALIGNED PDB STRUCTURES
# --------------------------------------------------

experimental_output = (
    output_directory / "aligned_experimental.pdb"
)

alphafold_output = (
    output_directory / "aligned_alphafold.pdb"
)

experimental_writer = PDBIO()
experimental_writer.set_structure(experimental_structure)
experimental_writer.save(str(experimental_output))

alphafold_writer = PDBIO()
alphafold_writer.set_structure(alphafold_structure)
alphafold_writer.save(str(alphafold_output))


# --------------------------------------------------
# 16. GENERATE PYMOL VISUALIZATION SCRIPT
# --------------------------------------------------

pymol_script = output_directory / "visualize_alignment.pml"

experimental_path = experimental_output.resolve()
alphafold_path = alphafold_output.resolve()

pymol_commands = f'''
# Load experimental structure
load "{experimental_path}", experimental

# Load AlphaFold structure
load "{alphafold_path}", alphafold

# Display structures as cartoons
hide everything
show cartoon, experimental
show cartoon, alphafold

# Color experimental structure blue
color blue, experimental

# Color AlphaFold structure red
color red, alphafold

# Apply transparency
set cartoon_transparency, 0.25, experimental
set cartoon_transparency, 0.25, alphafold

# Set white background
bg_color white

# Center and zoom
orient
zoom
'''

with open(pymol_script, "w") as file:
    file.write(pymol_commands)

print("\nPyMOL script saved:", pymol_script)



# --------------------------------------------------
# 17. GENERATE BROWSER-BASED NGL VISUALIZATION
# WITH PLDDT CONFIDENCE COLORS
# --------------------------------------------------

html_file = output_directory / "protein_alignment.html"

# Read the aligned PDB files
with open(experimental_output, "r") as file:
    experimental_pdb_text = file.read()

with open(alphafold_output, "r") as file:
    alphafold_pdb_text = file.read()

# Safely insert PDB text into JavaScript
experimental_json = json.dumps(experimental_pdb_text)
alphafold_json = json.dumps(alphafold_pdb_text)

html_content = f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Protein Structure Alignment</title>

    <script src="https://unpkg.com/ngl@2.4.0/dist/ngl.js"></script>

    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: white;
        }}

        h2 {{
            text-align: center;
            padding: 12px;
        }}

        #viewport {{
            width: 100%;
            height: 75vh;
        }}

        #legend {{
            text-align: center;
            padding: 15px;
            font-size: 15px;
            line-height: 2;
        }}

        .color-box {{
            display: inline-block;
            width: 15px;
            height: 15px;
            margin-left: 12px;
            margin-right: 4px;
            vertical-align: middle;
        }}

        .blue {{
            color: blue;
            font-weight: bold;
        }}
    </style>
</head>

<body>

    <h2>Experimental vs AlphaFold Protein Structure</h2>

    <div id="legend">

        <span class="blue">Blue: Experimental Structure</span>

        <br>

        <b>AlphaFold pLDDT Confidence:</b>

        <br>

        <span class="color-box"
              style="background: #00008B;"></span>
        Very high (90–100)

        <span class="color-box"
              style="background: #00BFFF;"></span>
        Confident (70–89)

        <span class="color-box"
              style="background: #FFFF00;"></span>
        Low (50–69)

        <span class="color-box"
              style="background: #FF0000;"></span>
        Very low (below 50)

    </div>

    <div id="viewport"></div>

    <script>

        const stage = new NGL.Stage("viewport", {{
            backgroundColor: "white"
        }});

        const experimentalPDB = {experimental_json};
        const alphafoldPDB = {alphafold_json};

        async function loadStructures() {{

            try {{

                // Load experimental structure
                const experimentalBlob = new Blob(
                    [experimentalPDB],
                    {{type: "text/plain"}}
                );

                const experimental = await stage.loadFile(
                    experimentalBlob,
                    {{ext: "pdb"}}
                );

                experimental.addRepresentation("cartoon", {{
                    color: "blue",
                    opacity: 0.75
                }});

                // Load AlphaFold structure
                const alphafoldBlob = new Blob(
                    [alphafoldPDB],
                    {{type: "text/plain"}}
                );

                const alphafold = await stage.loadFile(
                    alphafoldBlob,
                    {{ext: "pdb"}}
                );

                // Color AlphaFold according to pLDDT.
                // AlphaFold stores pLDDT in the PDB B-factor column.
                alphafold.addRepresentation("cartoon", {{

                    colorScheme: "bfactor",

                    colorScale: [
                        "#FF0000",
                        "#FFFF00",
                        "#00BFFF",
                        "#00008B"
                    ],

                    colorDomain: [0, 100],
                    opacity: 0.75

                }});

                // Center both structures
                stage.autoView();

            }} catch (error) {{

                console.error(
                    "Error loading protein structures:",
                    error
                );

                document.body.insertAdjacentHTML(
                    "beforeend",
                    "<p>Unable to load protein structures. " +
                    "Check the browser console for details.</p>"
                );
            }}
        }}

        window.addEventListener("resize", function() {{
            stage.handleResize();
        }});

        loadStructures();

    </script>

</body>
</html>
"""

with open(html_file, "w", encoding="utf-8") as file:
    file.write(html_content)

print("\nBrowser visualization saved:", html_file)

# --------------------------------------------------
# 18. SAVE ANALYSIS SUMMARY
# --------------------------------------------------

summary_file = output_directory / "analysis_summary.txt"

with open(summary_file, "w") as file:

    file.write("PROTEIN STRUCTURE COMPARISON RESULTS\n")
    file.write("====================================\n\n")

    file.write("EXPERIMENTAL STRUCTURE\n")
    file.write(f"Chains: {experimental_results['chains']}\n")
    file.write(f"Residues: {experimental_results['residues']}\n")
    file.write(f"Atoms: {experimental_results['atoms']}\n\n")

    file.write("ALPHAFOLD STRUCTURE\n")
    file.write(f"Chains: {alphafold_results['chains']}\n")
    file.write(f"Residues: {alphafold_results['residues']}\n")
    file.write(f"Atoms: {alphafold_results['atoms']}\n\n")

    file.write("STRUCTURAL COMPARISON\n")
    file.write(f"Matched residues: {len(common_keys)}\n")
    file.write(f"Overall RMSD: {overall_rmsd:.3f} Angstroms\n\n")

    file.write("ALPHAFOLD CONFIDENCE\n")
    file.write(f"Average pLDDT: {np.mean(plddt_scores):.2f}\n")
    file.write(f"Highest pLDDT: {np.max(plddt_scores):.2f}\n")
    file.write(f"Lowest pLDDT: {np.min(plddt_scores):.2f}\n\n")

    file.write("CONFIDENCE AND DISTANCE CORRELATION\n")
    file.write(f"Pearson correlation: {correlation:.3f}\n\n")

    file.write("REGIONS TO INVESTIGATE\n")
    file.write(
        f"Low-confidence residues with distance above 3 Å: "
        f"{np.sum(problem_regions)}\n"
    )

print("\nAnalysis summary saved:", summary_file)


# --------------------------------------------------
# 19. DISPLAY ALL SAVED FILES
# --------------------------------------------------

print("\n======================================")
print("ALL RESULTS SAVED SUCCESSFULLY")
print("======================================")

for saved_file in sorted(output_directory.iterdir()):

    if saved_file.is_file():
        print(saved_file.name)

print("\nResults folder:")
print(output_directory)

print("\nExperimental structure: BLUE")
print("AlphaFold structure: RED")

print("\nProtein structure analysis complete!")
