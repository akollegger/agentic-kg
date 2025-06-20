#!/usr/bin/env python3
import csv
import random

# Read Swedish towns
towns = []
with open('data/bom/swedish_towns.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        towns.append(row['town_name'])

# Read furniture types
furniture = []
with open('data/bom/furniture_types.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        furniture.append(row['furniture_type'])

# Price ranges for different furniture types (in USD)
price_ranges = {
    'Chair': (79, 299),
    'Table': (149, 599),
    'Desk': (129, 499),
    'Sofa': (399, 1299),
    'Bookshelf': (89, 349),
    'Lamp': (29, 149),
    'Bed': (299, 999),
    'Dresser': (199, 699),
    'Coffee Table': (99, 399),
    'Nightstand': (59, 199)
}

# IKEA-inspired descriptions
descriptions = {
    'Chair': [
        "Ergonomic design with minimalist Scandinavian style",
        "Comfortable seating with durable fabric upholstery"
    ],
    'Table': [
        "Spacious dining surface with sturdy wooden legs",
        "Modern design that brings people together"
    ],
    'Desk': [
        "Perfect workspace with smart cable management",
        "Functional design with ample storage solutions"
    ],
    'Sofa': [
        "Plush comfort with clean lines and removable covers",
        "Modular design that adapts to your living space"
    ],
    'Bookshelf': [
        "Versatile storage solution with adjustable shelves",
        "Simple yet elegant display for your favorite items"
    ],
    'Lamp': [
        "Warm ambient lighting with energy-efficient LED",
        "Stylish accent piece that brightens any room"
    ],
    'Bed': [
        "Restful sleep with supportive frame and clean design",
        "Comfortable platform with hidden storage options"
    ],
    'Dresser': [
        "Spacious drawers with smooth-gliding mechanism",
        "Timeless design that complements any bedroom"
    ],
    'Coffee Table': [
        "Centerpiece for your living room with hidden storage",
        "Sleek surface perfect for books and beverages"
    ],
    'Nightstand': [
        "Compact bedside solution with convenient drawer",
        "Essential bedroom companion with minimalist charm"
    ]
}

# Generate products.csv
with open('data/bom/products.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['product_name', 'price', 'description'])
    
    # Create 10 products by combining towns and furniture
    for i in range(10):
        town = towns[i]
        furniture_type = furniture[i]
        product_name = f"{town} {furniture_type}"
        
        # Generate a reasonable price
        min_price, max_price = price_ranges[furniture_type]
        price = random.randint(min_price, max_price)
        
        # Get a description
        description = random.choice(descriptions[furniture_type])
        
        writer.writerow([product_name, f"${price}", description])

print("Created products.csv with 10 products")
