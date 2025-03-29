"""
This module compines all the .dat files into one csv table and does all the necessary ajustments:
- some file contain systematic uncertainty. This column is unifies across all the files
- the fifth column of any E02-019 (Fomin:2010ei) data was in x=Q^2/2mν instead of energy loss, it was recalculated
"""

import os
import csv
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


def write_to_csv(output_csv_path, all_data) -> None:
    """
    Writes the collected data to a CSV file.
    """
    with open(output_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for row in all_data:
            writer.writerow(row)


def process_files_in_directory(directory_path, output_csv_path):
    """
    Iterates over all .dat files in the given directory and subdirectories, processes them, and writes all data to a CSV.
    Adds the filename as an additional column to each row. Special handling for two specific files.
    """
    all_data = []  # List to store all the DataFrames

    special_files = [
        "E12-14-012_statUncertainties.dat",
        "E12-14-012_totUncertainties.dat",
    ]  # Replace with actual filenames of the two special files
    processed_special_files = set()  # Set to track processed special files
    special_data = []  # Will store data from special files for later merging

    # Use os.walk to iterate through all subdirectories and files
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            if filename.endswith(".dat"):  # Process only .dat files

                file_path = os.path.join(dirpath, filename)

                # Read the file into a DataFrame
                df = pd.read_csv(file_path, delim_whitespace=True, header=None)

                # Add the filename as the last column
                df["filename"] = filename

                # If the file is one of the special files and hasn't been processed yet
                if (
                    filename in special_files
                    and filename not in processed_special_files
                ):
                    print(f"Processing special file: {filename}")
                    special_data.append((filename, df))  # Store the special data
                    processed_special_files.add(filename)
                else:
                    # Otherwise, add it to the all_data list
                    print(f"Processing regular file: {filename}")
                    all_data.append(df)

    # After processing all files, merge the special files if both are processed
    if len(processed_special_files) == 2:  # If we have both special files
        # Extract data for merging (i.e., columns from special files)
        file1_data = special_data[0][1]
        file2_data = special_data[1][1]

        # Merge the second-to-last columns from both files (file1 and file2)
        min_rows = min(len(file1_data), len(file2_data))  # To avoid index mismatch
        file1_data.insert(
            len(file1_data.columns) - 1,
            "second_last_column_file2",
            file2_data.iloc[:min_rows, -2].values,
        )

        # Append the merged data to the final result
        all_data.append(file1_data)  # Append the merged data for special files

    # Concatenate all DataFrames into one
    final_data = pd.concat(all_data, ignore_index=True)

    # Write the final data to a CSV file
    final_data.to_csv(output_csv_path, index=False)


process_files_in_directory("scrapped_data", "merged_table.csv")
