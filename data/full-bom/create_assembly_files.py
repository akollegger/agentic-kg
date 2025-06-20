#!/usr/bin/env python3
import csv
import os
import re

# Define components for each furniture type
furniture_components = {
    'Chair': [
        ('Seat', 1),
        ('Back Rest', 1),
        ('Legs', 4),
        ('Screws', 12),
        ('Allen Key', 1)
    ],
    'Table': [
        ('Table Top', 1),
        ('Legs', 4),
        ('Support Beam', 2),
        ('Screws', 16),
        ('Allen Key', 1)
    ],
    'Desk': [
        ('Desktop', 1),
        ('Legs', 4),
        ('Drawer Unit', 1),
        ('Screws', 20),
        ('Cable Management', 1),
        ('Allen Key', 1)
    ],
    'Sofa': [
        ('Seat Cushion', 3),
        ('Back Cushion', 3),
        ('Frame', 1),
        ('Armrest', 2),
        ('Legs', 4),
        ('Cover', 1),
        ('Screws', 24)
    ],
    'Bookshelf': [
        ('Side Panels', 2),
        ('Shelves', 5),
        ('Back Panel', 1),
        ('Screws', 30),
        ('Shelf Pins', 20),
        ('Allen Key', 1)
    ],
    'Lamp': [
        ('Base', 1),
        ('Stem', 1),
        ('Shade', 1),
        ('Light Bulb Socket', 1),
        ('Screws', 6),
        ('Power Cord', 1)
    ],
    'Bed': [
        ('Headboard', 1),
        ('Footboard', 1),
        ('Side Rails', 2),
        ('Slats', 14),
        ('Center Support', 1),
        ('Screws', 24),
        ('Allen Key', 1)
    ],
    'Dresser': [
        ('Top Panel', 1),
        ('Side Panels', 2),
        ('Bottom Panel', 1),
        ('Back Panel', 1),
        ('Drawers', 4),
        ('Drawer Handles', 4),
        ('Screws', 36),
        ('Allen Key', 1)
    ],
    'Coffee Table': [
        ('Table Top', 1),
        ('Legs', 4),
        ('Shelf', 1),
        ('Screws', 16),
        ('Allen Key', 1)
    ],
    'Nightstand': [
        ('Top Panel', 1),
        ('Side Panels', 2),
        ('Bottom Panel', 1),
        ('Back Panel', 1),
        ('Drawer', 1),
        ('Drawer Handle', 1),
        ('Legs', 4),
        ('Screws', 20),
        ('Allen Key', 1)
    ]
}

# Read products.csv
products = []
with open('data/bom/products.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        products.append(row)

# Create assembly files directory if it doesn't exist
assembly_dir = 'data/bom/assembly'
os.makedirs(assembly_dir, exist_ok=True)

# Create assembly files for each product
for product in products:
    # Extract furniture type from product name
    product_name = product['product_name']
    furniture_type = None
    
    for ftype in furniture_components.keys():
        if ftype in product_name:
            furniture_type = ftype
            break
    
    if not furniture_type:
        print(f"Could not determine furniture type for {product_name}")
        continue
    
    # Create sanitized filename
    filename = re.sub(r'[^\w\s]', '', product_name.lower()).replace(' ', '_') + '_assembly.csv'
    filepath = os.path.join(assembly_dir, filename)
    
    # Write assembly components to file
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['component_name', 'quantity'])
        
        for component, quantity in furniture_components[furniture_type]:
            writer.writerow([component, quantity])
    
    print(f"Created {filepath}")

print("All assembly files created successfully")
