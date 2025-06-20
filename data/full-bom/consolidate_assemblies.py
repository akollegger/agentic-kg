#!/usr/bin/env python3
import os
import csv
import glob

# Create the output file with headers
output_file = "/Users/akollegger/Developer/genai/dlai/agentic-kg/data/bom/assemblies.csv"
with open(output_file, 'w', newline='') as f_out:
    writer = csv.writer(f_out)
    writer.writerow(['assembly_name', 'component_name', 'quantity', 'part_number', 'parent_part_number'])

# Get all assembly CSV files
assembly_dir = "/Users/akollegger/Developer/genai/dlai/agentic-kg/data/bom/assembly"
csv_files = glob.glob(os.path.join(assembly_dir, "*.csv"))

# Process each file
for file_path in csv_files:
    # Extract assembly name from the file path
    file_name = os.path.basename(file_path)
    assembly_name = os.path.splitext(file_name)[0]
    
    # Read the file and append to the consolidated file
    with open(file_path, 'r', newline='') as f_in, open(output_file, 'a', newline='') as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        
        # Skip the header row
        next(reader, None)
        
        # Write each row with the assembly name added
        for row in reader:
            if row:  # Skip empty rows
                writer.writerow([assembly_name] + row)

print(f"Consolidated {len(csv_files)} assembly files into {output_file}")
