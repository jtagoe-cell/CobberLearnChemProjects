"""Tox21 androgen antagonist assay quality assessment.

Outputs:
- *_quality_assessment.csv
- tox21_androgen_antagonist_missing_data_report.csv
- tox21_chemical_smiles_and_structures.csv
- chemical_structures/*.png

Install dependencies in the PyCharm terminal:
    python -m pip install pandas requests rdkit
"""

from pathlib import Path
import re
import time
import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd
import requests
from rdkit import Chem, RDLogger

# Hide noisy RDKit parse messages; invalid strings are handled in the code.
RDLogger.DisableLog("rdApp.error")


# ============================= SETTINGS =============================
PRIMARY_OUTCOMES = {
    "Androgen antagonist 1": ["antagonist1"],
    "Androgen antagonist 2": ["antagonist2"],
}

VIABILITY_KEYWORDS = [
    "viability", "cytotoxicity", "cytotoxic", "cell survival",
    "cell death", "cell health",
]
CHEMICAL_COLUMN = "PUBCHEM_CID"
ASSAY_COLUMN = "PROTOCOL_NAME"
RESULT_COLUMN = "ASSAY_OUTCOME"

# Set False to prevent generating 2D PNG structure images.
GENERATE_STRUCTURE_IMAGES = False

# ============================= FILE INPUT =============================
def select_input_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    selected = filedialog.askopenfilename(
        title="Select your Tox21 assay file",
        filetypes=[("Text files", "*.txt"), ("TSV files", "*.tsv"),
                   ("CSV files", "*.csv"), ("All files", "*.*")],
    )
    root.destroy()
    return Path(selected) if selected else None


def load_data(file_path):
    """Read the file once, preserving chemical and sample identifiers as text."""
    try:
        data = pd.read_csv(
            file_path, sep=None, engine="python", dtype=str,
            comment="#", on_bad_lines="warn",
        )
    except Exception:
        data = pd.read_csv(
            file_path, sep="\t", dtype=str, comment="#", on_bad_lines="warn"
        )
    if data.empty:
        raise ValueError("The selected file contains no data rows.")
    data.columns = [str(c).strip() for c in data.columns]
    return data


def normalize_text(value):
    return str(value).strip().lower() if pd.notna(value) else ""


def contains_any(value, keywords):
    text = normalize_text(value)
    return any(str(word).lower() in text for word in keywords)


def print_protocol_summary(data):
    print("\nPROTOCOL NAMES FOUND")
    for protocol in sorted(data[ASSAY_COLUMN].dropna().astype(str).unique()):
        print(" -", protocol)
    print("\nASSAY OUTCOME COUNTS")
    print(data[RESULT_COLUMN].value_counts(dropna=False).to_string())
    print("\nIDENTIFIER COVERAGE")
    for col in ["TOX21_ID", "SAMPLE_ID", "CAS", "PUBCHEM_CID", "PUBCHEM_SID", "SMILES"]:
        if col in data.columns:
            values = data[col].fillna("").astype(str).str.strip()
            print(f"{col}: {(values != '').sum():,} nonempty rows")

# ============================= MISSING DATA =============================
def characterize_missing_data(data):
    total_rows, total_cols = data.shape
    total_cells = total_rows * total_cols
    missing_cells = int(data.isna().sum().sum())
    print("\n" + "=" * 65)
    print("MISSING DATA CHARACTERIZATION")
    print("=" * 65)
    print(f"Rows: {total_rows:,}; columns: {total_cols:,}")
    print(f"Missing cells: {missing_cells:,} / {total_cells:,} ({100 * missing_cells / total_cells:.2f}%)")

    summary = pd.DataFrame({
        "column": data.columns,
        "missing_count": data.isna().sum().values,
        "nonmissing_count": data.notna().sum().values,
        "missing_percent": data.isna().mean().values * 100,
    }).sort_values("missing_percent", ascending=False)
    print("\nMissingness by column:")
    print(summary.to_string(index=False, formatters={"missing_percent": "{:.2f}%".format}))

    if ASSAY_COLUMN in data.columns:
        rows = []
        for protocol, group in data.groupby(ASSAY_COLUMN, dropna=False):
            cells = group.shape[0] * group.shape[1]
            missing = int(group.isna().sum().sum())
            rows.append({
                "PROTOCOL_NAME": protocol,
                "rows": len(group),
                "missing_cells": missing,
                "missing_percent": 100 * missing / cells if cells else 0,
            })
        protocol_summary = pd.DataFrame(rows)
        print("\nMissingness by protocol:")
        print(protocol_summary.to_string(index=False, formatters={"missing_percent": "{:.2f}%".format}))
    return summary


# ============================= CHEMICAL SMILES / STRUCTURES =============================
def is_valid_smiles(value):
    """Validate a potential SMILES, rejecting known identifiers before RDKit parsing."""
    if value is None or pd.isna(value):
        return False
    text = str(value).strip()
    if not text or re.match(r"^(tox21[_ -]|pubchem|cas[:_ -])", text, re.I):
        return False
    # Tox21 identifiers are labels, not molecular notation.
    if re.fullmatch(r"[A-Za-z]+[_-]\d+", text):
        return False
    return Chem.MolFromSmiles(text) is not None


def fetch_pubchem_smiles_batch(cids, batch_size=80):
    """Retrieve connectivity SMILES in batches to avoid one request per chemical."""
    found = {}
    session = requests.Session()
    clean_cids = []
    for cid in cids:
        cid_text = str(cid).strip()
        if cid_text.isdigit():
            clean_cids.append(cid_text)

    for start in range(0, len(clean_cids), batch_size):
        batch = clean_cids[start:start + batch_size]
        url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
            + ",".join(batch)
            + "/property/ConnectivitySMILES/JSON"
        )
        try:
            response = session.get(url, timeout=30)
            if response.status_code == 200:
                for item in response.json().get("PropertyTable", {}).get("Properties", []):
                    cid = str(item.get("CID", ""))
                    smiles = item.get("ConnectivitySMILES", "")
                    if smiles and is_valid_smiles(smiles):
                        found[cid] = smiles
            else:
                print(f"PubChem batch request returned HTTP {response.status_code}; batch starting at {start} skipped.")
        except Exception as exc:
            print(f"PubChem batch request failed near record {start + 1}: {exc}")
        if start + batch_size < len(clean_cids):
            time.sleep(0.15)
        print(f"PubChem lookup progress: {min(start + batch_size, len(clean_cids)):,}/{len(clean_cids):,}", end="\r")
    if clean_cids:
        print()
    return found




def generate_chemical_structures(data, output_folder):
    """Retrieve actual SMILES from PubChem and save a chemical lookup CSV.
    Does not generate any 2D structure images.
    """
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    if "PUBCHEM_CID" not in data.columns:
        raise ValueError("PUBCHEM_CID column is required.")

    # Get one row per chemical.
    unique_chemicals = data[["PUBCHEM_CID"]].drop_duplicates().copy()

    unique_chemicals["PUBCHEM_CID"] = (
        unique_chemicals["PUBCHEM_CID"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    # Retrieve real molecular SMILES from PubChem.
    cids = unique_chemicals.loc[
        unique_chemicals["PUBCHEM_CID"].str.fullmatch(r"\d+"),
        "PUBCHEM_CID"
    ].drop_duplicates().tolist()

    print(f"\nRetrieving actual SMILES for {len(cids):,} unique PubChem CIDs...")
    smiles_by_cid = fetch_pubchem_smiles_batch(cids)

    # Create the chemical lookup table.
    output_rows = []

    for cid in unique_chemicals["PUBCHEM_CID"]:
        smiles = smiles_by_cid.get(cid, "")

        if smiles and is_valid_smiles(smiles):
            status = "Actual SMILES retrieved and validated"
        elif not cid:
            status = "Missing PubChem CID"
        elif not cid.isdigit():
            status = "Invalid PubChem CID"
        else:
            status = "SMILES retrieval failed or unavailable"

        output_rows.append({
            "PUBCHEM_CID": cid,
            "SMILES": smiles,
            "STRUCTURE_STATUS": status,
            "IMAGE_PATH": ""
        })

    output = pd.DataFrame(output_rows)

    csv_path = output_folder / "tox21_chemical_smiles_and_structures.csv"
    output.to_csv(csv_path, index=False)

    retrieved_count = output["SMILES"].ne("").sum()
    unresolved_count = len(output) - retrieved_count

    print(f"Unique chemicals: {len(output):,}")
    print(f"Actual SMILES retrieved: {retrieved_count:,}")
    print(f"Unresolved chemicals: {unresolved_count:,}")
    print(f"Chemical lookup CSV saved: {csv_path}")
    print("2D structure image generation is disabled.")

    return smiles_by_cid

    # Use SAMPLE_ID only if it actually finds a record in the paired protocol.
    if sample_id and "SAMPLE_ID" in group.columns:
        matching = group[group["_sample_key"] == sample_id]
        if not matching.empty:
            method = "SAMPLE_ID"
    if matching.empty and chemical_id:
        matching = group[group["_chemical_key"] == chemical_id]
        method = "PUBCHEM_CID"
    if matching.empty:
        return {
            "matched_viability_assay": paired,
            "matched_viability_result": "",
            "viability_match_status": "No paired viability record",
            "quality_assessment": "Inconclusive: viability unavailable",
        }

    outcomes = matching[result_col].dropna().astype(str).unique().tolist()
    outcome_text = " | ".join(outcomes)
    if len(matching) > 1:
        status = f"Multiple records ({len(matching)}) matched by {method}; review before interpretation"
        assessment = "Ambiguous viability match; verify sample identity, concentration, and assay conditions"
    else:
        status = f"One record matched by {method}"
        assessment = "Viability record matched; verify outcome-code meaning and assay conditions"
    return {
        "matched_viability_assay": paired,
        "matched_viability_result": outcome_text,
        "viability_match_status": status,
        "quality_assessment": assessment,
    }
def identify_viability_rows(data):
    """
    Identify rows belonging to viability/cytotoxicity protocols.
    """
    if "PROTOCOL_NAME" not in data.columns:
        print("ERROR: PROTOCOL_NAME column is missing.")
        return data.iloc[0:0].copy()

    protocol_names = (
        data["PROTOCOL_NAME"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    viability_mask = protocol_names.str.startswith("viability")

    viability_data = data.loc[viability_mask].copy()

    print(f"Viability records identified: {len(viability_data):,}")

    return viability_data

def run_analysis(input_path):
    input_path = Path(input_path)
    output_folder = input_path.parent
    print("\nANDROGEN ANTAGONIST ASSAY QUALITY ASSESSMENT")
    print("=" * 65)
    print(f"Input file: {input_path}")

    data = load_data(input_path)
    print(f"Rows loaded: {len(data):,}")
    print("Duplicate column names:")
    print(data.columns[data.columns.duplicated()].tolist())

    print("Data shape:", data.shape)
    print("Column names:", data.columns.tolist())

    print("\n--- SMILES COLUMN DIAGNOSTIC ---")
    print("Column names:", data.columns.tolist())

    if "PUBCHEM_CID" in data.columns and "SMILES" in data.columns:
        print(
            data[["PUBCHEM_CID", "SMILES"]]
            .drop_duplicates()
            .head(20)
            .to_string(index=False)
        )
    else:
        print("PUBCHEM_CID or SMILES column is missing.")

    print("\n--- SMILES COLUMN DIAGNOSTIC ---")
    print("Column names:", data.columns.tolist())

    if "PUBCHEM_CID" in data.columns and "SMILES" in data.columns:
        print(
            data[["PUBCHEM_CID", "SMILES"]]
            .drop_duplicates()
            .head(20)
            .to_string(index=False)
        )
    else:
        print("PUBCHEM_CID or SMILES column is missing.")

    # Keep the rest of the existing function below this point.
    print(f"Rows loaded: {len(data):,}")
    required = [CHEMICAL_COLUMN, ASSAY_COLUMN, RESULT_COLUMN]
    missing_required = [c for c in required if c not in data.columns]
    if missing_required:
        raise ValueError(f"Required column(s) missing: {missing_required}. Available columns: {list(data.columns)}")

    print_protocol_summary(data)
    missing_summary = characterize_missing_data(data)
    missing_path = output_folder / "tox21_androgen_antagonist_missing_data_report.csv"
    missing_summary.to_csv(missing_path, index=False)
    print(f"Missing-data report saved: {missing_path}")

    if "PUBCHEM_CID" in data.columns and "SMILES" in data.columns:
        generate_chemical_structures(data, output_folder)
    else:
        print("Skipping chemical structures: PUBCHEM_CID or SMILES column is missing.")

    viability_mask = identify_viability_rows(data)
    viability_data = data.loc[viability_mask].copy()
    print(f"\nViability/cytotoxicity records identified: {len(viability_data):,}")
    selected = select_primary_rows(data, viability_mask)
    if selected.empty:
        raise ValueError("No primary records matched PRIMARY_OUTCOMES. Check the protocol names and settings.")

    # Normalize keys and index viability rows once, rather than repeatedly scanning all rows.
    viability_data["_chemical_key"] = viability_data[CHEMICAL_COLUMN].fillna("").astype(str).str.strip().str.lower()
    viability_data["_sample_key"] = viability_data.get("SAMPLE_ID", pd.Series("", index=viability_data.index)).fillna("").astype(str).str.strip().str.lower()
    viability_lookup = {
        normalize_text(protocol): group
        for protocol, group in viability_data.groupby(ASSAY_COLUMN, dropna=False)
    }

    records = []
    for _, row in selected.iterrows():
        match_info = match_viability(row, viability_lookup, CHEMICAL_COLUMN, ASSAY_COLUMN, RESULT_COLUMN)
        record = row.to_dict()
        record.update(match_info)
        records.append(record)
    results = pd.DataFrame(records)

    output_path = input_path.with_name(input_path.stem + "_quality_assessment.csv")
    results.to_csv(output_path, index=False)
    print("\n" + "=" * 65)
    print("ANALYSIS COMPLETE")
    print("=" * 65)
    print(f"Primary records selected: {len(selected):,}")
    print(f"Viability records identified: {len(viability_data):,}")
    print(f"Quality-assessment CSV saved: {output_path}")
    print("\nViability match status counts:")
    print(results["viability_match_status"].value_counts(dropna=False).to_string())
    preview = [c for c in ["primary_outcome_group", CHEMICAL_COLUMN, ASSAY_COLUMN, RESULT_COLUMN,
                           "matched_viability_assay", "matched_viability_result",
                           "viability_match_status", "quality_assessment"] if c in results.columns]
    print("\nPreview:")
    print(results[preview].head(10).to_string(index=False))
    print("\nReminder: multiple chemical-level matches are ambiguous; confirm protocol metadata and outcome-code definitions.")
    return output_path


def main():
    input_path = select_input_file()
    if input_path is None:
        print("No file selected. Analysis cancelled.")
        return
    try:
        output_path = run_analysis(input_path)
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Analysis Complete", f"Quality-assessment report saved to:\n\n{output_path}")
        root.destroy()
    except Exception as exc:
        print("\nERROR\n" + "=" * 65)
        print(exc)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Analysis Error", str(exc))
            root.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    main()
