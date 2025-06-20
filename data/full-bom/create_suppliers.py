#!/usr/bin/env python3
import csv
import os
import glob
import random

# Define suppliers with their specialties and locations
suppliers = [
    {
        "supplier_id": "SUP-001",
        "name": "Nordic Wood Industries",
        "specialty": "Wood",
        "city": "Stockholm",
        "country": "Sweden",
        "website": "www.nordicwood.se",
        "contact_email": "info@nordicwood.se"
    },
    {
        "supplier_id": "SUP-002",
        "name": "Shanghai Metal Corp",
        "specialty": "Metal",
        "city": "Shanghai",
        "country": "China",
        "website": "www.shanghaimetal.com",
        "contact_email": "sales@shanghaimetal.com"
    },
    {
        "supplier_id": "SUP-003",
        "name": "Bangalore Textiles Ltd",
        "specialty": "Fabric",
        "city": "Bangalore",
        "country": "India",
        "website": "www.bangaloretextiles.in",
        "contact_email": "contact@bangaloretextiles.in"
    },
    {
        "supplier_id": "SUP-004",
        "name": "German Precision Fasteners",
        "specialty": "Fasteners",
        "city": "Munich",
        "country": "Germany",
        "website": "www.germanfasteners.de",
        "contact_email": "info@germanfasteners.de"
    },
    {
        "supplier_id": "SUP-005",
        "name": "Brazilian Foam Solutions",
        "specialty": "Foam",
        "city": "São Paulo",
        "country": "Brazil",
        "website": "www.brazilfoam.com.br",
        "contact_email": "sales@brazilfoam.com.br"
    },
    {
        "supplier_id": "SUP-006",
        "name": "American Hardware Inc",
        "specialty": "Hardware",
        "city": "Chicago",
        "country": "USA",
        "website": "www.americanhardware.com",
        "contact_email": "support@americanhardware.com"
    },
    {
        "supplier_id": "SUP-007",
        "name": "Tokyo Electronics Co",
        "specialty": "Electronics",
        "city": "Tokyo",
        "country": "Japan",
        "website": "www.tokyoelectronics.jp",
        "contact_email": "info@tokyoelectronics.jp"
    },
    {
        "supplier_id": "SUP-008",
        "name": "Sydney Glass Works",
        "specialty": "Glass",
        "city": "Sydney",
        "country": "Australia",
        "website": "www.sydneyglass.com.au",
        "contact_email": "orders@sydneyglass.com.au"
    },
    {
        "supplier_id": "SUP-009",
        "name": "Cape Town Adhesives",
        "specialty": "Adhesives",
        "city": "Cape Town",
        "country": "South Africa",
        "website": "www.capetownadhesives.co.za",
        "contact_email": "sales@capetownadhesives.co.za"
    },
    {
        "supplier_id": "SUP-010",
        "name": "Dubai Packaging Solutions",
        "specialty": "Packaging",
        "city": "Dubai",
        "country": "UAE",
        "website": "www.dubaipackaging.ae",
        "contact_email": "info@dubaipackaging.ae"
    }
]

# Define part categories and their supplier specialties
part_categories = {
    "Wood Panel": "Wood",
    "Edge Banding": "Wood",
    "Reinforcement Strips": "Wood",
    "Wood Glue": "Adhesives",
    "Foam Insert": "Foam",
    "Cushion Cover": "Fabric",
    "Zipper": "Hardware",
    "Batting": "Fabric",
    "Screws": "Fasteners",
    "Allen Key": "Hardware",
    "Drawer Front": "Wood",
    "Drawer Bottom": "Wood",
    "Drawer Sides": "Wood",
    "Drawer Back": "Wood",
    "Drawer Rails": "Metal",
    "Drawer Handle": "Metal",
    "Cable Tray": "Metal",
    "Cable Clips": "Hardware",
    "Zip Ties": "Hardware",
    "Adhesive Pads": "Adhesives",
    "Base Frame": "Metal",
    "Back Frame": "Metal",
    "Side Frames": "Metal",
    "Support Slats": "Wood",
    "Corner Brackets": "Metal",
    "Headboard Panel": "Wood",
    "Headboard Frame": "Metal",
    "Decorative Trim": "Wood",
    "Mounting Brackets": "Metal",
    "Wooden Slat": "Wood",
    "Fabric Sleeve": "Fabric",
    "Shelf Support Holes": "Hardware",
    "Legs": "Wood",
    "Back Panel": "Wood",
    "Shelves": "Wood",
    "Shelf Pins": "Hardware",
    "Base": "Metal",
    "Stem": "Metal",
    "Shade": "Fabric",
    "Light Bulb Socket": "Electronics",
    "Power Cord": "Electronics",
    "Shade Frame": "Metal",
    "Shade Fabric": "Fabric",
    "Diffuser": "Glass",
    "Mounting Ring": "Metal",
    "Seat Base": "Wood",
    "Foam Padding": "Foam",
    "Fabric Cover": "Fabric",
    "Support Frame": "Metal",
    "Top Panel": "Wood",
    "Side Panels": "Wood",
    "Bottom Panel": "Wood",
    "Cover": "Fabric"
}

# Find all sub-assembly files to get the lowest level parts
sub_assembly_files = glob.glob('data/bom/sub_assembly/*.csv')
sub_assembly_files.extend(glob.glob('data/bom/sub_assembly/bed_slats/*.csv'))

# Collect all lowest level parts
lowest_level_parts = []

for sub_file in sub_assembly_files:
    with open(sub_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'part_name' in row and 'part_number' in row:
                part = {
                    'part_name': row['part_name'],
                    'part_number': row['part_number'],
                    'parent_part_number': row.get('parent_part_number', 'UNKNOWN')
                }
                lowest_level_parts.append(part)

# Create part-supplier mappings
part_supplier_mappings = []

for part in lowest_level_parts:
    part_name = part['part_name']
    category = part_categories.get(part_name, "Hardware")  # Default to Hardware if not found
    
    # Find suppliers that match this category
    matching_suppliers = [s for s in suppliers if s['specialty'] == category]
    
    if matching_suppliers:
        supplier = random.choice(matching_suppliers)
        mapping = {
            'part_number': part['part_number'],
            'part_name': part_name,
            'supplier_id': supplier['supplier_id'],
            'supplier_name': supplier['name'],
            'lead_time_days': random.randint(5, 30),
            'unit_cost': round(random.uniform(0.5, 50.0), 2)
        }
        part_supplier_mappings.append(mapping)

# Create suppliers.csv
with open('data/bom/suppliers.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['supplier_id', 'name', 'specialty', 'city', 'country', 'website', 'contact_email'])
    
    for supplier in suppliers:
        writer.writerow([
            supplier['supplier_id'],
            supplier['name'],
            supplier['specialty'],
            supplier['city'],
            supplier['country'],
            supplier['website'],
            supplier['contact_email']
        ])

print("Created suppliers.csv with 10 global suppliers")

# Create part_suppliers.csv to map parts to suppliers
with open('data/bom/part_suppliers.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['part_number', 'part_name', 'supplier_id', 'supplier_name', 'lead_time_days', 'unit_cost'])
    
    for mapping in part_supplier_mappings:
        writer.writerow([
            mapping['part_number'],
            mapping['part_name'],
            mapping['supplier_id'],
            mapping['supplier_name'],
            mapping['lead_time_days'],
            f"${mapping['unit_cost']}"
        ])

print("Created part_suppliers.csv mapping lowest level parts to suppliers")
