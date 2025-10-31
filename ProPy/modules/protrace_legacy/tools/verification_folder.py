#!/usr/bin/env python3
"""
Verify Folder X images match registry hashes
"""

import os
from protrace.image_dna import compute_dna

def verify_folder_x():
    """Verify that Folder X images actually have the hashes in the registry"""

    # The claimed matches
    folder_x_images = [
        "Folder X/# (433).png",  # claimed to match cccc20777.png
        "Folder X/# (450).png",  # claimed to match ccccc (222).png
        "Folder X/# (511).png",  # claimed to match neeed# (3).png
        "Folder X/# (517).png",  # claimed to match neeed# (1).png
    ]

    # Expected hashes from registry
    expected_hashes = {
        "Folder X/# (433).png": "339399585a43738917c3c0ede13f3f0017c300ede13f3f003f0780cfe73f0700",
        "Folder X/# (450).png": "1333231d0b8babc9ff8783c3e3333300df83a3e7e71b3b00d987c7c7673b2300",
        "Folder X/# (511).png": "032929292b2707c9ffe3c3c3c3133900ffe3e3c7c71b1900fbc3c7cf873b2000",
        "Folder X/# (517).png": "1323a3598bc34bc5d9e3c393e03b3f00c8e3e39dc03b3f00f9e7f78de53b0b00",
    }

    print("Verifying Folder X images match registry hashes:")
    print("=" * 50)

    for img_path in folder_x_images:
        print(f"\nChecking: {os.path.basename(img_path)}")

        if not os.path.exists(img_path):
            print(f"  File not found: {img_path}")
            continue

        try:
            dna_result = compute_dna(img_path)
            actual_hash = dna_result['dna_hex']
            expected_hash = expected_hashes[img_path]

            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")

            if actual_hash == expected_hash:
                print("  RESULT: MATCH ✅")
            else:
                print("  RESULT: MISMATCH ❌")
                # Find first difference
                for i, (a, b) in enumerate(zip(actual_hash, expected_hash)):
                    if a != b:
                        print(f"  First difference at position {i}: '{a}' vs '{b}'")
                        break

        except Exception as e:
            print(f"  ERROR: {e}")

if __name__ == "__main__":
    verify_folder_x()
