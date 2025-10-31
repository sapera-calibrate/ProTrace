#!/usr/bin/env python3
"""
Find Matching Hashes: Identify which registry images match rejected ones
"""

import os
import json
from protrace.image_dna import compute_dna


def load_registry_data(merkle_file: str = "merkle_tree.json"):
    """Load registry and extract image info."""
    if not os.path.exists(merkle_file):
        return []
    
    with open(merkle_file, 'r') as f:
        data = json.load(f)
    
    registry_entries = []
    for i, leaf_hex in enumerate(data['leaves']):
        leaf_bytes = bytes.fromhex(leaf_hex)
        leaf_str = leaf_bytes.decode('utf-8')
        parts = leaf_str.split('|')
        dna_hex = parts[0]
        pointer = parts[1]
        platform_id = parts[2]
        timestamp = int(parts[3])
        
        registry_entries.append({
            'index': i,
            'dna': dna_hex,
            'pointer': pointer,
            'platform_id': platform_id,
            'timestamp': timestamp
        })
    
    return registry_entries


def find_matches(rejected_images, folder_path="tobe_minted"):
    """Find which registry images match the rejected ones."""
    
    # Load registry
    registry = load_registry_data()
    if not registry:
        print("No registry found.")
        return
    
    # Create hash to registry entries mapping
    hash_to_entries = {}
    for entry in registry:
        dna = entry['dna']
        if dna not in hash_to_entries:
            hash_to_entries[dna] = []
        hash_to_entries[dna].append(entry)
    
    # Process rejected images
    matches = {}
    for img_name in rejected_images:
        img_path = os.path.join(folder_path, img_name)
        if not os.path.exists(img_path):
            continue
        
        try:
            dna_result = compute_dna(img_path)
            rejected_dna = dna_result['dna_hex']
            
            if rejected_dna in hash_to_entries:
                matches[img_name] = {
                    'rejected_dna': rejected_dna,
                    'matching_entries': hash_to_entries[rejected_dna]
                }
        except Exception as e:
            print(f"Error processing {img_name}: {e}")
    
    return matches


def main():
    # Rejected images from previous batch
    rejected_images = [
        "cccc20777.png",
        "ccccc (222).png", 
        "neeed# (1).png",
        "neeed# (3).png"
    ]
    
    print("Finding registry matches for rejected images...")
    print("=" * 50)
    
    matches = find_matches(rejected_images)
    
    for rejected_img, match_info in matches.items():
        print(f"\nRejected: {rejected_img}")
        print(f"DNA: {match_info['rejected_dna']}")
        print("Matches in registry:")
        
        for entry in match_info['matching_entries']:
            print(f"  Index: {entry['index']}")
            print(f"  Pointer: {entry['pointer']}")
            print(f"  Platform: {entry['platform_id']}")
            print(f"  Timestamp: {entry['timestamp']}")
            print()


if __name__ == "__main__":
    main()
