#!/usr/bin/env python3
"""
Image Registration with Duplicate Detection
===========================================

Registers a new image to the Merkle tree registry after checking for duplicates.
Images with >90% similarity to existing entries are flagged as plagiarized.
"""

import os
import sys
import json
import time
from typing import Dict, List, Tuple, Optional
from protrace.image_dna import compute_dna, dna_similarity, hamming_distance
from protrace.merkle import MerkleTree


def load_merkle_tree(filename: str = "merkle_tree.json") -> Tuple[MerkleTree, List[str]]:
    """Load existing Merkle tree from JSON file."""
    merkle = MerkleTree()
    dna_hashes = []
    
    if not os.path.exists(filename):
        print(f"⚠️  No existing tree found at {filename}. Creating new tree.")
        return merkle, dna_hashes
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    # Reconstruct leaves
    for leaf_hex in data['leaves']:
        leaf_bytes = bytes.fromhex(leaf_hex)
        merkle.leaves.append(leaf_bytes)
        
        # Extract DNA hash from leaf data
        leaf_str = leaf_bytes.decode('utf-8')
        dna_hex = leaf_str.split('|')[0]
        dna_hashes.append(dna_hex)
    
    # Rebuild tree
    if merkle.leaves:
        merkle.build_tree()
    
    print(f"✅ Loaded {len(merkle.leaves)} existing entries from registry")
    return merkle, dna_hashes


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


def check_for_duplicates(new_dna: str, existing_dnas: List[str], 
                         threshold: float = 0.90) -> Tuple[bool, Optional[Dict]]:
    """
    Check if new DNA matches any existing DNA above similarity threshold.
    
    Args:
        new_dna: DNA hash of new image
        existing_dnas: List of existing DNA hashes
        threshold: Similarity threshold (0.90 = 90%)
    
    Returns:
        (is_duplicate, match_info)
    """
    if not existing_dnas:
        return False, None
    
    max_similarity = 0.0
    best_match_idx = -1
    
    for idx, existing_dna in enumerate(existing_dnas):
        similarity = dna_similarity(new_dna, existing_dna)
        
        if similarity > max_similarity:
            max_similarity = similarity
            best_match_idx = idx
        
        # Early exit if we find a match above threshold
        if similarity >= threshold:
            match_info = {
                'index': idx,
                'similarity': similarity * 100,  # Convert to percentage
                'hamming_distance': hamming_distance(new_dna, existing_dna),
                'existing_dna': existing_dna
            }
            return True, match_info
    
    # Return best match even if below threshold
    if best_match_idx >= 0:
        match_info = {
            'index': best_match_idx,
            'similarity': max_similarity * 100,
            'hamming_distance': hamming_distance(new_dna, existing_dnas[best_match_idx]),
            'existing_dna': existing_dnas[best_match_idx]
        }
        return False, match_info
    
    return False, None


def register_image(image_path: str, pointer: str = None, 
                   platform_id: str = "manual", 
                   merkle_file: str = "merkle_tree.json",
                   similarity_threshold: float = 0.90) -> Dict:
    """
    Register a new image to the Merkle tree registry.
    
    Args:
        image_path: Path to image file
        pointer: Unique identifier (defaults to filename)
        platform_id: Platform identifier
        merkle_file: Path to Merkle tree JSON file
        similarity_threshold: Duplicate detection threshold (default 0.90 = 90%)
    
    Returns:
        Dictionary with registration result
    """
    print("\n" + "=" * 60)
    print("ProTrace Image Registration")
    print("=" * 60)
    
    # Validate image exists
    if not os.path.exists(image_path):
        return {
            'success': False,
            'error': f"Image not found: {image_path}"
        }
    
    # Set default pointer
    if pointer is None:
        pointer = os.path.basename(image_path)
    
    # Compute DNA
    print(f"\n📷 Computing DNA for: {os.path.basename(image_path)}")
    try:
        dna_result = compute_dna(image_path)
        new_dna = dna_result['dna_hex']
        print(f"✅ DNA computed: {new_dna[:32]}...")
    except Exception as e:
        return {
            'success': False,
            'error': f"Failed to compute DNA: {e}"
        }
    
    # Load existing tree
    print(f"\n📂 Loading registry from: {merkle_file}")
    merkle, existing_dnas = load_merkle_tree(merkle_file)
    
    # Check for duplicates
    print(f"\n🔍 Checking for duplicates (threshold: {similarity_threshold * 100}%)...")
    is_duplicate, match_info = check_for_duplicates(new_dna, existing_dnas, similarity_threshold)
    
    if is_duplicate:
        print(f"\n❌ PLAGIARISM DETECTED!")
        print(f"   Similarity: {match_info['similarity']:.2f}%")
        print(f"   Hamming Distance: {match_info['hamming_distance']} bits")
        print(f"   Matched Entry: #{match_info['index']}")
        print(f"   Existing DNA: {match_info['existing_dna'][:32]}...")
        print(f"\n🚫 Image REJECTED - Not added to registry")
        
        return {
            'success': False,
            'plagiarized': True,
            'dna': new_dna,
            'match': match_info,
            'reason': f"Image matches existing entry #{match_info['index']} with {match_info['similarity']:.2f}% similarity"
        }
    
    # Show best match if any
    if match_info:
        print(f"✅ No duplicates found")
        print(f"   Best match: {match_info['similarity']:.2f}% (Entry #{match_info['index']})")
        print(f"   Hamming Distance: {match_info['hamming_distance']} bits")
    else:
        print(f"✅ No duplicates found (first entry in registry)")
    
    # Add to tree
    print(f"\n➕ Adding to registry...")
    timestamp = int(time.time())
    merkle.add_leaf(new_dna, pointer=pointer, platform_id=platform_id, timestamp=timestamp)
    
    # Rebuild tree
    root_hash = merkle.build_tree()
    print(f"✅ Tree rebuilt")
    print(f"   New Root: {root_hash}")
    print(f"   Total Entries: {len(merkle.leaves)}")
    
    # Save tree
    save_merkle_tree(merkle, merkle_file)
    print(f"✅ Registry saved to: {merkle_file}")
    
    print(f"\n✅ SUCCESS - Image registered!")
    print("=" * 60)
    
    return {
        'success': True,
        'plagiarized': False,
        'dna': new_dna,
        'pointer': pointer,
        'platform_id': platform_id,
        'timestamp': timestamp,
        'root_hash': root_hash,
        'registry_size': len(merkle.leaves),
        'best_match': match_info
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python register_image.py <image_path> [pointer] [platform_id]")
        print("\nExample:")
        print("  python register_image.py new_image.png")
        print("  python register_image.py new_image.png my_nft opensea")
        sys.exit(1)
    
    image_path = sys.argv[1]
    pointer = sys.argv[2] if len(sys.argv) > 2 else None
    platform_id = sys.argv[3] if len(sys.argv) > 3 else "manual"
    
    result = register_image(image_path, pointer, platform_id)
    
    # Exit with error code if registration failed
    if not result['success']:
        sys.exit(1)


if __name__ == "__main__":
    main()
