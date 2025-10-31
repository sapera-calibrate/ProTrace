#!/usr/bin/env python3
"""
Debug hash computation and comparison
"""

import os
from protrace.image_dna import compute_dna

def debug_hashes():
    """Debug hash computation for specific images."""

    # Test images
    test_pairs = [
        ("tobe_minted/cccc20777.png", "Folder X/# (433).png"),
        ("tobe_minted/ccccc (222).png", "Folder X/# (450).png"),
        ("tobe_minted/neeed# (1).png", "Folder X/# (517).png"),
        ("tobe_minted/neeed# (3).png", "Folder X/# (511).png"),
    ]

    print("DEBUG: Computing DNA hashes for claimed duplicate pairs")
    print("=" * 60)

    for duplicate_path, original_path in test_pairs:
        print(f"\nChecking pair:")
        print(f"  Duplicate: {duplicate_path}")
        print(f"  Original:  {original_path}")

        # Compute duplicate hash
        if os.path.exists(duplicate_path):
            try:
                dup_result = compute_dna(duplicate_path)
                dup_hash = dup_result['dna_hex']
                print(f"  Duplicate DNA: {dup_hash[:32]}...")
            except Exception as e:
                print(f"  ERROR computing duplicate: {e}")
                continue
        else:
            print(f"  ERROR: Duplicate file not found: {duplicate_path}")
            continue

        # Compute original hash
        if os.path.exists(original_path):
            try:
                orig_result = compute_dna(original_path)
                orig_hash = orig_result['dna_hex']
                print(f"  Original DNA:  {orig_hash[:32]}...")
            except Exception as e:
                print(f"  ERROR computing original: {e}")
                continue
        else:
            print(f"  ERROR: Original file not found: {original_path}")
            continue

        # Compare
        if dup_hash == orig_hash:
            print("  RESULT: IDENTICAL HASHES ❌ (Should be unique!)")
        else:
            print("  RESULT: DIFFERENT HASHES ✅ (Are unique)")
            # Show first difference
            for i, (a, b) in enumerate(zip(dup_hash, orig_hash)):
                if a != b:
                    print(f"  First difference at position {i}: '{a}' vs '{b}'")
                    break

        print("-" * 40)

if __name__ == "__main__":
    debug_hashes()
