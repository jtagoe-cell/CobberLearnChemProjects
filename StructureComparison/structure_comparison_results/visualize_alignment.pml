
# Load experimental structure
load "/Users/janicetagoe/PycharmProjects/CobberLearnChemProjects/StructureComparison/structure_comparison_results/aligned_experimental.pdb", experimental

# Load AlphaFold structure
load "/Users/janicetagoe/PycharmProjects/CobberLearnChemProjects/StructureComparison/structure_comparison_results/aligned_alphafold.pdb", alphafold

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
