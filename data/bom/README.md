# Furniture Product Data Structure

This directory contains the data structure for furniture products used in the agentic-kg project. The data is organized to support knowledge graph extraction and agent-based analysis.

## Data Structure Overview

1. **Products (P-xxxx)**: Swedish town + furniture type combinations
2. **Assemblies (A-xxxx)**: Major components for each product
3. **Sub-assemblies (S-xxxx)**: Detailed breakdown of components
4. **Supplier data**: 20 global suppliers with specialties (wood, metal, fabric, etc.)
5. **Multiple supplier options per part**: For pricing competition and supply chain resiliency
6. **Supplier-specific catalogs**: With proprietary part numbers (e.g., 001-H21RG4)
7. **Part number mapping**: Between internal part numbers and supplier part numbers

## Files

### Core Data Files

- `products.csv`: Master list of products with descriptions and pricing
- `assemblies.csv`: Consolidated file of all product assemblies
- `sub_assemblies.csv`: Consolidated file of all component sub-assemblies
- `part_supplier_details.csv`: Supplier information for parts including lead times, costs, and minimum order quantities
- `part_number_mapping.csv`: Mapping between internal part numbers and supplier-specific part numbers

### Supplier Data

- `suppliers.csv`: List of all suppliers with contact information
- `supplier_catalogs/*.csv`: Individual supplier catalogs with their proprietary part numbers and pricing

### Unstructured Data

- `assembly_instructions/*.md`: Markdown files with assembly instructions for each product
- `product_reviews/*.md`: Consumer reviews for each product

## Data Consolidation

The data structure has been streamlined by:

1. Consolidating individual assembly files into `assemblies.csv`
2. Consolidating individual sub-assembly files into `sub_assemblies.csv`
3. Consolidating supplier information into `part_supplier_details.csv`
4. Removing temporary reference files used for initial data generation

## Usage for Knowledge Graph

This data structure is designed to support:

1. **Product Hierarchy**: Products → Assemblies → Sub-assemblies → Parts
2. **Supply Chain Analysis**: Parts → Suppliers → Lead times/Costs
3. **Root Cause Analysis**: Tracing faulty parts through the supply chain to affected products
4. **Unstructured Data Integration**: Connecting assembly instructions and consumer reviews to the structured product data

## Scripts

- `create_assembly_instructions.py`: Generates markdown assembly instructions for each product
- `consolidate_assemblies.py`: Script used to consolidate individual assembly files
- `consolidate_subassemblies.py`: Script used to consolidate individual sub-assembly files
