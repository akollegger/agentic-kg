#!/usr/bin/env python3
import csv
import os
import random
import string
import glob
from collections import defaultdict

# Ensure directories exist
os.makedirs('data/bom/supplier_catalogs', exist_ok=True)

# Read the suppliers data
suppliers = []
with open('data/bom/suppliers.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        suppliers.append(row)

# Read the part-supplier mappings to know what parts each supplier provides
supplier_parts = defaultdict(list)
with open('data/bom/part_supplier_options.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        supplier_id = row['supplier_id']
        part_info = {
            'part_number': row['part_number'],
            'part_name': row['part_name'],
            'unit_cost': row['unit_cost'].replace('$', ''),
            'minimum_order_quantity': row['minimum_order_quantity']
        }
        supplier_parts[supplier_id].append(part_info)

# Define additional part categories by specialty
specialty_parts = {
    "Wood": [
        "Pine Board", "Oak Plank", "Birch Veneer", "Mahogany Panel", "Walnut Strip",
        "Cedar Plank", "Teak Board", "Maple Dowel", "Cherry Panel", "Bamboo Sheet",
        "Plywood Sheet", "MDF Board", "Particle Board", "Hardwood Trim", "Wood Plug",
        "Corner Block", "Wood Spacer", "Wooden Peg", "Wood Veneer", "Wooden Bracket",
        "Wooden Knob", "Wooden Bead", "Wood Molding", "Wood Edging", "Wood Inlay",
        "Wood Corbel", "Wood Spindle", "Wood Finial", "Wood Rosette", "Wood Applique"
    ],
    "Metal": [
        "Steel Rod", "Aluminum Tube", "Brass Fitting", "Copper Wire", "Iron Bracket",
        "Stainless Hinge", "Metal Plate", "Chrome Handle", "Zinc Fastener", "Bronze Knob",
        "Metal Mesh", "Wire Frame", "Metal Grommet", "Metal Clasp", "Metal Chain",
        "Metal Spring", "Metal Washer", "Metal Spacer", "Metal Rivet", "Metal Eyelet",
        "Metal Clip", "Metal Hook", "Metal Staple", "Metal Angle", "Metal Strap",
        "Metal Tube", "Metal Cap", "Metal Flange", "Metal Bushing", "Metal Stud"
    ],
    "Fabric": [
        "Cotton Cloth", "Polyester Blend", "Linen Sheet", "Silk Cover", "Wool Padding",
        "Velvet Material", "Microfiber Cloth", "Canvas Sheet", "Denim Cover", "Leather Patch",
        "Suede Strip", "Felt Padding", "Mesh Fabric", "Nylon Webbing", "Elastic Band",
        "Twill Fabric", "Satin Lining", "Fleece Sheet", "Jersey Knit", "Chenille Fabric",
        "Corduroy Material", "Vinyl Cover", "Faux Leather", "Upholstery Fabric", "Outdoor Fabric",
        "Quilted Padding", "Embroidered Patch", "Woven Trim", "Jacquard Fabric", "Tapestry Material"
    ],
    "Fasteners": [
        "Wood Screw", "Machine Bolt", "Carriage Bolt", "Hex Nut", "Lock Washer",
        "Flat Washer", "Anchor Bolt", "Toggle Bolt", "Drywall Screw", "Deck Screw",
        "Lag Bolt", "Eye Bolt", "J-Bolt", "U-Bolt", "Threaded Rod",
        "Wing Nut", "Cap Nut", "T-Nut", "Coupling Nut", "Expansion Anchor",
        "Concrete Anchor", "Rivet Nut", "Thumb Screw", "Set Screw", "Shoulder Bolt",
        "Hanger Bolt", "Dowel Screw", "Confirmat Screw", "Security Screw", "Self-Tapping Screw"
    ],
    "Foam": [
        "Memory Foam", "High-Density Foam", "Open Cell Foam", "Closed Cell Foam", "Rebond Foam",
        "Polyurethane Foam", "Latex Foam", "Acoustic Foam", "Foam Padding", "Foam Sheet",
        "Foam Block", "Foam Strip", "Foam Wedge", "Foam Cylinder", "Foam Cube",
        "Convoluted Foam", "Egg Crate Foam", "Foam Topper", "Foam Insert", "Foam Cushion",
        "Anti-Static Foam", "Fire Retardant Foam", "Waterproof Foam", "Outdoor Foam", "Marine Foam",
        "Foam Tape", "Foam Gasket", "Foam Seal", "Foam Filter", "Foam Insulation"
    ],
    "Hardware": [
        "Door Hinge", "Drawer Slide", "Cabinet Knob", "Door Handle", "Caster Wheel",
        "Furniture Leg", "Corner Bracket", "Shelf Support", "Furniture Glide", "Furniture Lock",
        "Magnetic Catch", "Touch Latch", "Drawer Pull", "Door Stop", "Furniture Bolt",
        "Furniture Connector", "Leveling Foot", "Furniture Nail", "Furniture Tack", "Furniture Staple",
        "Cable Grommet", "Furniture Bumper", "Furniture Cap", "Furniture Clip", "Furniture Hook",
        "Furniture Plate", "Furniture Spacer", "Furniture Strap", "Furniture Tie", "Furniture Wedge"
    ],
    "Electronics": [
        "Power Supply", "LED Light", "Light Socket", "Dimmer Switch", "Power Cord",
        "USB Port", "HDMI Port", "Cable Clip", "Wire Connector", "Battery Pack",
        "Touch Sensor", "Motion Sensor", "Light Sensor", "Remote Control", "Control Panel",
        "Speaker Unit", "Bluetooth Module", "WiFi Module", "Charging Port", "Power Button",
        "LED Strip", "Cable Organizer", "Wireless Charger", "Audio Jack", "Microphone",
        "Camera Module", "Display Screen", "Circuit Board", "Heat Sink", "Cooling Fan"
    ],
    "Glass": [
        "Clear Glass", "Frosted Glass", "Tempered Glass", "Laminated Glass", "Tinted Glass",
        "Mirror Glass", "Glass Panel", "Glass Shelf", "Glass Door", "Glass Insert",
        "Glass Tube", "Glass Rod", "Glass Bead", "Glass Tile", "Glass Block",
        "Glass Dome", "Glass Vase", "Glass Bowl", "Glass Plate", "Glass Cup",
        "Glass Knob", "Glass Handle", "Glass Ornament", "Glass Pendant", "Glass Shade",
        "Glass Mosaic", "Glass Cabochon", "Glass Prism", "Glass Lens", "Glass Filter"
    ],
    "Adhesives": [
        "Wood Glue", "Super Glue", "Epoxy Resin", "Contact Cement", "Construction Adhesive",
        "Spray Adhesive", "Hot Melt Glue", "Silicone Sealant", "Polyurethane Adhesive", "Rubber Cement",
        "Fabric Glue", "Leather Adhesive", "Plastic Cement", "Metal Epoxy", "Glass Adhesive",
        "Foam Adhesive", "Tile Adhesive", "Wallpaper Paste", "Carpet Adhesive", "Vinyl Adhesive",
        "Adhesive Tape", "Double-Sided Tape", "Mounting Tape", "Duct Tape", "Masking Tape",
        "Electrical Tape", "Foam Tape", "Velcro Tape", "Weather Stripping", "Adhesive Dots"
    ],
    "Packaging": [
        "Cardboard Box", "Bubble Wrap", "Packing Peanuts", "Kraft Paper", "Tissue Paper",
        "Shrink Wrap", "Stretch Film", "Packing Tape", "Shipping Label", "Air Pillows",
        "Foam Insert", "Corrugated Sheet", "Poly Bag", "Padded Envelope", "Shipping Tube",
        "Edge Protector", "Corner Protector", "Void Fill", "Packaging Strap", "Packaging Seal",
        "Gift Box", "Gift Bag", "Gift Wrap", "Gift Ribbon", "Gift Tag",
        "Retail Box", "Display Box", "Hang Tag", "Product Label", "Barcode Label"
    ]
}

# Generate supplier-specific part numbers
def generate_supplier_part_number(supplier_id):
    prefix = supplier_id.replace('SUP-', '')
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{random_chars}"

# Create supplier catalogs
for supplier in suppliers:
    supplier_id = supplier['supplier_id']
    specialty = supplier['specialty']
    
    # Get the parts this supplier already provides
    existing_parts = supplier_parts[supplier_id]
    
    # Create a catalog with both existing parts and additional parts from their specialty
    catalog = []
    
    # Add existing parts with supplier-specific part numbers
    for part in existing_parts:
        catalog_entry = {
            'supplier_part_number': generate_supplier_part_number(supplier_id),
            'customer_part_number': part['part_number'],
            'description': part['part_name'],
            'category': specialty,
            'unit_price': part['unit_cost'],
            'minimum_order': part['minimum_order_quantity'],
            'stock_quantity': random.randint(100, 10000),
            'lead_time_days': random.randint(3, 30)
        }
        catalog.append(catalog_entry)
    
    # Add additional parts from their specialty (50-100 more items)
    additional_count = random.randint(50, 100)
    specialty_part_list = specialty_parts.get(specialty, [])
    
    if specialty_part_list:
        # Make sure we don't exceed the available specialty parts
        additional_count = min(additional_count, len(specialty_part_list))
        selected_parts = random.sample(specialty_part_list, additional_count)
        
        for part_name in selected_parts:
            catalog_entry = {
                'supplier_part_number': generate_supplier_part_number(supplier_id),
                'customer_part_number': '',  # Empty as these aren't used by our furniture company
                'description': part_name,
                'category': specialty,
                'unit_price': f"{random.uniform(0.5, 100.0):.2f}",
                'minimum_order': str(random.randint(10, 200)),
                'stock_quantity': str(random.randint(100, 10000)),
                'lead_time_days': str(random.randint(3, 30))
            }
            catalog.append(catalog_entry)
    
    # Write the catalog to a CSV file
    supplier_name_safe = supplier['name'].replace(' ', '_').replace(',', '').lower()
    catalog_filename = f"data/bom/supplier_catalogs/{supplier_id}_{supplier_name_safe}_catalog.csv"
    
    with open(catalog_filename, 'w', newline='') as f:
        fieldnames = ['supplier_part_number', 'customer_part_number', 'description', 
                     'category', 'unit_price', 'minimum_order', 'stock_quantity', 'lead_time_days']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in catalog:
            writer.writerow(entry)
    
    print(f"Created catalog for {supplier['name']} with {len(catalog)} items")

# Create a mapping file that connects our part numbers to supplier part numbers
with open('data/bom/supplier_catalogs/part_number_mapping.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['part_number', 'supplier_id', 'supplier_part_number', 'description'])
    
    for supplier_id, parts in supplier_parts.items():
        # Find the corresponding catalog file
        supplier_name = next((s['name'] for s in suppliers if s['supplier_id'] == supplier_id), '')
        supplier_name_safe = supplier_name.replace(' ', '_').replace(',', '').lower()
        catalog_filename = f"data/bom/supplier_catalogs/{supplier_id}_{supplier_name_safe}_catalog.csv"
        
        if os.path.exists(catalog_filename):
            with open(catalog_filename, 'r') as catalog_file:
                catalog_reader = csv.DictReader(catalog_file)
                for catalog_entry in catalog_reader:
                    if catalog_entry['customer_part_number']:  # Only map parts that we use
                        writer.writerow([
                            catalog_entry['customer_part_number'],
                            supplier_id,
                            catalog_entry['supplier_part_number'],
                            catalog_entry['description']
                        ])

print("Created part number mapping file connecting internal part numbers to supplier part numbers")
