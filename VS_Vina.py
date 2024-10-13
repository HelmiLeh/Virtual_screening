#!/usr/bin/env python3

import os
import subprocess
import argparse
import csv

# Automatically create 'ligand.txt' by listing all .pdbqt files in the 'ligand' folder
ligand_folder = './ligand'
ligand_file = 'ligand.txt'

# List all .pdbqt files in the 'ligand' folder
ligand_list = [f for f in os.listdir(ligand_folder) if f.endswith('.pdbqt')]

# Write the list of ligands to 'ligand.txt'
with open(ligand_file, 'w') as lf:
    for ligand in ligand_list:
        lf.write(f"{ligand}\n")

# Define the path to the Vina executable (in the current working directory)
vina_path = './vina'  # ./ indicates the current directory

# Create a folder for log files
log_folder = 'logfile'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Open CSV file to record values from log files (keep it open during the loop)
with open('logfile_summary.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Ligand', 'Binding free energy kcal/mol'])

    # Read the ligands from 'ligand.txt' that was just created
    with open(ligand_file, 'r') as fh:
        arr_file = fh.readlines()

    # Iterate over each ligand in the list
    for ligand in arr_file:
        ligand = ligand.strip()  # Remove any trailing newline characters

        # Skip if the line is empty
        if not ligand:
            continue

        # Print the ligand file name
        print(f"Processing ligand: {ligand}")

        # Extract the base name of the ligand (without path or extension)
        base_name = os.path.splitext(os.path.basename(ligand))[0]  # Removes the .pdbqt extension

        # Check if base_name is defined
        if not base_name:
            print(f"Skipping invalid ligand name: {ligand}")
            continue

        # Construct the command to run AutoDock Vina
        ligand_path = os.path.join(ligand_folder, ligand)
        log_file = os.path.join(log_folder, f'{base_name}_log.log')
        command = [vina_path, '--config', 'config.txt', '--ligand', ligand_path, '--log', log_file]

        # Execute the command
        try:
            subprocess.run(command, check=True)
            print(f"Successfully processed: {ligand}")

            # Move the log file into the 'logfile' folder and extract row 29, col 13-20
            if os.path.isfile(log_file):
                with open(log_file, 'r') as log_fh:
                    lines = log_fh.readlines()
                    if len(lines) >= 29:
                        row_29_value = lines[28][12:20].strip()  # Extract columns 13-20
                        print(f"Ligand {base_name} - Value from row 29 (col 13-20): {row_29_value}")
                        # Write ligand name (without .pdbqt) and value to the CSV
                        csvwriter.writerow([base_name, row_29_value])
                    else:
                        print(f"Log file for {ligand} is too short to extract row 29.")
                        csvwriter.writerow([base_name, 'N/A'])
        except subprocess.CalledProcessError:
            print(f"Failed to execute: {' '.join(command)}")

