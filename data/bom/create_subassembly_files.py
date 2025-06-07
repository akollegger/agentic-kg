#!/usr/bin/env python3
import csv
import os
import re

# Define sub-assemblies for complex components
sub_assemblies = {
    # Desk components
    'Drawer Unit': [
        ('Drawer Front', 1),
        ('Drawer Bottom', 1),
        ('Drawer Sides', 2),
        ('Drawer Back', 1),
        ('Drawer Rails', 2),
        ('Drawer Handle', 1),
        ('Screws', 8)
    ],
    'Cable Management': [
        ('Cable Tray', 1),
        ('Cable Clips', 4),
        ('Zip Ties', 5),
        ('Adhesive Pads', 2)
    ],
    
    # Sofa components
    'Frame': [
        ('Base Frame', 1),
        ('Back Frame', 1),
        ('Side Frames', 2),
        ('Support Slats', 12),
        ('Corner Brackets', 4),
        ('Screws', 32)
    ],
    'Seat Cushion': [
        ('Foam Insert', 1),
        ('Cushion Cover', 1),
        ('Zipper', 1),
        ('Batting', 1)
    ],
    'Back Cushion': [
        ('Foam Insert', 1),
        ('Cushion Cover', 1),
        ('Zipper', 1),
        ('Batting', 1)
    ],
    
    # Bed components
    'Headboard': [
        ('Headboard Panel', 1),
        ('Headboard Frame', 1),
        ('Decorative Trim', 1),
        ('Mounting Brackets', 2),
        ('Screws', 12)
    ],
    'Slats': [
        ('Wooden Slat', 1),
        ('Fabric Sleeve', 1)
    ],
    
    # Bookshelf components
    'Side Panels': [
        ('Wood Panel', 1),
        ('Edge Banding', 1),
        ('Shelf Support Holes', 10),
        ('Mounting Brackets', 2)
    ],
    
    # Table components
    'Table Top': [
        ('Wood Panels', 3),
        ('Edge Banding', 1),
        ('Reinforcement Strips', 2),
        ('Wood Glue', 1)
    ],
    
    # Dresser components
    'Drawers': [
        ('Drawer Front', 1),
        ('Drawer Bottom', 1),
        ('Drawer Sides', 2),
        ('Drawer Back', 1),
        ('Drawer Rails', 2),
        ('Screws', 8)
    ],
    
    # Chair components
    'Back Rest': [
        ('Back Panel', 1),
        ('Foam Padding', 1),
        ('Fabric Cover', 1),
        ('Support Frame', 1),
        ('Screws', 6)
    ],
    'Seat': [
        ('Seat Base', 1),
        ('Foam Padding', 1),
        ('Fabric Cover', 1),
        ('Mounting Brackets', 4),
        ('Screws', 8)
    ],
    
    # Lamp components
    'Shade': [
        ('Shade Frame', 1),
        ('Shade Fabric', 1),
        ('Diffuser', 1),
        ('Mounting Ring', 1)
    ]
}

# Create sub-assembly directory
sub_assembly_dir = 'data/bom/sub_assembly'
os.makedirs(sub_assembly_dir, exist_ok=True)

# Create sub-assembly files
for component, parts in sub_assemblies.items():
    # Create sanitized filename
    filename = re.sub(r'[^\w\s]', '', component.lower()).replace(' ', '_') + '_subassembly.csv'
    filepath = os.path.join(sub_assembly_dir, filename)
    
    # Write sub-assembly components to file
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['part_name', 'quantity'])
        
        for part, quantity in parts:
            writer.writerow([part, quantity])
    
    print(f"Created {filepath}")

# Create a special case for slats - each slat is identical but there are multiple in a bed
slats_dir = os.path.join(sub_assembly_dir, 'bed_slats')
os.makedirs(slats_dir, exist_ok=True)

for i in range(1, 15):  # 14 slats in a bed
    filepath = os.path.join(slats_dir, f'slat_{i}.csv')
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['part_name', 'quantity'])
        writer.writerow(['Wooden Slat', 1])
        writer.writerow(['Fabric Sleeve', 1])
    
    print(f"Created {filepath}")

print("All sub-assembly files created successfully")
