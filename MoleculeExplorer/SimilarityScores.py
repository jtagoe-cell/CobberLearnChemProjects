
import pubchempy as pcp
from rdkit import Chem, DataStructs
from rdkit.Chem import Descriptors, Lipinski, rdFingerprintGenerator


# Choose what you want to compare:
# "molecular_weight"
# "tpsa"
# "h_bond_donors"
# "flexibility"

comparison = "molecular_weight"


# Common formulas
formula_names = {
    "h2o": "water",
    "nh3": "ammonia",
    "nh4": "ammonium",
    "co2": "carbon dioxide",
    "ch4": "methane",
    "c2h6": "ethane",
    "c2h5oh": "ethanol",
    "c6h12o6": "glucose",
    "c8h10n4o2": "caffeine"
}


def get_molecule(compound_input):

    # Remove spaces and make input lowercase
    user_input = compound_input.strip().lower()

    # If a formula was entered, convert it to a compound name
    if user_input in formula_names:
        search_name = formula_names[user_input]
    else:
        search_name = user_input

    # Search PubChem by name
    compounds = pcp.get_compounds(search_name, "name")

    if not compounds:
        print(f"Could not find: {compound_input}")
        return None

    compound = compounds[0]

    # Get the compound record
    record = compound.to_dict()

    # Get SMILES
    smiles = record.get("connectivity_smiles")

    if not smiles:
        print(f"SMILES not found for {compound_input}")
        return None

    print(f"{compound_input} SMILES: {smiles}")

    # Create RDKit molecule
    molecule = Chem.MolFromSmiles(smiles)

    if molecule is None:
        print(
            f"RDKit could not create the molecule "
            f"for {compound_input}"
        )
        return None

    return molecule


def get_property(molecule):

    if comparison == "molecular_weight":

        return Descriptors.ExactMolWt(molecule)

    elif comparison == "tpsa":

        return Descriptors.TPSA(molecule)

    elif comparison == "h_bond_donors":

        return Lipinski.NumHDonors(molecule)

    elif comparison == "flexibility":

        # Number of rotatable bonds
        return Lipinski.NumRotatableBonds(molecule)

    else:

        print("Invalid comparison property.")
        return None


def get_similarity(molecule1, molecule2):

    # Generate Morgan fingerprints
    generator = rdFingerprintGenerator.GetMorganGenerator(
        radius=2
    )

    fingerprint1 = generator.GetFingerprint(molecule1)
    fingerprint2 = generator.GetFingerprint(molecule2)

    # Calculate Tanimoto similarity
    similarity = DataStructs.TanimotoSimilarity(
        fingerprint1,
        fingerprint2
    )

    return similarity


def get_molecular_weight_similarity(molecule1, molecule2):

    # Calculate exact molecular weights
    weight1 = Descriptors.ExactMolWt(molecule1)
    weight2 = Descriptors.ExactMolWt(molecule2)

    # Avoid division by zero
    if max(weight1, weight2) == 0:
        return 0

    # Smaller weight divided by larger weight
    similarity = min(weight1, weight2) / max(weight1, weight2)

    return similarity


# Get two compounds
compound1 = input(
    "Enter first compound name or formula: "
)

compound2 = input(
    "Enter second compound name or formula: "
)


# Create molecule objects
molecule1 = get_molecule(compound1)
molecule2 = get_molecule(compound2)


# Only continue if both molecules were successfully created
if molecule1 is not None and molecule2 is not None:

    # Get property values
    value1 = get_property(molecule1)
    value2 = get_property(molecule2)

    print("\n--- Comparison ---")

    if comparison == "flexibility":

        print(
            compound1,
            "rotatable bonds:",
            value1
        )

        print(
            compound2,
            "rotatable bonds:",
            value2
        )

    else:

        print(compound1, ":", value1)
        print(compound2, ":", value2)


    # Compare property values

    if value1 > value2:

        if comparison == "flexibility":

            print(
                compound1,
                "is more flexible."
            )

        else:

            print(
                compound1,
                "has the higher",
                comparison
            )


    elif value2 > value1:

        if comparison == "flexibility":

            print(
                compound2,
                "is more flexible."
            )

        else:

            print(
                compound2,
                "has the higher",
                comparison
            )


    else:

        if comparison == "flexibility":

            print(
                "Both compounds have the same "
                "number of rotatable bonds."
            )

        else:

            print(
                "Both compounds have the same",
                comparison
            )


    # Calculate structural similarity
    similarity = get_similarity(
        molecule1,
        molecule2
    )

    print("\n--- Structural Similarity ---")

    print(
        "Tanimoto similarity:",
        round(similarity, 4)
    )

    print(
        "Similarity percentage:",
        round(similarity * 100, 2),
        "%"
    )


    # Calculate molecular weight similarity
    mw_similarity = get_molecular_weight_similarity(
        molecule1,
        molecule2
    )

    print("\n--- Molecular Weight Similarity ---")

    print(
        "Molecular weight similarity:",
        round(mw_similarity, 4)
    )

    print(
        "Molecular weight similarity percentage:",
        round(mw_similarity * 100, 2),
        "%"
    )
