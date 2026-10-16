

"""
Estrogen/Androgen Assay Quality Assessment
For Tox21-style TXT files.

Features:
1. Opens a file-selection window.
2. Reads a TXT, TSV, or CSV file.
3. Recognizes columns such as TOX21_ID, PROTOCOL_NAME,
   ASSAY_OUTCOME, AC50, EFFICACY, CAS, and PUBCHEM_CID.
4. Prints protocol names and assay outcome counts.
5. Selects two primary outcomes using configurable keywords.
6. Searches for matching viability/cytotoxicity records.
7. Saves a quality-assessment CSV beside the input file.

Install dependency in PyCharm Terminal:
    python3 -m pip install pandas
"""

from pathlib import Path
import re
import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd


# ==========================================================
# 1. SETTINGS
# ==========================================================

# Configure these after reviewing the printed protocol names.
# Use distinctive words that actually appear in PROTOCOL_NAME.


PRIMARY_OUTCOMES = {
    "Androgen antagonist 1": ["antagonist1"],
    "Androgen antagonist 2": ["antagonist2"],
}

VIABILITY_KEYWORDS = ["viability"]

# Keywords used to identify viability/cytotoxicity protocols.
VIABILITY_KEYWORDS = [
    "viability",
    "cytotoxicity",
    "cytotoxic",
    "cell survival",
    "cell death",
    "cell health",
]

# Used only when a result is explicitly interpreted as percent viability.
LOW_VIABILITY_PERCENT_CUTOFF = 70.0

# Column names based on the file you reported.
CHEMICAL_COLUMN = "PUBCHEM_CID"
ASSAY_COLUMN = "PROTOCOL_NAME"
RESULT_COLUMN = "ASSAY_OUTCOME"

# Your file has CONC0 through CONC15 rather than one concentration
# column. The script will compare dose-response concentration arrays
# when it can; it does not assume that AC50 equals a tested concentration.
CONCENTRATION_COLUMN = None

# If TOX21_ID is missing or does not identify chemicals consistently,
# change this to "PUBCHEM_CID", "CAS", or "SAMPLE_ID" after checking
# the identifier coverage and consistency in your file.
ALTERNATIVE_CHEMICAL_COLUMNS = [
    "PUBCHEM_CID",
    "CAS",
    "SAMPLE_ID",
]


# ==========================================================
# 2. FILE SELECTION
# ==========================================================

def select_input_file():
    """Let the user select the assay file from their computer."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    selected_file = filedialog.askopenfilename(
        title="Select your assay TXT file",
        filetypes=[
            ("Text files", "*.txt"),
            ("Tab-separated files", "*.tsv"),
            ("CSV files", "*.csv"),
            ("All files", "*.*"),
        ],
    )

    root.destroy()

    if not selected_file:
        print("No file selected. Analysis cancelled.")
        return None

    return Path(selected_file)
# ==========================================================
 # Smiles structures
# ==========================================================

import os
import time
import pandas as pd
import requests

from rdkit import Chem
from rdkit.Chem import Draw


def get_chemical_smiles(cid, existing_smiles=None):
    """
    Use the dataset SMILES when available.
    Otherwise, try retrieving canonical SMILES from PubChem.
    """
    if pd.notna(existing_smiles) and str(existing_smiles).strip():
        return str(existing_smiles).strip(), "Source dataset"

    if pd.isna(cid):
        return "", "Missing PubChem CID"

    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
        f"cid/{int(float(cid))}/property/CanonicalSMILES,ConnectivitySMILES/JSON"
    )

    try:
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            properties = response.json()["PropertyTable"]["Properties"][0]
            smiles = (
                properties.get("ConnectivitySMILES")
                or properties.get("CanonicalSMILES")
                or ""
            )

            if smiles:
                return smiles, "Retrieved from PubChem"

        return "", f"PubChem unavailable ({response.status_code})"

    except Exception as error:
        return "", f"Retrieval error: {error}"


def generate_chemical_structures(data, output_folder):
    """
    Add SMILES to a chemical lookup table and generate PNG structures.
    Returns one row per PubChem CID.
    """
    os.makedirs(output_folder, exist_ok=True)
    structure_folder = os.path.join(output_folder, "chemical_structures")
    os.makedirs(structure_folder, exist_ok=True)

    # Keep one record per chemical identifier.
    chemicals = data[["PUBCHEM_CID", "SMILES"]].copy()
    chemicals = chemicals.dropna(subset=["PUBCHEM_CID"])
    chemicals["PUBCHEM_CID"] = chemicals["PUBCHEM_CID"].astype(str).str.strip()
    chemicals = chemicals[chemicals["PUBCHEM_CID"] != ""]
    chemicals = chemicals.drop_duplicates(subset=["PUBCHEM_CID"])

    results = []

    for number, (_, row) in enumerate(chemicals.iterrows(), start=1):
        cid = row["PUBCHEM_CID"]
        original_smiles = row["SMILES"]

        smiles, smiles_source = get_chemical_smiles(
            cid, original_smiles
        )

        canonical_smiles = ""
        structure_file = ""
        structure_status = ""

        if smiles:
            molecule = Chem.MolFromSmiles(smiles)

            if molecule is not None:
                canonical_smiles = Chem.MolToSmiles(molecule)

                safe_cid = "".join(
                    character for character in cid
                    if character.isalnum() or character in "-_"
                )
                structure_file = os.path.join(
                    structure_folder, f"{safe_cid}.png"
                )

                try:
                    image = Draw.MolToImage(molecule, size=(500, 400))
                    image.save(structure_file)
                    structure_status = "Structure generated"
                except Exception as error:
                    structure_status = f"Image error: {error}"
                    structure_file = ""
            else:
                structure_status = "Invalid SMILES"
                smiles = ""
        else:
            structure_status = "SMILES unavailable"

        results.append({
            "PUBCHEM_CID": cid,
            "SMILES": smiles,
            "CANONICAL_SMILES": canonical_smiles,
            "SMILES_SOURCE": smiles_source,
            "STRUCTURE_FILE": structure_file,
            "STRUCTURE_STATUS": structure_status,
        })

        # Brief pause between external requests.
        if smiles_source == "Retrieved from PubChem":
            time.sleep(0.2)

        if number % 500 == 0:
            print(f"Processed {number:,}/{len(chemicals):,} chemicals")

    chemical_results = pd.DataFrame(results)

    smiles_path = os.path.join(
        output_folder, "tox21_chemical_smiles_and_structures.csv"
    )
    chemical_results.to_csv(smiles_path, index=False)

    print("\nChemical structure extraction complete.")
    print(f"Chemical records: {len(chemical_results):,}")
    print(f"SMILES available: {chemical_results['SMILES'].ne('').sum():,}")
    print(f"Structures generated: "
          f"{chemical_results['STRUCTURE_STATUS'].eq('Structure generated').sum():,}")
    print(f"Chemical lookup CSV: {smiles_path}")
    print(f"Structure images folder: {structure_folder}")

    return chemical_results

# ==========================================================
# 3. LOAD DATA
# ==========================================================

def load_data(file_path):
    """Read a delimited text file and preserve identifiers as strings."""
    try:
        data = pd.read_csv(
            file_path,
            sep=None,
            engine="python",
            dtype=str,
            comment="#",
            on_bad_lines="warn",
        )
    except Exception:
        data = pd.read_csv(
            file_path,
            sep="\t",
            dtype=str,
            comment="#",
            on_bad_lines="warn",
        )

    df = pd.read_csv(file_path, sep=None, engine="python")

    df = pd.read_csv(file_path, sep=None, engine="python")

    print("\n=== IDENTIFIER EXAMPLE ===")
    print(
        df[["TOX21_ID", "PUBCHEM_CID", "PUBCHEM_SID", "CAS"]]
        .head(10)
        .to_string(index=False)
    )

    print("\n=== UNIQUE IDENTIFIER COUNTS ===")
    for col in ["TOX21_ID", "PUBCHEM_CID", "PUBCHEM_SID", "CAS"]:
        print(f"{col}: {df[col].nunique(dropna=True)} unique values; "
              f"{df[col].isna().sum()} missing")

    if data.empty:
        raise ValueError("The selected file contains no data rows.")

    data.columns = [str(c).strip() for c in data.columns]
    return data

print("\n--- SMILES COLUMN DIAGNOSTIC ---")
print(data[["PUBCHEM_CID", "SMILES", "SAMPLE_NAME"]].head(20))

print("\nSMILES examples:")
print(data["SMILES"].dropna().astype(str).head(30).to_list())

print("\nValues beginning with Tox21_:")
print(
    data.loc[
        data["SMILES"].astype(str).str.startswith("Tox21_", na=False),
        ["PUBCHEM_CID", "SMILES", "SAMPLE_NAME"]
    ].head(20)
)
# ==========================================================
# 4. COLUMN AND TEXT HELPERS
# ==========================================================

def normalize_name(name):
    return re.sub(
        r"[^a-z0-9]+", "_", str(name).lower()
    ).strip("_")


def get_column(data, preferred, alternatives=None, required=True):
    """Find a configured column or a listed alternative."""
    alternatives = alternatives or []
    candidates = [preferred] + alternatives

    for candidate in candidates:
        if candidate and candidate in data.columns:
            return candidate

    if required:
        raise ValueError(
            f"Could not find column {preferred!r}.\n"
            f"Available columns: {list(data.columns)}"
        )

    return None


def contains_any(text, keywords):
    """Case-insensitive literal keyword search."""
    text = str(text).lower()
    return any(
        str(keyword).lower() in text
        for keyword in keywords
    )


def print_protocol_summary(data, assay_col, result_col):
    """Display assay names and outcome counts for configuring filters."""
    print("\n" + "=" * 65)
    print("PROTOCOL NAMES FOUND IN YOUR FILE")
    print("=" * 65)

    protocols = sorted(
        data[assay_col].dropna().astype(str).unique()
    )

    for protocol in protocols:
        print(" -", protocol)

    print(f"\nNumber of unique protocols: {len(protocols)}")

    print("\n" + "=" * 65)
    print("ASSAY OUTCOME COUNTS")
    print("=" * 65)

    print(
        data[result_col]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\n" + "=" * 65)
    print("CHEMICAL IDENTIFIER COVERAGE")
    print("=" * 65)

    for col in [
        "TOX21_ID",
        "SAMPLE_ID",
        "CAS",
        "PUBCHEM_CID",
        "PUBCHEM_SID",
    ]:
        if col in data.columns:
            nonempty = data[col].notna() & (
                data[col].astype(str).str.strip() != ""
            )
            print(f"{col}: {nonempty.sum()} nonempty rows")


# ==========================================================
# 5. IDENTIFY VIABILITY RECORDS
# ==========================================================

def identify_viability_rows(data, assay_col):
    """
    Find records whose protocol names contain viability keywords.

    NOTE: This is a keyword-based first pass. Review the printed
    protocol names because viability assays may have unfamiliar names.
    """
    return data[assay_col].fillna("").apply(
        lambda name: contains_any(name, VIABILITY_KEYWORDS)
    )


# ==========================================================
# 6. SELECT PRIMARY ASSAY OUTCOMES
# ==========================================================

def select_primary_rows(data, assay_col, viability_mask):
    """Select rows whose protocol names match configured keywords."""
    primary_data = data.loc[~viability_mask].copy()
    selected_groups = []

    for group_name, keywords in PRIMARY_OUTCOMES.items():
        mask = primary_data[assay_col].fillna("").apply(
            lambda name: contains_any(name, keywords)
        )

        group = primary_data.loc[mask].copy()
        group["primary_outcome_group"] = group_name
        selected_groups.append(group)

        print(
            f"{group_name}: {len(group)} matching assay records"
        )

    selected = pd.concat(
        selected_groups, ignore_index=True
    ).drop_duplicates()

    return selected


# ==========================================================
# 7. MATCH VIABILITY RECORDS
# ==========================================================




def match_viability(
    primary_row,
    viability_data,
    chemical_col,
    assay_col,
    result_col,
):
    """Match to the paired viability protocol, preferring SAMPLE_ID."""

    primary_protocol = str(primary_row.get(assay_col, "")).strip().lower()
    chemical_id = primary_row.get(chemical_col)

    if primary_protocol not in {"antagonist1", "antagonist2", "antagonist3"}:
        return {
            "matched_viability_assay": "",
            "matched_viability_result": "",
            "viability_match_status": "Unknown antagonist protocol",
            "quality_assessment": "Inconclusive: verify protocol pairing",
        }

    paired_protocol = primary_protocol.replace("antagonist", "viability")

    paired_data = viability_data[
        viability_data[assay_col].astype(str).str.strip().str.lower()
        == paired_protocol
    ].copy()

    # Prefer SAMPLE_ID if it identifies the same sample across protocols.
    sample_id = primary_row.get("SAMPLE_ID")
    matching = pd.DataFrame()

    if (
        "SAMPLE_ID" in paired_data.columns
        and pd.notna(sample_id)
        and str(sample_id).strip()
    ):
        matching = paired_data[
            paired_data["SAMPLE_ID"].astype("string").str.strip()
            == str(sample_id).strip()
        ]

    match_method = "SAMPLE_ID"

    # Fall back to chemical ID if there is no sample-ID match.
    if matching.empty:
        match_method = "PUBCHEM_CID"

        if pd.isna(chemical_id) or not str(chemical_id).strip():
            return {
                "matched_viability_assay": paired_protocol,
                "matched_viability_result": "",
                "viability_match_status": "No usable identifier",
                "quality_assessment": "Inconclusive: identifier unavailable",
            }

        matching = paired_data[
            paired_data[chemical_col].astype("string").str.strip()
            == str(chemical_id).strip()
        ]

    if matching.empty:
        return {
            "matched_viability_assay": paired_protocol,
            "matched_viability_result": "",
            "viability_match_status": "No paired viability record",
            "quality_assessment": "Inconclusive: viability unavailable",
        }

    results = " | ".join(
        matching[result_col].dropna().astype(str).unique()
    )

    if len(matching) > 1:
        status = (
            f"Multiple records ({len(matching)}) matched by {match_method}; "
            "review before interpretation"
        )
        assessment = (
            "Ambiguous viability match; verify sample identity, "
            "concentration, and assay conditions"
        )
    else:
        status = f"One record matched by {match_method}"
        assessment = (
            "Viability record matched; verify outcome-code meaning "
            "and assay conditions"
        )

    return {
        "matched_viability_assay": paired_protocol,
        "matched_viability_result": results,
        "viability_match_status": status,
        "quality_assessment": assessment,
    }
#============================================================
# CHARACTERIZE MISSING DATA
#=============================================================

def characterize_missing_data(data):
    """Summarize missing values overall and by assay protocol."""

    print("\n" + "=" * 70)
    print("MISSING DATA CHARACTERIZATION")
    print("=" * 70)

    total_rows, total_columns = data.shape
    total_cells = total_rows * total_columns
    missing_cells = int(data.isna().sum().sum())

    print(f"\nTotal rows: {total_rows:,}")
    print(f"Total columns: {total_columns:,}")
    print(f"Total data cells: {total_cells:,}")
    print(f"Missing cells: {missing_cells:,}")
    print(f"Overall missingness: {missing_cells / total_cells * 100:.2f}%")

    # Missing values in each column
    missing_summary = pd.DataFrame({
        "column": data.columns,
        "missing_count": data.isna().sum().values,
        "nonmissing_count": data.notna().sum().values,
        "missing_percent": (
                data.isna().mean().values * 100
        ),
    })

    missing_summary = missing_summary.sort_values(
        "missing_percent", ascending=False
    )

    print("\n--- MISSING VALUES BY COLUMN ---")
    print(missing_summary.to_string(
        index=False,
        formatters={"missing_percent": "{:.2f}%".format}
    ))

    # Columns with no missing values
    complete_columns = missing_summary.loc[
        missing_summary["missing_count"] == 0, "column"
    ].tolist()

    print("\n--- COLUMNS WITH NO MISSING VALUES ---")
    if complete_columns:
        print(", ".join(complete_columns))
    else:
        print("None")

    # Columns that are entirely missing
    empty_columns = missing_summary.loc[
        missing_summary["missing_count"] == total_rows, "column"
    ].tolist()

    print("\n--- COLUMNS ENTIRELY MISSING ---")
    if empty_columns:
        print(", ".join(empty_columns))
    else:
        print("None")

    # Missingness by assay protocol
    if "PROTOCOL_NAME" in data.columns:
        print("\n--- MISSINGNESS BY PROTOCOL ---")

        protocol_missing = data.groupby(
            "PROTOCOL_NAME", dropna=False
        ).apply(
            lambda group: pd.Series({
                "rows": len(group),
                "missing_cells": int(group.isna().sum().sum()),
                "missing_percent": (
                    group.isna().sum().sum()
                    / (len(group) * len(group.columns)) * 100
                    if len(group) > 0 else 0
                ),
            }),
            include_groups=False
        )

        print(protocol_missing.to_string(
            formatters={
                "missing_percent": "{:.2f}%".format
            }
        ))

    # Missingness in important assay and identifier fields
    important_columns = [
        "SAMPLE_ID",
        "SAMPLE_DATA_ID",
        "PROTOCOL_NAME",
        "SAMPLE_DATA_TYPE",
        "ASSAY_OUTCOME",
        "AC50",
        "EFFICACY",
        "PUBCHEM_CID",
        "CAS",
        "PUBCHEM_SID",
        "TOX21_ID",
    ]

    available_columns = [
        column for column in important_columns
        if column in data.columns
    ]

    print("\n--- KEY ASSAY FIELD COMPLETENESS ---")
    for column in available_columns:
        missing_count = int(data[column].isna().sum())
        missing_percent = data[column].isna().mean() * 100

        print(
            f"{column}: {missing_count:,} missing "
            f"({missing_percent:.2f}%)"
        )

    return missing_summary

# ==========================================================
# 8. MAIN ANALYSIS
# ==========================================================

def run_analysis(input_path):
    print("\nESTROGEN/ANDROGEN ASSAY QUALITY ASSESSMENT")
    print("=" * 65)
    print(f"Input file: {input_path}")

    data = load_data(input_path)
    output_folder = os.path.dirname(input_path)

    chemical_results = generate_chemical_structures(
        data,
        output_folder
    )
    missing_summary = characterize_missing_data(data)

    output_folder = os.path.dirname(input_path)

    missing_report_path = os.path.join(
        output_folder,
        "tox21_androgen_antagonist_missing_data_report.csv"
    )

    missing_summary.to_csv(missing_report_path, index=False)

    print(f"\nMissing-data report saved to:\n{missing_report_path}")
    print(f"Rows loaded: {len(data):,}")
    print("\nColumns in the file:")
    for col in data.columns:
        print(" -", col)

    # Identify chemical ID. Prefer TOX21_ID, then check alternatives.
    chemical_col = get_column(
        data,
        CHEMICAL_COLUMN,
        alternatives=ALTERNATIVE_CHEMICAL_COLUMNS,
    )

    assay_col = get_column(
        data,
        ASSAY_COLUMN,
        alternatives=["ASSAY", "ASSAY_NAME", "PROTOCOL"],
    )

    result_col = get_column(
        data,
        RESULT_COLUMN,
        alternatives=["RESULT", "ACTIVITY_OUTCOME", "OUTCOME"],
    )

    print(f"\nChemical identifier used: {chemical_col}")
    print(f"Protocol column used: {assay_col}")
    print(f"Outcome column used: {result_col}")

    # Print these before filtering so keywords can be configured properly.
    print_protocol_summary(data, assay_col, result_col)

    viability_mask = identify_viability_rows(data, assay_col)
    viability_data = data.loc[viability_mask].copy()


    # Check chemical overlap between corresponding protocols.
    print("\n--- ANTIGONIST / VIABILITY CHEMICAL MATCH CHECK ---")

    if chemical_col and assay_col:
        for i in [1, 2, 3]:
            antagonist_name = f"antagonist{i}"
            viability_name = f"viability{i}"

            antagonist_rows = data[
                data[assay_col].astype(str).str.strip().str.lower()
                == antagonist_name
            ]

            viability_rows = data[
                data[assay_col].astype(str).str.strip().str.lower()
                == viability_name
            ]

            antagonist_ids = set(
                antagonist_rows[chemical_col].dropna().astype(str).str.strip()
            )
            viability_ids = set(
                viability_rows[chemical_col].dropna().astype(str).str.strip()
            )

            shared_ids = antagonist_ids & viability_ids

            print(f"\n{antagonist_name} vs {viability_name}")
            print("Antagonist rows:", len(antagonist_rows))
            print("Viability rows:", len(viability_rows))
            print("Shared chemical IDs:", len(shared_ids))

    print(
        f"\nViability/cytotoxicity records identified: "
        f"{len(viability_data):,}"
    )

    selected = select_primary_rows(
        data,
        assay_col,
        viability_mask,
    )

    if selected.empty:
        print("\nNo primary rows matched your current settings.")
        print("Update PRIMARY_OUTCOMES at the top of the script.")
        print("Use distinctive words from the printed protocol names.")
        return None

    if viability_data.empty:
        print(
            "\nWARNING: No protocols matched VIABILITY_KEYWORDS. "
            "The file may not contain viability data, or the viability "
            "protocol names may use different wording."
        )

    # Match each selected primary record to viability records.
    output_records = []

    for _, primary_row in selected.iterrows():
        match_info = match_viability(
            primary_row,
            viability_data,
            chemical_col,
            assay_col,
            result_col,
        )

        record = primary_row.to_dict()
        record.update(match_info)

        # Preserve relevant Tox21 dose-response summary values if present.
        for optional_col in [
            "AC50",
            "EFFICACY",
            "CURVE_CLASS2",
            "R2",
            "ZERO_ACTIVITY",
            "INF_ACTIVITY",
        ]:
            if optional_col in data.columns:
                record[optional_col] = primary_row.get(optional_col)

        output_records.append(record)

    results = pd.DataFrame(output_records)

    output_path = input_path.with_name(
        input_path.stem + "_quality_assessment.csv"
    )

    results.to_csv(output_path, index=False)

    print("\n" + "=" * 65)
    print("ANALYSIS COMPLETE")
    print("=" * 65)
    print(f"Primary records selected: {len(selected):,}")
    print(f"Viability records identified: {len(viability_data):,}")
    print(f"Results saved to:\n{output_path}")

    preview_cols = [
        "primary_outcome_group",
        chemical_col,
        assay_col,
        result_col,
        "AC50",
        "EFFICACY",
        "matched_viability_assay",
        "matched_viability_result",
        "viability_match_status",
        "quality_assessment",
    ]

    preview_cols = [
        col for col in preview_cols if col in results.columns
    ]

    print("\nPreview of the output:")
    print(results[preview_cols].head(15).to_string(index=False))

    print("\nINTERPRETATION REMINDERS")
    print("- Check the two selected protocols are the intended endpoints.")
    print("- Confirm chemical IDs are consistent across assay records.")
    print("- Confirm viability assay conditions and concentration.")
    print("- A missing viability match does not mean a chemical is safe.")
    print("- A viability record alone does not establish causation.")

    print("\n--- MATCH QUALITY SUMMARY ---")

    print("\nViability match status:")
    print(results["viability_match_status"].value_counts(dropna=False))

    print("\nNumber of matched records per primary chemical:")
    print(
        results.groupby(
            ["PROTOCOL_NAME", chemical_col]
        )["matched_viability_result"]
        .size()
        .describe()
    )

    print("\nRows with multiple viability results:")
    multiple_matches = results[
        results["viability_match_status"].str.contains(
            r"Matched ([2-9]|[1-9][0-9]+) record",
            na=False,
            regex=True,
        )
    ]

    print(
        multiple_matches[
            [
                "PROTOCOL_NAME",
                chemical_col,
                "matched_viability_assay",
                "matched_viability_result",
                "viability_match_status",
            ]
        ].head(10).to_string(index=False)
    )

    return output_path


# ==========================================================
# 9. START PROGRAM AND HANDLE ERRORS
# ==========================================================

def main():
    input_path = select_input_file()

    if input_path is None:
        return

    try:
        output_path = run_analysis(input_path)

        if output_path:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(
                "Analysis Complete",
                "The quality-assessment report was saved to:\n\n"
                f"{output_path}",
            )
            root.destroy()

    except Exception as error:
        print("\nERROR")
        print("=" * 65)
        print(error)

        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Analysis Error", str(error))
            root.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    main()


