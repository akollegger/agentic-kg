#!/usr/bin/env python3
import csv
import os
import re
import glob
import unicodedata

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

def normalize_name(name):
    """Normalize a name by removing accents and converting to lowercase"""
    # Remove accents and convert to ASCII
    normalized = unicodedata.normalize('NFKD', name)
    normalized = ''.join([c for c in normalized if not unicodedata.combining(c)])
    # Convert to lowercase and replace spaces with underscores
    normalized = normalized.lower().replace(' ', '_')
    # Remove any non-alphanumeric characters
    normalized = re.sub(r'[^\w]', '', normalized)
    return normalized

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

# Create a mapping of normalized product names to part numbers
product_part_map = {}
for product in products:
    normalized_name = normalize_name(product['product_name'])
    product_part_map[normalized_name] = product['part_number']

# Process assembly files
assembly_files = glob.glob(f"{assembly_dir}/*.csv")
assembly_component_map = {}  # Map component names to their part numbers

for assembly_file in assembly_files:
    # Extract product name from filename
    filename = os.path.basename(assembly_file)
    file_product_name = filename.replace('_assembly.csv', '')
    
    # Find matching product to get its part number
    product_part_number = None
    for norm_name, part_num in product_part_map.items():
        if norm_name in normalize_name(file_product_name):
            product_part_number = part_num
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
            component_part_number = get_part_number(f"{file_product_name}_{component_name}", 'A')
            row['part_number'] = component_part_number
            row['parent_part_number'] = product_part_number
            components.append(row)
            
            # Store the component part number for sub-assembly reference
            assembly_component_map[normalize_name(component_name)] = component_part_number
    
    # Write updated assembly file
    with open(assembly_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(components)
    
    print(f"Updated {assembly_file} with part numbers")

# Process sub-assembly files
sub_assembly_files = glob.glob(f"{sub_assembly_dir}/*.csv")
for sub_file in sub_assembly_files:
    # Skip the bed_slats directory
    if 'bed_slats' in sub_file:
        continue
        
    # Extract component name from filename
    filename = os.path.basename(sub_file)
    component_name = filename.replace('_subassembly.csv', '')
    normalized_component = normalize_name(component_name)
    
    # Find parent part number
    parent_part_number = assembly_component_map.get(normalized_component, "UNKNOWN")
    if parent_part_number == "UNKNOWN":
        print(f"Warning: Could not find parent assembly for {filename}")
    
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
if slat_files:
    # Find parent part number for slats
    parent_part_number = assembly_component_map.get('slats', "UNKNOWN")
    if parent_part_number == "UNKNOWN":
        print(f"Warning: Could not find parent assembly for bed slats")
    
    for slat_file in slat_files:
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
    writer.writerow(['part_number', 'part_name', 'parent_part_number'])
    
    # Add products (no parent)
    for product in products:
        writer.writerow([product['part_number'], product['product_name'], ''])
    
    # Add all other parts with their parent references
    for name, number in part_numbers.items():
        if any(product['part_number'] == number for product in products):
            continue  # Skip products as we already added them
            
        parent = "UNKNOWN"
        # Find parent by checking if name contains component names
        for component_name, component_number in assembly_component_map.items():
            if component_name in normalize_name(name):
                parent = component_number
                break
        
        writer.writerow([number, name, parent])

print("Created part_numbers_reference.csv with all part numbers")
print("All files updated with part numbers and parent references")
