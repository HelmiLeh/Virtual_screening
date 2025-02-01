import os
import subprocess
import csv
import time

# Define folders and files
ligand_folder = './ligand'
ligand_file = 'ligand.txt'
out_folder = './out'
log_folder = './logfile'
completed_ligands_file = 'completed_ligands.txt'
unsorted_csv_file = 'logfile_summary_unsorted.csv'
sorted_csv_file = 'logfile_summary.csv'
vina_path = './vina'
config_file = 'config.txt'

# Ensure necessary directories exist
os.makedirs(log_folder, exist_ok=True)
os.makedirs(out_folder, exist_ok=True)

# Load completed ligands
completed_ligands = set()
if os.path.exists(completed_ligands_file):
    with open(completed_ligands_file, 'r') as f:
        completed_ligands = set(f.read().splitlines())

# Function to run docking for a given ligand
def run_docking(ligand):
    base_name = os.path.splitext(os.path.basename(ligand))[0]
    ligand_path = os.path.join(ligand_folder, ligand)
    log_file = os.path.join(log_folder, f'{base_name}_log.log')
    out_file = os.path.join(out_folder, f'{base_name}_out.pdbqt')
    
    command = [
        vina_path, '--config', config_file, '--ligand', ligand_path,
        '--log', log_file, '--out', out_file
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Successfully processed: {ligand}")
        
        # Extract binding affinity from log file
        binding_affinity = 'N/A'
        if os.path.isfile(log_file):
            with open(log_file, 'r') as log_fh:
                for line in log_fh:
                    if line.strip().startswith('1'):
                        parts = line.split()
                        if len(parts) >= 2:
                            binding_affinity = parts[1]
                            break
        
        # Write result to CSV
        with open(unsorted_csv_file, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([base_name, float(binding_affinity) if binding_affinity != 'N/A' else 'N/A'])
        
        # Mark as completed
        with open(completed_ligands_file, 'a') as f:
            f.write(ligand + '\n')
        
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to process: {ligand}")
        return False

# Initialize CSV file if it doesn't exist
if not os.path.exists(unsorted_csv_file):
    with open(unsorted_csv_file, 'w', newline='') as csvfile:
        csv.writer(csvfile).writerow(['Ligand', 'Binding Affinity (kcal/mol)'])

print("Monitoring for new ligands. Press Ctrl+C to stop.")
no_new_ligand_counter = 0
while True:
    try:
        # Get list of .pdbqt files
        ligand_list = [f for f in os.listdir(ligand_folder) if f.endswith('.pdbqt')]
        new_ligands = [ligand for ligand in ligand_list if ligand not in completed_ligands]
        
        if new_ligands:
            no_new_ligand_counter = 0
            for ligand in new_ligands:
                print(f"Processing ligand: {ligand}")
                success = run_docking(ligand)
                if success:
                    completed_ligands.add(ligand)
        else:
            no_new_ligand_counter += 1
            print("No new ligands found.")
        
        # Sort the results periodically
        with open(unsorted_csv_file, 'r') as infile, open(sorted_csv_file, 'w', newline='') as outfile:
            csvreader = csv.reader(infile)
            csvwriter = csv.writer(outfile)
            header = next(csvreader)
            data = [row for row in csvreader if row[1] != 'N/A']
            data = sorted(data, key=lambda x: float(x[1]))
            csvwriter.writerow(header)
            csvwriter.writerows(data)
        
        if no_new_ligand_counter >= 3:
            print("No new ligands detected for 3 seconds. Exiting...")
            break
        
        time.sleep(1)  # Check every second
    except KeyboardInterrupt:
        print("Script stopped by user.")
        break
    except Exception as e:
        print(f"Error encountered: {e}")

