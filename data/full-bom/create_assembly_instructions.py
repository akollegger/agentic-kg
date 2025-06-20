#!/usr/bin/env python3
import csv
import os
import re
import unicodedata

def normalize_filename(name):
    """Normalize a string to create a valid filename."""
    # Map Swedish special characters to their ASCII equivalents
    swedish_chars = {
        'å': 'a', 'ä': 'a', 'ö': 'o',
        'Å': 'A', 'Ä': 'A', 'Ö': 'O'
    }
    
    # Replace Swedish characters first
    for char, replacement in swedish_chars.items():
        name = name.replace(char, replacement)
    
    # Convert to lowercase
    name = name.lower()
    
    # Replace spaces with underscores
    name = re.sub(r'\s+', '_', name)
    
    # Remove any remaining non-alphanumeric characters
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    
    return name

def get_product_info():
    """Read product information from products.csv."""
    products = {}
    with open('data/bom/products.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product_name = row['product_name']
            products[product_name] = {
                'price': row['price'],
                'description': row['description'],
                'part_number': row['part_number']
            }
    return products

def get_assembly_components(product_name):
    """Get assembly components for a product."""
    # Get the normalized filename
    normalized_name = normalize_filename(product_name)
    filename = f"data/bom/assembly/{normalized_name}_assembly.csv"
    
    # Print for debugging
    print(f"Looking for assembly file: {filename}")
    
    components = []
    
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                components.append({
                    'name': row['component_name'],
                    'quantity': row['quantity'],
                    'part_number': row['part_number']
                })
    except FileNotFoundError:
        # Try to find the file by listing directory contents
        print(f"File not found: {filename}")
        print(f"Attempting to find the correct file...")
        
        import glob
        assembly_files = glob.glob('data/bom/assembly/*.csv')
        
        # Print available files
        print("Available assembly files:")
        for f in assembly_files:
            print(f"  {f}")
        
        # Try to match by product name part
        product_key = product_name.split(' ')[1].lower()
        matching_files = [f for f in assembly_files if product_key in f.lower()]
        
        if matching_files:
            print(f"Found matching file: {matching_files[0]}")
            with open(matching_files[0], 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    components.append({
                        'name': row['component_name'],
                        'quantity': row['quantity'],
                        'part_number': row['part_number']
                    })
        else:
            raise FileNotFoundError(f"Could not find assembly file for {product_name}")
    
    return components

def is_sub_assembly(component_name):
    """Check if a component is a sub-assembly."""
    # Define components that are pre-assembled
    pre_assembled = [
        'Seat Cushion', 'Back Cushion', 'Drawer', 'Drawer Unit', 
        'Cable Management', 'Headboard', 'Bed Frame', 'Bed Slats',
        'Shelf', 'Lamp Shade', 'Lamp Base'
    ]
    
    return any(pre in component_name for pre in pre_assembled)

def get_tools_required(components):
    """Determine tools required based on components."""
    tools = ["Allen Key"]
    
    if any("Screw" in comp['name'] for comp in components):
        if not any("Allen Key" in comp['name'] for comp in components):
            tools.append("Screwdriver")
    
    if any(comp['name'] in ["Drawer", "Drawer Unit"] for comp in components):
        tools.append("Hammer")
    
    return tools

def generate_assembly_steps(product_name, components):
    """Generate assembly steps based on product type and components."""
    steps = []
    product_type = product_name.split(" ")[1].lower()
    
    # Common first step
    steps.append("Unpack all components and arrange them on a clean, flat surface. Check that all parts are included using the parts list above.")
    
    if product_type == "chair":
        steps.append("Attach the legs to the seat base using the provided screws. Tighten with the Allen key but don't fully tighten yet.")
        steps.append("Align the back rest with the seat base and secure using the designated screws.")
        steps.append("Once all parts are properly aligned, fully tighten all screws.")
        steps.append("Place the chair upright and ensure it's stable on a level surface.")
    
    elif product_type == "table":
        steps.append("Lay the table top upside down on a soft surface to prevent scratches.")
        steps.append("Attach the legs to the table top using the provided screws. Start by hand-tightening.")
        steps.append("Once all legs are attached, fully tighten all screws with the Allen key.")
        steps.append("With help from another person, carefully turn the table upright.")
    
    elif product_type == "desk":
        steps.append("Lay the desk top upside down on a soft surface to prevent scratches.")
        steps.append("Assemble the desk frame by connecting the side panels using the provided screws.")
        steps.append("Attach the frame to the desk top using the designated mounting points.")
        steps.append("If included, install any drawers or cable management systems.")
        steps.append("With help from another person, carefully turn the desk upright.")
    
    elif product_type == "sofa":
        steps.append("Assemble the sofa frame by connecting the side panels to the base using the provided screws.")
        steps.append("Attach the back panel to the assembled frame.")
        steps.append("Place the seat cushions and back cushions on the frame.")
        steps.append("Adjust the cushions to ensure they're properly positioned.")
    
    elif product_type == "bookshelf":
        steps.append("Lay the side panel flat and attach the shelves using the provided shelf pins or screws.")
        steps.append("Attach the other side panel to complete the basic structure.")
        steps.append("Secure the back panel to the bookshelf using the small nails or screws provided.")
        steps.append("With help from another person, carefully stand the bookshelf upright.")
        steps.append("Adjust the shelf positions if needed.")
    
    elif product_type == "lamp":
        steps.append("Assemble the lamp base if it comes in multiple parts.")
        steps.append("Thread the power cord through the base and stem.")
        steps.append("Attach the lamp shade to the socket.")
        steps.append("Install a light bulb (not included) of the recommended wattage.")
        steps.append("Place the lamp on a stable surface and plug it in to test.")
    
    elif product_type == "bed":
        steps.append("Assemble the headboard by attaching all components according to the markings.")
        steps.append("Connect the side rails to the headboard using the provided brackets and screws.")
        steps.append("Attach the footboard to the side rails to complete the bed frame.")
        steps.append("Place the support slats across the frame, spacing them evenly.")
        steps.append("Place your mattress (not included) on top of the slats.")
    
    elif product_type == "dresser":
        steps.append("Assemble the dresser frame by connecting the side panels to the top and bottom panels.")
        steps.append("Attach the back panel to the assembled frame.")
        steps.append("Install the drawer slides to the inside of the dresser frame.")
        steps.append("Assemble each drawer and attach the drawer handles.")
        steps.append("Slide the drawers into the frame and check that they open and close smoothly.")
    
    elif product_type in ["coffee", "nightstand"]:
        steps.append("Lay the top panel upside down on a soft surface to prevent scratches.")
        steps.append("Attach the legs or side panels to the top using the provided screws.")
        steps.append("If included, install any shelves or drawers.")
        steps.append("Carefully turn the piece upright and check that it's stable.")
    
    # Add care instructions as the final step
    steps.append("Care instructions: Clean with a damp cloth. Avoid using harsh chemicals. Periodically check and tighten any loose screws.")
    
    return steps

def create_assembly_instructions():
    """Create assembly instructions for each product."""
    products = get_product_info()
    
    for product_name, info in products.items():
        try:
            components = get_assembly_components(product_name)
            
            # Separate pre-assembled components
            assembly_components = []
            pre_assembled_components = []
            
            for component in components:
                if is_sub_assembly(component['name']):
                    pre_assembled_components.append(component)
                else:
                    assembly_components.append(component)
            
            tools = get_tools_required(components)
            steps = generate_assembly_steps(product_name, components)
            
            # Create markdown content
            markdown_content = f"# {product_name} Assembly Instructions\n\n"
            markdown_content += f"## Product Information\n\n"
            markdown_content += f"**Price:** {info['price']}\n\n"
            markdown_content += f"**Description:** {info['description']}\n\n"
            markdown_content += f"**Part Number:** {info['part_number']}\n\n"
            
            markdown_content += f"## Parts List\n\n"
            markdown_content += "| Component | Quantity | Part Number |\n"
            markdown_content += "|----------|----------|------------|\n"
            
            for component in assembly_components:
                markdown_content += f"| {component['name']} | {component['quantity']} | {component['part_number']} |\n"
            
            if pre_assembled_components:
                markdown_content += f"\n## Pre-Assembled Components\n\n"
                markdown_content += "| Component | Quantity | Part Number |\n"
                markdown_content += "|----------|----------|------------|\n"
                
                for component in pre_assembled_components:
                    markdown_content += f"| {component['name']} | {component['quantity']} | {component['part_number']} |\n"
            
            markdown_content += f"\n## Tools Required\n\n"
            for tool in tools:
                markdown_content += f"- {tool}\n"
            
            markdown_content += f"\n## Assembly Steps\n\n"
            for i, step in enumerate(steps, 1):
                markdown_content += f"{i}. {step}\n"
            
            markdown_content += f"\n## Customer Support\n\n"
            markdown_content += f"If you encounter any issues during assembly, please contact our customer support:\n\n"
            markdown_content += f"- Phone: +46-771-123-456\n"
            markdown_content += f"- Email: support@swedishfurniture.com\n"
            markdown_content += f"- Online: www.swedishfurniture.com/support\n\n"
            markdown_content += f"Thank you for choosing Swedish Furniture. Enjoy your new {product_name}!\n"
            
            # Write to file
            filename = f"data/bom/assembly_instructions/{normalize_filename(product_name)}_instructions.md"
            with open(filename, 'w') as f:
                f.write(markdown_content)
            
            print(f"Created assembly instructions for {product_name}")
            
        except Exception as e:
            print(f"Error creating instructions for {product_name}: {e}")

if __name__ == "__main__":
    create_assembly_instructions()
