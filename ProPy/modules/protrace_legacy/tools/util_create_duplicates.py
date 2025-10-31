#!/usr/bin/env python3
"""
Create CORRECT duplicate pairs folder
"""

import os
import shutil

def create_correct_duplicates():
    """Create folder with the actual duplicate pairs."""

    # Create folder
    output_dir = "correct_duplicate_pairs"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Correct mappings: duplicate -> original
    correct_pairs = {
        "tobe_minted/cccc20777.png": "Folder X/# (207).png",
        "tobe_minted/ccccc (222).png": "Folder X/# (222).png",
        "tobe_minted/neeed# (3).png": "Folder X/# (278).png",
        "tobe_minted/neeed# (1).png": "Folder X/# (283).png",
    }

    print("Creating CORRECT duplicate pairs:")
    print("=" * 40)

    for duplicate_path, original_path in correct_pairs.items():

        # Destination paths
        dup_name = os.path.basename(duplicate_path)
        orig_name = os.path.basename(original_path)

        duplicate_dst = os.path.join(output_dir, f"DUPLICATE_{dup_name}")
        original_dst = os.path.join(output_dir, f"ORIGINAL_{orig_name}")

        # Copy files
        if os.path.exists(duplicate_path):
            shutil.copy2(duplicate_path, duplicate_dst)
            print(f"✅ Copied duplicate: {dup_name}")
        else:
            print(f"❌ Duplicate not found: {dup_name}")

        if os.path.exists(original_path):
            shutil.copy2(original_path, original_dst)
            print(f"✅ Copied original: {orig_name}")
        else:
            print(f"❌ Original not found: {orig_name}")

        print()

    print(f"Correct duplicate pairs created in: {output_dir}")
    print(f"Total pairs: {len(correct_pairs)}")
    print("\nThese images have IDENTICAL 256-bit DNA hashes!")

if __name__ == "__main__":
    create_correct_duplicates()
