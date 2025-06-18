#!/usr/bin/env python3
import os
import csv
import glob

# Create the output file with headers
output_file = "/Users/akollegger/Developer/genai/dlai/agentic-kg/data/bom/components.csv"
with open(output_file, 'w', newline='') as f_out:
    writer = csv.writer(f_out)
    writer.writerow(['sub_assembly_name', 'part_name', 'quantity', 'part_number', 'parent_part_number'])

# Get all component CSV files
component_dir = "/Users/akollegger/Developer/genai/dlai/agentic-kg/data/bom/sub_assembly"
csv_files = []
for root, dirs, files in os.walk(component_dir):
    for file in files:
        if file.endswith('.csv'):
            csv_files.append(os.path.join(root, file))

# Process each file
for file_path in csv_files:
    # Extract sub-assembly name from the file path
    file_name = os.path.basename(file_path)
    sub_assembly_name = os.path.splitext(file_name)[0]
    
    # Special handling for bed slats
    if 'bed_slats' in file_path:
        sub_assembly_name = f"bed_{os.path.splitext(os.path.basename(file_path))[0]}"
    
    # Read the file and append to the consolidated file
    with open(file_path, 'r', newline='') as f_in, open(output_file, 'a', newline='') as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        
        # Skip the header row
        next(reader, None)
        
        # Write each row with the sub-assembly name added
        for row in reader:
            if row:  # Skip empty rows
                writer.writerow([sub_assembly_name] + row)

print(f"Consolidated {len(csv_files)} sub-assembly files into {output_file}")
