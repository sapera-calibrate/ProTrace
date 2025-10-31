#!/usr/bin/env python3
"""
Verify the CORRECT Folder X images match registry hashes
"""

import os
from protrace.image_dna import compute_dna

def verify_correct_matches():
    """Verify that the correct Folder X images match the registry hashes"""

    # Correct mappings based on os.listdir() order
    correct_mappings = {
        "Folder X/# (207).png": 433,  # image_433
        "Folder X/# (222).png": 450,  # image_450
        "Folder X/# (278).png": 511,  # image_511
        "Folder X/# (283).png": 517,  # image_517
    }

    print("Verifying CORRECT Folder X images match registry hashes:")
    print("=" * 55)

    # Load registry
    import json
    with open("merkle_tree.json", 'r') as f:
        data = json.load(f)

    for img_path, registry_idx in correct_mappings.items():
        print(f"\nChecking: {os.path.basename(img_path)} (registry index {registry_idx})")

        if not os.path.exists(img_path):
            print(f"  File not found: {img_path}")
            continue

        # Get hash from registry
        if registry_idx < len(data['leaves']):
            leaf_hex = data['leaves'][registry_idx]
            leaf_bytes = bytes.fromhex(leaf_hex)
            leaf_str = leaf_bytes.decode('utf-8')
            registry_hash = leaf_str.split('|')[0]
        else:
            print(f"  Registry index {registry_idx} out of range")
            continue

        # Compute current hash
        try:
            dna_result = compute_dna(img_path)
            current_hash = dna_result['dna_hex']

            print(f"  Registry hash: {registry_hash}")
            print(f"  Current hash:  {current_hash}")

            if current_hash == registry_hash:
                print("  RESULT: MATCH ✅")
            else:
                print("  RESULT: MISMATCH ❌")
                # Find first difference
                for i, (a, b) in enumerate(zip(current_hash, registry_hash)):
                    if a != b:
                        print(f"  First difference at position {i}: '{a}' vs '{b}'")
                        break

        except Exception as e:
            print(f"  ERROR: {e}")

if __name__ == "__main__":
    verify_correct_matches()
