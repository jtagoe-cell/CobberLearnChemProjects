# ============================================================
# TOX21 / TOXCAST
# INITIAL DESCRIPTIVE ANALYSIS
# ============================================================
#
# REPORTS:
#   1. Total chemical counts
#   2. Total record counts
#   3. Active/inactive counts
#   4. Active/inactive percentages
#   5. Results by primary endpoint
#   6. Numerical-variable summaries
#   7. Missing-data summaries
#
# OUTPUT:
#   descriptive_analysis_summary.csv
#   endpoint_activity_summary.csv
#   numerical_variable_summary.csv
#   descriptive_analysis.txt
#
# ============================================================

import os
import re
import numpy as np
import pandas as pd

from tkinter import Tk, filedialog


# ============================================================
# SETTINGS
# ============================================================

# Directory where results will be saved
PYCHARM_DIRECTORY = (
    "/Users/janicetagoe/"
    "PycharmProjects/"
    "CobberLearnChemProjects/"
    "AndrogenAntagonist"
)

OUTPUT_FOLDER = os.path.join(
    PYCHARM_DIRECTORY,
    "Tox21_Assay_Comparison_Results"
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ============================================================
# 1. SELECT ASSAY FILES
# ============================================================

root = Tk()
root.withdraw()

print("=" * 70)
print("SELECT TOX21/TOXCAST ASSAY FILE")
print("=" * 70)

file1 = filedialog.askopenfilename(
    title="Select Tox21/ToxCast Assay",
    filetypes=[
        ("Text files", "*.txt"),
        ("CSV files", "*.csv"),
        ("All files", "*.*")
    ]
)

root.destroy()

if not file1:
    raise SystemExit(
        "No assay file was selected."
    )


print("\nSelected file:")
print(file1)


# ============================================================
# 2. LOAD FILE
# ============================================================

def load_data(file_path):

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
            "Trying tab-delimited format."
        )

        data = pd.read_csv(
            file_path,
            sep="\t",
            low_memory=False
        )

    print(
        "\nRows:",
        len(data)
    )

    print(
        "Columns:",
        len(data.columns)
    )

    return data


data = load_data(file1)


# ============================================================
# 3. DISPLAY COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("AVAILABLE COLUMNS")
print("=" * 70)

for i, column in enumerate(data.columns):

    print(
        f"{i}: {column}"
    )


# ============================================================
# 4. COLUMN DETECTION
# ============================================================

def find_column(
    data,
    possible_names
):

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    for name in possible_names:

        if name in data.columns:

            return name


    # --------------------------------------------------------
    # Case-insensitive match
    # --------------------------------------------------------

    lower_map = {

        str(column).lower():
            column

        for column in data.columns
    }


    for name in possible_names:

        if name.lower() in lower_map:

            return lower_map[
                name.lower()
            ]


    # --------------------------------------------------------
    # Partial match
    # --------------------------------------------------------

    for column in data.columns:

        column_lower = (
            str(column).lower()
        )

        for name in possible_names:

            if name.lower() in column_lower:

                return column


    return None


# ============================================================
# 5. CHEMICAL IDENTIFIER
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


chemical_column = find_column(
    data,
    chemical_names
)


print("\nChemical identifier:")
print(chemical_column)


# ============================================================
# 6. ENDPOINT COLUMN
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


endpoint_column = find_column(
    data,
    endpoint_names
)


print("\nEndpoint column:")
print(endpoint_column)


# ============================================================
# 7. ACTIVITY COLUMN
# ============================================================

activity_names = [

    "activity",

    "Activity",

    "activity_call",

    "Activity Call",

    "activity_call_name",

    "Activity Call Name",

    "active",

    "Active",

    "active_inactive",

    "Active_Inactive",

    "hit_call",

    "Hit Call",

    "hit",

    "Hit",

    "response",

    "Response",

    "result",

    "Result",

    "call",

    "Call"
]


activity_column = find_column(
    data,
    activity_names
)


print("\nActivity column:")
print(activity_column)


# ============================================================
# 8. POTENCY COLUMN
# ============================================================

potency_names = [

    "AC50",

    "ac50",

    "AC50_uM",

    "ac50_uM",

    "EC50",

    "ec50",

    "EC50_uM",

    "ec50_uM",

    "IC50",

    "ic50",

    "IC50_uM",

    "ic50_uM"
]


potency_column = find_column(
    data,
    potency_names
)


print("\nPotency column:")
print(potency_column)


# ============================================================
# 9. NUMERICAL VARIABLES
# ============================================================

print("\n" + "=" * 70)
print("NUMERICAL VARIABLES")
print("=" * 70)


numeric_columns = []

for column in data.columns:

    converted = pd.to_numeric(
        data[column],
        errors="coerce"
    )

    numeric_count = converted.notna().sum()

    if numeric_count > 0:

        numeric_columns.append(
            column
        )

        print(
            f"{column}: "
            f"{numeric_count} numeric values"
        )


# ============================================================
# 10. CHEMICAL COUNT
# ============================================================

if chemical_column is not None:

    chemical_values = (
        data[chemical_column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    total_unique_chemicals = (
        chemical_values
        .nunique()
    )

else:

    total_unique_chemicals = np.nan


total_records = len(data)


# ============================================================
# 11. GENERAL DESCRIPTIVE SUMMARY
# ============================================================

general_summary = pd.DataFrame({

    "Measure": [

        "Total records",

        "Unique chemicals",

        "Number of columns"
    ],

    "Value": [

        total_records,

        total_unique_chemicals,

        len(data.columns)
    ]
})


# ============================================================
# 12. ACTIVITY STANDARDIZATION
# ============================================================

def classify_activity(value):

    if pd.isna(value):

        return np.nan


    value_string = (
        str(value)
        .strip()
        .lower()
    )


    # --------------------------------------------------------
    # Active values
    # --------------------------------------------------------

    active_values = {

        "active",

        "a",

        "1",

        "true",

        "yes",

        "hit",

        "positive",

        "pos",

        "active hit",

        "active_hit",

        "activity"
    }


    # --------------------------------------------------------
    # Inactive values
    # --------------------------------------------------------

    inactive_values = {

        "inactive",

        "i",

        "0",

        "false",

        "no",

        "not active",

        "negative",

        "neg",

        "inactive hit",

        "inactive_hit"
    }


    if value_string in active_values:

        return "Active"


    if value_string in inactive_values:

        return "Inactive"


    return "Other"


# ============================================================
# 13. OVERALL ACTIVITY ANALYSIS
# ============================================================

if activity_column is not None:

    data["Activity_Class"] = (
        data[activity_column]
        .apply(
            classify_activity
        )
    )


    activity_counts = (
        data["Activity_Class"]
        .value_counts(
            dropna=False
        )
    )


    active_count = (
        activity_counts
        .get("Active", 0)
    )


    inactive_count = (
        activity_counts
        .get("Inactive", 0)
    )


    classified_count = (
        active_count
        +
        inactive_count
    )


    if classified_count > 0:

        active_percentage = (
            active_count
            /
            classified_count
            *
            100
        )


        inactive_percentage = (
            inactive_count
            /
            classified_count
            *
            100
        )

    else:

        active_percentage = np.nan

        inactive_percentage = np.nan


    print("\n" + "=" * 70)
    print("OVERALL ACTIVITY")
    print("=" * 70)


    print(
        "Active:",
        active_count,
        f"({active_percentage:.2f}%)"
    )


    print(
        "Inactive:",
        inactive_count,
        f"({inactive_percentage:.2f}%)"
    )


else:

    print("\nNo activity column detected.")


# ============================================================
# 14. PRIMARY ENDPOINT ANALYSIS
# ============================================================

if endpoint_column is not None:

    endpoint_values = (
        data[endpoint_column]
        .dropna()
        .astype(str)
        .str.strip()
    )


    endpoint_counts = (
        endpoint_values
        .value_counts()
    )


    print("\n" + "=" * 70)
    print("ENDPOINT COUNTS")
    print("=" * 70)


    print(
        endpoint_counts.to_string()
    )


    # --------------------------------------------------------
    # Endpoint activity summary
    # --------------------------------------------------------

    if activity_column is not None:

        endpoint_activity = (

            data

            .groupby(
                [
                    endpoint_column,
                    "Activity_Class"
                ]
            )

            .size()

            .reset_index(
                name="Count"
            )
        )


        # ----------------------------------------------------
        # Total observations per endpoint
        # ----------------------------------------------------

        endpoint_totals = (

            endpoint_activity

            .groupby(
                endpoint_column
            )["Count"]

            .sum()

            .reset_index(
                name="Total"
            )
        )


        # ----------------------------------------------------
        # Merge totals
        # ----------------------------------------------------

        endpoint_activity = (
            endpoint_activity
            .merge(
                endpoint_totals,
                on=endpoint_column
            )
        )


        # ----------------------------------------------------
        # Percentage
        # ----------------------------------------------------

        endpoint_activity[
            "Percentage"
        ] = (

            endpoint_activity[
                "Count"
            ]

            /

            endpoint_activity[
                "Total"
            ]

            *

            100
        )


        # ----------------------------------------------------
        # Rename endpoint column
        # ----------------------------------------------------

        endpoint_activity = (
            endpoint_activity
            .rename(
                columns={
                    endpoint_column:
                    "Endpoint"
                }
            )
        )


        # ----------------------------------------------------
        # Save endpoint activity
        # ----------------------------------------------------

        endpoint_activity_file = os.path.join(

            OUTPUT_FOLDER,

            "endpoint_activity_summary.csv"
        )


        endpoint_activity.to_csv(

            endpoint_activity_file,

            index=False
        )


        print(
            "\nEndpoint activity summary saved:"
        )

        print(
            endpoint_activity_file
        )


    else:

        endpoint_activity = None


else:

    endpoint_counts = None

    endpoint_activity = None


    print(
        "\nNo endpoint column detected."
    )


# ============================================================
# 15. NUMERICAL VARIABLE SUMMARY
# ============================================================

numerical_summary_rows = []


for column in numeric_columns:

    numeric_values = pd.to_numeric(

        data[column],

        errors="coerce"
    ).dropna()


    if len(numeric_values) == 0:

        continue


    numerical_summary_rows.append({

        "Variable":
            column,

        "N":
            len(numeric_values),

        "Missing":
            data[column].isna().sum(),

        "Missing_Percentage":
            data[column].isna().mean() * 100,

        "Mean":
            numeric_values.mean(),

        "Median":
            numeric_values.median(),

        "Standard_Deviation":
            numeric_values.std(),

        "Minimum":
            numeric_values.min(),

        "25th_Percentile":
            numeric_values.quantile(0.25),

        "75th_Percentile":
            numeric_values.quantile(0.75),

        "Maximum":
            numeric_values.max()
    })


numerical_summary = pd.DataFrame(
    numerical_summary_rows
)


# ============================================================
# 16. SAVE NUMERICAL SUMMARY
# ============================================================

numerical_summary_file = os.path.join(

    OUTPUT_FOLDER,

    "numerical_variable_summary.csv"
)


numerical_summary.to_csv(

    numerical_summary_file,

    index=False
)


print(
    "\nNumerical-variable summary saved:"
)

print(
    numerical_summary_file
)


# ============================================================
# 17. MISSING DATA SUMMARY
# ============================================================

missing_summary = pd.DataFrame({

    "Column":
        data.columns,

    "Missing_Count":
        data.isna().sum().values,

    "Missing_Percentage":
        (
            data.isna().mean()
            *
            100
        ).values
})


missing_summary = (
    missing_summary
    .sort_values(
        "Missing_Percentage",
        ascending=False
    )
)


missing_file = os.path.join(

    OUTPUT_FOLDER,

    "missing_data_summary.csv"
)


missing_summary.to_csv(

    missing_file,

    index=False
)


# ============================================================
# 18. SAVE GENERAL SUMMARY
# ============================================================

general_summary_file = os.path.join(

    OUTPUT_FOLDER,

    "descriptive_analysis_summary.csv"
)


general_summary.to_csv(

    general_summary_file,

    index=False
)


# ============================================================
# 19. CREATE TEXT REPORT
# ============================================================

report_file = os.path.join(

    OUTPUT_FOLDER,

    "descriptive_analysis.txt"
)


with open(
    report_file,
    "w"
) as report:

    report.write(
        "TOX21 / TOXCAST "
        "INITIAL DESCRIPTIVE ANALYSIS\n"
    )

    report.write(
        "=" * 70
        +
        "\n\n"
    )


    report.write(
        f"Input file:\n{file1}\n\n"
    )


    report.write(
        f"Total records: "
        f"{total_records}\n"
    )


    report.write(
        f"Unique chemicals: "
        f"{total_unique_chemicals}\n"
    )


    report.write(
        f"Number of columns: "
        f"{len(data.columns)}\n\n"
    )


    # --------------------------------------------------------
    # Activity
    # --------------------------------------------------------

    if activity_column is not None:

        report.write(
            "ACTIVITY SUMMARY\n"
        )

        report.write(
            "-" * 50
            +
            "\n"
        )


        report.write(
            f"Activity column: "
            f"{activity_column}\n"
        )


        report.write(
            f"Active count: "
            f"{active_count}\n"
        )


        report.write(
            f"Active percentage: "
            f"{active_percentage:.2f}%\n"
        )


        report.write(
            f"Inactive count: "
            f"{inactive_count}\n"
        )


        report.write(
            f"Inactive percentage: "
            f"{inactive_percentage:.2f}%\n\n"
        )


    # --------------------------------------------------------
    # Endpoint
    # --------------------------------------------------------

    if endpoint_counts is not None:

        report.write(
            "ENDPOINT COUNTS\n"
        )

        report.write(
            "-" * 50
            +
            "\n"
        )


        report.write(
            endpoint_counts
            .to_string()
        )


        report.write(
            "\n\n"
        )


    # --------------------------------------------------------
    # Numerical variables
    # --------------------------------------------------------

    report.write(
        "NUMERICAL VARIABLE SUMMARY\n"
    )

    report.write(
        "-" * 50
        +
        "\n"
    )


    if not numerical_summary.empty:

        report.write(
            numerical_summary
            .to_string(
                index=False
            )
        )

    else:

        report.write(
            "No numerical variables detected."
        )


    report.write(
        "\n\n"
    )


    # --------------------------------------------------------
    # Missing data
    # --------------------------------------------------------

    report.write(
        "MISSING DATA SUMMARY\n"
    )

    report.write(
        "-" * 50
        +
        "\n"
    )


    report.write(
        missing_summary
        .to_string(
            index=False
        )
    )


# ============================================================
# 20. FINAL PRINTED SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("INITIAL DESCRIPTIVE ANALYSIS COMPLETE")
print("=" * 70)


print(
    "\nTotal records:",
    total_records
)


print(
    "Unique chemicals:",
    total_unique_chemicals
)


if activity_column is not None:

    print(
        "\nActivity column:",
        activity_column
    )


    print(
        "Active:",
        active_count,
        f"({active_percentage:.2f}%)"
    )


    print(
        "Inactive:",
        inactive_count,
        f"({inactive_percentage:.2f}%)"
    )


if endpoint_column is not None:

    print(
        "\nPrimary endpoint column:",
        endpoint_column
    )


print(
    "\nResults saved to:"
)

print(
    OUTPUT_FOLDER
)


print(
    "\nGenerated files:"
)


print(
    "1. descriptive_analysis_summary.csv"
)


print(
    "2. endpoint_activity_summary.csv"
)


print(
    "3. numerical_variable_summary.csv"
)


print(
    "4. missing_data_summary.csv"
)


print(
    "5. descriptive_analysis.txt"
)


print("\nDone!")


# ============================================================
# 21. OPEN RESULTS FOLDER AUTOMATICALLY
# ============================================================

import subprocess

try:

    subprocess.run(
        [
            "open",
            OUTPUT_FOLDER
        ],
        check=False
    )

except Exception as error:

    print(
        "\nCould not automatically open "
        "the results folder:"
    )

    print(error)
