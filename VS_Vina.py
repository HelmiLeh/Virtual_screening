#!/usr/bin/env python3

import os
import subprocess
import csv

# Automatically create 'ligand.txt' by listing all .pdbqt files in the 'ligand' folder
ligand_folder = './ligand'
ligand_file = 'ligand.txt'
out_folder = './out'

# List all .pdbqt files in the 'ligand' folder
ligand_list = [f for f in os.listdir(ligand_folder) if f.endswith('.pdbqt')]

# Write the list of ligands to 'ligand.txt'
with open(ligand_file, 'w') as lf:
    for ligand in ligand_list:
        lf.write(f"{ligand}\n")

# Define the path to the Vina executable (in the current working directory)
vina_path = './vina'

# Create a folder for log files
log_folder = 'logfile'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Create a folder for output files if it doesn't exist
if not os.path.exists(out_folder):
    os.makedirs(out_folder)

# File to store unsorted binding affinities
unsorted_csv_file = 'logfile_summary_unsorted.csv'
sorted_csv_file = 'logfile_summary.csv'

with open(unsorted_csv_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Ligand', 'Binding Affinity (kcal/mol)'])

    # Read the ligands from 'ligand.txt'
    with open(ligand_file, 'r') as fh:
        arr_file = fh.readlines()

    # Iterate over each ligand in the list
    for ligand in arr_file:
        ligand = ligand.strip()

        # Skip if the line is empty
        if not ligand:
            continue

        print(f"Processing ligand: {ligand}")

        base_name = os.path.splitext(os.path.basename(ligand))[0]

        # Skip invalid ligand names
        if not base_name:
            print(f"Skipping invalid ligand name: {ligand}")
            continue

        # Construct the command to run AutoDock Vina
        ligand_path = os.path.join(ligand_folder, ligand)
        log_file = os.path.join(log_folder, f'{base_name}_log.log')
        command = [
            vina_path, '--config', 'config.txt', '--ligand', ligand_path,
            '--log', log_file, '--out', os.path.join(out_folder, f'{base_name}_out.pdbqt')
        ]

        # Execute the command
        try:
            subprocess.run(command, check=True)
            print(f"Successfully processed: {ligand}")

            # Parse the Vina log file to extract mode 1 binding affinity
            if os.path.isfile(log_file):
                with open(log_file, 'r') as log_fh:
                    for line in log_fh:
                        if line.strip().startswith('1'):  # Look for mode 1
                            parts = line.split()
                            if len(parts) >= 2:
                                binding_affinity = parts[1]  # Affinity is in the second column
                                print(f"Ligand {base_name} - Binding Affinity (mode 1): {binding_affinity}")
                                # Write ligand name and binding affinity to the unsorted CSV
                                csvwriter.writerow([base_name, float(binding_affinity)])
                                break
                    else:
                        print(f"No binding affinity found for {ligand}")
                        csvwriter.writerow([base_name, 'N/A'])
        except subprocess.CalledProcessError:
            print(f"Failed to execute: {' '.join(command)}")

# Sort the CSV file based on binding affinity
try:
    with open(unsorted_csv_file, 'r') as infile, open(sorted_csv_file, 'w', newline='') as outfile:
        csvreader = csv.reader(infile)
        csvwriter = csv.writer(outfile)

        # Read the header and data rows
        header = next(csvreader)
        data = [row for row in csvreader if row[1] != 'N/A']  # Exclude rows with 'N/A'
        data = sorted(data, key=lambda x: float(x[1]))  # Sort by binding affinity (column 1)

        # Write the sorted data back to the new file
        csvwriter.writerow(header)
        csvwriter.writerows(data)

    print(f"Results have been sorted and saved to '{sorted_csv_file}'")
except Exception as e:
    print(f"Failed to sort results: {e}")
