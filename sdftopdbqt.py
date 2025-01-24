import os
import subprocess

def convert_sdf_to_pdbqt_folder(input_folder):
    """
    Converts all SDF files in a folder to PDBQT format using Open Babel.
    The original filenames are preserved, and output files are saved in an 'outpdbqt' folder
    located in the parent directory of the input folder.
    """
    # Check if the input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' does not exist.")
        return
    
    # Define the output folder in the parent directory of the input folder
    parent_dir = os.path.dirname(input_folder)
    output_folder = os.path.join(parent_dir, "ligand")
    os.makedirs(output_folder, exist_ok=True)
    
    # List all SDF files in the input folder
    sdf_files = [f for f in os.listdir(input_folder) if f.endswith(".sdf")]
    
    if not sdf_files:
        print("No SDF files found in the folder.")
        return
    
    print(f"Found {len(sdf_files)} SDF file(s) in the folder.")
    
    for sdf_file in sdf_files:
        sdf_path = os.path.join(input_folder, sdf_file)
        base_name = os.path.splitext(sdf_file)[0]
        pdbqt_file = os.path.join(output_folder, f"{base_name}.pdbqt")
        
        # Run the Open Babel conversion command
        try:
            subprocess.run(
                ["obabel", sdf_path, "-O", pdbqt_file],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"Converted: '{sdf_file}' -> '{pdbqt_file}'")
        except subprocess.CalledProcessError as e:
            print(f"Error converting '{sdf_file}': {e.stderr.decode()}")

# Example usage
input_folder = "out3D"  # Replace with the path to your folder containing SDF files
convert_sdf_to_pdbqt_folder(input_folder)

