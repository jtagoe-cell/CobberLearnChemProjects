
import pandas as pd
from pathlib import Path

folder = Path(
    "/Users/janicetagoe/Downloads/"
    "tox21-ar-mda-kb2-luc-antagonist-p1"
)

input_file = folder / (
    "tox21-ar-mda-kb2-luc-antagonist-p1.txt"
)


df = pd.read_csv(input_file, sep=None, engine="python", dtype=str)

# Normalize column names.
df.columns = df.columns.str.strip()

# Check for duplicate column names.
duplicates = df.columns[df.columns.duplicated(keep=False)].tolist()

if duplicates:
    print("Duplicate column names found:", sorted(set(duplicates)))
else:
    print("No duplicate column names found.")

# Reset row index to ensure it is unique.
df = df.reset_index(drop=True)

# Check the proposed protocol pairings.
pairs = [
    ("antagonist1", "viability1"),
    ("antagonist2", "viability2"),
    ("antagonist3", "viability3"),
]

for primary_name, viability_name in pairs:
    primary = df[df["PROTOCOL_NAME"] == primary_name].copy()
    viability = df[df["PROTOCOL_NAME"] == viability_name].copy()

    primary_cids = set(primary["PUBCHEM_CID"].dropna())
    viability_cids = set(viability["PUBCHEM_CID"].dropna())

    shared = primary_cids & viability_cids
    no_viability = primary_cids - viability_cids

    print(f"\n{primary_name} -> {viability_name}")
    print("-" * 45)
    print("Primary rows:", len(primary))
    print("Viability rows:", len(viability))
    print("Unique primary chemicals:", len(primary_cids))
    print("Unique shared chemicals:", len(shared))
    print("Primary chemicals without a viability CID:", len(no_viability))

    # Confirm both names refer to single columns.
    for column in ["ASSAY_OUTCOME", "SAMPLE_DATA_TYPE"]:
        print(f"{column} column count:", list(df.columns).count(column))

    if (
            list(df.columns).count("ASSAY_OUTCOME") == 1
            and list(df.columns).count("SAMPLE_DATA_TYPE") == 1
    ):
        print("\nASSAY_OUTCOME by SAMPLE_DATA_TYPE")

        outcome_table = pd.crosstab(
            df["ASSAY_OUTCOME"].reset_index(drop=True),
            df["SAMPLE_DATA_TYPE"].reset_index(drop=True),
            dropna=False
        )

        print(outcome_table.to_string())
    else:
        print("Fix duplicate column names before generating the table.")

    # Count viability records per chemical.
    counts = viability.groupby("PUBCHEM_CID").size()

    print("Chemicals with one viability record:",
          int((counts == 1).sum()))
    print("Chemicals with multiple viability records:",
          int((counts > 1).sum()))

    # Inspect sample IDs; these may differ between protocols.
    print("Sample IDs present in both protocols:",
          len(set(primary["SAMPLE_ID"].dropna()) &
              set(viability["SAMPLE_ID"].dropna())))

# Inspect how numeric outcomes relate to the supplied classifications.
print("\nASSAY_OUTCOME by SAMPLE_DATA_TYPE")
print(pd.crosstab(
    df["ASSAY_OUTCOME"],
    df["SAMPLE_DATA_TYPE"],
    dropna=False
).to_string())

# Show the actual categories for each protocol.
print("\nSAMPLE_DATA_TYPE by protocol")
print(pd.crosstab(
    df["PROTOCOL_NAME"],
    df["SAMPLE_DATA_TYPE"],
    dropna=False
).to_string())

# Save diagnostics for review.
diagnostic_file = folder / "tox21_validation_diagnostics.txt"

with open(diagnostic_file, "w") as f:
    f.write("ASSAY_OUTCOME by SAMPLE_DATA_TYPE\n")
    f.write(pd.crosstab(
        df["ASSAY_OUTCOME"], df["SAMPLE_DATA_TYPE"]
    ).to_string())
    f.write("\n\nSAMPLE_DATA_TYPE by protocol\n")
    f.write(pd.crosstab(
        df["PROTOCOL_NAME"], df["SAMPLE_DATA_TYPE"]
    ).to_string())

print("\nDiagnostics saved to:", diagnostic_file)

primary = df[df["PROTOCOL_NAME"] == "antagonist1"]
viability = df[df["PROTOCOL_NAME"] == "viability1"]

duplicate_cids = (
    viability.groupby("PUBCHEM_CID")
    .size()
    .loc[lambda counts: counts > 1]
    .index
)

print("\nExample chemicals with multiple viability records:")

for cid in list(duplicate_cids[:5]):
    print(f"\nPUBCHEM_CID: {cid}")

    print(
        viability.loc[
            viability["PUBCHEM_CID"] == cid,
            [
                "PUBCHEM_CID",
                "SAMPLE_ID",
                "SAMPLE_DATA_ID",
                "PROTOCOL_NAME",
                "ASSAY_OUTCOME",
                "SAMPLE_DATA_TYPE",
            ],
        ].to_string(index=False)
    )
