#!/usr/bin/env python3
import csv
import os
import re
import glob

# Define base directories
products_file = 'data/bom/products.csv'
assembly_dir = 'data/bom/assembly'
sub_assembly_dir = 'data/bom/sub_assembly'

# Create a dictionary to store all part numbers
part_numbers = {}
next_part_id = 1000

def get_part_number(name, prefix):
    """Generate a unique part number for a component"""
    global next_part_id
    if name not in part_numbers:
        part_numbers[name] = f"{prefix}-{next_part_id}"
        next_part_id += 1
    return part_numbers[name]

# First, assign part numbers to products
products = []
with open(products_file, 'r') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames + ['part_number']
    for row in reader:
        product_name = row['product_name']
        row['part_number'] = get_part_number(product_name, 'P')
        products.append(row)

# Write updated products file
with open(products_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(products)

print(f"Updated {products_file} with part numbers")

# Process assembly files
assembly_files = glob.glob(f"{assembly_dir}/*.csv")
for assembly_file in assembly_files:
    # Extract product name from filename
    filename = os.path.basename(assembly_file)
    product_name = filename.replace('_assembly.csv', '').replace('_', ' ')
    
    # Find matching product to get its part number
    product_part_number = None
    for product in products:
        sanitized_name = re.sub(r'[^\w\s]', '', product['product_name'].lower()).replace(' ', '_')
        if sanitized_name == product_name:
            product_part_number = product['part_number']
            break
    
    if not product_part_number:
        print(f"Warning: Could not find product for {filename}")
        continue
    
    # Read assembly components
    components = []
    with open(assembly_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ['part_number', 'parent_part_number']
        for row in reader:
            component_name = row['component_name']
            row['part_number'] = get_part_number(f"{product_name}_{component_name}", 'A')
            row['parent_part_number'] = product_part_number
            components.append(row)
    
    # Write updated assembly file
    with open(assembly_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(components)
    
    print(f"Updated {assembly_file} with part numbers")

# Process sub-assembly files
sub_assembly_files = glob.glob(f"{sub_assembly_dir}/*.csv")
for sub_file in sub_assembly_files:
    # Extract component name from filename
    filename = os.path.basename(sub_file)
    component_name = filename.replace('_subassembly.csv', '').replace('_', ' ')
    
    # Find all assembly components that match this sub-assembly
    parent_part_numbers = []
    for assembly_file in assembly_files:
        with open(assembly_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'component_name' in row and row['component_name'].lower() == component_name.lower():
                    parent_part_numbers.append(row['part_number'])
    
    if not parent_part_numbers:
        print(f"Warning: Could not find parent assembly for {filename}")
        # Still assign part numbers even if no parent is found
        parent_part_number = "UNKNOWN"
    else:
        # Use the first parent found (there could be multiple)
        parent_part_number = parent_part_numbers[0]
    
    # Read sub-assembly parts
    parts = []
    with open(sub_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ['part_number', 'parent_part_number']
        for row in reader:
            part_name = row['part_name']
            row['part_number'] = get_part_number(f"{component_name}_{part_name}", 'S')
            row['parent_part_number'] = parent_part_number
            parts.append(row)
    
    # Write updated sub-assembly file
    with open(sub_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parts)
    
    print(f"Updated {sub_file} with part numbers")

# Process bed slats (special case)
slat_files = glob.glob(f"{sub_assembly_dir}/bed_slats/*.csv")
for slat_file in slat_files:
    # Find parent part number for slats
    parent_part_number = None
    for key, value in part_numbers.items():
        if key == "Slats":
            parent_part_number = value
            break
    
    if not parent_part_number:
        print(f"Warning: Could not find parent assembly for bed slats")
        parent_part_number = "UNKNOWN"
    
    # Read slat parts
    parts = []
    with open(slat_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ['part_number', 'parent_part_number']
        for row in reader:
            part_name = row['part_name']
            # Use slat number in the part number
            slat_num = os.path.basename(slat_file).replace('slat_', '').replace('.csv', '')
            row['part_number'] = get_part_number(f"Slat_{slat_num}_{part_name}", 'S')
            row['parent_part_number'] = parent_part_number
            parts.append(row)
    
    # Write updated slat file
    with open(slat_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parts)
    
    print(f"Updated {slat_file} with part numbers")

# Create a reference file showing all part numbers
with open('data/bom/part_numbers_reference.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['part_number', 'part_name'])
    for name, number in part_numbers.items():
        writer.writerow([number, name])

print("Created part_numbers_reference.csv with all part numbers")
print("All files updated with part numbers and parent references")
