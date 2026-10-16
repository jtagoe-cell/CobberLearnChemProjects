
import pandas as pd
import numpy as np
from pathlib import Path
from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

data_folder = Path(
    "/Users/janicetagoe/Downloads/"
    "tox21-ar-mda-kb2-luc-antagonist-p1"
)

input_file = data_folder / "tox21_chemical_smiles_and_structures.csv"
output_file = data_folder / "tox21_morgan_fingerprints.csv"

# --------------------------------------------------
# 2. CHECK INPUT FILE
# --------------------------------------------------

if not input_file.exists():
    raise FileNotFoundError(
        f"Input file not found: {input_file}\n"
        "Check that your chemical lookup CSV exists."
    )

chemicals = pd.read_csv(input_file, dtype=str)
chemicals.columns = chemicals.columns.str.strip()

print("Input file loaded successfully.")
print("Number of rows:", len(chemicals))
print("Available columns:", chemicals.columns.tolist())

# --------------------------------------------------
# 3. IDENTIFY CID AND SMILES COLUMNS
# --------------------------------------------------

cid_column = "PUBCHEM_CID"

# Find a column containing actual molecular SMILES.
# Adjust this list if your lookup CSV uses another name.
possible_smiles_columns = [
    "SMILES",
    "PUBCHEM_SMILES",
    "CanonicalSMILES",
    "ConnectivitySMILES",
    "IsomericSMILES"
]

smiles_column = next(
    (column for column in possible_smiles_columns
     if column in chemicals.columns),
    None
)

if cid_column not in chemicals.columns:
    raise ValueError(
        f"Missing {cid_column}. Available columns: "
        f"{chemicals.columns.tolist()}"
    )

if smiles_column is None:
    raise ValueError(
        "Could not identify the molecular SMILES column. "
        "Check the available columns printed above and set "
        "smiles_column to the correct column name."
    )

print("Chemical identifier column:", cid_column)
print("Molecular SMILES column:", smiles_column)

# --------------------------------------------------
# 4. CONFIGURE MORGAN FINGERPRINTS
# --------------------------------------------------

radius = 2
fingerprint_size = 2048

generator = rdFingerprintGenerator.GetMorganGenerator(
    radius=radius,
    fpSize=fingerprint_size
)

# --------------------------------------------------
# 5. GENERATE FINGERPRINTS
# --------------------------------------------------

fingerprint_records = []
fingerprint_objects = []

invalid_smiles = 0
missing_smiles = 0

for _, row in chemicals.iterrows():

    cid = row[cid_column]
    smiles = row[smiles_column]

    if pd.isna(smiles) or not str(smiles).strip():
        missing_smiles += 1
        continue

    molecule = Chem.MolFromSmiles(str(smiles).strip())

    if molecule is None:
        invalid_smiles += 1
        continue

    fingerprint = generator.GetFingerprint(molecule)

    # Convert fingerprint into 2048 binary values
    bits = np.zeros((fingerprint_size,), dtype=np.int8)
    DataStructs.ConvertToNumpyArray(fingerprint, bits)

    record = {
        "PUBCHEM_CID": cid,
        "Morgan_Radius": radius,
        "Morgan_Bits": fingerprint_size,
        "Morgan_On_Bit_Count": int(bits.sum()),
        "Morgan_Fingerprint_BitString": fingerprint.ToBitString()
    }

    # Add individual fingerprint bits as columns
    for bit_index, bit_value in enumerate(bits):
        record[f"FP_{bit_index:04d}"] = int(bit_value)

    fingerprint_records.append(record)
    fingerprint_objects.append((cid, fingerprint))

# --------------------------------------------------
# 6. SAVE RESULTS
# --------------------------------------------------

if not fingerprint_records:
    raise ValueError(
        "No valid fingerprints were generated. "
        "Check that the selected column contains actual molecular SMILES."
    )

fingerprint_df = pd.DataFrame(fingerprint_records)
fingerprint_df.to_csv(output_file, index=False)

# --------------------------------------------------
# 7. REPORT RESULTS
# --------------------------------------------------

print("\n----------------------------------------")
print("MORGAN FINGERPRINT GENERATION COMPLETE")
print("----------------------------------------")
print("Input chemicals:", len(chemicals))
print("Fingerprints generated:", len(fingerprint_records))
print("Missing SMILES:", missing_smiles)
print("Invalid SMILES:", invalid_smiles)
print("Fingerprint radius:", radius)
print("Fingerprint size:", fingerprint_size)
print("Output file:", output_file)

# --------------------------------------------------
# 8. OPTIONAL: EXAMPLE SIMILARITY COMPARISON
# --------------------------------------------------

if len(fingerprint_objects) >= 2:

    cid_1, fingerprint_1 = fingerprint_objects[0]
    cid_2, fingerprint_2 = fingerprint_objects[1]

    similarity = DataStructs.TanimotoSimilarity(
        fingerprint_1,
        fingerprint_2
    )

    print("\nExample Tanimoto similarity:")
    print("Chemical 1 CID:", cid_1)
    print("Chemical 2 CID:", cid_2)
    print(f"Similarity: {similarity:.4f}")
