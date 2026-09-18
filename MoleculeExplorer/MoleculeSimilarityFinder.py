
import pubchempy as pcp
from rdkit import Chem, DataStructs
from rdkit.Chem import Descriptors, rdFingerprintGenerator


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
    compounds = pcp.get_compounds(
        search_name,
        "name"
    )

    if not compounds:
        print(
            f"Could not find: {compound_input}"
        )
        return None

    compound = compounds[0]

    # Get compound record
    record = compound.to_dict()

    # Get SMILES
    smiles = record.get(
        "connectivity_smiles"
    )

    if not smiles:
        print(
            f"SMILES not found for {compound_input}"
        )
        return None

    print(
        f"{compound_input} SMILES: {smiles}"
    )

    # Create RDKit molecule
    molecule = Chem.MolFromSmiles(smiles)

    if molecule is None:
        print(
            f"RDKit could not create molecule "
            f"for {compound_input}"
        )
        return None

    return molecule


def get_molecular_weight(molecule):

    return Descriptors.ExactMolWt(molecule)


def molecular_weight_similarity(
    weight1,
    weight2
):

    # Avoid division by zero
    if max(weight1, weight2) == 0:
        return 0

    # Compare smaller weight to larger weight
    similarity = (
        min(weight1, weight2)
        / max(weight1, weight2)
    )

    return similarity * 100


def structural_similarity(
    molecule1,
    molecule2
):

    # Create Morgan fingerprints
    generator = rdFingerprintGenerator.GetMorganGenerator(
        radius=2
    )

    fingerprint1 = generator.GetFingerprint(
        molecule1
    )

    fingerprint2 = generator.GetFingerprint(
        molecule2
    )

    # Calculate Tanimoto similarity
    similarity = DataStructs.TanimotoSimilarity(
        fingerprint1,
        fingerprint2
    )

    return similarity * 100


# --------------------------------
# Molecules to search
# --------------------------------

molecule_database = [
    "water",
    "ammonia",
    "methane",
    "ethane",
    "methanol",
    "ethanol",
    "propanol",
    "butanol",
    "acetone",
    "acetic acid",
    "glucose",
    "caffeine",
    "benzene",
    "toluene",
    "phenol",
    "urea"
]


# --------------------------------
# Get user's molecule
# --------------------------------

user_input = input(
    "Enter a molecule to find similar "
    "molecules: "
)


# --------------------------------
# Create user's molecule
# --------------------------------

user_molecule = get_molecule(
    user_input
)


if user_molecule is not None:

    # Calculate user's molecular weight
    user_weight = get_molecular_weight(
        user_molecule
    )

    print(
        "\nMolecule:",
        user_input
    )

    print(
        "Molecular weight:",
        round(user_weight, 4),
        "g/mol"
    )


    # --------------------------------
    # Compare against database
    # --------------------------------

    results = []

    for compound_name in molecule_database:

        # Don't compare molecule against itself
        if (
            compound_name.lower()
            == user_input.strip().lower()
        ):
            continue

        # Get molecule
        molecule = get_molecule(
            compound_name
        )

        if molecule is None:
            continue

        # Calculate molecular weight
        weight = get_molecular_weight(
            molecule
        )

        # Calculate molecular-weight difference
        difference = abs(
            user_weight - weight
        )

        # Calculate molecular-weight similarity
        mw_similarity = molecular_weight_similarity(
            user_weight,
            weight
        )

        # Calculate structural similarity
        structure_similarity = structural_similarity(
            user_molecule,
            molecule
        )

        # Store results
        results.append(
            (
                compound_name,
                weight,
                difference,
                mw_similarity,
                structure_similarity
            )
        )


    # --------------------------------
    # Sort by molecular-weight
    # difference
    # --------------------------------

    mw_results = sorted(
        results,
        key=lambda x: x[2]
    )


    # --------------------------------
    # Most similar by molecular weight
    # --------------------------------

    print(
        "\n--- Most Similar Molecular Weight ---"
    )

    for result in mw_results[:5]:

        name = result[0]
        weight = result[1]
        difference = result[2]
        mw_similarity = result[3]
        structure_similarity = result[4]

        print(
            f"{name}: "
            f"{weight:.4f} g/mol | "
            f"MW difference: {difference:.4f} g/mol | "
            f"MW similarity: {mw_similarity:.2f}% | "
            f"Structural similarity: "
            f"{structure_similarity:.2f}%"
        )


    # --------------------------------
    # Least similar by molecular weight
    # --------------------------------

    print(
        "\n--- Least Similar Molecular Weight ---"
    )

    for result in mw_results[-3:]:

        name = result[0]
        weight = result[1]
        difference = result[2]
        mw_similarity = result[3]
        structure_similarity = result[4]

        print(
            f"{name}: "
            f"{weight:.4f} g/mol | "
            f"MW difference: {difference:.4f} g/mol | "
            f"MW similarity: {mw_similarity:.2f}% | "
            f"Structural similarity: "
            f"{structure_similarity:.2f}%"
        )


    # --------------------------------
    # Sort by structural similarity
    # --------------------------------

    structural_results = sorted(
        results,
        key=lambda x: x[4],
        reverse=True
    )


    # --------------------------------
    # Most structurally similar
    # --------------------------------

    print(
        "\n--- Most Structurally Similar ---"
    )

    for result in structural_results[:5]:

        name = result[0]
        weight = result[1]
        difference = result[2]
        mw_similarity = result[3]
        structure_similarity = result[4]

        print(
            f"{name}: "
            f"Structural similarity: "
            f"{structure_similarity:.2f}% | "
            f"MW: {weight:.4f} g/mol | "
            f"MW difference: {difference:.4f} g/mol | "
            f"MW similarity: {mw_similarity:.2f}%"
        )


    # --------------------------------
    # Least structurally similar
    # --------------------------------

    print(
        "\n--- Least Structurally Similar ---"
    )

    for result in structural_results[-3:]:

        name = result[0]
        weight = result[1]
        difference = result[2]
        mw_similarity = result[3]
        structure_similarity = result[4]

        print(
            f"{name}: "
            f"Structural similarity: "
            f"{structure_similarity:.2f}% | "
            f"MW: {weight:.4f} g/mol | "
            f"MW difference: {difference:.4f} g/mol | "
            f"MW similarity: {mw_similarity:.2f}%"
        )
