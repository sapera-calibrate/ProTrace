#!/usr/bin/env python3
"""
Create duplicate pairs folder: Copy original and duplicate images
"""

import os
import shutil

def create_duplicates_folder():
    """Create folder with duplicate pairs."""
    
    # Create folder
    output_dir = "duplicate_pairs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Mapping of rejected to original
    # From previous analysis
    pairs = {
        "cccc20777.png": "# (433).png",
        "ccccc (222).png": "# (450).png", 
        "neeed# (1).png": "# (517).png",
        "neeed# (3).png": "# (511).png"
    }
    
    print(f"Creating duplicate pairs in: {output_dir}")
    
    for duplicate_name, original_name in pairs.items():
        
        # Source paths
        duplicate_src = os.path.join("tobe_minted", duplicate_name)
        original_src = os.path.join("Folder X", original_name)
        
        # Destination paths
        duplicate_dst = os.path.join(output_dir, f"DUPLICATE_{duplicate_name}")
        original_dst = os.path.join(output_dir, f"ORIGINAL_{original_name}")
        
        # Copy files
        if os.path.exists(duplicate_src):
            shutil.copy2(duplicate_src, duplicate_dst)
            print(f"✅ Copied duplicate: {duplicate_name}")
        else:
            print(f"❌ Duplicate not found: {duplicate_name}")
        
        if os.path.exists(original_src):
            shutil.copy2(original_src, original_dst)
            print(f"✅ Copied original: {original_name}")
        else:
            print(f"❌ Original not found: {original_name}")
        
        print()
    
    print(f"Duplicate pairs created in: {output_dir}")
    print(f"Total pairs: {len(pairs)}")


if __name__ == "__main__":
    create_duplicates_folder()
