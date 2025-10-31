#!/usr/bin/env python3
"""
Check specific registry entries
"""

import json

def check_registry_entries():
    """Check the specific registry entries that were claimed to match"""

    with open("merkle_tree.json", 'r') as f:
        data = json.load(f)

    # Indices from find_matches.py
    indices_to_check = [433, 450, 511, 517]

    print("Registry entries for claimed matches:")
    print("=" * 50)

    for idx in indices_to_check:
        if idx < len(data['leaves']):
            leaf_hex = data['leaves'][idx]
            leaf_bytes = bytes.fromhex(leaf_hex)
            leaf_str = leaf_bytes.decode('utf-8')
            dna_hex = leaf_str.split('|')[0]
            pointer = leaf_str.split('|')[1]

            print(f"Index {idx}: {pointer}")
            print(f"DNA: {dna_hex}")
            print()

if __name__ == "__main__":
    check_registry_entries()
