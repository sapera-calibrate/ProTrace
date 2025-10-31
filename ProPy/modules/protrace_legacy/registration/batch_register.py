#!/usr/bin/env python3
"""
Batch Registration: Process Images in Folder
===========================================

Computes DNA hash for each image and adds to Merkle tree if unique.
Rejects if exact hash already exists in registry.
"""

import os
import sys
import json
import time
from typing import List
from protrace.image_dna import compute_dna
from protrace.merkle import MerkleTree


def load_existing_hashes(merkle_file: str = "merkle_tree.json") -> set:
    """Load existing DNA hashes from registry."""
    if not os.path.exists(merkle_file):
        return set()
    
    with open(merkle_file, 'r') as f:
        data = json.load(f)
    
    existing_hashes = set()
    for leaf_hex in data['leaves']:
        leaf_bytes = bytes.fromhex(leaf_hex)
        leaf_str = leaf_bytes.decode('utf-8')
        dna_hex = leaf_str.split('|')[0]
        existing_hashes.add(dna_hex)
    
    return existing_hashes


def load_merkle_tree(merkle_file: str = "merkle_tree.json") -> MerkleTree:
    """Load existing Merkle tree."""
    merkle = MerkleTree()
    
    if not os.path.exists(merkle_file):
        return merkle
    
    with open(merkle_file, 'r') as f:
        data = json.load(f)
    
    # Reconstruct leaves
    for leaf_hex in data['leaves']:
        leaf_bytes = bytes.fromhex(leaf_hex)
        merkle.leaves.append(leaf_bytes)
    
    # Rebuild tree if leaves exist
    if merkle.leaves:
        merkle.build_tree()
    
    return merkle


def save_merkle_tree(merkle: MerkleTree, filename: str = "merkle_tree.json"):
    """Save Merkle tree to JSON file."""
    leaves_serialized = [leaf.hex() for leaf in merkle.leaves]
    root_hex = merkle.root.hash.hex() if merkle.root else None
    
    data = {
        'leaves': leaves_serialized,
        'root_hash': root_hex,
        'leaf_count': len(merkle.leaves)
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def process_folder(folder_path: str, merkle_file: str = "merkle_tree.json"):
    """Process all images in folder for registration."""
    
    # Find images
    extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
    images = []
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.lower().endswith(extensions):
                images.append(os.path.join(folder_path, file))
    
    if not images:
        print("No images found in folder.")
        return
    
    print(f"Found {len(images)} images to process.")
    
    # Load existing registry
    existing_hashes = load_existing_hashes(merkle_file)
    merkle = load_merkle_tree(merkle_file)
    
    print(f"Registry has {len(existing_hashes)} existing hashes.")
    
    # Process each image
    accepted = 0
    rejected = 0
    
    for img_path in images:
        filename = os.path.basename(img_path)
        
        try:
            # Compute DNA
            dna_result = compute_dna(img_path)
            dna_hex = dna_result['dna_hex']
            
            # Check if exists
            if dna_hex in existing_hashes:
                print(f"REJECT: {filename}")
                rejected += 1
            else:
                # Add to registry
                timestamp = int(time.time())
                merkle.add_leaf(dna_hex, pointer=filename, platform_id='batch', timestamp=timestamp)
                existing_hashes.add(dna_hex)
                print(f"ACCEPT: {filename}")
                accepted += 1
                
        except Exception as e:
            print(f"ERROR: {filename} - {e}")
    
    # Rebuild and save tree if any accepted
    if accepted > 0:
        root_hash = merkle.build_tree()
        save_merkle_tree(merkle, merkle_file)
        print(f"\nUpdated registry with {accepted} new images.")
        print(f"New registry size: {len(merkle.leaves)} images")
        print(f"Root hash: {root_hash}")
    
    print(f"\nSummary: {accepted} accepted, {rejected} rejected")


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_register.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    process_folder(folder_path)


if __name__ == "__main__":
    main()
