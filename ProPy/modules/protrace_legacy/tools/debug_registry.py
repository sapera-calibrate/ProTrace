#!/usr/bin/env python3
"""
Debug registry format
"""

def debug_registry():
    """Debug the registry data format."""

    with open("merkle_tree.json", 'r') as f:
        data = json.load(f)

    # Take first leaf
    first_leaf_hex = data['leaves'][0]
    print(f"First leaf hex: {first_leaf_hex}")

    # Decode from hex to bytes
    leaf_bytes = bytes.fromhex(first_leaf_hex)
    print(f"Decoded bytes length: {len(leaf_bytes)}")

    # Convert to string
    leaf_str = leaf_bytes.decode('utf-8')
    print(f"Decoded string: {leaf_str}")

    # Split by |
    parts = leaf_str.split('|')
    print(f"Parts: {parts}")
    print(f"DNA hash: {parts[0]}")
    print(f"Pointer: {parts[1]}")
    print(f"Platform: {parts[2]}")
    print(f"Timestamp: {parts[3]}")

if __name__ == "__main__":
    import json
    debug_registry()
