# ============================================================
# Tox21 / ToxCast TWO-ASSAY COMPARISON
# ============================================================
#
# INPUT:
#   Two downloaded .txt assay files
#
# OUTPUT:
#   - Standardized assay 1 CSV
#   - Standardized assay 2 CSV
#   - Matched chemical comparison CSV
#   - Assay-vs-assay scatter plot
#   - Potency difference plot
#   - Endpoint comparison CSV
#   - Endpoint comparison graph
#
# OUTPUT LOCATION:
#   A "Tox21_Assay_Comparison_Results" folder is automatically
#   created in the same directory as this Python script.
#
# ============================================================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from tkinter import Tk, filedialog


# ============================================================
# SETTINGS
# ============================================================

# Number of endpoints shown in endpoint graph
TOP_N_ENDPOINTS = 20

# Target concentration unit
TARGET_UNIT = "uM"

# IMPORTANT:
# If your AC50/EC50 column does not have a separate unit
# column, this is the unit the script will assume.
#
# Change to "nM" if your file reports AC50 in nanomolar.
#
DEFAULT_POTENCY_UNIT = "uM"


# ============================================================
# 1. SELECT TWO FILES
# ============================================================

root = Tk()
root.withdraw()

print("=" * 70)
print("SELECT ASSAY 1")
print("=" * 70)

file1 = filedialog.askopenfilename(
    title="Select Tox21/ToxCast Assay 1",
    filetypes=[
        ("Text files", "*.txt"),
        ("All files", "*.*")
    ]
)

if not file1:
    raise SystemExit("Assay 1 was not selected.")

print("\nAssay 1:")
print(file1)


print("\n" + "=" * 70)
print("SELECT ASSAY 2")
print("=" * 70)

file2 = filedialog.askopenfilename(
    title="Select Tox21/ToxCast Assay 2",
    filetypes=[
        ("Text files", "*.txt"),
        ("All files", "*.*")
    ]
)

if not file2:
    raise SystemExit("Assay 2 was not selected.")

print("\nAssay 2:")
print(file2)


# Close Tkinter window
root.destroy()


# ============================================================
# 2. LOAD TXT FILE
# ============================================================

def load_txt_file(file_path):

    print("\nLoading:")
    print(file_path)

    try:

        data = pd.read_csv(
            file_path,
            sep=None,
            engine="python",
            low_memory=False
        )

    except Exception:

        print(
            "Automatic delimiter detection failed."
        )

        print(
            "Trying tab-delimited format..."
        )

        data = pd.read_csv(
            file_path,
            sep="\t",
            low_memory=False
        )

    print(
        "Rows:",
        len(data),
        "| Columns:",
        len(data.columns)
    )

    return data


# ============================================================
# 3. LOAD DATASETS
# ============================================================

assay1 = load_txt_file(file1)

assay2 = load_txt_file(file2)


# ============================================================
# 4. DISPLAY COLUMNS
# ============================================================

def show_columns(data, name):

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    for i, column in enumerate(data.columns):

        print(f"{i}: {column}")


show_columns(
    assay1,
    "ASSAY 1 COLUMNS"
)

show_columns(
    assay2,
    "ASSAY 2 COLUMNS"
)


# ============================================================
# 5. COLUMN DETECTION
# ============================================================

def find_column(data, possible_names):

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    for name in possible_names:

        if name in data.columns:

            return name


    # --------------------------------------------------------
    # Case-insensitive exact match
    # --------------------------------------------------------

    lower_map = {
        str(column).lower(): column
        for column in data.columns
    }

    for name in possible_names:

        if name.lower() in lower_map:

            return lower_map[name.lower()]


    # --------------------------------------------------------
    # Partial match
    # --------------------------------------------------------

    for column in data.columns:

        column_lower = str(column).lower()

        for name in possible_names:

            if name.lower() in column_lower:

                return column


    return None


# ============================================================
# 6. CHEMICAL IDENTIFIER
# ============================================================

chemical_names = [

    "DTXSID",
    "DSSTox_CID",
    "CASRN",
    "CAS",
    "chemical_name",
    "Chemical Name",
    "chemical",
    "Chemical",
    "compound_name",
    "Compound Name",
    "compound",
    "Compound"
]


chemical_col1 = find_column(
    assay1,
    chemical_names
)

chemical_col2 = find_column(
    assay2,
    chemical_names
)


print("\n" + "=" * 70)
print("CHEMICAL IDENTIFIER")
print("=" * 70)

print("Assay 1:", chemical_col1)

print("Assay 2:", chemical_col2)


# ============================================================
# 7. POTENCY COLUMN
# ============================================================

potency_names = [

    "AC50",
    "ac50",
    "AC50_uM",
    "ac50_uM",
    "AC50 (uM)",
    "AC50 (µM)",
    "AC50 (μM)",

    "EC50",
    "ec50",
    "EC50_uM",
    "ec50_uM",
    "EC50 (uM)",
    "EC50 (µM)",
    "EC50 (μM)"
]


potency_col1 = find_column(
    assay1,
    potency_names
)

potency_col2 = find_column(
    assay2,
    potency_names
)


print("\n" + "=" * 70)
print("POTENCY COLUMNS")
print("=" * 70)

print("Assay 1:", potency_col1)

print("Assay 2:", potency_col2)


# ============================================================
# 8. UNIT COLUMN
# ============================================================

unit_names = [

    "AC50_unit",
    "AC50_unit_name",
    "AC50 units",

    "EC50_unit",
    "EC50_unit_name",

    "unit",
    "units",
    "Unit",
    "Units",

    "concentration_unit",
    "Concentration Unit"
]


unit_col1 = find_column(
    assay1,
    unit_names
)

unit_col2 = find_column(
    assay2,
    unit_names
)


print("\n" + "=" * 70)
print("UNIT COLUMNS")
print("=" * 70)

print("Assay 1:", unit_col1)

print("Assay 2:", unit_col2)


# ============================================================
# 9. ENDPOINT COLUMN
# ============================================================

endpoint_names = [

    "endpoint",
    "Endpoint",

    "endpoint_name",
    "Endpoint Name",

    "assay",
    "Assay",

    "assay_name",
    "Assay Name",

    "assay_component_endpoint_name",
    "assay_component_endpoint"
]


endpoint_col1 = find_column(
    assay1,
    endpoint_names
)

endpoint_col2 = find_column(
    assay2,
    endpoint_names
)


print("\n" + "=" * 70)
print("ENDPOINT COLUMNS")
print("=" * 70)

print("Assay 1:", endpoint_col1)

print("Assay 2:", endpoint_col2)


# ============================================================
# 10. CHECK REQUIRED COLUMNS
# ============================================================

if chemical_col1 is None:

    raise ValueError(
        "\nCould not identify the chemical identifier "
        "column in Assay 1.\n\n"
        "Columns found were printed above."
    )


if chemical_col2 is None:

    raise ValueError(
        "\nCould not identify the chemical identifier "
        "column in Assay 2.\n\n"
        "Columns found were printed above."
    )


if potency_col1 is None:

    raise ValueError(
        "\nCould not identify the potency column "
        "in Assay 1."
    )


if potency_col2 is None:

    raise ValueError(
        "\nCould not identify the potency column "
        "in Assay 2."
    )


# ============================================================
# 11. CONCENTRATION CONVERSION
# ============================================================

def normalize_unit(unit):

    if pd.isna(unit):

        return None

    unit = str(unit).strip().lower()

    unit = (
        unit
        .replace("μ", "u")
        .replace("µ", "u")
        .replace(" ", "")
    )

    return unit


def convert_to_uM(value, unit):

    if pd.isna(value):

        return np.nan

    try:

        value = float(value)

    except (ValueError, TypeError):

        return np.nan

    unit = normalize_unit(unit)

    if unit is None:

        return np.nan


    # Conversion factors TO µM

    conversion = {

        # Molar
        "m": 1_000_000,
        "mol/l": 1_000_000,
        "molar": 1_000_000,

        # Millimolar
        "mm": 1_000,
        "mmol/l": 1_000,
        "millimolar": 1_000,

        # Micromolar
        "um": 1,
        "umol/l": 1,
        "micromolar": 1,

        # Nanomolar
        "nm": 0.001,
        "nmol/l": 0.001,
        "nanomolar": 0.001,

        # Picomolar
        "pm": 0.000001,
        "pmol/l": 0.000001,
        "picomolar": 0.000001,

        # Femtomolar
        "fm": 0.000000001,
        "fmol/l": 0.000000001
    }


    if unit not in conversion:

        return np.nan


    return value * conversion[unit]


# ============================================================
# 12. PREPARE ASSAY DATA
# ============================================================

def prepare_assay(
    data,
    chemical_column,
    potency_column,
    unit_column,
    assay_name
):

    result = data.copy()


    # --------------------------------------------------------
    # Chemical identifier
    # --------------------------------------------------------

    result["Chemical_ID"] = (
        result[chemical_column]
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # Potency
    # --------------------------------------------------------

    result["Original_Potency"] = pd.to_numeric(
        result[potency_column],
        errors="coerce"
    )


    # --------------------------------------------------------
    # UNIT HANDLING
    # --------------------------------------------------------

    if unit_column is not None:

        # A separate unit column exists.

        result["Original_Unit"] = (
            result[unit_column]
            .astype(str)
            .str.strip()
        )

        result["Potency_uM"] = result.apply(
            lambda row: convert_to_uM(
                row["Original_Potency"],
                row["Original_Unit"]
            ),
            axis=1
        )


    else:

        # No unit column was detected.
        #
        # First inspect the potency column name.

        column_name = (
            str(potency_column)
            .lower()
            .strip()
        )


        # ----------------------------------------------------
        # Nanomolar
        # ----------------------------------------------------

        if (
            "nm" in column_name
        ):

            result["Original_Unit"] = "nM"

            result["Potency_uM"] = (
                result["Original_Potency"] * 0.001
            )


        # ----------------------------------------------------
        # Micromolar
        # ----------------------------------------------------

        elif (
            "um" in column_name
            or "µm" in column_name
            or "μm" in column_name
        ):

            result["Original_Unit"] = "uM"

            result["Potency_uM"] = (
                result["Original_Potency"]
            )


        # ----------------------------------------------------
        # Millimolar
        # ----------------------------------------------------

        elif (
            "mm" in column_name
        ):

            result["Original_Unit"] = "mM"

            result["Potency_uM"] = (
                result["Original_Potency"] * 1000
            )


        # ----------------------------------------------------
        # Plain AC50 / EC50
        # ----------------------------------------------------

        elif column_name in [
            "ac50",
            "ec50"
        ]:

            result["Original_Unit"] = (
                DEFAULT_POTENCY_UNIT
            )

            result["Potency_uM"] = result[
                "Original_Potency"
            ].apply(
                lambda x: convert_to_uM(
                    x,
                    DEFAULT_POTENCY_UNIT
                )
            )


        # ----------------------------------------------------
        # Unknown unit
        # ----------------------------------------------------

        else:

            raise ValueError(
                f"\n{assay_name}: Could not determine "
                f"the concentration unit for "
                f"'{potency_column}'.\n\n"
                f"Set DEFAULT_POTENCY_UNIT at the "
                f"top of the script."
            )


    # --------------------------------------------------------
    # Remove missing concentrations
    # --------------------------------------------------------

    result = result[
        result["Potency_uM"].notna()
    ].copy()


    # --------------------------------------------------------
    # Remove zero/negative concentrations
    # --------------------------------------------------------

    result = result[
        result["Potency_uM"] > 0
    ].copy()


    # --------------------------------------------------------
    # Calculate pPotency
    # --------------------------------------------------------

    result["pPotency"] = (
        -np.log10(
            result["Potency_uM"]
        )
    )


    # --------------------------------------------------------
    # Keep useful fields
    # --------------------------------------------------------

    result = result[
        [
            "Chemical_ID",
            "Original_Potency",
            "Original_Unit",
            "Potency_uM",
            "pPotency"
        ]
    ].copy()


    # --------------------------------------------------------
    # If a chemical appears multiple times,
    # use median potency.
    # --------------------------------------------------------

    result = (
        result
        .groupby(
            "Chemical_ID",
            as_index=False
        )
        .agg(
            Original_Potency=(
                "Original_Potency",
                "median"
            ),

            Potency_uM=(
                "Potency_uM",
                "median"
            ),

            pPotency=(
                "pPotency",
                "median"
            )
        )
    )


    return result


# ============================================================
# 13. PREPARE BOTH ASSAYS
# ============================================================

prepared1 = prepare_assay(
    assay1,
    chemical_col1,
    potency_col1,
    unit_col1,
    "Assay 1"
)


prepared2 = prepare_assay(
    assay2,
    chemical_col2,
    potency_col2,
    unit_col2,
    "Assay 2"
)


print("\n" + "=" * 70)
print("STANDARDIZATION RESULTS")
print("=" * 70)

print(
    "Assay 1 usable chemicals:",
    len(prepared1)
)

print(
    "Assay 2 usable chemicals:",
    len(prepared2)
)

print(
    "\nAll concentrations are standardized to µM."
)


# ============================================================
# 14. MATCH CHEMICALS
# ============================================================

comparison = pd.merge(

    prepared1[
        [
            "Chemical_ID",
            "Potency_uM",
            "pPotency"
        ]
    ],

    prepared2[
        [
            "Chemical_ID",
            "Potency_uM",
            "pPotency"
        ]
    ],

    on="Chemical_ID",

    how="inner",

    suffixes=(
        "_Assay1",
        "_Assay2"
    )
)


print("\n" + "=" * 70)
print("MATCHED CHEMICALS")
print("=" * 70)

print(
    "Chemicals in both assays:",
    len(comparison)
)


if len(comparison) < 2:

    raise ValueError(
        "\nFewer than two chemicals were found "
        "in both assays."
    )


# ============================================================
# 15. CALCULATE DIFFERENCES
# ============================================================

comparison["pPotency_Difference"] = (

    comparison["pPotency_Assay1"]

    -

    comparison["pPotency_Assay2"]
)


comparison["Fold_Difference"] = (

    comparison["Potency_uM_Assay2"]

    /

    comparison["Potency_uM_Assay1"]
)


# ============================================================
# 16. CORRELATION
# ============================================================

correlation = comparison[
    [
        "pPotency_Assay1",
        "pPotency_Assay2"
    ]
].corr().iloc[0, 1]


print(
    "\nPearson correlation:",
    round(correlation, 4)
)


# ============================================================
# 17. OUTPUT DIRECTORY
# ============================================================

# Explicit PyCharm project directory
pycharm_directory = (
    "/Users/janicetagoe/"
    "PycharmProjects/"
    "CobberLearnChemProjects/"
    "AndrogenAgonist"
)

# Results folder inside the AndrogenAgonist project
output_folder = os.path.join(
    pycharm_directory,
    "Tox21_Assay_Comparison_Results"
)

# Create the folder automatically
os.makedirs(
    output_folder,
    exist_ok=True
)

print("\n" + "=" * 70)
print("OUTPUT DIRECTORY")
print("=" * 70)

print("PyCharm project directory:")
print(pycharm_directory)

print("\nResults directory:")
print(output_folder)

print(
    "\nDirectory exists:",
    os.path.exists(output_folder)
)

print(
    "Directory is writable:",
    os.access(output_folder, os.W_OK)
)

# ============================================================
# 18. SAVE MATCHED DATA
# ============================================================

comparison_file = os.path.join(
    output_folder,
    "matched_assay_data.csv"
)


comparison.to_csv(
    comparison_file,
    index=False
)


print(
    "\nSaved:",
    comparison_file
)


# ============================================================
# 19. ASSAY-VS-ASSAY SCATTER PLOT
# ============================================================

plt.figure(
    figsize=(9, 8)
)


sns.regplot(
    data=comparison,

    x="pPotency_Assay1",

    y="pPotency_Assay2",

    scatter_kws={
        "alpha": 0.65
    },

    line_kws={
        "color": "red"
    }
)


plt.xlabel(
    "Assay 1 pPotency"
)

plt.ylabel(
    "Assay 2 pPotency"
)

plt.title(
    "Tox21/ToxCast Assay Comparison"
)


plt.text(
    0.05,
    0.95,

    f"Pearson r = {correlation:.3f}",

    transform=plt.gca().transAxes,

    verticalalignment="top"
)


plt.tight_layout()


scatter_file = os.path.join(
    output_folder,
    "assay_vs_assay_scatter.png"
)


plt.savefig(
    scatter_file,
    dpi=300,
    bbox_inches="tight"
)


plt.show()


print(
    "Saved:",
    scatter_file
)


# ============================================================
# 20. POTENCY DIFFERENCE GRAPH
# ============================================================

plt.figure(
    figsize=(10, 7)
)


sns.histplot(
    comparison["pPotency_Difference"],
    bins=30,
    kde=True
)


plt.axvline(
    0,
    color="black",
    linestyle="--"
)


plt.xlabel(
    "Assay 1 pPotency - Assay 2 pPotency"
)

plt.ylabel(
    "Number of chemicals"
)

plt.title(
    "Difference in Standardized Assay Potency"
)


plt.tight_layout()


difference_file = os.path.join(
    output_folder,
    "assay_potency_difference.png"
)


plt.savefig(
    difference_file,
    dpi=300,
    bbox_inches="tight"
)


plt.show()


print(
    "Saved:",
    difference_file
)


# ============================================================
# 21. ENDPOINT COMPARISON
# ============================================================

if (
    endpoint_col1 is not None
    and endpoint_col2 is not None
):

    print(
        "\nEndpoint information detected "
        "in both files."
    )


    # --------------------------------------------------------
    # Prepare endpoint assay 1
    # --------------------------------------------------------

    endpoint1 = assay1[
        [
            chemical_col1,
            endpoint_col1,
            potency_col1
        ]
    ].copy()


    # --------------------------------------------------------
    # Prepare endpoint assay 2
    # --------------------------------------------------------

    endpoint2 = assay2[
        [
            chemical_col2,
            endpoint_col2,
            potency_col2
        ]
    ].copy()


    # --------------------------------------------------------
    # Potency numeric conversion
    # --------------------------------------------------------

    endpoint1["Potency"] = pd.to_numeric(
        endpoint1[potency_col1],
        errors="coerce"
    )


    endpoint2["Potency"] = pd.to_numeric(
        endpoint2[potency_col2],
        errors="coerce"
    )


    # --------------------------------------------------------
    # Standardize endpoint assay 1
    # --------------------------------------------------------

    if unit_col1 is not None:

        endpoint1["Unit"] = (
            assay1.loc[
                endpoint1.index,
                unit_col1
            ]
        )


        endpoint1["Potency_uM"] = endpoint1.apply(
            lambda row: convert_to_uM(
                row["Potency"],
                row["Unit"]
            ),
            axis=1
        )


    else:

        # Use the same default unit assumption
        # used for the main assay.

        endpoint1["Potency_uM"] = (
            endpoint1["Potency"].apply(
                lambda x: convert_to_uM(
                    x,
                    DEFAULT_POTENCY_UNIT
                )
            )
        )


    # --------------------------------------------------------
    # Standardize endpoint assay 2
    # --------------------------------------------------------

    if unit_col2 is not None:

        endpoint2["Unit"] = (
            assay2.loc[
                endpoint2.index,
                unit_col2
            ]
        )


        endpoint2["Potency_uM"] = endpoint2.apply(
            lambda row: convert_to_uM(
                row["Potency"],
                row["Unit"]
            ),
            axis=1
        )


    else:

        endpoint2["Potency_uM"] = (
            endpoint2["Potency"].apply(
                lambda x: convert_to_uM(
                    x,
                    DEFAULT_POTENCY_UNIT
                )
            )
        )


    # --------------------------------------------------------
    # Remove invalid concentrations
    # --------------------------------------------------------

    endpoint1 = endpoint1[
        endpoint1["Potency_uM"] > 0
    ].copy()


    endpoint2 = endpoint2[
        endpoint2["Potency_uM"] > 0
    ].copy()


    # --------------------------------------------------------
    # Calculate pPotency
    # --------------------------------------------------------

    endpoint1["pPotency"] = (
        -np.log10(
            endpoint1["Potency_uM"]
        )
    )


    endpoint2["pPotency"] = (
        -np.log10(
            endpoint2["Potency_uM"]
        )
    )


    # --------------------------------------------------------
    # Endpoint summary - Assay 1
    # --------------------------------------------------------

    summary1 = (
        endpoint1
        .groupby(endpoint_col1)
        .agg(
            Number_of_records=(
                "pPotency",
                "count"
            ),

            Median_pPotency=(
                "pPotency",
                "median"
            )
        )
        .reset_index()
    )


    summary1["Assay"] = "Assay 1"


    summary1 = summary1.rename(
        columns={
            endpoint_col1: "Endpoint"
        }
    )


    # --------------------------------------------------------
    # Endpoint summary - Assay 2
    # --------------------------------------------------------

    summary2 = (
        endpoint2
        .groupby(endpoint_col2)
        .agg(
            Number_of_records=(
                "pPotency",
                "count"
            ),

            Median_pPotency=(
                "pPotency",
                "median"
            )
        )
        .reset_index()
    )


    summary2["Assay"] = "Assay 2"


    summary2 = summary2.rename(
        columns={
            endpoint_col2: "Endpoint"
        }
    )


    # --------------------------------------------------------
    # Combine summaries
    # --------------------------------------------------------

    endpoint_summary = pd.concat(
        [
            summary1,
            summary2
        ],
        ignore_index=True
    )


    # --------------------------------------------------------
    # Save endpoint summary
    # --------------------------------------------------------

    endpoint_csv = os.path.join(
        output_folder,
        "endpoint_comparison_summary.csv"
    )


    endpoint_summary.to_csv(
        endpoint_csv,
        index=False
    )


    print(
        "Saved:",
        endpoint_csv
    )


    # --------------------------------------------------------
    # Find endpoints present in both assays
    # --------------------------------------------------------

    common_endpoints = set(
        summary1["Endpoint"]
    ).intersection(
        set(summary2["Endpoint"])
    )


    endpoint_plot_data = endpoint_summary[
        endpoint_summary["Endpoint"].isin(
            common_endpoints
        )
    ].copy()


    # --------------------------------------------------------
    # Select endpoints with the most observations
    # --------------------------------------------------------

    top_endpoints = (
        endpoint_plot_data
        .groupby("Endpoint")
        ["Number_of_records"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(TOP_N_ENDPOINTS)
        .index
    )


    endpoint_plot_data = endpoint_plot_data[
        endpoint_plot_data["Endpoint"].isin(
            top_endpoints
        )
    ]


    # --------------------------------------------------------
    # Endpoint graph
    # --------------------------------------------------------

    if len(endpoint_plot_data) > 0:

        plt.figure(
            figsize=(14, 9)
        )


        sns.barplot(
            data=endpoint_plot_data,

            x="Median_pPotency",

            y="Endpoint",

            hue="Assay"
        )


        plt.xlabel(
            "Median pPotency (-log10 concentration in µM)"
        )

        plt.ylabel(
            "Endpoint"
        )

        plt.title(
            "Comparison of Tox21/ToxCast Assay Endpoints"
        )


        plt.legend(
            title="Assay"
        )


        plt.tight_layout()


        endpoint_graph = os.path.join(
            output_folder,
            "endpoint_comparison.png"
        )


        plt.savefig(
            endpoint_graph,
            dpi=300,
            bbox_inches="tight"
        )


        plt.show()


        print(
            "Saved:",
            endpoint_graph
        )


    else:

        print(
            "\nNo common endpoints were found."
        )


else:

    print(
        "\nEndpoint comparison was skipped."
    )

    print(
        "An endpoint column was not detected "
        "in both files."
    )


# ============================================================
# 22. SAVE STANDARDIZED DATA
# ============================================================

standardized1_file = os.path.join(
    output_folder,
    "assay1_standardized.csv"
)


standardized2_file = os.path.join(
    output_folder,
    "assay2_standardized.csv"
)


prepared1.to_csv(
    standardized1_file,
    index=False
)


prepared2.to_csv(
    standardized2_file,
    index=False
)


print(
    "Saved:",
    standardized1_file
)

print(
    "Saved:",
    standardized2_file
)


# ============================================================
# 23. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)

print(
    "ANALYSIS COMPLETE"
)

print("=" * 70)


print(
    "\nResults folder:"
)

print(
    output_folder
)


print(
    "\nChemicals compared:",
    len(comparison)
)


print(
    "Pearson correlation:",
    round(correlation, 4)
)


print(
    "\nConcentration standardization:"
)

print(
    "Target unit: µM"
)


print(
    "Default AC50/EC50 unit:",
    DEFAULT_POTENCY_UNIT
)


print(
    "\nAll available graphs and CSV files "
    "have been saved automatically."
)


print(
    "\nDone!"
)
