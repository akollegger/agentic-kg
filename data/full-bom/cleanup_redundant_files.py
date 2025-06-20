#!/usr/bin/env python3
import os
import shutil
import glob

def remove_files(directory, pattern):
    """Remove files matching pattern in directory"""
    files = glob.glob(os.path.join(directory, pattern))
    count = 0
    for file in files:
        if os.path.isfile(file):
            os.remove(file)
            count += 1
    return count

def remove_directory(directory):
    """Remove directory and all its contents"""
    if os.path.exists(directory) and os.path.isdir(directory):
        shutil.rmtree(directory)
        return True
    return False

# Base directory
base_dir = "/Users/akollegger/Developer/genai/dlai/agentic-kg/data/bom"

# Remove assembly files
assembly_dir = os.path.join(base_dir, "assembly")
assembly_count = remove_files(assembly_dir, "*.csv")
print(f"Removed {assembly_count} assembly files")

# Remove sub-assembly files and directories
sub_assembly_dir = os.path.join(base_dir, "sub_assembly")
sub_assembly_count = remove_files(sub_assembly_dir, "*.csv")

# Remove bed_slats directory
bed_slats_dir = os.path.join(sub_assembly_dir, "bed_slats")
if remove_directory(bed_slats_dir):
    print(f"Removed bed_slats directory")

print(f"Removed {sub_assembly_count} sub-assembly files")

# Remove empty directories
if len(os.listdir(assembly_dir)) == 0:
    os.rmdir(assembly_dir)
    print(f"Removed empty assembly directory")

if len(os.listdir(sub_assembly_dir)) == 0:
    os.rmdir(sub_assembly_dir)
    print(f"Removed empty sub_assembly directory")

print("Cleanup complete!")
