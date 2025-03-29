"""
This module compines all the .dat files into one csv table and does all the necessary ajustments:
- some file contain systematic uncertainty. This column is unifies across all the files
- the fifth column of any E02-019 (Fomin:2010ei) data was in x=Q^2/2mν instead of energy loss, it was recalculated
"""

import os
import pandas as pd


def is_valid_data_row(row) -> bool:
    """
    Checks if the row follows the expected data format:
    - 7 or 8 numeric columns
    - The last value should be a string (e.g., filename or other strings)
    """
    # Check if row length is 8 or 9
    if len(row) not in [8, 9]:
        return False

    numeric_values = 0
    # Check for numeric values in all but the last column
    for value in row[:-1]:  # Check all but the last value
        try:
            float(value)  # Try to convert to float
            numeric_values += 1
        except ValueError:
            return False  # If it's not a number, return False

    # The last column should be a string (non-numeric)
    try:
        float(row[-1])  # If the last value is numeric, it's not valid
        return False
    except ValueError:
        pass  # It's fine if the last value is non-numeric (string)

    # Row is valid if there are 7 or 8 numeric values and the last one is a string
    return numeric_values in [7, 8]


def merge_special_files(file1_data, file2_data) -> list:
    """
    Merges two datasets from special treatment files and returns the merged data.
    """
    df1 = pd.DataFrame(file1_data)
    df2 = pd.DataFrame(file2_data)

    # Remove empty columns
    df1 = df1.loc[:, (df1 != "").any(axis=0)]
    df2 = df2.loc[:, (df2 != "").any(axis=0)]

    # Merge the dataframes on the common columns
    merge_columns = df1.columns[[0, 1, 2, 3, 4, 5, 7]]
    merged_data = pd.merge(
        df1, df2, on=merge_columns.tolist(), suffixes=("_df1", "_df2")
    )

    # Reorganize columns to preferred order
    merged_data = merged_data.iloc[
        :,
        list(range(len(merged_data.columns) - 2))
        + [len(merged_data.columns) - 1, len(merged_data.columns) - 2],
    ]
    return merged_data.values.tolist()


def process_dat_file(file_path) -> list:
    """
    Processes the content of a .dat file and returns the data in a list format.
    The first line might contain column names if the file has headers.
    """
    data = []
    with open(file_path, "r") as file:
        lines = file.readlines()

        # Process the rest of the lines
        for line in lines:
            row = line.strip().split()  # Split by spaces or tabs
            if row and is_valid_data_row(row):  # Only add non-empty rows
                if len(row) == 8:
                    row.insert(
                        -1, ""
                    )  # Insert empty string before the last column if there is no sys unsrt
                data.append(row)

    return data


def process_files_in_directory(directory_path, output_csv_path) -> None:
    """
    Iterates over all .dat files in the given directory, processes them, and writes all data to a CSV.
    """
    all_data = []
    special_tratment_files = [
        "E12-14-012_statUncertainties.dat",
        "E12-14-012_totUncertainties.dat",
    ]
    special_treatment_data = []
    # Use os.walk to iterate through all subdirectories and files
    for dirpath, _, filenames in os.walk(directory_path):

        for filename in filenames:
            if filename.endswith(".dat"):  # Process only .dat files
                if (
                    filename in special_tratment_files
                ):  # If it's one of the special files
                    print(f"Processing special file: {filename}")
                    file_path = os.path.join(dirpath, filename)
                    file_data = process_dat_file(file_path)
                    special_treatment_data.append((filename, file_data))
                else:
                    file_path = os.path.join(dirpath, filename)
                    print(f"Processing {filename}...")
                    file_data = process_dat_file(file_path)

                    # add the initial filename as the last row for debugging reasons
                    for row in file_data:
                        row.append(filename)  # Append the filename as the last column

                    all_data.extend(file_data)  # Add data to the main list

    # 2 files need to be merged before being added to the final dataset,
    # they are the same but contain different sets of uncertainties
    if len(special_treatment_data) == 2:
        file1_data = special_treatment_data[0][1]
        file2_data = special_treatment_data[1][1]
        merged_data = merge_special_files(file1_data, file2_data)
        all_data.extend(merged_data)

    # Write collected data to CSV
    column_names = [
        "Z",
        "A",
        "E (GeV)",
        "Theta (degrees)",
        "energy loss (GeV)",
        "sigma (nb/sr/GeV)",
        "error (random)",
        "error (total)",
        "citation",
        "initial file name",
    ]

    # Convert all_data into a DataFrame for easy column renaming
    all_data_df = pd.DataFrame(all_data)

    # Set the new column names for all_data
    all_data_df.columns = column_names

    # Write collected data to CSV
    all_data_df.to_csv(output_csv_path, index=False)
    print(f"Data has been written to {output_csv_path}")


process_files_in_directory("scrapped_data", "merged_table.csv")
