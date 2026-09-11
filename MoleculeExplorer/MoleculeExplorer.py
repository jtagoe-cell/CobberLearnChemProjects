import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski

# Enter compound name
compound_name = input("Enter compound name: ")

# Search PubChem
compounds = pcp.get_compounds(compound_name, "name")

if compounds:
    compound = compounds[0]

    # Get the SMILES directly from the PubChem record
    record = compound.to_dict()

    smiles = record.get("connectivity_smiles")

    if smiles is None:
        smiles = record.get("isomeric_smiles")

    print("\nCompound:", compound_name)
    print("SMILES:", smiles)

    # Create RDKit molecule object
    mol = Chem.MolFromSmiles(smiles)

    if mol is not None:

        # Calculate RDKit properties
        molecular_weight = Descriptors.ExactMolWt(mol)
        tpsa = Descriptors.TPSA(mol)
        h_bond_donors = Lipinski.NumHDonors(mol)

        print("Molecule object created successfully!")
        print("Exact molecular weight:", molecular_weight)
        print("TPSA:", tpsa)
        print("Hydrogen bond donors:", h_bond_donors)

    else:
        print("Could not create RDKit molecule.")

else:
    print("Compound not found in PubChem.")













